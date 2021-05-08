#!/usr/bin/env python

from enum import IntEnum

from PyQt5.QtCore import Qt, QPersistentModelIndex, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QMouseEvent
from PyQt5.QtWidgets import QAbstractItemView, QComboBox, QLabel, QMenu, QCheckBox

from electrum.i18n import _
from electrum.util import ipfs_explorer_URL, profiler, format_satoshis

from .util import MyTreeView, MONOSPACE_FONT, webopen


class AssetList(MyTreeView):
    class Columns(IntEnum):
        NAME = 0
        BALANCE = 1
        IPFS = 2
        REISSUABLE = 3
        DIVISIONS = 4

    filter_columns = [Columns.NAME, Columns.BALANCE, Columns.IPFS, Columns.REISSUABLE, Columns.DIVISIONS]

    def __init__(self, parent=None):
        super().__init__(parent, self.create_menu, stretch_column=None)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setModel(QStandardItemModel(self))
        self.asset_meta = {}
        self.update()

    def on_hide_toolbar(self):
        self.update()

    def get_toolbar_buttons(self):
        return tuple()

    def webopen_safe(self, url):
        show_warn = self.parent.config.get('show_ipfs_warning', True)
        if show_warn:
            cb = QCheckBox(_("Don't show this message again."))
            cb_checked = False
            def on_cb(x):
                nonlocal cb_checked
                cb_checked = x == Qt.Checked

            cb.stateChanged.connect(on_cb)
            goto = self.parent.question(_('You are about to visit:\n\n'
                                          '{}\n\n'
                                          'IPFS hashes can link to anything. Please follow '
                                          'safe practices and common sense. If you are unsure '
                                          'about what\'s on the other end of an IPFS, don\'t '
                                          'visit it!\n\n'
                                          'Are you sure you want to continue?').format(url),
                                        title=_('Warning: External Data'), checkbox=cb)

            if cb_checked:
                self.parent.config.set_key('show_ipfs_warning', False)
            if goto:
                webopen(url)
        else:
            webopen(url)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        idx = self.indexAt(event.pos())
        if not idx.isValid():
            return
        selected = self.selected_in_column(self.Columns.IPFS)
        multi_select = len(selected) > 1
        ipfses = [self.model().itemFromIndex(item).text() for item in selected]
        if not multi_select:
            ipfs = ipfses[0]
            if ipfs:
                url = ipfs_explorer_URL(self.parent.config, 'ipfs', ipfs)
                self.webopen_safe(url)


    def refresh_headers(self):
        headers = {
            self.Columns.NAME: _('Name'),
            self.Columns.BALANCE: _('Balance'),
            self.Columns.IPFS: _('IPFS'),
            self.Columns.REISSUABLE: _('Reissuable'),
            self.Columns.DIVISIONS: _('Decimals'),
        }
        self.update_headers(headers)

    @profiler
    def update(self):

        self.wallet = self.parent.wallet
        addr_list = self.wallet.get_addresses()
        self.model().clear()
        self.asset_meta.clear()

        current_asset = self.current_item_user_role(col=self.Columns.IPFS)
        set_asset = None
        self.refresh_headers()

        assets = {}

        for address in addr_list:
            for asset, (c, u, x) in self.wallet.get_addr_balance(address)['ASSETS'].items():
                if asset in assets:
                    assets[asset]['balance'] += (c + u + x)
                else:
                    meta = self.wallet.get_or_request_asset_meta(self.parent.network, asset)
                    meta['balance'] = (c + u + x)
                    assets[asset] = meta

        for asset, meta in assets.items():

            self.asset_meta[asset] = meta  # 'Deep' copy

            balance = meta['balance']
            reissuable = ''
            if 'reissuable' in meta:
                reissuable = str('No' if meta['reissuable'] == 0 else 'Yes')
            divisions = ''
            div_amt = 0
            if 'divisions' in meta:
                div_amt = meta['divisions']
                divisions = str(div_amt)
            ipfs = ''
            if 'ipfs' in meta:
                ipfs = meta['ipfs']

            balance_text = format_satoshis(
                balance, div_amt, self.parent.decimal_point, is_diff=False, whitespaces=False)

            labels = [asset, balance_text, ipfs, reissuable, divisions]
            address_item = [QStandardItem(e) for e in labels]
            # align text and set fonts
            for i, item in enumerate(address_item):
                item.setTextAlignment(Qt.AlignVCenter)
                if i not in (self.Columns.NAME, self.Columns.IPFS):
                    item.setFont(QFont(MONOSPACE_FONT))
                item.setEditable(i in self.editable_columns)

            # address_item[self.Columns.BALANCE].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            count = self.model().rowCount()
            self.model().insertRow(count, address_item)
            address_idx = self.model().index(count, self.Columns.IPFS)

            if asset == current_asset:
                set_address = QPersistentModelIndex(address_idx)

        self.set_current_idx(set_asset)

        self.filter()

    def create_menu(self, position):
        selected = self.selected_in_column(self.Columns.NAME)
        if not selected:
            return
        multi_select = len(selected) > 1
        assets = [self.model().itemFromIndex(item).text() for item in selected]
        menu = QMenu()
        if not multi_select:
            idx = self.indexAt(position)
            if not idx.isValid():
                return
            col = idx.column()
            item = self.model().itemFromIndex(idx)
            if not item:
                return
            asset = assets[0]

            column_title = self.model().horizontalHeaderItem(col).text()
            copy_text = self.model().itemFromIndex(idx).text()
            if col == self.Columns.BALANCE:
                copy_text = copy_text.strip()
            menu.addAction(_("Copy {}").format(column_title), lambda: self.place_text_on_clipboard(copy_text))
            menu.addAction(_('Send {}').format(asset), lambda: ())
            if asset in self.asset_meta and \
                    'ipfs' in self.asset_meta[asset]:
                url = ipfs_explorer_URL(self.parent.config, 'ipfs', self.asset_meta[asset]['ipfs'])
                menu.addAction(_('View IPFS'), lambda: self.webopen_safe(url))
            menu.addAction(_('View History'), lambda: self.parent.show_asset(asset))
            menu.addAction(_('Mark as spam'), lambda: ())

        menu.exec_(self.viewport().mapToGlobal(position))

    def place_text_on_clipboard(self, text):
        self.parent.app.clipboard().setText(text)
