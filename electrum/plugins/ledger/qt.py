from functools import partial

from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import QInputDialog, QLabel, QVBoxLayout, QLineEdit, QWidget, QPushButton

from electrum.i18n import _
from electrum.plugin import hook
from electrum.wallet import Standard_Wallet
from electrum.gui.qt.util import WindowModalDialog

from .ledger import LedgerPlugin, AtomicBoolean
from ..hw_wallet.qt import QtHandlerBase, QtPluginBase
from ..hw_wallet.plugin import only_hook_if_libraries_available


class Plugin(LedgerPlugin, QtPluginBase):
    icon_unpaired = "ledger_unpaired.png"
    icon_paired = "ledger.png"

    def create_handler(self, window):
        return Ledger_Handler(window)

    @only_hook_if_libraries_available
    @hook
    def receive_menu(self, menu, addrs, wallet):
        if type(wallet) is not Standard_Wallet:
            return
        keystore = wallet.get_keystore()
        if type(keystore) == self.keystore_class and len(addrs) == 1:
            def show_address():
                keystore.thread.add(partial(self.show_address, wallet, addrs[0]))

            menu.addAction(_("Show on Ledger"), show_address)

class Abstract_Ledger_UI(WindowModalDialog):
    def __init__(self, atomic_b: AtomicBoolean, parent=None, title='Abstract Ledger UI Title'):
        super().__init__(parent, title)
        # self.setWindowModality(Qt.NonModal)
        # Thread interrupter. If we cancel, set true
        self.atomic_b = atomic_b
        self.label = QLabel('')
        self.label.setText("Generating Information...")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.cancel = QPushButton('Cancel')

        def end():
            self.finished()
            self.close()
            self.atomic_b.set_true()
        self.cancel.clicked.connect(end)
        layout.addWidget(self.cancel)

        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_text)

    # Implemented in subclasses
    def begin(self):
        self.timer.start(500)

    def finished(self):
        self.timer.stop()

    def update_text(self):
        pass

class Parsing_UI(Abstract_Ledger_UI):
    def __init__(self, parse_data, atomic_b, parent=None):
        super().__init__(atomic_b, parent, 'Parsing Transaction...')
        self.parse_data = parse_data

    def update_text(self):
        self.label.setText(self.parse_data.parsed_string())

class Signing_UI(Abstract_Ledger_UI):
    def __init__(self, parse_data, atomic_b, parent=None):
        super().__init__(atomic_b, parent, 'Signing Transaction...')
        self.parse_data = parse_data

    def update_text(self):
        self.label.setText(self.parse_data.parsed_string())


class Ledger_Handler(QtHandlerBase):
    setup_signal = pyqtSignal()
    auth_signal = pyqtSignal(object)
    parse_start_signal = pyqtSignal(object, object)
    parse_stop_signal = pyqtSignal()
    signing_start_signal = pyqtSignal(object, object)
    signing_stop_signal = pyqtSignal()

    def __init__(self, win):
        super(Ledger_Handler, self).__init__(win, 'Ledger')
        self.setup_signal.connect(self.setup_dialog)
        self.auth_signal.connect(self.auth_dialog)
        self.parse_start_signal.connect(self.parse_dialog)
        self.parse_stop_signal.connect(self.stop_parse_dialog)
        self.signing_start_signal.connect(self.signing_dialog)
        self.signing_stop_signal.connect(self.stop_signing_dialog)

    def word_dialog(self, msg):
        response = QInputDialog.getText(self.top_level_window(), "Ledger Wallet Authentication", msg,
                                        QLineEdit.Password)
        if not response[1]:
            self.word = None
        else:
            self.word = str(response[0])
        self.done.set()

    def parse_dialog(self, stopped_boolean, parse_data):
        self.clear_dialog()
        self.dialog = Parsing_UI(parse_data, stopped_boolean, self.top_level_window())
        self.dialog.show()
        self.dialog.begin()

    def signing_dialog(self, stopped_boolean, parse_data):
        self.clear_dialog()
        self.dialog = Signing_UI(parse_data, stopped_boolean, self.top_level_window())
        self.dialog.show()
        self.dialog.begin()

    def stop_parse_dialog(self):
        if self.dialog is Parsing_UI:
            self.dialog.finished()

    def stop_signing_dialog(self):
        if self.dialog is Signing_UI:
            self.dialog.finished()

    def message_dialog(self, msg):
        self.clear_dialog()
        self.dialog = dialog = WindowModalDialog(self.top_level_window(), _("Ledger Status"))
        l = QLabel(msg)
        vbox = QVBoxLayout(dialog)
        vbox.addWidget(l)
        dialog.show()

    def auth_dialog(self, data):
        try:
            from .auth2fa import LedgerAuthDialog
        except ImportError as e:
            self.message_dialog(str(e))
            return
        dialog = LedgerAuthDialog(self, data)
        dialog.exec_()
        self.word = dialog.pin
        self.done.set()

    def get_auth(self, data):
        self.done.clear()
        self.auth_signal.emit(data)
        self.done.wait()
        return self.word

    def get_setup(self):
        self.done.clear()
        self.setup_signal.emit()
        self.done.wait()
        return

    def get_parse_ui(self, atomic_b, data):
        self.parse_start_signal.emit(atomic_b, data)
        return

    def finished_parse(self):
        self.parse_stop_signal.emit()
        return

    def get_signing_ui(self, atomic_b, data):
        self.signing_start_signal.emit(atomic_b, data)
        return

    def finished_signing(self):
        self.signing_stop_signal.emit()
        return

    def setup_dialog(self):
        self.show_error(_('Initialization of Ledger HW devices is currently disabled.'))
