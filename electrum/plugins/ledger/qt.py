from functools import partial

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QInputDialog, QLabel, QVBoxLayout, QLineEdit

from electrum.i18n import _
from electrum.plugin import hook
from electrum.wallet import Standard_Wallet
from electrum.gui.qt.util import WindowModalDialog

from .ledger import LedgerPlugin
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


class Ledger_Handler(QtHandlerBase):
    setup_signal = pyqtSignal()
    auth_signal = pyqtSignal(object)
    parse_signal = pyqtSignal(object, object)

    def __init__(self, win):
        super(Ledger_Handler, self).__init__(win, 'Ledger')
        self.setup_signal.connect(self.setup_dialog)
        self.auth_signal.connect(self.auth_dialog)
        self.parse_signal.connect(self.parse_dialog)
        self.loop_ui = False

    def word_dialog(self, msg):
        response = QInputDialog.getText(self.top_level_window(), "Ledger Wallet Authentication", msg,
                                        QLineEdit.Password)
        if not response[1]:
            self.word = None
        else:
            self.word = str(response[0])
        self.done.set()

    def parse_dialog(self, ui_tracker, start):
        if start:
            self.loop_ui = True
            self.clear_dialog()
            self.dialog = dialog = WindowModalDialog(self.top_level_window(), _("Ledger Status"))
            label = QLabel(ui_tracker.parsed_string())

            def update():
                label.setText(ui_tracker.parsed_string())
                if self.loop_ui:
                    QTimer.singleShot(500, update)

            update()
            vbox = QVBoxLayout(dialog)
            vbox.addWidget(label)
            dialog.show()
        else:
            self.loop_ui = False

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

    def parse_ui(self, ui_tracker, start=True):
        self.loop_ui = True
        self.clear_dialog()
        self.parse_signal.emit(ui_tracker, start)

    def setup_dialog(self):
        self.show_error(_('Initialization of Ledger HW devices is currently disabled.'))
