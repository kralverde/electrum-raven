#!/usr/bin/env python

from enum import IntEnum

from PyQt5.QtCore import Qt, QPersistentModelIndex, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import QAbstractItemView, QComboBox, QLabel, QMenu

from electrum.i18n import _
from electrum.util import block_explorer_URL, profiler, format_satoshis
from electrum.plugin import run_hook
from electrum.bitcoin import is_address
from electrum.wallet import InternalAddressCorruption

from .util import MyTreeView, MONOSPACE_FONT, ColorScheme, webopen


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
        self.update()

    def on_hide_toolbar(self):
        self.update()

    def get_toolbar_buttons(self):
        return QLabel(_("TEST")),

    def toggle_change(self, state):
        self.update()

    def toggle_used(self, state):
        self.update()

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

        current_asset = self.current_item_user_role(col=self.Columns.IPFS)
        set_asset = None
        self.refresh_headers()

        assets = {}

        for address in addr_list:
            for asset, (c, u, x) in self.wallet.get_addr_balance(address)['ASSETS'].items():
                if asset in assets:
                    assets[asset]['balance'] += (c+u+x)
                else:
                    meta = self.wallet.get_or_request_asset_meta(self.parent.network, asset)
                    meta['balance'] = (c+u+x)
                    assets[asset] = meta

        for asset, meta in assets.items():

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

            #address_item[self.Columns.BALANCE].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            count = self.model().rowCount()
            self.model().insertRow(count, address_item)
            address_idx = self.model().index(count, self.Columns.IPFS)

            if asset == current_asset:
                set_address = QPersistentModelIndex(address_idx)

        self.set_current_idx(set_asset)

        self.filter()

    def create_menu(self, position):
        from electrum.wallet import Multisig_Wallet
        is_multisig = isinstance(self.wallet, Multisig_Wallet)
        can_delete = self.wallet.can_delete_address()
        selected = self.selected_in_column(self.Columns.ADDRESS)
        if not selected:
            return
        multi_select = len(selected) > 1
        addrs = [self.model().itemFromIndex(item).text() for item in selected]
        menu = QMenu()
        if not multi_select:
            idx = self.indexAt(position)
            if not idx.isValid():
                return
            col = idx.column()
            item = self.model().itemFromIndex(idx)
            if not item:
                return
            addr = addrs[0]

            addr_column_title = self.model().horizontalHeaderItem(self.Columns.IPFS).text()
            addr_idx = idx.sibling(idx.row(), self.Columns.LABEL)

            column_title = self.model().horizontalHeaderItem(col).text()
            copy_text = self.model().itemFromIndex(idx).text()
            if col == self.Columns.COIN_BALANCE or col == self.Columns.FIAT_BALANCE:
                copy_text = copy_text.strip()
            menu.addAction(_("Copy {}").format(column_title), lambda: self.place_text_on_clipboard(copy_text))
            menu.addAction(_('Details'), lambda: self.parent.show_address(addr))
            persistent = QPersistentModelIndex(addr_idx)
            menu.addAction(_("Edit {}").format(addr_column_title), lambda p=persistent: self.edit(QModelIndex(p)))
            menu.addAction(_("Request payment"), lambda: self.parent.receive_at(addr))
            if self.wallet.can_export():
                menu.addAction(_("Private key"), lambda: self.parent.show_private_key(addr))
            if not is_multisig and not self.wallet.is_watching_only():
                menu.addAction(_("Sign/verify message"), lambda: self.parent.sign_verify_message(addr))
                menu.addAction(_("Encrypt/decrypt message"), lambda: self.parent.encrypt_message(addr))
            if can_delete:
                menu.addAction(_("Remove from wallet"), lambda: self.parent.remove_address(addr))
            addr_URL = block_explorer_URL(self.config, 'addr', addr)
            if addr_URL:
                menu.addAction(_("View on block explorer"), lambda: webopen(addr_URL))

            if not self.wallet.is_frozen_address(addr):
                menu.addAction(_("Freeze"), lambda: self.parent.set_frozen_state_of_addresses([addr], True))
            else:
                menu.addAction(_("Unfreeze"), lambda: self.parent.set_frozen_state_of_addresses([addr], False))

        coins = self.wallet.get_spendable_coins(addrs, config=self.config)
        if coins:
            menu.addAction(_("Spend from"), lambda: self.parent.spend_coins(coins))

        run_hook('receive_menu', menu, addrs, self.wallet)
        menu.exec_(self.viewport().mapToGlobal(position))

    def place_text_on_clipboard(self, text):
        if is_address(text):
            try:
                self.wallet.check_address(text)
            except InternalAddressCorruption as e:
                self.parent.show_error(str(e))
                raise
        self.parent.app.clipboard().setText(text)
