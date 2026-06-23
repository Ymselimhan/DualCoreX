#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pardus Hello (Sistem Karşılama ve Hızlı Ayar Aracı)
Debian tabanlı Pardus işletim sistemi için Teknofest Kavram Kanıtı (PoC) Çalışması.
CachyOS Hello (CachyOS-Welcome) arayüzü ve özellikleri esas alınarak Pardus için uyarlanmıştır.
"""

import os
import sys
import platform
import webbrowser
import subprocess
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QScrollArea,
    QDialog,
    QLineEdit,
    QProgressBar,
    QMessageBox,
    QCheckBox,
    QButtonGroup,
    QRadioButton
)

# ==============================================================================
# SİSTEM TEMA ALGILAMA YÖNTEMİ
# ==============================================================================

def detect_system_dark_mode():
    """Sistemin karanlık modda olup olmadığını gdbus portal veya gsettings ile algılar."""
    try:
        # 1. Yöntem: D-Bus Portal okuması (Modern GNOME, KDE, XFCE vb.)
        cmd = [
            "gdbus", "call", "--session",
            "--dest", "org.freedesktop.portal.Desktop",
            "--object-path", "/org/freedesktop/portal/desktop",
            "--method", "org.freedesktop.portal.Settings.Read",
            "org.freedesktop.appearance", "color-scheme"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1)
        if "uint32 1" in result.stdout:  # 1: prefer-dark
            return True
        elif "uint32 2" in result.stdout:  # 2: prefer-light
            return False
    except Exception:
        pass

    try:
        # 2. Yöntem: GNOME Gsettings Renk Şeması
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True, text=True, timeout=1
        )
        if "prefer-dark" in result.stdout.lower():
            return True
    except Exception:
        pass

    try:
        # 3. Yöntem: GNOME Gsettings GTK Teması
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            capture_output=True, text=True, timeout=1
        )
        if "dark" in result.stdout.lower():
            return True
    except Exception:
        pass

    # Varsayılan olarak karanlık tema (Jüri sunumu ve CachyOS estetiği için)
    return True


# ==============================================================================
# QSS STİL ŞABLONLARI (Karanlık ve Aydınlık Modlar)
# ==============================================================================

DARK_QSS = """
/* Ana Pencere ve Genel Ayarlar */
QMainWindow {
    background-color: #0f111a;
}

QWidget#centralWidget {
    background-color: #0f111a;
}

QWidget#rightContainer {
    background-color: #0f111a;
}

QWidget#stackedWidget {
    background-color: #0f111a;
}

QLabel {
    color: #c8d3f5;
    background-color: transparent;
}

/* Sol Navigasyon Paneli (Sidebar) */
QFrame#sidebarFrame {
    background-color: #151724;
    border-right: 1px solid #1f2335;
}

QListWidget#sidebarList {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#sidebarList::item {
    background-color: transparent;
    color: #a9b1d6;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 6px 12px;
    font-weight: 600;
}

QListWidget#sidebarList::item:hover {
    background-color: #1c1f30;
    color: #c8d3f5;
}

QListWidget#sidebarList::item:selected {
    background-color: #00f5d4;
    color: #0f111a;
    font-weight: 700;
}

QLabel#brandLabel {
    color: #ffffff;
    font-weight: bold;
    background-color: transparent;
}

QLabel#footerVersion {
    color: #565f89;
    background-color: transparent;
}

/* Kartlar ve Çerçeveler */
QFrame#cardFrame {
    background-color: #151724;
    border: 1px solid #1f2335;
    border-radius: 12px;
}

QFrame#hardwareCard {
    background-color: #1e2030;
    border: 1px solid #2d3149;
    border-radius: 12px;
}

QFrame#bannerFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00f5d4, stop:1 #00b4d8);
    border-radius: 12px;
}

QLabel#bannerTitle {
    color: #0f111a;
    background-color: transparent;
}

QLabel#bannerSubtitle {
    color: #1c2030;
    background-color: transparent;
}

/* Kaydırma Alanı */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea QWidget {
    background-color: transparent;
}

/* Kaydırma Çubukları */
QScrollBar:vertical {
    border: none;
    background-color: #0f111a;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #1f2335;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00f5d4;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Butonlar */
QPushButton {
    background-color: #1e2030;
    color: #c8d3f5;
    border: 1px solid #2d3149;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #2d3149;
    color: #ffffff;
    border-color: #414868;
}

QPushButton:pressed {
    background-color: #24283b;
}

/* Tema Değiştirme Butonu */
QPushButton#themeToggleBtn {
    background-color: transparent;
    border: 1px solid #2d3149;
    border-radius: 18px;
    font-size: 14px;
}

QPushButton#themeToggleBtn:hover {
    background-color: #1e2030;
    border-color: #00f5d4;
}

/* Birincil Eylem Butonları (Yeşil Vurgu) */
QPushButton#primaryActionBtn {
    background-color: #00f5d4;
    color: #0f111a;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    padding: 8px 16px;
}

QPushButton#primaryActionBtn:hover {
    background-color: #33ffeb;
}

QPushButton#primaryActionBtn:pressed {
    background-color: #00d2b4;
}

QPushButton#primaryActionBtn:disabled {
    background-color: #1c1f30;
    color: #565f89;
}

/* Kaldır/Tehlike Butonları (Kırmızı Vurgu) */
QPushButton#dangerActionBtn {
    background-color: #ff007f;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-weight: 700;
}

QPushButton#dangerActionBtn:hover {
    background-color: #ff3399;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
    font-weight: 600;
    color: #c8d3f5;
    background-color: transparent;
}

/* Radio Button (Segmented Control) */
QRadioButton {
    padding: 6px 12px;
    font-weight: 600;
    color: #a9b1d6;
    background-color: transparent;
}

/* Başlıklar ve Etiketler */
QLabel#headerTitle {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
}

QLabel#sectionTitle {
    font-size: 16px;
    font-weight: 700;
    color: #00f5d4;
}

QLabel#sectionDesc {
    font-size: 12px;
    color: #a9b1d6;
}

QLabel#cardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#groupTitle {
    font-weight: bold;
    font-size: 14px;
    color: #ffffff;
}

QLabel#cardDesc {
    font-size: 12px;
    color: #9ab3db;
}

QLabel#introText {
    color: #c8d3f5;
}

/* İletişim Kutuları (Dialogs) */
QDialog {
    background-color: #151724;
    border: 1px solid #1f2335;
    border-radius: 12px;
}

QDialog QLabel#dialogTitle {
    color: #ffffff;
    font-weight: bold;
}

QDialog QLabel#dialogDetail {
    color: #a9b1d6;
}

QLineEdit {
    background-color: #0f111a;
    border: 1px solid #1f2335;
    border-radius: 6px;
    padding: 8px 12px;
    color: #c8d3f5;
}

QLineEdit:focus {
    border: 1px solid #00f5d4;
}

QProgressBar {
    background-color: #0f111a;
    border: 1px solid #1f2335;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #00f5d4;
    border-radius: 5px;
}
"""

LIGHT_QSS = """
/* Ana Pencere ve Genel Ayarlar */
QMainWindow {
    background-color: #eff1f5;
}

QWidget#centralWidget {
    background-color: #eff1f5;
}

QWidget#rightContainer {
    background-color: #eff1f5;
}

QWidget#stackedWidget {
    background-color: #eff1f5;
}

QLabel {
    color: #4c4f69;
    background-color: transparent;
}

/* Sol Navigasyon Paneli (Sidebar) */
QFrame#sidebarFrame {
    background-color: #e6e9ef;
    border-right: 1px solid #ccd0da;
}

QListWidget#sidebarList {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#sidebarList::item {
    background-color: transparent;
    color: #5c5f77;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 6px 12px;
    font-weight: 600;
}

QListWidget#sidebarList::item:hover {
    background-color: #ccd0da;
    color: #4c4f69;
}

QListWidget#sidebarList::item:selected {
    background-color: #00a896;
    color: #ffffff;
    font-weight: 700;
}

QLabel#brandLabel {
    color: #1e1f29;
    font-weight: bold;
    background-color: transparent;
}

QLabel#footerVersion {
    color: #6c6f85;
    background-color: transparent;
}

/* Kartlar ve Çerçeveler */
QFrame#cardFrame {
    background-color: #e6e9ef;
    border: 1px solid #ccd0da;
    border-radius: 12px;
}

QFrame#hardwareCard {
    background-color: #dce0e8;
    border: 1px solid #bcc0cc;
    border-radius: 12px;
}

QFrame#bannerFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00f5d4, stop:1 #00b4d8);
    border-radius: 12px;
}

QLabel#bannerTitle {
    color: #0f111a;
    background-color: transparent;
}

QLabel#bannerSubtitle {
    color: #1c2030;
    background-color: transparent;
}

/* Kaydırma Alanı */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea QWidget {
    background-color: transparent;
}

/* Kaydırma Çubukları */
QScrollBar:vertical {
    border: none;
    background-color: #eff1f5;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #ccd0da;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00a896;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Butonlar */
QPushButton {
    background-color: #dce0e8;
    color: #4c4f69;
    border: 1px solid #bcc0cc;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #ccd0da;
    color: #1e1f29;
    border-color: #bcc0cc;
}

QPushButton:pressed {
    background-color: #acb0be;
}

/* Tema Değiştirme Butonu */
QPushButton#themeToggleBtn {
    background-color: transparent;
    border: 1px solid #ccd0da;
    border-radius: 18px;
    font-size: 14px;
}

QPushButton#themeToggleBtn:hover {
    background-color: #ccd0da;
    border-color: #00a896;
}

/* Birincil Eylem Butonları (Yeşil Vurgu) */
QPushButton#primaryActionBtn {
    background-color: #00a896;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    padding: 8px 16px;
}

QPushButton#primaryActionBtn:hover {
    background-color: #00c2ad;
}

QPushButton#primaryActionBtn:pressed {
    background-color: #008e7f;
}

QPushButton#primaryActionBtn:disabled {
    background-color: #ccd0da;
    color: #9ca0b0;
}

/* Kaldır/Tehlike Butonları (Kırmızı Vurgu) */
QPushButton#dangerActionBtn {
    background-color: #d20f39;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-weight: 700;
}

QPushButton#dangerActionBtn:hover {
    background-color: #e64553;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
    font-weight: 600;
    color: #4c4f69;
    background-color: transparent;
}

/* Radio Button (Segmented Control) */
QRadioButton {
    padding: 6px 12px;
    font-weight: 600;
    color: #5c5f77;
    background-color: transparent;
}

/* Başlıklar ve Etiketler */
QLabel#headerTitle {
    font-size: 24px;
    font-weight: 800;
    color: #1e1f29;
}

QLabel#sectionTitle {
    font-size: 16px;
    font-weight: 700;
    color: #008e7f;
}

QLabel#sectionDesc {
    font-size: 12px;
    color: #5c5f77;
}

QLabel#cardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #1e1f29;
}

QLabel#groupTitle {
    font-weight: bold;
    font-size: 14px;
    color: #1e1f29;
}

QLabel#cardDesc {
    font-size: 12px;
    color: #5c5f77;
}

QLabel#introText {
    color: #4c4f69;
}

/* İletişim Kutuları (Dialogs) */
QDialog {
    background-color: #e6e9ef;
    border: 1px solid #ccd0da;
    border-radius: 12px;
}

QDialog QLabel#dialogTitle {
    color: #1e1f29;
    font-weight: bold;
}

QDialog QLabel#dialogDetail {
    color: #5c5f77;
}

QLineEdit {
    background-color: #eff1f5;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 8px 12px;
    color: #4c4f69;
}

QLineEdit:focus {
    border: 1px solid #00a896;
}

QProgressBar {
    background-color: #eff1f5;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    text-align: center;
    color: #4c4f69;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #00a896;
    border-radius: 5px;
}
"""


# ==============================================================================
# SİMÜLASYON DİYALOGLARI (Polkit Yetki ve İlerleme Pencereleri)
# ==============================================================================

class AuthDialog(QDialog):
    def __init__(self, parent=None, action_text="", package_name=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(420, 230)
        self.setWindowTitle("Kimlik Doğrulama Gerekli")
        
        self.init_ui(action_text, package_name)

    def init_ui(self, action_text, package_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QIcon.fromTheme("dialog-password").pixmap(36, 36))
        
        title_label = QLabel("Yetkilendirme")
        title_label.setObjectName("dialogTitle")
        title_label.setFont(QFont("Inter", 12, QFont.Bold))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        desc_text = f"Sistem güvenliği için <b>{action_text}</b> işlemi yönetici hakları gerektiriyor.<br>Komut: <i>sudo apt install {package_name}</i>"
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Inter", 10))
        layout.addWidget(desc_label)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Yönetici (sudo) şifresi giriniz")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFont(QFont("Inter", 10))
        layout.addWidget(self.pass_input)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = QPushButton("Kimliği Doğrula")
        self.ok_btn.setObjectName("primaryActionBtn")
        self.ok_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)


class ProgressDialog(QDialog):
    def __init__(self, parent=None, operation_text="", package_name=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(450, 160)
        self.setWindowTitle("İşlem Sürüyor...")
        
        self.operation_text = operation_text
        self.package_name = package_name
        self.counter = 0

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.status_label = QLabel(f"<b>{self.operation_text}</b> başlatılıyor...")
        self.status_label.setFont(QFont("Inter", 10))
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.detail_label = QLabel("Ağ bağlantısı kuruluyor...")
        self.detail_label.setObjectName("dialogDetail")
        self.detail_label.setFont(QFont("Inter", 9))
        layout.addWidget(self.detail_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(25)

    def update_progress(self):
        self.counter += 1
        self.progress_bar.setValue(self.counter)
        
        if self.counter == 15:
            self.detail_label.setText("Paket depolarından metadata okunuyor...")
        elif self.counter == 35:
            self.detail_label.setText("Bağımlılık ağacı kontrol ediliyor...")
        elif self.counter == 55:
            self.detail_label.setText(f"{self.package_name} paketi indiriliyor...")
        elif self.counter == 75:
            self.detail_label.setText("Dosyalar disk üzerine yazılıyor...")
        elif self.counter == 90:
            self.detail_label.setText("Sistem tetikleyicileri (triggers) çalıştırılıyor...")
        
        if self.counter >= 100:
            self.timer.stop()
            self.accept()


# ==============================================================================
# ANA UYGULAMA PENCERESİ (MainWindow)
# ==============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Pardus Hello — Hoş Geldiniz")
        self.setMinimumSize(960, 640)
        self.resize(1000, 680)
        
        # Dock/Görev çubuğu ayarı
        self.setWindowIcon(QIcon.fromTheme("pardus", QIcon.fromTheme("start-here", QIcon.fromTheme("computer"))))
        
        # Donanım Bilgileri
        self.cpu_info = self.get_cpu_info()
        self.ram_info = self.get_ram_info()
        self.os_info = self.get_os_info()
        self.kernel_info = platform.release()

        # Sistem Temasını Algıla (Aydınlık / Karanlık) ve QSS Şablonunu Uygula
        self.current_theme = "dark" if detect_system_dark_mode() else "light"
        if self.current_theme == "dark":
            self.setStyleSheet(DARK_QSS)
        else:
            self.setStyleSheet(LIGHT_QSS)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ======================================================================
        # SIDEBAR (SOL MENÜ - CachyOS Hello Tarzı)
        # ======================================================================
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebarFrame")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(16)

        # Logo/Başlık Grubu
        logo_container = QFrame()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(20, 10, 20, 10)
        logo_layout.setSpacing(12)

        logo_label = QLabel()
        logo_pixmap = QIcon.fromTheme("pardus", QIcon.fromTheme("start-here")).pixmap(36, 36)
        if logo_pixmap.isNull():
            logo_label.setText("🐾")
            logo_label.setStyleSheet("font-size: 28px; color: #00f5d4;")
        else:
            logo_label.setPixmap(logo_pixmap)

        brand_label = QLabel("Pardus Hello")
        brand_label.setObjectName("brandLabel")
        brand_label.setFont(QFont("Inter", 14, QFont.Bold))

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(brand_label)
        logo_layout.addStretch()
        sidebar_layout.addWidget(logo_container)

        # Sidebar Menü Listesi
        self.sidebar_list = QListWidget()
        self.sidebar_list.setObjectName("sidebarList")
        self.sidebar_list.setIconSize(QSize(22, 22))
        self.sidebar_list.setSpacing(6)
        
        self.menu_items = [
            {"text": "Hoş Geldiniz", "icon": "go-home"},
            {"text": "Uygulamalar ve Ayarlar", "icon": "system-run"},
            {"text": "Çekirdek Yöneticisi", "icon": "utilities-terminal"},
            {"text": "Paket Kurucu", "icon": "system-software-install"},
            {"text": "Destek ve Topluluk", "icon": "network-workgroup"}
        ]

        for item in self.menu_items:
            list_item = QListWidgetItem()
            list_item.setText(item["text"])
            icon = QIcon.fromTheme(item["icon"])
            if icon.isNull():
                icon = QIcon.fromTheme("dialog-information")
            list_item.setIcon(icon)
            self.sidebar_list.addItem(list_item)

        self.sidebar_list.setCurrentRow(0)
        self.sidebar_list.currentRowChanged.connect(self.change_page)
        sidebar_layout.addWidget(self.sidebar_list)
        
        # Altbilgi sürümü
        footer_version = QLabel("Pardus Hello v2026.1 (PoC)")
        footer_version.setObjectName("footerVersion")
        footer_version.setAlignment(Qt.AlignCenter)
        footer_version.setStyleSheet("font-size: 10px;")
        sidebar_layout.addWidget(footer_version)

        main_layout.addWidget(sidebar_frame, stretch=1)

        # ======================================================================
        # SAĞ Taraf (Üst Bar ve QStackedWidget)
        # ======================================================================
        right_container = QWidget()
        right_container.setObjectName("rightContainer")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Üst Bar (Tema Değiştirme Butonu)
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(50)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 5, 20, 5)
        top_bar_layout.addStretch()

        self.theme_btn = QPushButton()
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.setObjectName("themeToggleBtn")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.update_theme_button()
        top_bar_layout.addWidget(self.theme_btn)

        right_layout.addWidget(top_bar)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stackedWidget")
        
        # Sayfaları Ekle
        self.create_welcome_page()
        self.create_apps_tweaks_page()
        self.create_kernel_manager_page()
        self.create_package_installer_page()
        self.create_support_page()
        
        right_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(right_container, stretch=3)

    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def toggle_theme(self):
        """Karanlık ve Aydınlık temalar arasında geçiş yapar."""
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.setStyleSheet(LIGHT_QSS)
        else:
            self.current_theme = "dark"
            self.setStyleSheet(DARK_QSS)
        self.update_theme_button()

    def update_theme_button(self):
        """Tema durumuna göre butonun simgesini ve tooltip bilgisini günceller."""
        if self.current_theme == "dark":
            self.theme_btn.setText("☀️")
            self.theme_btn.setToolTip("Aydınlık Temaya Geç")
        else:
            self.theme_btn.setText("🌙")
            self.theme_btn.setToolTip("Karanlık Temaya Geç")

    # ==============================================================================
    # DONANIM BİLGİSİ SORGULARI
    # ==============================================================================
    
    def get_cpu_info(self):
        try:
            if platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
            return platform.processor() or "Bilinmeyen x86_64 İşlemci"
        except Exception:
            return "İşlemci Bilgisi Alınamadı"

    def get_ram_info(self):
        try:
            if platform.system() == "Linux":
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if "MemTotal" in line:
                            kb_val = int(line.split()[1])
                            gb_val = round(kb_val / (1024 * 1024), 1)
                            return f"{gb_val} GB"
            return "8.0 GB"
        except Exception:
            return "RAM Bilgisi Alınamadı"

    def get_os_info(self):
        try:
            if os.path.exists("/etc/os-release"):
                release_data = {}
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            release_data[k] = v.strip('"')
                return release_data.get("PRETTY_NAME", "Pardus GNU/Linux")
            return "Pardus GNU/Linux (Debian)"
        except Exception:
            return "Pardus GNU/Linux"

    # ==============================================================================
    # SAYFA OLUŞTURUCULAR
    # ==============================================================================

    def create_welcome_page(self):
        """1. Hoş Geldiniz Sayfası"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 0, 30, 30)  # Üst bar eklendiği için üst marjı sıfıra çektik
        layout.setSpacing(24)

        # CachyOS Hello Gradyan Banner
        banner = QFrame()
        banner.setObjectName("bannerFrame")
        banner.setFixedHeight(120)
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(20, 20, 20, 20)
        banner_layout.setSpacing(4)
        
        banner_title = QLabel("PARDUS HELLO")
        banner_title.setObjectName("bannerTitle")
        banner_title.setFont(QFont("Inter", 22, QFont.Bold))
        
        banner_subtitle = QLabel("Pardus GNU/Linux Hızlı Yapılandırma ve Kurulum Portalı")
        banner_subtitle.setObjectName("bannerSubtitle")
        banner_subtitle.setFont(QFont("Inter", 12, QFont.Medium))
        
        banner_layout.addWidget(banner_title)
        banner_layout.addWidget(banner_subtitle)
        layout.addWidget(banner)

        # Açıklama Kutusu
        intro_card = QFrame()
        intro_card.setObjectName("cardFrame")
        intro_layout = QVBoxLayout(intro_card)
        intro_layout.setContentsMargins(20, 20, 20, 20)
        
        intro_text = QLabel(
            "Milli İşletim Sistemimiz Pardus'a hoş geldiniz! Bu arayüz, CachyOS Hello "
            "mimarisinden esinlenilerek geliştirilmiş bir kavram kanıtı (PoC) çalışmasıdır.\n\n"
            "Sol menüden sistem ayarlarını düzenleyebilir, bağımsız kernel geçişlerini simüle edebilir, "
            "sık kullanılan paketleri kurabilir veya resmi topluluk sitelerini ziyaret edebilirsiniz."
        )
        intro_text.setObjectName("introText")
        intro_text.setWordWrap(True)
        intro_text.setFont(QFont("Inter", 11))
        intro_layout.addWidget(intro_text)
        layout.addWidget(intro_card)

        # Sistem Donanım Bilgileri Kartı
        sys_info_title = QLabel("Sistem Donanım Özellikleri")
        sys_info_title.setObjectName("sectionTitle")
        layout.addWidget(sys_info_title)

        hw_card = QFrame()
        hw_card.setObjectName("hardwareCard")
        hw_layout = QGridLayout(hw_card)
        hw_layout.setContentsMargins(20, 20, 20, 20)
        hw_layout.setSpacing(16)

        fields = [
            ("İşletim Sistemi:", self.os_info, "system-run"),
            ("Çekirdek Sürümü:", self.kernel_info, "utilities-terminal"),
            ("İşlemci (CPU):", self.cpu_info, "cpu"),
            ("Sistem RAM (Bellek):", self.ram_info, "media-flash")
        ]

        for i, (label_name, label_val, icon_name) in enumerate(fields):
            icon_lbl = QLabel()
            icon_lbl.setPixmap(QIcon.fromTheme(icon_name).pixmap(24, 24))
            
            lbl_title = QLabel(label_name)
            lbl_title.setStyleSheet("font-weight: bold; color: #00f5d4;" if self.current_theme == "dark" else "font-weight: bold; color: #00a896;")
            
            lbl_val = QLabel(label_val)
            lbl_val.setWordWrap(True)
            
            hw_layout.addWidget(icon_lbl, i, 0)
            hw_layout.addWidget(lbl_title, i, 1)
            hw_layout.addWidget(lbl_val, i, 2)

        hw_layout.setColumnStretch(2, 1)
        layout.addWidget(hw_card)

        # Calamares Entegrasyon Butonu
        btn_layout = QHBoxLayout()
        self.calamares_btn = QPushButton("Pardus Kurulum Sihirbazını Başlat (Calamares)")
        self.calamares_btn.setObjectName("primaryActionBtn")
        self.calamares_btn.setIcon(QIcon.fromTheme("system-run"))
        self.calamares_btn.clicked.connect(self.simulate_calamares)
        btn_layout.addWidget(self.calamares_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()
        self.stacked_widget.addWidget(page)

    def create_apps_tweaks_page(self):
        """2. Uygulamalar ve İnce Ayarlar Sayfası (Apps/Tweaks)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 0, 30, 30)
        layout.setSpacing(20)

        # Başlık
        title_label = QLabel("Uygulamalar ve İnce Ayarlar (Apps/Tweaks)")
        title_label.setObjectName("headerTitle")
        layout.addWidget(title_label)

        desc_label = QLabel("Sistem servislerini açıp kapatın veya genel bakım işlemlerini tetikleyin (Simüle Edilmiştir).")
        desc_label.setObjectName("sectionDesc")
        layout.addWidget(desc_label)

        # 1. Bölüm: Sistem Servisleri (Checkboxes)
        services_frame = QFrame()
        services_frame.setObjectName("cardFrame")
        sf_layout = QVBoxLayout(services_frame)
        sf_layout.setContentsMargins(20, 20, 20, 20)
        sf_layout.setSpacing(16)

        sf_title = QLabel("Sistem Servisleri ve Güvenlik")
        sf_title.setObjectName("groupTitle")
        sf_layout.addWidget(sf_title)

        # Servis Checkboxları
        self.chk_bluetooth = QCheckBox("Bluetooth Servisi (systemctl enable bluetooth)")
        self.chk_bluetooth.setChecked(True)
        self.chk_bluetooth.stateChanged.connect(lambda state: self.simulate_service_toggle("Bluetooth", state))

        self.chk_apparmor = QCheckBox("AppArmor Güvenlik Modülü (systemctl enable apparmor)")
        self.chk_apparmor.setChecked(True)
        self.chk_apparmor.stateChanged.connect(lambda state: self.simulate_service_toggle("AppArmor", state))

        self.chk_dnscrypt = QCheckBox("DNSCrypt Proxy (Şifreli DNS Protokolü)")
        self.chk_dnscrypt.setChecked(False)
        self.chk_dnscrypt.stateChanged.connect(lambda state: self.simulate_service_toggle("DNSCrypt-Proxy", state))

        self.chk_oomd = QCheckBox("Systemd-OOMD (Bellek Dolduğunda Korumayı Aktifleştir)")
        self.chk_oomd.setChecked(True)
        self.chk_oomd.stateChanged.connect(lambda state: self.simulate_service_toggle("Systemd-OOMD", state))

        sf_layout.addWidget(self.chk_bluetooth)
        sf_layout.addWidget(self.chk_apparmor)
        sf_layout.addWidget(self.chk_dnscrypt)
        sf_layout.addWidget(self.chk_oomd)

        layout.addWidget(services_frame)

        # 2. Bölüm: Sistem Düzeltmeleri (Fixes / Maintenance)
        fixes_frame = QFrame()
        fixes_frame.setObjectName("cardFrame")
        ff_layout = QVBoxLayout(fixes_frame)
        ff_layout.setContentsMargins(20, 20, 20, 20)
        ff_layout.setSpacing(14)

        ff_title = QLabel("Bakım ve Hızlı Düzeltmeler (System Fixes)")
        ff_title.setObjectName("groupTitle")
        ff_layout.addWidget(ff_title)

        # Buton Izgarası
        btn_grid_widget = QWidget()
        btn_grid = QGridLayout(btn_grid_widget)
        btn_grid.setContentsMargins(0, 0, 0, 0)
        btn_grid.setSpacing(12)

        btn_lock = QPushButton("db Kilitlerini Kaldır")
        btn_lock.clicked.connect(self.simulate_remove_lock)
        btn_lock.setIcon(QIcon.fromTheme("dialog-warning"))
        
        btn_cache = QPushButton("Önbellek Temizle")
        btn_cache.clicked.connect(self.simulate_clean_cache)
        btn_cache.setIcon(QIcon.fromTheme("edit-clear-all"))

        btn_reinstall = QPushButton("Sistem Paketlerini Güncelle")
        btn_reinstall.clicked.connect(self.simulate_update_packages)
        btn_reinstall.setIcon(QIcon.fromTheme("system-software-update"))

        btn_grid.addWidget(btn_lock, 0, 0)
        btn_grid.addWidget(btn_cache, 0, 1)
        btn_grid.addWidget(btn_reinstall, 0, 2)
        ff_layout.addWidget(btn_grid_widget)

        layout.addWidget(fixes_frame)
        layout.addStretch()

        self.stacked_widget.addWidget(page)

    def create_kernel_manager_page(self):
        """3. Çekirdek Yöneticisi Sayfası (CachyOS Kernel Manager Tarzı)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 0, 30, 30)
        layout.setSpacing(20)

        # Başlık
        title_label = QLabel("Çekirdek Yöneticisi (Kernel Manager)")
        title_label.setObjectName("headerTitle")
        layout.addWidget(title_label)

        desc_label = QLabel(
            "Debian/Pardus için optimize edilmiş çekirdek paketlerini kurabilir ve geçiş yapabilirsiniz.\n"
            "Mevcut sisteminizde çalışan sürüm: <b>" + self.kernel_info + "</b>"
        )
        desc_label.setObjectName("sectionDesc")
        layout.addWidget(desc_label)

        # Çekirdek Listesi (CachyOS tarzı)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        scroll_layout.setSpacing(12)

        self.kernels = [
            {"id": "default", "name": "linux-image-amd64", "desc": "Pardus Standart Kararlı Çekirdek (Önerilen)", "active": True},
            {"id": "rt", "name": "linux-image-rt-amd64", "desc": "Düşük Gecikmeli Gerçek Zamanlı Çekirdek (Realtime)", "active": False},
            {"id": "lts", "name": "linux-image-6.1.0-amd64", "desc": "Uzun Süreli Desteklenen Çekirdek (Debian Stable)", "active": False},
            {"id": "liquorix", "name": "linux-image-liquorix-amd64", "desc": "Liquorix Yüksek Performanslı Oyun ve Masaüstü Çekirdeği", "active": False}
        ]

        for k in self.kernels:
            card = QFrame()
            card.setObjectName("cardFrame")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)
            card_layout.setSpacing(16)

            # İkon
            icon_lbl = QLabel()
            icon_lbl.setPixmap(QIcon.fromTheme("utilities-terminal").pixmap(32, 32))
            card_layout.addWidget(icon_lbl)

            # Bilgiler
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(4)

            k_title = QLabel()
            k_title.setObjectName("cardTitle")
            
            # Çalışan çekirdeği belirle (Pardus / Debian standartlarına göre)
            is_currently_running = (k["id"] == "default")
                
            if is_currently_running:
                k_title.setText(k["name"] + f" <span style='color: {'#00f5d4' if self.current_theme == 'dark' else '#00a896'}; font-size: 10px; font-weight: bold;'>[ AKTİF ]</span>")
            else:
                k_title.setText(k["name"])
            k_title.setFont(QFont("Inter", 12, QFont.Bold))

            k_desc = QLabel(k["desc"])
            k_desc.setObjectName("cardDesc")

            info_layout.addWidget(k_title)
            info_layout.addWidget(k_desc)
            card_layout.addWidget(info_widget, stretch=1)

            # İşlem Butonları (Kur / Kaldır)
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(8)

            if is_currently_running:
                status_lbl = QLabel("Çalışıyor")
                status_lbl.setStyleSheet("color: #00f5d4; font-weight: bold;" if self.current_theme == "dark" else "color: #008e7f; font-weight: bold;")
                btn_layout.addWidget(status_lbl)
            else:
                install_btn = QPushButton("Kur")
                install_btn.setObjectName("primaryActionBtn")
                install_btn.clicked.connect(lambda checked, kn=k["name"]: self.simulate_kernel_install(kn))
                
                remove_btn = QPushButton("Kaldır")
                remove_btn.setObjectName("dangerActionBtn")
                remove_btn.clicked.connect(lambda checked, kn=k["name"]: self.simulate_kernel_remove(kn))
                
                btn_layout.addWidget(remove_btn)
                btn_layout.addWidget(install_btn)

            card_layout.addWidget(btn_container)
            scroll_layout.addWidget(card)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        self.stacked_widget.addWidget(page)

    def create_package_installer_page(self):
        """4. Paket Kurucu Sayfası (Kategorilendirilmiş Popüler Yazılımlar)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 0, 30, 30)
        layout.setSpacing(16)

        # Başlık
        title_label = QLabel("Popüler Yazılım Kurucu")
        title_label.setObjectName("headerTitle")
        layout.addWidget(title_label)

        # Kategori Seçimi (CachyOS Segmented Control Tarzı Radio Button Grubu)
        cat_frame = QFrame()
        cat_frame.setObjectName("cardFrame")
        cat_frame.setFixedHeight(50)
        cat_layout = QHBoxLayout(cat_frame)
        cat_layout.setContentsMargins(6, 6, 6, 6)
        cat_layout.setSpacing(4)

        categories = [
            ("Tarayıcılar", 0),
            ("Ofis & Tasarım", 1),
            ("Geliştirici Araçları", 2),
            ("Multimedya & Oyun", 3)
        ]

        self.cat_group = QButtonGroup(self)
        self.radio_buttons = []

        for name, idx in categories:
            radio = QRadioButton(name)
            
            # Segmented control active themes
            if self.current_theme == "dark":
                radio.setStyleSheet(
                    "QRadioButton { background-color: transparent; border: none; border-radius: 6px; padding: 6px 16px; text-align: center; font-weight: bold; color: #a9b1d6; }"
                    "QRadioButton::indicator { width: 0px; height: 0px; }"
                    "QRadioButton:hover { background-color: #1e2030; color: #ffffff; }"
                    "QRadioButton:checked { background-color: #00f5d4; color: #0f111a; }"
                )
            else:
                radio.setStyleSheet(
                    "QRadioButton { background-color: transparent; border: none; border-radius: 6px; padding: 6px 16px; text-align: center; font-weight: bold; color: #5c5f77; }"
                    "QRadioButton::indicator { width: 0px; height: 0px; }"
                    "QRadioButton:hover { background-color: #ccd0da; color: #1e1f29; }"
                    "QRadioButton:checked { background-color: #00a896; color: #ffffff; }"
                )
                
            cat_layout.addWidget(radio)
            self.cat_group.addButton(radio, idx)
            self.radio_buttons.append(radio)

        self.radio_buttons[0].setChecked(True)
        self.cat_group.buttonClicked[int].connect(self.change_software_category)
        layout.addWidget(cat_frame)

        # Stacked Widget (Her kategori için ayrı sayfa düzeni sunar)
        self.software_stack = QStackedWidget()
        
        # Kategorilerdeki yazılımları tanımlayalım
        self.software_data = {
            0: [ # Tarayıcılar
                {"id": "chrome", "name": "Google Chrome", "desc": "Hızlı, güvenli ve en popüler ağ tarayıcısı.", "pkg": "google-chrome-stable", "icon": "google-chrome"},
                {"id": "firefox", "name": "Mozilla Firefox", "desc": "Gizlilik odaklı, kararlı ve açık kaynaklı web tarayıcı.", "pkg": "firefox-esr", "icon": "firefox"},
                {"id": "brave", "name": "Brave Browser", "desc": "Reklamları otomatik engelleyen, gizlilik merkezli hızlı tarayıcı.", "pkg": "brave-browser", "icon": "brave"},
                {"id": "vivaldi", "name": "Vivaldi", "desc": "Kişiselleştirilebilir ve gelişmiş sekme özellikli tarayıcı.", "pkg": "vivaldi-stable", "icon": "vivaldi"}
            ],
            1: [ # Ofis ve Tasarım
                {"id": "libreoffice", "name": "LibreOffice", "desc": "Tam donanımlı, popüler açık kaynaklı ofis paketi.", "pkg": "libreoffice", "icon": "libreoffice"},
                {"id": "onlyoffice", "name": "OnlyOffice Desktop Editors", "desc": "MS Office formatları ile yüksek uyumluluğa sahip ofis düzenleyici.", "pkg": "onlyoffice-desktopeditors", "icon": "onlyoffice"},
                {"id": "gimp", "name": "GIMP", "desc": "GNU Resim Düzenleme Programı, güçlü photoshop alternatifi.", "pkg": "gimp", "icon": "gimp"},
                {"id": "inkscape", "name": "Inkscape", "desc": "Vektörel grafik ve çizim tasarım aracı.", "pkg": "inkscape", "icon": "inkscape"}
            ],
            2: [ # Geliştirici Araçları
                {"id": "vscode", "name": "Visual Studio Code", "desc": "Modern diller için en yaygın kod düzenleme platformu.", "pkg": "code", "icon": "visual-studio-code"},
                {"id": "pycharm", "name": "PyCharm Community", "desc": "Python geliştiricileri için akıllı IDE aracı.", "pkg": "pycharm-community", "icon": "pycharm"},
                {"id": "gitkraken", "name": "GitKraken", "desc": "Git yönetimini kolaylaştıran şık ve görsel arayüz.", "pkg": "gitkraken", "icon": "gitkraken"},
                {"id": "docker", "name": "Docker Engine", "desc": "Konteyner tabanlı sanallaştırma teknolojisi.", "pkg": "docker-ce", "icon": "docker"}
            ],
            3: [ # Multimedya ve Oyun
                {"id": "steam", "name": "Steam Client", "desc": "En geniş dijital oyun mağazası ve çalıştırma platformu.", "pkg": "steam", "icon": "steam"},
                {"id": "lutris", "name": "Lutris", "desc": "Linux üzerindeki tüm oyun kütüphanelerinizi birleştiren başlatıcı.", "pkg": "lutris", "icon": "lutris"},
                {"id": "vlc", "name": "VLC Media Player", "desc": "Açık kaynak kodlu, neredeyse tüm formatları oynatan medya oynatıcı.", "pkg": "vlc", "icon": "vlc"},
                {"id": "spotify", "name": "Spotify Client", "desc": "Müzik, podcast ve çalma listesi akış servisi.", "pkg": "spotify-client", "icon": "spotify"}
            ]
        }

        self.installer_buttons = {}

        # Her kategori için ekranı kur
        for cat_id, app_list in self.software_data.items():
            cat_page = QWidget()
            cat_page_layout = QVBoxLayout(cat_page)
            cat_page_layout.setContentsMargins(0, 0, 0, 0)
            
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setContentsMargins(0, 0, 10, 0)
            scroll_layout.setSpacing(10)

            for app in app_list:
                card = QFrame()
                card.setObjectName("cardFrame")
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(16, 16, 16, 16)
                card_layout.setSpacing(16)

                # İkon
                app_icon_lbl = QLabel()
                app_icon = QIcon.fromTheme(app["icon"])
                if app_icon.isNull():
                    app_icon = QIcon.fromTheme("application-x-executable")
                app_icon_lbl.setPixmap(app_icon.pixmap(36, 36))
                card_layout.addWidget(app_icon_lbl)

                # Yazı bölmesi
                text_container = QWidget()
                text_layout = QVBoxLayout(text_container)
                text_layout.setContentsMargins(0, 0, 0, 0)
                text_layout.setSpacing(4)

                app_title = QLabel(app["name"])
                app_title.setObjectName("cardTitle")
                app_title.setFont(QFont("Inter", 11, QFont.Bold))
                
                app_desc = QLabel(app["desc"])
                app_desc.setObjectName("cardDesc")
                app_desc.setWordWrap(True)

                text_layout.addWidget(app_title)
                text_layout.addWidget(app_desc)
                card_layout.addWidget(text_container, stretch=1)

                # Yükleme butonu
                install_btn = QPushButton("Kur")
                install_btn.setObjectName("primaryActionBtn")
                install_btn.setMinimumWidth(80)
                install_btn.clicked.connect(lambda checked, a=app: self.simulate_install(a))
                
                self.installer_buttons[app["id"]] = install_btn
                card_layout.addWidget(install_btn)

                scroll_layout.addWidget(card)

            scroll_content.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_content)
            cat_page_layout.addWidget(scroll_area)
            self.software_stack.addWidget(cat_page)

        layout.addWidget(self.software_stack)
        self.stacked_widget.addWidget(page)

    def change_software_category(self, cat_id):
        self.software_stack.setCurrentIndex(cat_id)

    def create_support_page(self):
        """5. Destek ve Topluluk Sayfası (CachyOS Tarzı)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 0, 30, 30)
        layout.setSpacing(20)

        # Başlık
        title_label = QLabel("Destek ve Topluluk Kaynakları")
        title_label.setObjectName("headerTitle")
        layout.addWidget(title_label)

        desc_label = QLabel("Pardus ile ilgili teknik dökümantasyona ulaşın, sorunlarınızı forumda paylaşın ve yardım alın.")
        desc_label.setObjectName("sectionDesc")
        layout.addWidget(desc_label)

        # Grid Düzeni
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(16)

        support_items = [
            {"title": "Pardus Forum", "desc": "Kullanıcılar arası teknik destek ve dayanışma forumu.", "url": "https://forum.pardus.org.tr", "icon": "internet-group-chat"},
            {"title": "Pardus Wiki", "desc": "Resmi rehberler, teknik makaleler ve bilgi havuzu.", "url": "https://wiki.pardus.org.tr", "icon": "accessories-dictionary"},
            {"title": "Talep Portalı", "desc": "Sorun ve özellik isteklerinizi resmi geliştirici ekibine iletin.", "url": "https://talep.pardus.org.tr", "icon": "mail-send-receive"},
            {"title": "Resmi Web Sitesi", "desc": "Pardus ana web sayfası, güncel duyurular ve resmi paket indirme portalı.", "url": "https://www.pardus.org.tr", "icon": "applications-internet"},
            {"title": "Pardus GitHub", "desc": "Pardus projelerinin açık kaynak kod depoları.", "url": "https://github.com/pardus", "icon": "github"},
            {"title": "Pardus Gönüllüleri", "desc": "Topluluk projelerine katkıda bulunmak ve yer almak için gönüllülük portalı.", "url": "https://gonullu.pardus.org.tr", "icon": "system-users"}
        ]

        for idx, item in enumerate(support_items):
            card = QFrame()
            card.setObjectName("cardFrame")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 20, 20, 20)
            card_layout.setSpacing(10)

            # Üst satır: İkon ve Başlık
            h_layout = QHBoxLayout()
            icon_lbl = QLabel()
            icon_lbl.setPixmap(QIcon.fromTheme(item["icon"]).pixmap(28, 28))
            
            s_title = QLabel(item["title"])
            s_title.setObjectName("cardTitle")
            s_title.setFont(QFont("Inter", 11, QFont.Bold))
            
            h_layout.addWidget(icon_lbl)
            h_layout.addWidget(s_title)
            h_layout.addStretch()
            card_layout.addLayout(h_layout)

            # Açıklama
            s_desc = QLabel(item["desc"])
            s_desc.setObjectName("cardDesc")
            s_desc.setWordWrap(True)
            card_layout.addWidget(s_desc)
            card_layout.addStretch()

            # Ziyaret et butonu
            visit_btn = QPushButton("Bağlantıyı Aç")
            visit_btn.clicked.connect(lambda checked, url=item["url"]: webbrowser.open(url))
            card_layout.addWidget(visit_btn)

            row = idx // 2
            col = idx % 2
            grid.addWidget(card, row, col)

        layout.addWidget(grid_widget)
        layout.addStretch()
        self.stacked_widget.addWidget(page)

    # ==============================================================================
    # SİMÜLASYON YÖNETİM METOTLARI
    # ==============================================================================

    def simulate_calamares(self):
        auth = AuthDialog(self, action_text="Pardus Canlı Kurulum Sihirbazı", package_name="calamares-settings-pardus")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Kurulum Sihirbazı Yükleniyor", package_name="calamares")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(
                    self,
                    "PoC Kurulum Simülasyonu",
                    "PoC Sürümü: Arka planda '/usr/bin/calamares' kurulum sihirbazının çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )

    def simulate_service_toggle(self, service_name, state):
        status_text = "Etkinleştiriliyor" if state == Qt.Checked else "Devre Dışı Bırakılıyor"
        action_cmd = "enable" if state == Qt.Checked else "disable"
        
        auth = AuthDialog(self, action_text=f"{service_name} Servisi ({status_text})", package_name=f"systemd-service-{service_name.lower()}")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text=f"Servis Durumu Değiştiriliyor ({service_name})", package_name="systemctl")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(
                    self,
                    "Servis Yapılandırıldı",
                    f"PoC Sürümü: Arka planda 'sudo systemctl {action_cmd} {service_name.lower()}' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )
        else:
            # İşlem iptal edildiyse eski durumuna çek (sinyali geçici engellemek için)
            self.sender().blockSignals(True)
            self.sender().setChecked(not state)
            self.sender().blockSignals(False)

    def simulate_remove_lock(self):
        auth = AuthDialog(self, action_text="Veritabanı Paket Kilidini Kaldırma", package_name="dpkg-lock-remover")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Paket Kilidi Temizleniyor", package_name="dpkg")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(
                    self,
                    "Kilit Kaldırıldı",
                    "PoC Sürümü: Arka planda 'sudo rm -f /var/lib/dpkg/lock-frontend' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )

    def simulate_clean_cache(self):
        auth = AuthDialog(self, action_text="Paket Önbellek Temizleme", package_name="apt-cleaner")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Paket Önbelleği Temizleniyor", package_name="apt")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(
                    self,
                    "Önbellek Temizlendi",
                    "PoC Sürümü: Arka planda 'sudo apt-get clean && sudo apt-get autoremove' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )

    def simulate_update_packages(self):
        auth = AuthDialog(self, action_text="Sistem Paketlerini Güncelleme", package_name="system-updater")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Depolar Denetleniyor", package_name="apt-update")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(
                    self,
                    "Sistem Güncel",
                    "PoC Sürümü: Arka planda 'sudo apt-get update && sudo apt-get upgrade -y' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )

    def simulate_kernel_install(self, kernel_name):
        auth = AuthDialog(self, action_text=f"Yeni Çekirdek Kurulumu ({kernel_name})", package_name=kernel_name)
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text=f"{kernel_name} İndiriliyor ve Kuruluyor", package_name=kernel_name)
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(
                    self,
                    "Çekirdek Kuruldu",
                    f"PoC Sürümü: Arka planda 'sudo apt install {kernel_name}' komutunun çalıştırılması simüle edildi.\n\nSistemi yeniden başlatarak bu çekirdeği aktif edebilirsiniz.",
                    QMessageBox.Ok
                )

    def simulate_kernel_remove(self, kernel_name):
        auth = AuthDialog(self, action_text=f"Çekirdek Kaldırma ({kernel_name})", package_name=kernel_name)
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text=f"{kernel_name} Sistemden Siliniyor", package_name=kernel_name)
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(
                    self,
                    "Çekirdek Kaldırıldı",
                    f"PoC Sürümü: Arka planda 'sudo apt purge {kernel_name}' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )

    def simulate_install(self, app_info):
        auth = AuthDialog(self, action_text=f"{app_info['name']} Kurulumu", package_name=app_info["pkg"])
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text=f"{app_info['name']} Kuruluyor", package_name=app_info["pkg"])
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(
                    self,
                    "Uygulama Kuruldu",
                    f"PoC Sürümü: Arka planda 'sudo apt install {app_info['pkg']}' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )
                btn = self.installer_buttons[app_info["id"]]
                btn.setText("Kuruldu")
                btn.setEnabled(False)
                
                # Temaya göre kurulu butonu rengini ayarla
                if self.current_theme == "dark":
                    btn.setStyleSheet("background-color: #00f5d4; color: #0f111a; font-weight: bold; border: none;")
                else:
                    btn.setStyleSheet("background-color: #00a896; color: #ffffff; font-weight: bold; border: none;")


# ==============================================================================
# ANA ÇALIŞTIRICI
# ==============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PardusHello")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
