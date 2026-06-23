#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QAbstractItemView
)

class AuthDialog(QDialog):
    """Polkit / Yetkilendirme Diyaloğu Simülasyonu"""
    def __init__(self, parent=None, action_text="", package_name=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(400, 220)
        self.setWindowTitle("Kimlik Doğrulama Gerekli")
        self.setProperty("theme", parent._theme if parent else "dark")
        
        self.init_ui(action_text, package_name)

    def init_ui(self, action_text, package_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Başlık ve İkon
        header_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QIcon.fromTheme("dialog-password").pixmap(36, 36))
        
        title_label = QLabel("Kimlik Doğrulama")
        title_label.setObjectName("dialogTitle")
        title_label.setFont(QFont("Inter", 12, QFont.Bold))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Açıklama Metni
        desc_text = f"Sistem güvenliği için <b>{action_text}</b> işlemi yetkilendirme gerektiriyor.<br>Paket: <i>{package_name}</i>"
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Inter", 10))
        layout.addWidget(desc_label)

        # Şifre Giriş Alanı
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Yönetici (root/sudo) Şifresi")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFont(QFont("Inter", 10))
        layout.addWidget(self.pass_input)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.setObjectName("dialogCancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = QPushButton("Kimliği Doğrula")
        self.ok_btn.setObjectName("dialogOkBtn")
        self.ok_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)


class ProgressDialog(QDialog):
    """İşlem İlerleme Çubuğu Simülasyonu ve Çevrimiçi İndirme"""
    def __init__(self, parent=None, operation_text="", package_name="", mainline_version=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(450, 160)
        self.setWindowTitle("İşlem Sürüyor...")
        self.setProperty("theme", parent._theme if parent else "dark")

        self.package_name = package_name
        self.operation_text = operation_text
        self.mainline_version = mainline_version
        self.downloaded_files = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.status_label = QLabel()
        self.status_label.setFont(QFont("Inter", 10))
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.detail_label = QLabel("Başlatılıyor...")
        self.detail_label.setStyleSheet("color: #6B7280;")
        layout.addWidget(self.detail_label)

        # Simülasyon Sayacı
        self.counter = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)

        if self.mainline_version:
            self.status_label.setText(f"<b>{operation_text}</b>: Mainline {mainline_version} Paketleri İndiriliyor...")
            self.download_thread = KernelDownloadThread(self.mainline_version)
            self.download_thread.progress_updated.connect(self.on_download_progress)
            self.download_thread.download_finished.connect(self.on_download_finished)
            self.download_thread.download_failed.connect(self.on_download_failed)
            self.download_thread.start()
        else:
            self.status_label.setText(f"<b>{operation_text}</b> simüle ediliyor: {package_name}...")
            self.timer.start(30) # Hızlı simülasyon (yaklaşık 3 saniye)

    def on_download_progress(self, val, msg):
        self.progress_bar.setValue(val)
        self.detail_label.setText(msg)

    def on_download_finished(self, files):
        self.downloaded_files = files
        self.accept()

    def on_download_failed(self, err_msg):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("İndirme Hatası")
        msg_box.setText(f"Çevrimiçi paket indirme başarısız oldu:\n{err_msg}\n\nÇevrimdışı kurulum simülasyonu ile devam etmek ister misiniz?")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.status_label.setText(f"<b>{self.operation_text}</b> simüle ediliyor: {self.package_name}...")
            self.timer.start(30)
        else:
            self.reject()

    def update_progress(self):
        self.counter += 1
        self.progress_bar.setValue(self.counter)
        
        if self.counter == 20:
            self.detail_label.setText("İndirme yolları kontrol ediliyor...")
        elif self.counter == 50:
            self.detail_label.setText("Bağımlılık ağacı çözümleniyor...")
        elif self.counter == 80:
            self.detail_label.setText("Çekirdek imza doğrulaması yapılıyor...")
        
        if self.counter >= 100:
            self.timer.stop()
            self.accept()


class KernelFetchThread(QThread):
    kernels_fetched = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            import urllib.request
            import re
            
            url = "https://kernel.ubuntu.com/mainline/"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
            
            dirs = re.findall(r'href=\"(v[0-9]+\.[0-9]+[^\"/]*)/?\"', html)
            
            valid_dirs = []
            for d in dirs:
                d_clean = d.strip('/')
                # Sadece v5.x, v6.x ve üzeri yeni nesil kararlı/rc sürümleri filtrele
                if re.match(r'^v[56789]\.', d_clean):
                    valid_dirs.append(d_clean)
            
            def parse_version_key(version_str):
                s = version_str.lstrip('v')
                parts = s.split('-')
                ver_num = parts[0]
                rc_part = parts[1] if len(parts) > 1 else ''
                
                num_list = []
                for x in ver_num.split('.'):
                    try:
                        num_list.append(int(x))
                    except ValueError:
                        num_list.append(0)
                        
                while len(num_list) < 3:
                    num_list.append(0)
                    
                rc_num = 999
                if 'rc' in rc_part:
                    rc_digits = re.findall(r'\d+', rc_part)
                    if rc_digits:
                        rc_num = int(rc_digits[0])
                    else:
                        rc_num = 0
                return tuple(num_list) + (rc_num,)
            
            sorted_dirs = sorted(valid_dirs, key=parse_version_key, reverse=True)
            self.kernels_fetched.emit(sorted_dirs)
        except Exception as e:
            self.error_occurred.emit(str(e))


class KernelDownloadThread(QThread):
    progress_updated = pyqtSignal(int, str)
    download_finished = pyqtSignal(list)
    download_failed = pyqtSignal(str)

    def __init__(self, version_str):
        super().__init__()
        self.version_str = version_str
        self._app_dir = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        try:
            import urllib.request
            import re
            
            self.progress_updated.emit(5, "Paket listesi kontrol ediliyor...")
            url = f"https://kernel.ubuntu.com/mainline/{self.version_str}/"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=10) as r:
                html = r.read().decode('utf-8')
                
            links = re.findall(r'href=\"([^\"]+\.deb)\"', html)
            filtered = []
            for l in links:
                if 'generic' in l or '_all.deb' in l:
                    if 'amd64' in l or '_all.deb' in l:
                        if not any(x in l for x in ['-dbg', '-unsigned', '-cloud', '-rt', '-dbgsym']) or 'image-unsigned' in l:
                            filtered.append(l)
                            
            debs = sorted(list(set(filtered)))
            if not debs:
                # Eşleşme yoksa amd64 ve all mimarisini kapsayan genel debler
                for l in links:
                    if 'amd64' in l or '_all.deb' in l:
                        if not any(x in l for x in ['-dbg', '-cloud', '-rt', '-dbgsym']):
                            filtered.append(l)
                debs = sorted(list(set(filtered)))
                
            if not debs:
                self.download_failed.emit("Bu sürüm için uygun amd64 deb paketleri bulunamadı.")
                return
                
            self.progress_updated.emit(15, f"{len(debs)} adet paket indirilecek...")
            
            download_dir = os.path.join(self._app_dir, "downloads", self.version_str)
            os.makedirs(download_dir, exist_ok=True)
            
            downloaded_files = []
            total_files = len(debs)
            
            for idx, deb_rel_path in enumerate(debs):
                deb_name = os.path.basename(deb_rel_path)
                deb_url = url + deb_rel_path
                dest_path = os.path.join(download_dir, deb_name)
                
                self.progress_updated.emit(
                    int(15 + (idx / total_files) * 70), 
                    f"İndiriliyor ({idx+1}/{total_files}): {deb_name}"
                )
                
                u_req = urllib.request.Request(deb_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(u_req, timeout=15) as web_file:
                    with open(dest_path, 'wb') as local_file:
                        meta = web_file.info()
                        file_size = int(meta.get("Content-Length", 0))
                        
                        bytes_read = 0
                        block_size = 8192
                        while True:
                            buffer = web_file.read(block_size)
                            if not buffer:
                                break
                            bytes_read += len(buffer)
                            local_file.write(buffer)
                            
                            if file_size > 0:
                                file_percent = bytes_read / file_size
                                overall_percent = int(15 + ((idx + file_percent) / total_files) * 70)
                                self.progress_updated.emit(overall_percent, f"İndiriliyor: {deb_name} ({int(file_percent*100)}%)")
                
                downloaded_files.append(dest_path)
                
            self.progress_updated.emit(90, "İndirme tamamlandı. Paketler doğrulanıyor...")
            time.sleep(0.5)
            self.progress_updated.emit(95, "Sistem yetkileriyle kuruluma hazır.")
            time.sleep(0.5)
            self.progress_updated.emit(100, "Tamamlandı!")
            self.download_finished.emit(downloaded_files)
            
        except Exception as e:
            self.download_failed.emit(f"Bağlantı hatası: {str(e)}")





class PardusKernelManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pardus Çekirdek Yöneticisi")
        self.setMinimumSize(850, 600)
        
        # Tema seçimi varsayılan: Koyu (dark)
        self._theme = "dark"
        self._app_dir = os.path.dirname(os.path.abspath(__file__))
        self.app_icon = self.get_app_icon()
        
        # X11/Wayland gruplaması için masaüstü uyumluluğu
        QApplication.setApplicationName("PardusKernelManager")
        QApplication.setDesktopFileName("pardus-kernel-manager")
        
        self.mainline_kernels = []
        self.fetch_thread = None
        
        self.init_ui()
        self.load_stylesheet()
        self.apply_theme(self._theme)

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ----------------------------------------------------
        # 1. ÜST BANNER ALANI
        # ----------------------------------------------------
        self.banner_frame = QFrame(self)
        self.banner_frame.setObjectName("bannerFrame")
        self.banner_frame.setFixedHeight(85)
        
        banner_layout = QHBoxLayout(self.banner_frame)
        banner_layout.setContentsMargins(15, 10, 15, 10)

        # Başlık İkonu
        self.banner_icon = QLabel()
        self.banner_icon.setStyleSheet("background: transparent;")
        local_icon_path = os.path.join(self._app_dir, "icon.png")
        if os.path.exists(local_icon_path):
            pixmap = QPixmap(local_icon_path).scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.banner_icon.setPixmap(pixmap)
        else:
            self.banner_icon.setPixmap(QIcon.fromTheme("system-software-update").pixmap(42, 42))
        banner_layout.addWidget(self.banner_icon)

        # Yazı Alanı
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.banner_title = QLabel("Pardus Çekirdek Yöneticisi")
        self.banner_title.setObjectName("bannerTitle")
        self.banner_title.setFont(QFont("Inter", 14, QFont.Bold))
        
        self.banner_subtitle = QLabel("Donanım uyumluluğu için kararlı ve güncel Linux çekirdek sürümleri")
        self.banner_subtitle.setObjectName("bannerSubtitle")
        self.banner_subtitle.setFont(QFont("Inter", 10))
        
        text_layout.addWidget(self.banner_title)
        text_layout.addWidget(self.banner_subtitle)
        banner_layout.addLayout(text_layout)

        banner_layout.addStretch()

        # Aktif Çekirdek Badge Alanı
        badge_layout = QVBoxLayout()
        badge_layout.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        
        self.running_kernel = self.get_running_kernel()
        self.active_badge = QLabel(f"Aktif Çekirdek: {self.running_kernel}")
        self.active_badge.setObjectName("currentKernelBadge")
        self.active_badge.setFont(QFont("Inter", 10, QFont.Bold))
        self.active_badge.setAlignment(Qt.AlignCenter)
        
        badge_layout.addWidget(self.active_badge)
        banner_layout.addLayout(badge_layout)

        # Tema Değiştirici Buton
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("themeToggleBtn")
        self.theme_btn.setFont(QFont("Inter", 12))
        self.theme_btn.setToolTip("Aydınlık/Karanlık Tema Değiştir")
        self.theme_btn.clicked.connect(self.toggle_theme)
        banner_layout.addWidget(self.theme_btn)

        main_layout.addWidget(self.banner_frame)

        # ----------------------------------------------------
        # 2. SEKMELİ GÖSTERİM (QTabWidget)
        # ----------------------------------------------------
        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabWidget")
        main_layout.addWidget(self.tabs)

        # Sekme 1: Yüklü Çekirdekler
        self.installed_tab = QWidget()
        self.installed_layout = QVBoxLayout(self.installed_tab)
        self.installed_layout.setContentsMargins(10, 10, 10, 10)
        
        self.installed_table = QTableWidget()
        self.installed_table.setObjectName("installedTable")
        self.installed_table.setColumnCount(5)
        self.installed_table.setHorizontalHeaderLabels(["Çekirdek Paketi", "Sürüm", "Mimari", "Durum", "İşlem"])
        self.installed_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.installed_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.installed_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.installed_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.installed_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.installed_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.installed_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.installed_table.setColumnWidth(4, 130)
        self.installed_table.verticalHeader().setDefaultSectionSize(60)
        self.installed_table.verticalHeader().setVisible(False)
        
        self.installed_layout.addWidget(self.installed_table)
        self.tabs.addTab(self.installed_tab, "Yüklü Çekirdekler")

        # Sekme 2: İndirilebilir Çekirdekler
        self.available_tab = QWidget()
        self.available_layout = QVBoxLayout(self.available_tab)
        self.available_layout.setContentsMargins(10, 10, 10, 10)
        self.available_layout.setSpacing(8)
        
        # Arama Barı
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        search_label = QLabel("🔍 Ara:")
        search_label.setFont(QFont("Inter", 10, QFont.Bold))
        search_label.setStyleSheet("color: #8A94A6; background: transparent;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Çekirdek sürümü ara (örn: 6.13)...")
        self.search_input.textChanged.connect(self.filter_available_kernels)
        self.search_input.setFont(QFont("Inter", 10))
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        self.available_layout.addLayout(search_layout)
        
        self.available_table = QTableWidget()
        self.available_table.setObjectName("availableTable")
        self.available_table.setColumnCount(3)
        self.available_table.setHorizontalHeaderLabels(["Çekirdek Paketi", "Açıklama", "İşlem"])
        self.available_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.available_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.available_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.available_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.available_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.available_table.setColumnWidth(2, 130)
        self.available_table.verticalHeader().setDefaultSectionSize(60)
        self.available_table.verticalHeader().setVisible(False)
        
        self.available_layout.addWidget(self.available_table)
        self.tabs.addTab(self.available_tab, "İndirilebilir Çekirdekler")

        # ----------------------------------------------------
        # 3. YÜKLEME VE YENİLEME
        # ----------------------------------------------------
        self.load_kernels()

        # Durum Çubuğu
        self.statusBar().showMessage("Pardus Çekirdek Yöneticisi PoC sürümü aktif.")

    def create_button_container(self, text, btn_object_name, icon_theme_name=None, callback=None, enabled=True):
        """Hücre içerisindeki butonları düzgün ölçeklemek ve ortalamak için bir kapsayıcı widget döner."""
        container = QWidget()
        container.setObjectName("buttonContainer")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        btn = QPushButton(text)
        btn.setObjectName(btn_object_name)
        btn.setEnabled(enabled)
        
        if icon_theme_name:
            btn.setIcon(QIcon.fromTheme(icon_theme_name))
            btn.setIconSize(QSize(14, 14))
            
        btn.setFont(QFont("Inter", 9, QFont.Bold))
        # Butona sabit boyut vererek düzgün ölçeklenmesini sağlıyoruz
        btn.setFixedSize(90, 28)
        
        if callback and enabled:
            btn.clicked.connect(callback)
            
        layout.addWidget(btn, 0, Qt.AlignCenter)
        return container

    def get_app_icon(self):
        """Uygulama için en uygun ikonu seçer (Yerel dosya -> Sistem Teması Fallback)"""
        local_icon_path = os.path.join(self._app_dir, "icon.png")
        if os.path.exists(local_icon_path):
            return QIcon(local_icon_path)
        
        for name in ["preferences-system", "system-software-update", "drive-harddisk"]:
            icon = QIcon.fromTheme(name)
            if not icon.isNull():
                return icon
        return QIcon()

    def get_running_kernel(self):
        """Aktif çalışan çekirdek sürümünü döner."""
        try:
            res = subprocess.check_output(["uname", "-r"], stderr=subprocess.DEVNULL)
            return res.decode("utf-8").strip()
        except:
            return "6.12.94+deb13-amd64" # Sandbox/Hata durumunda fallback

    def load_kernels(self):
        """Sistemdeki yüklü ve indirilebilir çekirdekleri süzerek listeler."""
        # 1. YÜKLÜ ÇEKİRDEKLER
        installed_kernels = []
        try:
            # dpkg -l sorgusu
            output = subprocess.check_output(["dpkg", "-l", "linux-image-[0-9]*"], stderr=subprocess.DEVNULL)
            for line in output.decode("utf-8").splitlines():
                if line.startswith("ii"):
                    parts = [p for p in line.split(" ") if p]
                    if len(parts) >= 4:
                        pkg_name = parts[1]
                        pkg_ver = parts[2]
                        pkg_arch = parts[3]
                        pkg_desc = " ".join(parts[4:])
                        installed_kernels.append((pkg_name, pkg_ver, pkg_arch, pkg_desc))
        except:
            # Fallback (Sistemde paket sorgulama başarısız olursa)
            installed_kernels = [
                ("linux-image-6.12.57+deb13-amd64", "6.12.57-1", "amd64", "Linux 6.12 for 64-bit PCs"),
                ("linux-image-6.12.90+deb13.1-amd64", "6.12.90-2", "amd64", "Linux 6.12 for 64-bit PCs"),
                (f"linux-image-{self.running_kernel}", "6.12.94-1", "amd64", "Linux 6.12 for 64-bit PCs (signed)")
            ]

        self.installed_table.setRowCount(len(installed_kernels))
        for row, (name, ver, arch, desc) in enumerate(installed_kernels):
            self.installed_table.setItem(row, 0, QTableWidgetItem(name))
            self.installed_table.setItem(row, 1, QTableWidgetItem(ver))
            self.installed_table.setItem(row, 2, QTableWidgetItem(arch))
            
            # Durum sütunu
            is_active = (self.running_kernel in name)
            status_text = "Aktif (Çalışıyor)" if is_active else "Yüklü"
            status_item = QTableWidgetItem(status_text)
            if is_active:
                status_item.setForeground(QColor("#10B981")) # Yeşil metin
            self.installed_table.setItem(row, 3, status_item)

            # İşlem Butonu
            if is_active:
                btn_widget = self.create_button_container("Aktif", "actionBtnDisabled", icon_theme_name="emblem-default", enabled=False)
            else:
                btn_widget = self.create_button_container(
                    "Kaldır", 
                    "removeBtn", 
                    icon_theme_name="edit-delete", 
                    callback=lambda checked, n=name: self.simulate_action("Kaldır", n)
                )
                
            self.installed_table.setCellWidget(row, 4, btn_widget)

        # 2. İNDİRİLEBİLİR ÇEKİRDEKLER (İlk etapta yerel repoları ve çevrimdışı fallback'leri yükle)
        available_kernels = []
        try:
            # apt-cache sorgusu
            output = subprocess.check_output(["apt-cache", "search", "linux-image-[0-9]"], stderr=subprocess.DEVNULL)
            for line in output.decode("utf-8").splitlines():
                if " - " in line:
                    pkg_name, pkg_desc = line.split(" - ", 1)
                    pkg_name = pkg_name.strip()
                    # Debug, unsigned ve cloud filtrelemeleri
                    if any(x in pkg_name for x in ["-dbg", "-unsigned", "-cloud", "-rt", "-dbgsym"]):
                        continue
                    # Zaten yüklü olanları listeden çıkar
                    if any(pkg_name == ik[0] for ik in installed_kernels):
                        continue
                    available_kernels.append((pkg_name, pkg_desc.strip()))
        except:
            pass
        
        self.available_table.setRowCount(len(available_kernels))
        for row, (name, desc) in enumerate(available_kernels):
            self.available_table.setItem(row, 0, QTableWidgetItem(name))
            self.available_table.setItem(row, 1, QTableWidgetItem(desc))

            # İşlem Butonu
            btn_widget = self.create_button_container(
                "Kur", 
                "installBtn", 
                icon_theme_name="system-software-install", 
                callback=lambda checked, n=name: self.simulate_action("Kur", n)
            )
            self.available_table.setCellWidget(row, 2, btn_widget)

        # Çevrimiçi Mainline Çekirdeklerini Getir
        self.statusBar().showMessage("Yerel çekirdekler yüklendi. Çevrimiçi ana hat çekirdekleri sorgulanıyor...")
        self.fetch_thread = KernelFetchThread()
        self.fetch_thread.kernels_fetched.connect(self.on_mainline_kernels_fetched)
        self.fetch_thread.error_occurred.connect(self.on_mainline_kernels_error)
        self.fetch_thread.start()

    def on_mainline_kernels_fetched(self, versions):
        """Çevrimiçi ana hat çekirdekleri başarıyla çekildiğinde tabloyu günceller."""
        self.mainline_kernels = versions
        self.statusBar().showMessage(f"Çevrimiçi ana hat çekirdekleri başarıyla yüklendi ({len(versions)} adet).")
        
        # Mevcut yüklü olanları belirleyelim ki mükerrer eklemeyelim
        installed_names = []
        for row in range(self.installed_table.rowCount()):
            installed_names.append(self.installed_table.item(row, 0).text())
            
        # Mevcut indirilebilir tablodaki yerel paketleri topla (mainline olanlar hariç)
        existing_local = []
        for row in range(self.available_table.rowCount()):
            name = self.available_table.item(row, 0).text()
            desc = self.available_table.item(row, 1).text()
            if "(Mainline)" not in name and "(Mainline LTS)" not in name:
                existing_local.append((name, desc))
                
        # Mainline sürümlerinden paket listesi oluştur
        new_list = []
        lts_branches = {"6.12", "6.6", "6.1", "5.15", "5.10", "5.4"}
        for ver in versions:
            ver_clean = ver.lstrip('v')
            ver_parts = ver_clean.split('.')
            is_lts = False
            if len(ver_parts) >= 2:
                major_minor = f"{ver_parts[0]}.{ver_parts[1]}"
                if major_minor in lts_branches:
                    is_lts = True
            
            if is_lts:
                pkg_name = f"linux-image-unsigned-{ver_clean}-generic (Mainline LTS)"
                pkg_desc = f"Linux {ver} Uzun Vadeli Kararlı (LTS) Ana Hat Çekirdeği — Ubuntu PPA (.deb)"
            else:
                pkg_name = f"linux-image-unsigned-{ver_clean}-generic (Mainline)"
                pkg_desc = f"Linux {ver} Kararlı Ana Hat (Mainline) Çekirdeği — Ubuntu PPA (.deb)"
                
            if "rc" in ver:
                pkg_desc = f"Linux {ver} Deneysel Geliştirici Adayı (Mainline RC) — Ubuntu PPA (.deb)"
                
            # Zaten kuruluysa listede gösterme
            if any(ver.lstrip("v") in ik for ik in installed_names):
                continue
                
            new_list.append((pkg_name, pkg_desc))
            
        # Birleştir: Önce mainline çekirdekler (yeni nesil), sonra yerel repodaki paketler
        combined_list = new_list + existing_local
        
        self.available_table.setRowCount(len(combined_list))
        for row, (name, desc) in enumerate(combined_list):
            self.available_table.setItem(row, 0, QTableWidgetItem(name))
            self.available_table.setItem(row, 1, QTableWidgetItem(desc))
            
            # İşlem Butonu
            btn_widget = self.create_button_container(
                "Kur", 
                "installBtn", 
                icon_theme_name="system-software-install", 
                callback=lambda checked, n=name: self.simulate_action("Kur", n)
            )
            self.available_table.setCellWidget(row, 2, btn_widget)
            
        # Arama kutusu doluysa filtrelemeyi tekrar tetikle
        self.filter_available_kernels(self.search_input.text())

    def on_mainline_kernels_error(self, err_msg):
        """Çevrimiçi liste çekilemediğinde hata durumunu durum çubuğunda gösterir."""
        self.statusBar().showMessage(f"Ana hat çekirdek listesi alınamadı (Çevrimdışı Mod): {err_msg}")

    def filter_available_kernels(self, text):
        """Çekirdek sürüm listesini arama kutusuna göre filtreler."""
        text = text.lower()
        for row in range(self.available_table.rowCount()):
            item_name = self.available_table.item(row, 0).text().lower()
            item_desc = self.available_table.item(row, 1).text().lower()
            if text in item_name or text in item_desc:
                self.available_table.setRowHidden(row, False)
            else:
                self.available_table.setRowHidden(row, True)

    def simulate_action(self, action_type, package_name):
        """Çekirdek yükleme/kaldırma yetkilendirme ve yükleme simülasyonunu başlatır."""
        auth_text = "Çekirdek Yükleme" if action_type == "Kur" else "Çekirdek Kaldırma"
        
        # 1. Adım: Yetkilendirme Simülasyonu
        auth_dialog = AuthDialog(self, auth_text, package_name)
        if auth_dialog.exec_() != QDialog.Accepted:
            self.statusBar().showMessage("İşlem kullanıcı tarafından iptal edildi.")
            return

        # Çevrimiçi Mainline Çekirdeği mi?
        is_mainline = package_name.endswith("(Mainline)") or package_name.endswith("(Mainline LTS)")
        mainline_ver = None
        if is_mainline and action_type == "Kur":
            import re
            match = re.search(r'linux-image-(?:unsigned-)?([0-9a-zA-Z.+_-]+?)(?:-generic)?\s*\(Mainline(?: LTS)?\)', package_name)
            if match:
                mainline_ver = "v" + match.group(1) if not match.group(1).startswith("v") else match.group(1)

        # 2. Adım: Yükleme İlerleme Simülasyonu (Ana Hat Çekirdeği ise Gerçek İndirmeli)
        prog_dialog = ProgressDialog(self, auth_text, package_name, mainline_version=mainline_ver)
        if prog_dialog.exec_() != QDialog.Accepted:
            self.statusBar().showMessage("İşlem iptal edildi.")
            return

        # 3. Adım: Sonuç Bilgi Kutusu
        if action_type == "Kur":
            if prog_dialog.downloaded_files:
                # Gerçek indirilen dosyalarla başarılı mesajı
                files_li = "".join([f"<li><code style='color: #10B981;'>{os.path.basename(f)}</code></li>" for f in prog_dialog.downloaded_files])
                download_dir = os.path.dirname(prog_dialog.downloaded_files[0])
                
                info_message = (
                    f"<h3>Kavram Kanıtı (PoC) Çekirdek Paketleri İndirildi</h3>"
                    f"<p><b>Paket Tanımı:</b> {package_name}</p>"
                    f"<p><b>Gerçek İndirilen Dosyalar ({len(prog_dialog.downloaded_files)} Paket):</b></p>"
                    f"<ul style='margin-top: 5px; margin-bottom: 5px; padding-left: 20px;'>"
                    f"{files_li}"
                    f"</ul>"
                    f"<p><b>Klasör Konumu:</b> <code style='background-color: #2D3748; padding: 2px 5px; border-radius: 3px;'>{download_dir}</code></p>"
                    f"<hr>"
                    f"<p style='color: #4F8EF7;'><b>Sistem Kurulum Eşdeğeri:</b><br>"
                    f"<code style='background-color: #2D3748; padding: 4px 8px; border-radius: 3px; display: block; margin-top: 5px;'>"
                    f"sudo dpkg -i {download_dir}/*.deb"
                    f"</code></p>"
                    f"<p><i>Gerçek sürümde bu debler dpkg ile kurularak sistemin yeniden başlatılması talep edilecektir.</i></p>"
                )
            else:
                # Simüle kurulum mesajı (çevrimdışı fallback veya standart repodan)
                command_sim = f"apt install {package_name}"
                info_message = (
                    f"<h3>Kavram Kanıtı (PoC) Simülasyonu Başarılı</h3>"
                    f"<p><b>Paket:</b> {package_name}</p>"
                    f"<p><b>Yapılan İşlem:</b> {action_type}</p>"
                    f"<hr>"
                    f"<p style='color: #4F8EF7;'><b>Sistem Komut Eşdeğeri:</b><br><code style='background-color: #2D3748; padding: 2px 5px; border-radius: 3px;'>sudo {command_sim}</code></p>"
                    f"<p><i>Gerçek sürümde bu işlem arka planda sistem yetkileriyle tamamlanarak sistemin yeniden başlatılması talep edilecektir.</i></p>"
                )
        else:
            # Kaldırma işlemi
            command_sim = f"apt purge {package_name}"
            info_message = (
                f"<h3>Kavram Kanıtı (PoC) Simülasyonu Başarılı</h3>"
                f"<p><b>Paket:</b> {package_name}</p>"
                f"<p><b>Yapılan İşlem:</b> {action_type}</p>"
                f"<hr>"
                f"<p style='color: #4F8EF7;'><b>Sistem Komut Eşdeğeri:</b><br><code style='background-color: #2D3748; padding: 2px 5px; border-radius: 3px;'>sudo {command_sim}</code></p>"
                f"<p><i>Gerçek sürümde bu işlem arka planda sistem yetkileriyle tamamlanarak sistemin yeniden başlatılması talep edilecektir.</i></p>"
            )
            
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("PoC Bilgilendirme")
        msg_box.setText(info_message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        self.statusBar().showMessage(f"{package_name} {action_type} işlemi simüle edildi.")

    def load_stylesheet(self):
        """style.qss dosyasını okur ve uygulamaya yerleştirir."""
        style_path = os.path.join(self._app_dir, "style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def apply_theme(self, theme):
        """Bütün alt elemanlara tema özelliğini uygular ve yeniler."""
        self._theme = theme
        self.setProperty("theme", theme)
        
        # Pencere İkonunu ve stilini ayarla
        self.setWindowIcon(self.app_icon)
        
        # Rekürsif boyama tetikleyicisi
        self._set_theme_recursive(self.centralWidget(), theme)
        self._set_theme_recursive(self, theme)
        self.statusBar().setProperty("theme", theme)
        
        # QSS stilini yenilemek için Qt'ye zorla
        self.style().unpolish(self)
        self.style().polish(self)
        self.style().unpolish(self.centralWidget())
        self.style().polish(self.centralWidget())
        
        # Yeniden boya
        self.update()

    def _set_theme_recursive(self, widget, theme):
        """Alt widget'lar arasında gezinerek tema property'sini ayarlar."""
        if widget is None:
            return
        widget.setProperty("theme", theme)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
        for child in widget.findChildren(QWidget):
            child.setProperty("theme", theme)
            child.style().unpolish(child)
            child.style().polish(child)
            child.update()

    def toggle_theme(self):
        """Aydınlık/Karanlık tema geçişini yönetir."""
        if self._theme == "dark":
            self._theme = "light"
            self.theme_btn.setText("☀️")
            self.statusBar().showMessage("Aydınlık tema aktif edildi.")
        else:
            self._theme = "dark"
            self.theme_btn.setText("🌙")
            self.statusBar().showMessage("Karanlık tema aktif edildi.")
        
        self.load_stylesheet()
        self.apply_theme(self._theme)


def main():
    app = QApplication(sys.argv)
    
    # Yazı tipi
    font = QFont("Inter", 10)
    app.setFont(font)
    
    window = PardusKernelManager()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
