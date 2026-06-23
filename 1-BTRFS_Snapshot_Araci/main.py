#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtGui, QtCore
import btrfs_helper

def elevate_privileges():
    """
    Uygulamanın root (yetkili kullanıcı) haklarıyla çalışmasını sağlar.
    Eğer yetkili değilse pkexec ile kendini yeniden başlatır.
    Hem X11 hem de Wayland oturumlarını destekler.
    """
    if os.geteuid() != 0:
        script_path = os.path.abspath(sys.argv[0])
        display = os.environ.get("DISPLAY", ":0")
        xauth = os.environ.get("XAUTHORITY")
        if not xauth:
            xauth = "/home/yms/.Xauthority"
            if not os.path.exists(xauth):
                xauth = os.path.expanduser("~/.Xauthority")

        wayland_disp = os.environ.get("WAYLAND_DISPLAY", "")
        xdg_runtime = os.environ.get("XDG_RUNTIME_DIR", "")

        # Yerel grafik sunucu bağlantılarına izin ver
        try:
            subprocess.run(["xhost", "+local:"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        cmd = ["pkexec", "env", f"DISPLAY={display}", f"XAUTHORITY={xauth}"]
        if wayland_disp:
            cmd.append(f"WAYLAND_DISPLAY={wayland_disp}")
        if xdg_runtime:
            cmd.append(f"XDG_RUNTIME_DIR={xdg_runtime}")

        cmd += [sys.executable, script_path] + sys.argv[1:]
        try:
            # pkexec üzerinden uygulamayı çalıştır
            result = subprocess.run(cmd)
            sys.exit(result.returncode)
        except Exception as e:
            # Şifre girilmez veya pencere kapatılırsa uygulamayı sonlandır
            print(f"Yetki yükseltme hatası: {e}")
            sys.exit(1)

class BtrfsSnapshotApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pardus BTRFS Snapshot ve Geri Yükleme Aracı")
        self.resize(900, 640)
        
        # Uygulama ikon dosyasını yükle
        self._app_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(self._app_dir, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        else:
            self.setWindowIcon(QtGui.QIcon.fromTheme("system-backup"))
        
        # Mevcut tema (dark / light)
        self._theme = "dark"
        
        # Stil dosyasını yükle
        self.load_stylesheet()
        
        # Arayüzü oluştur
        self.init_ui()
        
        # Başlangıçta koyu temayı uygula
        self.apply_theme("dark")
        
        # Dosya sistemi kontrolü
        self.check_system()
        
        # Listeyi ilk kez doldur
        self.refresh_list()

    def load_stylesheet(self):
        """style.qss dosyasını okur ve ara yüze uygular."""
        css_path = os.path.join(self._app_dir, "style.qss")
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def apply_theme(self, theme):
        """Tüm widget'lara tema property'sini uygular ve stili yeniler."""
        self._theme = theme
        self._set_theme_recursive(self.centralWidget(), theme)
        self._set_theme_recursive(self, theme)
        # Status barı da güncelle
        self.statusBar().setProperty("theme", theme)
        self.style().unpolish(self.statusBar())
        self.style().polish(self.statusBar())
        self.update()

    def _set_theme_recursive(self, widget, theme):
        """Verilen widget ve tüm çocuklarına tema uygular."""
        if widget is None:
            return
        widget.setProperty("theme", theme)
        self.style().unpolish(widget)
        self.style().polish(widget)
        widget.update()
        for child in widget.findChildren(QtWidgets.QWidget):
            child.setProperty("theme", theme)
            self.style().unpolish(child)
            self.style().polish(child)
            child.update()

    def init_ui(self):
        # Ana widget ve layout
        central_widget = QtWidgets.QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 1. Başlık ve Bilgi Alanı (Header Frame)
        header_frame = QtWidgets.QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 10, 16, 10)

        # Sol: Uygulama ikonu + Başlık
        icon_path = os.path.join(self._app_dir, "icon.png")
        if os.path.exists(icon_path):
            app_icon_lbl = QtWidgets.QLabel()
            app_icon_lbl.setPixmap(QtGui.QPixmap(icon_path).scaled(36, 36, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            header_layout.addWidget(app_icon_lbl)

        title_block = QtWidgets.QVBoxLayout()
        title_block.setSpacing(1)
        self.title_label = QtWidgets.QLabel("BTRFS Snapshot Yöneticisi")
        self.title_label.setObjectName("titleLabel")
        sub_label = QtWidgets.QLabel("Pardus Sistem Yedekleme ve Geri Yükleme Aracı")
        sub_label.setObjectName("subtitleLabel")
        title_block.addWidget(self.title_label)
        title_block.addWidget(sub_label)
        header_layout.addLayout(title_block)
        header_layout.addStretch()

        # Sağ: Tema geçiş butonu
        self.theme_toggle_btn = QtWidgets.QPushButton("🌙")
        self.theme_toggle_btn.setObjectName("themeToggleBtn")
        self.theme_toggle_btn.setToolTip("Aydınlık / Koyu Tema")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_toggle_btn)

        main_layout.addWidget(header_frame)

        # 2. Dosya Sistemi Durum Paneli
        self.status_frame = QtWidgets.QFrame()
        self.status_frame.setObjectName("statusFrame")
        status_layout = QtWidgets.QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(12, 8, 12, 8)
        
        self.status_icon = QtWidgets.QLabel()
        self.status_icon.setPixmap(QtGui.QIcon.fromTheme("dialog-information").pixmap(24, 24))
        status_layout.addWidget(self.status_icon)
        
        self.status_label = QtWidgets.QLabel("Dosya sistemi kontrol ediliyor...")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label, 1)
        
        main_layout.addWidget(self.status_frame)

        # 3. Snapshot Alma Form Alanı (Action Frame)
        self.action_frame = QtWidgets.QFrame()
        self.action_frame.setObjectName("actionFrame")
        action_layout = QtWidgets.QHBoxLayout(self.action_frame)
        
        self.desc_input = QtWidgets.QLineEdit()
        self.desc_input.setPlaceholderText("Anlık görüntü (Snapshot) açıklaması yazın (isteğe bağlı)...")
        action_layout.addWidget(self.desc_input, 1)
        
        self.backup_btn = QtWidgets.QPushButton("Sistemi Yedekle")
        self.backup_btn.setObjectName("backupButton")
        self.backup_btn.setIcon(QtGui.QIcon.fromTheme("document-save"))
        self.backup_btn.clicked.connect(self.take_snapshot)
        action_layout.addWidget(self.backup_btn)
        
        main_layout.addWidget(self.action_frame)

        # 3.5. Otomatik Yedekleme Seçeneği
        self.auto_backup_cb = QtWidgets.QCheckBox("2 Saatte Bir Otomatik Sistem Yedeği Al (Systemd Zamanlayıcısı)")
        self.auto_backup_cb.setObjectName("autoBackupCheckBox")
        self.auto_backup_cb.setChecked(btrfs_helper.is_auto_backup_enabled())
        self.auto_backup_cb.toggled.connect(self.toggle_auto_backup)
        main_layout.addWidget(self.auto_backup_cb)

        # 4. Tablo Listesi
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Subvolume ID", "Oluşturulma Tarihi", "Açıklama / İsim", "Dosya Yolu"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        main_layout.addWidget(self.table)

        # 5. Alt Butonlar (Yenile, Geri Yükle, Sil)
        bottom_layout = QtWidgets.QHBoxLayout()
        
        self.refresh_btn = QtWidgets.QPushButton("Yenile")
        self.refresh_btn.setIcon(QtGui.QIcon.fromTheme("view-refresh"))
        self.refresh_btn.clicked.connect(self.refresh_list)
        bottom_layout.addWidget(self.refresh_btn)
        
        bottom_layout.addStretch()
        
        self.delete_btn = QtWidgets.QPushButton("Yedeği Sil")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.setIcon(QtGui.QIcon.fromTheme("edit-delete"))
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_selected)
        bottom_layout.addWidget(self.delete_btn)
        
        self.restore_btn = QtWidgets.QPushButton("Geri Yükle")
        self.restore_btn.setObjectName("restoreButton")
        self.restore_btn.setIcon(QtGui.QIcon.fromTheme("system-reboot"))
        self.restore_btn.setEnabled(False)
        self.restore_btn.clicked.connect(self.restore_selected)
        bottom_layout.addWidget(self.restore_btn)
        
        main_layout.addLayout(bottom_layout)

    def check_system(self):
        """Sistemin BTRFS olup olmadığını kontrol eder."""
        if not btrfs_helper.is_btrfs():
            # Hata durumunu güncelle
            self.status_icon.setPixmap(QtGui.QIcon.fromTheme("dialog-error").pixmap(24, 24))
            self.status_label.setText("Hata: Kök dizin (/) BTRFS dosya sistemi olarak kurulmamış!")
            self.status_label.setStyleSheet("color: #f28b82; font-weight: bold; background: transparent;")
            
            # Kontrolleri kilitle
            self.desc_input.setEnabled(False)
            self.backup_btn.setEnabled(False)
            self.auto_backup_cb.setEnabled(False)
            self.table.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.restore_btn.setEnabled(False)
            
            # MessageBox ile uyar
            QtWidgets.QMessageBox.critical(
                self, 
                "Uyumsuz Dosya Sistemi", 
                "Sistem BTRFS olarak kurulmamış.\nBu uygulama yalnızca BTRFS dosya sistemine sahip sistemlerde çalışabilir."
            )
        else:
            self.status_icon.setPixmap(QtGui.QIcon.fromTheme("dialog-ok").pixmap(24, 24))
            self.status_label.setText("Sistem BTRFS dosya sistemiyle uyumlu. Yedek almaya hazır.")
            # Temaya göre okunabilir parlak yeşil
            green = "#4ade80" if self._theme == "dark" else "#16a34a"
            self.status_label.setStyleSheet(f"color: {green}; background: transparent;")

    def refresh_list(self):
        """Mevcut snapshot'ları getirir ve tabloyu doldurur."""
        if not btrfs_helper.is_btrfs():
            return
            
        snapshots = btrfs_helper.list_snapshots()
        self.table.setRowCount(0)
        
        for row_idx, snap in enumerate(snapshots):
            self.table.insertRow(row_idx)
            
            # Tablo hücrelerini doldur
            id_item = QtWidgets.QTableWidgetItem(snap["id"])
            id_item.setFlags(id_item.flags() & ~QtCore.Qt.ItemIsEditable)
            
            date_item = QtWidgets.QTableWidgetItem(snap["date"])
            date_item.setFlags(date_item.flags() & ~QtCore.Qt.ItemIsEditable)
            
            # snapshot_ prefix'ini ve tarih damgasını temizleyerek sade ismi göster
            name_parts = snap["name"].split('_')
            clean_name = "_".join(name_parts[3:]) if len(name_parts) >= 4 else "Manuel Yedek"
            if not clean_name:
                clean_name = "Açıklama Belirtilmedi"
                
            name_item = QtWidgets.QTableWidgetItem(clean_name)
            name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
            
            path_item = QtWidgets.QTableWidgetItem(snap["path"])
            path_item.setFlags(path_item.flags() & ~QtCore.Qt.ItemIsEditable)
            
            self.table.setItem(row_idx, 0, id_item)
            self.table.setItem(row_idx, 1, date_item)
            self.table.setItem(row_idx, 2, name_item)
            self.table.setItem(row_idx, 3, path_item)
            
        self.table.resizeColumnsToContents()
        self.on_selection_changed()

    def on_selection_changed(self):
        """Tablodan satır seçildiğinde yedek silme ve geri yükleme butonlarını yönetir."""
        selected_rows = self.table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        self.delete_btn.setEnabled(has_selection)
        self.restore_btn.setEnabled(has_selection)

    def take_snapshot(self):
        """Yeni anlık görüntü alır."""
        description = self.desc_input.text().strip()
        
        # Yükleniyor göstergesi
        self.statusBar().showMessage("Yeni anlık görüntü (snapshot) oluşturuluyor...")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        success, msg = btrfs_helper.create_snapshot(description)
        
        QtWidgets.QApplication.restoreOverrideCursor()
        self.statusBar().clearMessage()
        
        if success:
            QtWidgets.QMessageBox.information(self, "İşlem Başarılı", msg)
            self.desc_input.clear()
            self.refresh_list()
        else:
            QtWidgets.QMessageBox.warning(self, "Hata", msg)

    def delete_selected(self):
        """Seçilen anlık görüntüyü siler."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        snap_name = self.table.item(row, 2).text()
        snap_path = self.table.item(row, 3).text()
        
        # Silme onayı iste
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Anlık Görüntüyü Sil",
            f"'{snap_name}' isimli yedeği kalıcı olarak silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if confirm == QtWidgets.QMessageBox.Yes:
            self.statusBar().showMessage("Anlık görüntü siliniyor...")
            success, msg = btrfs_helper.delete_snapshot(snap_path)
            self.statusBar().clearMessage()
            
            if success:
                QtWidgets.QMessageBox.information(self, "Başarılı", "Yedek başarıyla silindi.")
                self.refresh_list()
            else:
                QtWidgets.QMessageBox.warning(self, "Hata", msg)

    def restore_selected(self):
        """Seçilen anlık görüntüyü geri yükler."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        subvol_id = self.table.item(row, 0).text()
        snap_name = self.table.item(row, 2).text()
        snap_path = self.table.item(row, 3).text()
        
        # Ciddi güvenlik uyarısı ve onayı
        warning_msg = (
            f"DİKKAT: Sistemi '{snap_name}' tarihindeki durumuna geri yüklemek üzeresiniz.\n\n"
            f"Bu işlem sonucunda seçilen anlık görüntü ({snap_path}) varsayılan alt birim (default subvolume) olarak atanacaktır.\n\n"
            "Sistem bir sonraki önyüklemede (reboot) bu yedek üzerinden açılacaktır. Devam etmek istiyor musunuz?"
        )
        
        confirm = QtWidgets.QMessageBox.warning(
            self,
            "Sistem Geri Yükleme Onayı",
            warning_msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if confirm == QtWidgets.QMessageBox.Yes:
            self.statusBar().showMessage("Sistem geri yükleme ayarlanıyor...")
            success, msg = btrfs_helper.restore_snapshot(subvol_id, snap_path)
            self.statusBar().clearMessage()
            
            if success:
                # Yeniden başlatma onayı iste
                reboot_confirm = QtWidgets.QMessageBox.question(
                    self,
                    "Geri Yükleme Yapılandırıldı",
                    f"{msg}\n\nSistemi şimdi yeniden başlatmak ister misiniz?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.Yes
                )
                
                if reboot_confirm == QtWidgets.QMessageBox.Yes:
                    btrfs_helper.run_cmd(["reboot"], check=False)
            else:
                QtWidgets.QMessageBox.critical(self, "Hata", msg)

    def toggle_theme(self):
        """Aydınlık/Koyu tema arasında geçiş yapar."""
        new_theme = "light" if self._theme == "dark" else "dark"
        self.theme_toggle_btn.setText("☀️" if new_theme == "light" else "🌙")
        self.apply_theme(new_theme)

    def toggle_auto_backup(self, checked):
        """Otomatik yedekleme zamanlayıcısını kurar veya kaldırır."""
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        success, msg = btrfs_helper.setup_auto_backup(checked)
        QtWidgets.QApplication.restoreOverrideCursor()
        
        if success:
            QtWidgets.QMessageBox.information(self, "Bilgi", msg)
        else:
            self.auto_backup_cb.blockSignals(True)
            self.auto_backup_cb.setChecked(not checked)
            self.auto_backup_cb.blockSignals(False)
            QtWidgets.QMessageBox.critical(self, "Hata", msg)


def _build_app_icon():
    """
    Uygulama ikonunu oluşturur.
    Önce sistem temasından çeker; bulamazsa yerel icon.png'yi kullanır.
    """
    app_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(app_dir, "icon.png")

    # 1. Önce sistem temasından dene (birden fazla isim sırayla)
    for theme_name in ("btrfs-snapshot-manager", "drive-harddisk", "system-software-install", "document-save"):
        icon = QtGui.QIcon.fromTheme(theme_name)
        if not icon.isNull():
            return icon

    # 2. Fallback: yerel icon.png
    if os.path.exists(icon_path):
        return QtGui.QIcon(icon_path)

    # 3. Son çare: varsayılan boş ikon
    return QtGui.QIcon()


def main():
    # Arayüz açılmadan önce root yetkisi al
    elevate_privileges()

    app = QtWidgets.QApplication(sys.argv)

    # ── Görev çubuğu ve pencere gruplaması için metadata ──
    app.setApplicationName("BtrfsSnapshotManager")
    app.setApplicationDisplayName("BTRFS Snapshot Yöneticisi")
    app.setOrganizationName("DualCoreX")
    app.setOrganizationDomain("dualcorex.pardus")

    # Pardus/GNOME/XFCE görev çubuğunun .desktop ile eşleşmesi için:
    app.setDesktopFileName("btrfs-snapshot-manager")

    # QApplication seviyesinde ikon (görev çubuğu ve alt menüler için)
    app_icon = _build_app_icon()
    app.setWindowIcon(app_icon)

    window = BtrfsSnapshotApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
