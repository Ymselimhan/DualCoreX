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
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint, QRect, qInstallMessageHandler
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QPainter, QBrush, QPen

# ==============================================================================
# HATA VE UYARI MESAJI FİLTRELEME (Log Suppressor)
# ==============================================================================

def qt_message_handler(mode, context, message):
    # Wayland ve QSocketNotifier kaynaklı zararsız Qt uyarılarını terminalde gizler
    ignored_keywords = [
        "QSocketNotifier",
        "requestActivate",
        "Wayland does not support",
        "runtime directory"
    ]
    if any(kw in message for kw in ignored_keywords):
        return
    
    # Diğer kritik sistem mesajlarını ve hatalarını standart hata akışına yazdırır
    import sys
    sys.stderr.write(f"{message}\n")

qInstallMessageHandler(qt_message_handler)

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
    QRadioButton,
    QComboBox,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QSizeGrip,
    QAbstractButton,
    QTextEdit
)

# ==============================================================================
# SİSTEM TEMA ALGILAMA YÖNTEMİ
# ==============================================================================

def detect_system_dark_mode():
    """Sistemin karanlık modda olup olmadığını gdbus portal veya gsettings ile algılar."""
    try:
        cmd = [
            "gdbus", "call", "--session",
            "--dest", "org.freedesktop.portal.Desktop",
            "--object-path", "/org/freedesktop/portal/desktop",
            "--method", "org.freedesktop.portal.Settings.Read",
            "org.freedesktop.appearance", "color-scheme"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1)
        if "uint32 1" in result.stdout:
            return True
        elif "uint32 2" in result.stdout:
            return False
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True, text=True, timeout=1
        )
        if "prefer-dark" in result.stdout.lower():
            return True
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            capture_output=True, text=True, timeout=1
        )
        if "dark" in result.stdout.lower():
            return True
    except Exception:
        pass

    return True


# ==============================================================================
# QSS STİL ŞABLONLARI (CachyOS Tarzı Koyu ve Aydınlık Modlar)
# ==============================================================================

DARK_QSS = """
/* Ana Pencere ve Genel Ayarlar */
QMainWindow {
    background-color: #0c0f17;
}

QWidget#centralWidget {
    background-color: #0c0f17;
}

QLabel {
    color: #c8d3f5;
    background-color: transparent;
}

/* Özel Başlık Çubuğu */
CustomTitleBar {
    background-color: #090b10;
    border-bottom: 1px solid #1f2335;
}

QLabel#titleBarTitle {
    color: #ffffff;
    font-size: 13px;
    background-color: transparent;
}

QLabel#titleBarSubtitle {
    color: #565f89;
    font-size: 10px;
    background-color: transparent;
}

QPushButton#titleBarInfoBtn, QPushButton#titleBarMinBtn, QPushButton#titleBarMaxBtn, QPushButton#titleBarCloseBtn {
    background-color: #1e2030;
    color: #a9b1d6;
    border: none;
    border-radius: 13px;
    font-weight: bold;
}

QPushButton#titleBarInfoBtn:hover, QPushButton#titleBarMinBtn:hover, QPushButton#titleBarMaxBtn:hover {
    background-color: #2d3149;
    color: #ffffff;
}

QPushButton#titleBarCloseBtn:hover {
    background-color: #ff007f;
    color: #ffffff;
}

/* Kartlar ve Çerçeveler */
QFrame#cardFrame {
    background-color: #131620;
    border: 1px solid #1f2335;
    border-radius: 12px;
}

QFrame#hardwareCard {
    background-color: #151823;
    border: 1px solid #24283b;
    border-radius: 12px;
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
    background-color: #0c0f17;
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
    background-color: #1c1e2a;
    color: #c8d3f5;
    border: 1px solid #24283b;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #24283b;
    color: #ffffff;
    border-color: #3b3f5c;
}

QPushButton:pressed {
    background-color: #171922;
}

/* Grid Bağlantı Butonları */
QPushButton#linkGridBtn {
    background-color: #131620;
    color: #c8d3f5;
    border: 1px solid #1f2335;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#linkGridBtn:hover {
    background-color: #1c1e2a;
    border-color: #00f5d4;
    color: #ffffff;
}

/* Geri Butonu */
QPushButton#backBtn {
    background-color: #1c1e2a;
    border: 1px solid #24283b;
    border-radius: 6px;
    font-weight: bold;
    font-size: 14px;
    color: #c8d3f5;
}

QPushButton#backBtn:hover {
    border-color: #00f5d4;
    color: #00f5d4;
}

/* Birincil Eylem Butonları (Yeşil Vurgu) */
QPushButton#primaryActionBtn {
    background-color: #00f5d4;
    color: #0c0f17;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    padding: 10px 20px;
}

QPushButton#primaryActionBtn:hover {
    background-color: #33ffeb;
}

QPushButton#primaryActionBtn:pressed {
    background-color: #00d2b4;
}

QPushButton#primaryActionBtn:disabled {
    background-color: #171922;
    color: #565f89;
}

/* Kaldır/Tehlike Butonları (Kırmızı Vurgu) */
QPushButton#dangerActionBtn {
    background-color: #ff007f;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    padding: 10px 20px;
}

QPushButton#dangerActionBtn:hover {
    background-color: #ff3399;
}

QPushButton#dangerActionBtn:disabled {
    background-color: #171922;
    color: #565f89;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
    font-weight: 600;
    color: #c8d3f5;
    background-color: transparent;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid #3b3f5c;
    background-color: #1c1e2a;
}

QCheckBox::indicator:hover {
    border-color: #00f5d4;
}

QCheckBox::indicator:checked {
    background-color: #00f5d4;
    border-color: #00f5d4;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='24' height='24'><path d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z' fill='%230c0f17'/></svg>");
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
    font-size: 26px;
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

QLabel#groupTitle {
    font-weight: bold;
    font-size: 15px;
    color: #ffffff;
    border-bottom: 1px solid #1f2335;
    padding-bottom: 6px;
}

QLabel#cardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#cardDesc {
    font-size: 12px;
    color: #9ab3db;
}

/* Dil Seçimi (QComboBox) */
QComboBox#footerLangCombo {
    background-color: #131620;
    color: #c8d3f5;
    border: 1px solid #1f2335;
    border-radius: 6px;
    padding: 3px 10px;
}

QComboBox#footerLangCombo:hover {
    border-color: #00f5d4;
}

QComboBox#footerLangCombo QAbstractItemView {
    background-color: #131620;
    color: #c8d3f5;
    border: 1px solid #1f2335;
    selection-background-color: #00f5d4;
    selection-color: #0c0f17;
}

/* Sekme Yapısı (QTabWidget) */
QTabWidget::pane {
    border: 1px solid #1f2335;
    background-color: #131620;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #1c1e2a;
    color: #a9b1d6;
    padding: 8px 35px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #131620;
    color: #00f5d4;
    border-bottom: 2px solid #00f5d4;
}

QTabBar::tab:hover:!selected {
    background-color: #24283b;
    color: #ffffff;
}

/* Paket Ağacı (QTreeWidget) */
QTreeWidget {
    background-color: #131620;
    border: none;
    color: #c8d3f5;
    outline: none;
}

QTreeWidget::item {
    padding: 6px;
    border-bottom: 1px solid #1f2335;
}

QTreeWidget::item:hover {
    background-color: #1c1e2a;
    color: #ffffff;
}

QTreeWidget::item:selected {
    background-color: #1e2538;
    color: #00f5d4;
}

QHeaderView::section {
    background-color: #090b10;
    color: #00f5d4;
    padding: 6px;
    border: none;
    font-weight: bold;
}

/* İletişim Kutuları (Dialogs) */
QDialog {
    background-color: #131620;
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
    background-color: #0c0f17;
    border: 1px solid #1f2335;
    border-radius: 6px;
    padding: 8px 12px;
    color: #c8d3f5;
}

QLineEdit:focus {
    border: 1px solid #00f5d4;
}

QProgressBar {
    background-color: #0c0f17;
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

QLabel {
    color: #4c4f69;
    background-color: transparent;
}

/* Özel Başlık Çubuğu */
CustomTitleBar {
    background-color: #e6e9ef;
    border-bottom: 1px solid #ccd0da;
}

QLabel#titleBarTitle {
    color: #1e1f29;
    font-size: 13px;
    background-color: transparent;
}

QLabel#titleBarSubtitle {
    color: #6c6f85;
    font-size: 10px;
    background-color: transparent;
}

QPushButton#titleBarInfoBtn, QPushButton#titleBarMinBtn, QPushButton#titleBarMaxBtn, QPushButton#titleBarCloseBtn {
    background-color: #ccd0da;
    color: #5c5f77;
    border: none;
    border-radius: 13px;
    font-weight: bold;
}

QPushButton#titleBarInfoBtn:hover, QPushButton#titleBarMinBtn:hover, QPushButton#titleBarMaxBtn:hover {
    background-color: #bcc0cc;
    color: #1e1f29;
}

QPushButton#titleBarCloseBtn:hover {
    background-color: #d20f39;
    color: #ffffff;
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
    border-color: #acb0be;
}

QPushButton:pressed {
    background-color: #bcc0cc;
}

/* Grid Bağlantı Butonları */
QPushButton#linkGridBtn {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#linkGridBtn:hover {
    background-color: #dce0e8;
    border-color: #00a896;
    color: #1e1f29;
}

/* Geri Butonu */
QPushButton#backBtn {
    background-color: #dce0e8;
    border: 1px solid #bcc0cc;
    border-radius: 6px;
    font-weight: bold;
    font-size: 14px;
    color: #4c4f69;
}

QPushButton#backBtn:hover {
    border-color: #00a896;
    color: #00a896;
}

/* Birincil Eylem Butonları (Yeşil Vurgu) */
QPushButton#primaryActionBtn {
    background-color: #00a896;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    padding: 10px 20px;
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
    padding: 10px 20px;
}

QPushButton#dangerActionBtn:hover {
    background-color: #e64553;
}

QPushButton#dangerActionBtn:disabled {
    background-color: #ccd0da;
    color: #9ca0b0;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
    font-weight: 600;
    color: #4c4f69;
    background-color: transparent;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid #bcc0cc;
    background-color: #eff1f5;
}

QCheckBox::indicator:hover {
    border-color: #00a896;
}

QCheckBox::indicator:checked {
    background-color: #00a896;
    border-color: #00a896;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='24' height='24'><path d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z' fill='%23ffffff'/></svg>");
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
    font-size: 26px;
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

QLabel#groupTitle {
    font-weight: bold;
    font-size: 15px;
    color: #1e1f29;
    border-bottom: 1px solid #ccd0da;
    padding-bottom: 6px;
}

QLabel#cardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #1e1f29;
}

QLabel#cardDesc {
    font-size: 12px;
    color: #5c5f77;
}

/* Dil Seçimi (QComboBox) */
QComboBox#footerLangCombo {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 3px 10px;
}

QComboBox#footerLangCombo:hover {
    border-color: #00a896;
}

QComboBox#footerLangCombo QAbstractItemView {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    selection-background-color: #00a896;
    selection-color: #ffffff;
}

/* Sekme Yapısı (QTabWidget) */
QTabWidget::pane {
    border: 1px solid #ccd0da;
    background-color: #e6e9ef;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #dce0e8;
    color: #5c5f77;
    padding: 8px 35px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #e6e9ef;
    color: #008e7f;
    border-bottom: 2px solid #008e7f;
}

QTabBar::tab:hover:!selected {
    background-color: #ccd0da;
    color: #1e1f29;
}

/* Paket Ağacı (QTreeWidget) */
QTreeWidget {
    background-color: #e6e9ef;
    border: none;
    color: #4c4f69;
    outline: none;
}

QTreeWidget::item {
    padding: 6px;
    border-bottom: 1px solid #ccd0da;
}

QTreeWidget::item:hover {
    background-color: #dce0e8;
    color: #1e1f29;
}

QTreeWidget::item:selected {
    background-color: #d8dfeb;
    color: #008e7f;
}

QHeaderView::section {
    background-color: #dce0e8;
    color: #008e7f;
    padding: 6px;
    border: none;
    font-weight: bold;
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
# ÖZEL TOGGLE SWITCH BİLEŞENİ
# ==============================================================================

class ToggleSwitch(QAbstractButton):
    """Modern görünümlü, resim gerektirmeyen özel toggle switch."""
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setCheckable(True)
        self.setFixedSize(48, 24)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        is_dark = True
        if self.main_window and hasattr(self.main_window, 'current_theme'):
            is_dark = (self.main_window.current_theme == "dark")
            
        bg_color = QColor("#00f5d4") if self.isChecked() else (QColor("#2d3149") if is_dark else QColor("#bcc0cc"))
        handle_color = QColor("#0f111a") if self.isChecked() else (QColor("#a9b1d6") if is_dark else QColor("#eff1f5"))
        
        # Arka plan rayı
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() / 2, self.height() / 2)
        
        # Yuvarlak kaydırıcı düğme
        radius = self.height() - 6
        x_pos = (self.width() - radius - 3) if self.isChecked() else 3
        painter.setBrush(QBrush(handle_color))
        painter.drawEllipse(x_pos, 3, radius, radius)


# ==============================================================================
# ÖZEL BAŞLIK ÇUBUĞU (Custom Title Bar)
# ==============================================================================

class CustomTitleBar(QWidget):
    """Pencere çerçevesi yerine geçen, sürükleme ve pencere butonları barındıran başlık çubuğu."""
    def __init__(self, parent=None, title="Pardus Hello", subtitle="Pardus yirmibir"):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(50)
        self.drag_position = None
        self.init_ui(title, subtitle)

    def init_ui(self, title, subtitle):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)

        # Logo/İkon
        logo = QLabel()
        logo_pixmap = QIcon.fromTheme("pardus", QIcon.fromTheme("start-here")).pixmap(22, 22)
        if logo_pixmap.isNull():
            logo.setText("🐾")
            logo.setStyleSheet("font-size: 18px; color: #00f5d4;")
        else:
            logo.setPixmap(logo_pixmap)
        layout.addWidget(logo)

        # Başlık Grubu (Ortalanmış)
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 5, 0, 5)
        title_layout.setSpacing(1)
        title_layout.setAlignment(Qt.AlignCenter)

        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("titleBarTitle")
        self.title_lbl.setFont(QFont("Inter", 11, QFont.Bold))

        self.subtitle_lbl = QLabel(subtitle)
        self.subtitle_lbl.setObjectName("titleBarSubtitle")
        self.subtitle_lbl.setFont(QFont("Inter", 8))

        title_layout.addWidget(self.title_lbl)
        title_layout.addWidget(self.subtitle_lbl)
        layout.addWidget(title_container, stretch=1)

        # Bilgi Butonu
        self.info_btn = QPushButton("ⓘ")
        self.info_btn.setObjectName("titleBarInfoBtn")
        self.info_btn.setFixedSize(26, 26)
        self.info_btn.setCursor(Qt.PointingHandCursor)
        self.info_btn.clicked.connect(self.show_info)
        layout.addWidget(self.info_btn)

        # Simge Durumu Butonu
        self.min_btn = QPushButton("—")
        self.min_btn.setObjectName("titleBarMinBtn")
        self.min_btn.setFixedSize(26, 26)
        self.min_btn.setCursor(Qt.PointingHandCursor)
        self.min_btn.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.min_btn)

        # Ekranı Kapla Butonu
        self.max_btn = QPushButton("▢")
        self.max_btn.setObjectName("titleBarMaxBtn")
        self.max_btn.setFixedSize(26, 26)
        self.max_btn.setCursor(Qt.PointingHandCursor)
        self.max_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.max_btn)

        # Kapatma Butonu
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("titleBarCloseBtn")
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.parent.close)
        layout.addWidget(self.close_btn)

    def show_info(self):
        QMessageBox.information(
            self.parent,
            "Pardus Hello",
            "Pardus Hello — Karşılama ve Hızlı Ayar Portalı\nSürüm: v2026.1 (PoC)\n\nCachyOS Hello tasarımı esas alınarak kodlanmıştır.",
            QMessageBox.Ok
        )

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.max_btn.setText("▢")
        else:
            self.parent.showMaximized()
            self.max_btn.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()


# ==============================================================================
# SİMÜLASYON DİYALOGLARI (Polkit Yetki ve İlerleme Pencereleri)
# ==============================================================================

class AuthDialog(QDialog):
    def __init__(self, parent=None, action_text="", command_text="", package_name=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(420, 230)
        self.setWindowTitle("Kimlik Doğrulama Gerekli")
        
        if not command_text:
            if package_name:
                command_text = f"sudo apt install {package_name}"
            else:
                command_text = "sudo command"
                
        self.init_ui(action_text, command_text)

    def init_ui(self, action_text, command_text):
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

        desc_text = f"Sistem güvenliği için <b>{action_text}</b> işlemi yönetici hakları gerektiriyor.<br>Komut: <i>{command_text}</i>"
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
# MODERN POPÜLER YAZILIM KURUCU (Package Installer Window)
# ==============================================================================

class PackageInstallerWindow(QDialog):
    """CachyOS Package Installer arayüzünü birebir simüle eden popüler paket yükleyici."""
    def __init__(self, parent=None, is_dark_mode=True, lang_idx=0):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setMinimumSize(850, 580)
        self.is_dark_mode = is_dark_mode
        self.lang_idx = lang_idx
        self.parent_window = parent

        # Yüklü uygulamaları simüle etmek için veri yapısı
        self.installed_packages = {"firefox": True, "libreoffice": True}
        self.selected_app = None

        self.init_ui()

    def init_ui(self):
        is_tr = (self.lang_idx == 0)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Başlık Çubuğu
        title_text = "Pardus Paket Kurucu" if is_tr else "Pardus Package Installer"
        self.title_bar = CustomTitleBar(self, title=title_text, subtitle=title_text)
        main_layout.addWidget(self.title_bar)

        # Ana İçerik Alanı
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 15)
        content_layout.setSpacing(15)

        # Tab Widget
        self.tab_widget = QTabWidget()
        
        # POPULAR APPLICATIONS TAB
        pop_tab = QWidget()
        pop_layout = QVBoxLayout(pop_tab)
        pop_layout.setContentsMargins(15, 15, 15, 15)
        pop_layout.setSpacing(10)

        # Arama ve Üst Başlık Grubu
        top_bar_layout = QHBoxLayout()
        
        title_lbl_widget = QWidget()
        title_lbl_layout = QVBoxLayout(title_lbl_widget)
        title_lbl_layout.setContentsMargins(0, 0, 0, 0)
        title_lbl_layout.setSpacing(2)
        
        main_lbl_text = "Popüler Paketleri Yönetin" if is_tr else "Manage Popular Packages"
        sub_lbl_text = "Devre dışı bırakılan öğeler sisteminizde zaten yüklüdür." if is_tr else "Disabled items are already installed on your system."
        
        main_lbl = QLabel(main_lbl_text)
        main_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;" if self.is_dark_mode else "font-size: 16px; font-weight: bold; color: #1e1f29;")
        sub_lbl = QLabel(sub_lbl_text)
        sub_lbl.setStyleSheet("font-size: 11px; color: #a9b1d6;" if self.is_dark_mode else "font-size: 11px; color: #5c5f77;")
        
        title_lbl_layout.addWidget(main_lbl)
        title_lbl_layout.addWidget(sub_lbl)
        top_bar_layout.addWidget(title_lbl_widget)
        top_bar_layout.addStretch()

        # Arama kutusu
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Arama..." if is_tr else "Search...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_packages)
        top_bar_layout.addWidget(self.search_input)
        pop_layout.addLayout(top_bar_layout)

        # Paket Ağacı (Tree Widget)
        self.tree_widget = QTreeWidget()
        headers = ["Paket Adı", "Bilgi / Paket", "Açıklama"] if is_tr else ["Package Name", "Info / Package", "Description"]
        self.tree_widget.setHeaderLabels(headers)
        self.tree_widget.setColumnWidth(0, 220)
        self.tree_widget.setColumnWidth(1, 180)
        self.tree_widget.itemSelectionChanged.connect(self.on_item_selected)
        pop_layout.addWidget(self.tree_widget)

        self.tab_widget.addTab(pop_tab, "Popüler Uygulamalar" if is_tr else "Popular Applications")

        # REPO TAB (SIMULATED)
        repo_tab = QWidget()
        repo_layout = QVBoxLayout(repo_tab)
        repo_layout.setContentsMargins(30, 30, 30, 30)
        
        repo_desc_text = (
            "<b>Pardus Depo Yöneticisi</b><br><br>Bu sekmeden resmi Pardus ana depolarını kontrol edebilir ve katkıda bulunulan 'contrib' veya 'non-free' depolarını açıp kapatabilirsiniz."
            if is_tr else
            "<b>Pardus Repository Manager</b><br><br>From this tab, you can manage official Pardus repositories and enable/disable 'contrib' or 'non-free' software sources."
        )
        repo_desc = QLabel(repo_desc_text)
        repo_desc.setFont(QFont("Inter", 11))
        repo_desc.setWordWrap(True)
        repo_layout.addWidget(repo_desc)
        repo_layout.addStretch()
        self.tab_widget.addTab(repo_tab, "Depo" if is_tr else "Repo")

        # CONSOLE OUTPUT TAB (SIMULATED)
        console_tab = QWidget()
        console_layout = QVBoxLayout(console_tab)
        console_layout.setContentsMargins(15, 15, 15, 15)
        self.console_view = QLineEdit()
        self.console_view.setReadOnly(True)
        
        console_init_text = (
            "Pardus Paket Kurucu PoC Başlatıldı.\nPaket depoları yükleniyor...\nHazır."
            if is_tr else
            "Pardus Package Installer PoC Started.\nLoading package repositories...\nReady."
        )
        self.console_view.setText(console_init_text)
        console_layout.addWidget(self.console_view)
        self.tab_widget.addTab(console_tab, "Konsol Çıktısı" if is_tr else "Console Output")

        content_layout.addWidget(self.tab_widget)

        # Alt Eylem Düğmeleri
        btn_layout = QHBoxLayout()
        
        self.about_btn = QPushButton("Hakkında..." if is_tr else "About...")
        self.about_btn.clicked.connect(self.show_about)
        
        self.help_btn = QPushButton("Yardım" if is_tr else "Help")
        self.help_btn.clicked.connect(self.show_help)

        btn_layout.addWidget(self.about_btn)
        btn_layout.addWidget(self.help_btn)
        btn_layout.addStretch()

        self.uninstall_btn = QPushButton("Kaldır" if is_tr else "Uninstall")
        self.uninstall_btn.setObjectName("dangerActionBtn")
        self.uninstall_btn.setEnabled(False)
        self.uninstall_btn.clicked.connect(self.simulate_uninstall)

        self.install_btn = QPushButton("Kur" if is_tr else "Install")
        self.install_btn.setObjectName("primaryActionBtn")
        self.install_btn.setEnabled(False)
        self.install_btn.clicked.connect(self.simulate_install)

        self.close_btn = QPushButton("Kapat" if is_tr else "Close")
        self.close_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.uninstall_btn)
        btn_layout.addWidget(self.install_btn)
        btn_layout.addWidget(self.close_btn)

        content_layout.addLayout(btn_layout)
        main_layout.addWidget(content_widget)

        # Yükleme listesini oluştur
        self.load_packages()

    def load_packages(self):
        is_tr = (self.lang_idx == 0)
        # Kategori Paket Verileri
        if is_tr:
            self.package_data = {
                "Ses & Müzik (Audio)": [
                    {"name": "Audacity", "pkg": "audacity", "desc": "Açık kaynaklı ses düzenleme programı."},
                    {"name": "PulseEffects", "pkg": "pulseeffects", "desc": "Gelişmiş ses dengeleme ve efekt aracı."}
                ],
                "Tarayıcılar (Browsers)": [
                    {"name": "Google Chrome", "pkg": "google-chrome-stable", "desc": "Hızlı, güvenli ve en popüler ağ tarayıcısı."},
                    {"name": "Mozilla Firefox", "pkg": "firefox-esr", "desc": "Gizlilik odaklı, kararlı ve açık kaynaklı web tarayıcı."},
                    {"name": "Brave Browser", "pkg": "brave-browser", "desc": "Reklamları engelleyen, hızlı ve gizlilik merkezli tarayıcı."},
                    {"name": "Vivaldi", "pkg": "vivaldi-stable", "desc": "Kişiselleştirilebilir ve gelişmiş sekme özellikli tarayıcı."}
                ],
                "İletişim (Communication)": [
                    {"name": "Discord", "pkg": "discord", "desc": "Sesli, yazılı ve görüntülü popüler sohbet platformu."},
                    {"name": "Telegram Desktop", "pkg": "telegram-desktop", "desc": "Güvenli ve hızlı mesajlaşma istemcisi."}
                ],
                "Geliştirici Araçları (Development)": [
                    {"name": "Visual Studio Code", "pkg": "code", "desc": "Modern diller için en yaygın kod düzenleme platformu."},
                    {"name": "PyCharm Community", "pkg": "pycharm-community", "desc": "Python geliştiricileri için akıllı IDE aracı."},
                    {"name": "GitKraken", "pkg": "gitkraken", "desc": "Git yönetimini kolaylaştıran şık ve görsel arayüz."},
                    {"name": "Docker Engine", "pkg": "docker-ce", "desc": "Konteyner tabanlı sanallaştırma teknolojisi."}
                ],
                "Oyunlar (Games)": [
                    {"name": "Steam Client", "pkg": "steam", "desc": "En geniş dijital oyun mağazası ve çalıştırma platformu."},
                    {"name": "Lutris", "pkg": "lutris", "desc": "Tüm oyun kütüphanelerinizi birleştiren başlatıcı."}
                ],
                "Grafik Tasarım (Graphics)": [
                    {"name": "GIMP", "pkg": "gimp", "desc": "Photoshop alternatifi güçlü açık kaynaklı resim düzenleyici."},
                    {"name": "Inkscape", "pkg": "inkscape", "desc": "Vektörel grafik ve çizim tasarım aracı."},
                    {"name": "Blender", "pkg": "blender", "desc": "Profesyonel 3 boyutlu modelleme ve animasyon programı."}
                ],
                "Ofis Paketleri (Office)": [
                    {"name": "LibreOffice", "pkg": "libreoffice", "desc": "Tam donanımlı, popüler açık kaynaklı ofis paketi."},
                    {"name": "OnlyOffice Editors", "pkg": "onlyoffice-desktopeditors", "desc": "MS Office formatları ile yüksek uyumluluğa sahip ofis düzenleyici."}
                ],
                "Multimedya (Multimedia)": [
                    {"name": "VLC Media Player", "pkg": "vlc", "desc": "Neredeyse tüm formatları oynatan açık kaynaklı medya oynatıcı."},
                    {"name": "Spotify Client", "pkg": "spotify-client", "desc": "Müzik, podcast ve çalma listesi akış servisi."},
                    {"name": "OBS Studio", "pkg": "obs-studio", "desc": "Profesyonel ekran videosu kaydetme ve yayınlama yazılımı."}
                ]
            }
        else:
            self.package_data = {
                "Audio (Ses & Müzik)": [
                    {"name": "Audacity", "pkg": "audacity", "desc": "Open-source audio editing software."},
                    {"name": "PulseEffects", "pkg": "pulseeffects", "desc": "Advanced audio equalizer and effects tool."}
                ],
                "Browsers (Tarayıcılar)": [
                    {"name": "Google Chrome", "pkg": "google-chrome-stable", "desc": "Fast, secure, and the most popular web browser."},
                    {"name": "Mozilla Firefox", "pkg": "firefox-esr", "desc": "Privacy-focused, stable, and open-source web browser."},
                    {"name": "Brave Browser", "pkg": "brave-browser", "desc": "Ad-blocking, fast, and privacy-oriented browser."},
                    {"name": "Vivaldi", "pkg": "vivaldi-stable", "desc": "Customizable browser with advanced tab features."}
                ],
                "Communication (İletişim)": [
                    {"name": "Discord", "pkg": "discord", "desc": "Popular voice, video, and text chat platform."},
                    {"name": "Telegram Desktop", "pkg": "telegram-desktop", "desc": "Secure and fast messaging client."}
                ],
                "Development Tools (Geliştirici)": [
                    {"name": "Visual Studio Code", "pkg": "code", "desc": "The most widely used code editing platform for modern languages."},
                    {"name": "PyCharm Community", "pkg": "pycharm-community", "desc": "Smart IDE tool for Python developers."},
                    {"name": "GitKraken", "pkg": "gitkraken", "desc": "Sleek and visual interface for easy Git management."},
                    {"name": "Docker Engine", "pkg": "docker-ce", "desc": "Container-based virtualization technology."}
                ],
                "Games (Oyunlar)": [
                    {"name": "Steam Client", "pkg": "steam", "desc": "The largest digital game store and client."},
                    {"name": "Lutris", "pkg": "lutris", "desc": "Open source gaming platform that unifies all your game libraries."}
                ],
                "Graphics (Grafik Tasarım)": [
                    {"name": "GIMP", "pkg": "gimp", "desc": "Powerful open-source image editor alternative to Photoshop."},
                    {"name": "Inkscape", "pkg": "inkscape", "desc": "Vector graphics and illustration design tool."},
                    {"name": "Blender", "pkg": "blender", "desc": "Professional 3D modeling and animation suite."}
                ],
                "Office (Ofis Paketleri)": [
                    {"name": "LibreOffice", "pkg": "libreoffice", "desc": "Fully featured, popular open-source office suite."},
                    {"name": "OnlyOffice Editors", "pkg": "onlyoffice-desktopeditors", "desc": "Office editor with high compatibility for MS Office formats."}
                ],
                "Multimedia (Çoklu Ortam)": [
                    {"name": "VLC Media Player", "pkg": "vlc", "desc": "Open-source media player that plays almost all formats."},
                    {"name": "Spotify Client", "pkg": "spotify-client", "desc": "Music, podcast, and playlist streaming service."},
                    {"name": "OBS Studio", "pkg": "obs-studio", "desc": "Professional screen recorder and live streaming software."}
                ]
            }

        self.tree_widget.clear()
        for cat_name, apps in self.package_data.items():
            cat_item = QTreeWidgetItem(self.tree_widget)
            cat_item.setText(0, cat_name)
            cat_item.setFont(0, QFont("Inter", 10, QFont.Bold))
            cat_item.setIcon(0, QIcon.fromTheme("folder"))

            for app in apps:
                app_item = QTreeWidgetItem(cat_item)
                app_item.setText(0, app["name"])
                app_item.setText(1, app["pkg"])
                app_item.setText(2, app["desc"])
                app_item.setIcon(0, QIcon.fromTheme("application-x-executable"))

                is_installed = self.installed_packages.get(app["pkg"], False)
                if is_installed:
                    app_item.setText(0, app["name"] + " (Yüklü)")
                    for col in range(3):
                        app_item.setForeground(col, QColor("#565f89") if self.is_dark_mode else QColor("#9ca0b0"))

    def filter_packages(self, text):
        for i in range(self.tree_widget.topLevelItemCount()):
            cat_item = self.tree_widget.topLevelItem(i)
            cat_visible = False
            for j in range(cat_item.childCount()):
                child_item = cat_item.child(j)
                name_match = text.lower() in child_item.text(0).lower()
                pkg_match = text.lower() in child_item.text(1).lower()
                desc_match = text.lower() in child_item.text(2).lower()
                
                if name_match or pkg_match or desc_match:
                    child_item.setHidden(False)
                    cat_visible = True
                else:
                    child_item.setHidden(True)
            
            cat_item.setHidden(not cat_visible and text != "")
            if text != "":
                cat_item.setExpanded(cat_visible)
            else:
                cat_item.setExpanded(False)

    def on_item_selected(self):
        selected_items = self.tree_widget.selectedItems()
        if not selected_items or selected_items[0].parent() is None:
            self.install_btn.setEnabled(False)
            self.uninstall_btn.setEnabled(False)
            self.selected_app = None
            return

        item = selected_items[0]
        pkg_name = item.text(1)
        self.selected_app = {"name": item.text(0).replace(" (Yüklü)", ""), "pkg": pkg_name, "item": item}

        is_installed = self.installed_packages.get(pkg_name, False)
        if is_installed:
            self.install_btn.setEnabled(False)
            self.uninstall_btn.setEnabled(True)
        else:
            self.install_btn.setEnabled(True)
            self.uninstall_btn.setEnabled(False)

    def simulate_install(self):
        if not self.selected_app:
            return
        auth = AuthDialog(self, action_text=f"{self.selected_app['name']} Kurulumu", command_text=f"sudo apt install {self.selected_app['pkg']}")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text=f"{self.selected_app['name']} Kuruluyor", package_name=self.selected_app["pkg"])
            if progress.exec_() == QDialog.Accepted:
                pkg = self.selected_app["pkg"]
                self.installed_packages[pkg] = True
                
                # Parent diagnostic log kaydı
                if self.parent_window and hasattr(self.parent_window, 'diagnostic_logs'):
                    self.parent_window.diagnostic_logs.append(f"[INFO] Uygulama kuruldu: {self.selected_app['name']} (Komut: sudo apt install {pkg})")
                
                item = self.selected_app["item"]
                item.setText(0, self.selected_app["name"] + " (Yüklü)")
                for col in range(3):
                    item.setForeground(col, QColor("#565f89") if self.is_dark_mode else QColor("#9ca0b0"))
                
                self.on_item_selected()
                QMessageBox.information(self, "Kuruldu", f"{self.selected_app['name']} sisteminize başarıyla kuruldu (Simüle).")

    def simulate_uninstall(self):
        if not self.selected_app:
            return
        auth = AuthDialog(self, action_text=f"{self.selected_app['name']} Sistemden Kaldırılması", command_text=f"sudo apt purge {self.selected_app['pkg']}")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text=f"{self.selected_app['name']} Kaldırılıyor", package_name=self.selected_app["pkg"])
            if progress.exec_() == QDialog.Accepted:
                pkg = self.selected_app["pkg"]
                if pkg in self.installed_packages:
                    del self.installed_packages[pkg]
                
                # Parent diagnostic log kaydı
                if self.parent_window and hasattr(self.parent_window, 'diagnostic_logs'):
                    self.parent_window.diagnostic_logs.append(f"[INFO] Uygulama kaldırıldı: {self.selected_app['name']} (Komut: sudo apt purge {pkg})")
                
                item = self.selected_app["item"]
                item.setText(0, self.selected_app["name"])
                for col in range(3):
                    item.setForeground(col, QColor("#c8d3f5") if self.is_dark_mode else QColor("#4c4f69"))
                
                self.on_item_selected()
                QMessageBox.information(self, "Kaldırıldı", f"{self.selected_app['name']} sisteminizden başarıyla kaldırıldı (Simüle).")

    def show_about(self):
        QMessageBox.information(self, "Hakkında", "Pardus Paket Kurucu v2026.1\n\nBu program, en popüler ve sık kullanılan uygulamaları kolayca kurmanızı sağlayan hızlı bir yönetim aracıdır.")

    def show_help(self):
        QMessageBox.information(self, "Yardım", "Listeden kurmak veya kaldırmak istediğiniz programı seçin, ardından alt taraftaki Kur/Kaldır butonlarını kullanın.")


TRANSLATIONS = {
    "tr": {
        "title_bar_title": "Pardus Hello",
        "title_bar_subtitle": "Pardus 23.0 - Karşılama Ekranı",
        "welcome_title": "Pardus'a Hoş Geldiniz!",
        "welcome_subtitle": "Aramıza katıldığınız için size çok teşekkür ederiz!",
        "intro_text": "Pardus Geliştirici Ekibi olarak, bizler yapımında ne kadar zevk aldıysak, sizlerin de Pardus'u kullanırken o kadar memnun kalacağınızı umut ediyoruz. Aşağıdaki bağlantılar, yeni işletim sisteminizi kullanma konusunda sizlere yardımcı olacaktır. Bu vesileyle tecrübenizin tadını çıkarın, fikir ve düşüncelerinizi bizlerle paylaşmaktan çekinmeyin.",
        "col_doc": "DÖKÜMANTASYON",
        "col_sup": "DESTEK",
        "col_prj": "PROJE",
        "link_readme": "Beni oku",
        "link_release": "Sürüm bilgisi",
        "link_wiki": "Viki ↗",
        "link_forum": "Forum ↗",
        "link_software": "Yazılım ↗",
        "link_join": "Projeye katıl",
        "link_dev": "Geliştirme ↗",
        "link_donate": "Pardus Hakkında ↗",
        "btn_tweaks": "Uygulamalar/İyileştirmeler",
        "btn_installer": "Uygulama kur",
        "btn_trouble": "Troubleshooting",
        "tweaks_back_btn": "❮ Geri",
        "tweaks_page_title": "İnce Ayarlar ve Araçlar",
        "tweaks_section1": "İnce Ayarlar",
        "tweaks_section2": "Araçlar",
        "tweaks_section3": "Uygulamalar",
        "chk_psd": "Profile-sync-daemon etkinleştirildi.",
        "chk_ananicy": "Ananicy Cpp etkinleştirildi.",
        "chk_updater": "Pardus Güncelleyici etkinleştirildi.",
        "chk_oomd": "Systemd-oomd etkinleştirildi.",
        "chk_bpftune": "Bpftune etkinleştirildi.",
        "chk_bluetooth": "Bluetooth etkinleştirildi.",
        "btn_sys_update": "Sistem güncellemesi",
        "btn_mirrors": "Yansıları hıza göre sırala",
        "btn_orphans": "Artık (orphan) paketleri kaldır",
        "btn_vram": "VRAM yönetimini kur",
        "btn_winboat": "Winboat kur",
        "btn_games": "Oyun paketlerini kur",
        "btn_dns": "DNS sunucusunu değiştir",
        "btn_open_installer": "Pardus Paket Yükleyici",
        "btn_open_kernel": "Pardus Çekirdek Yöneticisi",
        "kernel_back_btn": "❮ Geri",
        "kernel_page_title": "Çekirdek Yöneticisi (Kernel Manager)",
        "kernel_desc": "Debian/Pardus için optimize edilmiş çekirdek paketlerini kurabilir ve geçiş yapabilirsiniz.\nMevcut sisteminizde çalışan sürüm: <b>{kernel}</b>",
        "desc_default": "Pardus Standart Kararlı Çekirdek (Önerilen)",
        "desc_rt": "Düşük Gecikmeli Gerçek Zamanlı Çekirdek (Realtime)",
        "desc_lts": "Uzun Süreli Desteklenen Çekirdek (Debian Stable)",
        "desc_liquorix": "Liquorix Yüksek Performanslı Oyun ve Masaüstü Çekirdeği",
        "running_lbl": "Çalışıyor",
        "install_lbl": "Kur",
        "remove_lbl": "Kaldır",
        "trouble_back_btn": "❮ Geri",
        "trouble_page_title": "Sorun Giderme (Troubleshooting)",
        "btn_clear_cache": "Önbellekteki paketleri temizle",
        "btn_db_lock": "Apt/dpkg veritabanı kilidini kaldır",
        "btn_keyring": "Anahtar halkalarını sıfırla",
        "btn_reinstall_all": "Tüm paketleri yeniden kur",
        "btn_kwin_debug": "Pardus Sistem ve Hata Günlüklerini Göster",
        "startup_lbl": "Başlangıçta aç:",
        "tooltip_theme": "Temayı Değiştir"
    },
    "en": {
        "title_bar_title": "Pardus Hello",
        "title_bar_subtitle": "Pardus 23.0 - Welcome Screen",
        "welcome_title": "Welcome to Pardus!",
        "welcome_subtitle": "Thank you very much for joining us!",
        "intro_text": "As the Pardus Developer Team, we hope you will enjoy using Pardus as much as we enjoyed building it. The links below will help you get started with your new operating system. Enjoy the experience, and please feel free to share your thoughts and ideas with us.",
        "col_doc": "DOCUMENTATION",
        "col_sup": "SUPPORT",
        "col_prj": "PROJECT",
        "link_readme": "Read me",
        "link_release": "Release notes",
        "link_wiki": "Wiki ↗",
        "link_forum": "Forum ↗",
        "link_software": "Software ↗",
        "link_join": "Join project",
        "link_dev": "Development ↗",
        "link_donate": "About Pardus ↗",
        "btn_tweaks": "Apps & Tweaks",
        "btn_installer": "Install Apps",
        "btn_trouble": "Troubleshooting",
        "tweaks_back_btn": "❮ Back",
        "tweaks_page_title": "Tweaks and Tools",
        "tweaks_section1": "Tweaks",
        "tweaks_section2": "Tools",
        "tweaks_section3": "Applications",
        "chk_psd": "Profile-sync-daemon enabled.",
        "chk_ananicy": "Ananicy Cpp enabled.",
        "chk_updater": "Pardus Updater enabled.",
        "chk_oomd": "Systemd-oomd enabled.",
        "chk_bpftune": "Bpftune enabled.",
        "chk_bluetooth": "Bluetooth enabled.",
        "btn_sys_update": "System update",
        "btn_mirrors": "Rank mirrors by speed",
        "btn_orphans": "Remove orphan packages",
        "btn_vram": "Setup VRAM management",
        "btn_winboat": "Install Winboat",
        "btn_games": "Install gaming packages",
        "btn_dns": "Change DNS server",
        "btn_open_installer": "Pardus Package Installer",
        "btn_open_kernel": "Pardus Kernel Manager",
        "kernel_back_btn": "❮ Back",
        "kernel_page_title": "Kernel Manager",
        "kernel_desc": "You can install and switch to optimized kernel packages for Debian/Pardus.\nCurrently running version on your system: <b>{kernel}</b>",
        "desc_default": "Pardus Standard Stable Kernel (Recommended)",
        "desc_rt": "Low Latency Realtime Kernel (Realtime)",
        "desc_lts": "Long Term Supported Kernel (Debian Stable)",
        "desc_liquorix": "Liquorix High Performance Gaming and Desktop Kernel",
        "running_lbl": "Running",
        "install_lbl": "Install",
        "remove_lbl": "Remove",
        "trouble_back_btn": "❮ Back",
        "trouble_page_title": "Troubleshooting",
        "btn_clear_cache": "Clear cached packages",
        "btn_db_lock": "Remove Apt/dpkg database lock",
        "btn_keyring": "Reset keyring keys",
        "btn_reinstall_all": "Reinstall all packages",
        "btn_kwin_debug": "Show Pardus System and Error Logs",
        "startup_lbl": "Open at startup:",
        "tooltip_theme": "Change Theme"
    }
}


# ==============================================================================
# ANA UYGULAMA PENCERESİ (MainWindow)
# ==============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Pardus Hello — Karşılama Ekranı")
        self.setMinimumSize(960, 640)
        self.resize(1000, 680)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        self.setWindowIcon(QIcon.fromTheme("pardus", QIcon.fromTheme("start-here", QIcon.fromTheme("computer"))))
        
        self.cpu_info = self.get_cpu_info()
        self.ram_info = self.get_ram_info()
        self.os_info = self.get_os_info()
        self.kernel_info = platform.release()

        # Tanılama Günlükleri listesi (Log Viewer için)
        self.diagnostic_logs = [
            "[INFO] Pardus Hello Başlatıldı.",
            f"[INFO] İşletim Sistemi: {self.os_info}",
            f"[INFO] Çekirdek Sürümü: {self.kernel_info}",
            f"[INFO] İşlemci (CPU): {self.cpu_info}",
            f"[INFO] Toplam RAM: {self.ram_info}"
        ]

        self.current_theme = "dark" if detect_system_dark_mode() else "light"
        self.apply_theme()
        self.init_ui()
        
        # Dil değiştiğinde arayüzü güncelle
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        self.retranslate_ui()

    def change_language(self, index):
        self.retranslate_ui()
        self.diagnostic_logs.append(f"[INFO] Dil değiştirildi: {'English' if index == 1 else 'Türkçe'}")

    def retranslate_ui(self):
        lang_idx = self.lang_combo.currentIndex()
        lang = "tr" if lang_idx == 0 else "en"
        t = TRANSLATIONS[lang]

        # Başlık Çubuğu
        self.title_bar.title_lbl.setText(t["title_bar_title"])
        self.title_bar.subtitle_lbl.setText(t["title_bar_subtitle"])

        # Karşılama Sayfası
        self.welcome_title.setText(t["welcome_title"])
        self.welcome_subtitle.setText(t["welcome_subtitle"])
        self.intro_text.setText(t["intro_text"])

        # Karşılama Kolon Kartları Başlıkları ve Linkler
        for label, col_key in self.col_title_labels:
            label.setText(t[col_key])
        for btn, link_key in self.link_buttons:
            btn.setText(t[link_key])

        self.btn_tweaks.setText(t["btn_tweaks"])
        self.btn_installer.setText(t["btn_installer"])
        self.btn_trouble.setText(t["btn_trouble"])

        # İnce Ayarlar Sayfası
        self.tweaks_back_btn.setText(t["tweaks_back_btn"])
        self.tweaks_page_title.setText(t["tweaks_page_title"])
        self.tweaks_section_title1.setText(t["tweaks_section1"])
        self.tweaks_section_title2.setText(t["tweaks_section2"])
        self.tweaks_section_title3.setText(t["tweaks_section3"])

        self.chk1.setText(t["chk_psd"])
        self.chk2.setText(t["chk_ananicy"])
        self.chk3.setText(t["chk_updater"])
        self.chk4.setText(t["chk_oomd"])
        self.chk5.setText(t["chk_bpftune"])
        self.chk6.setText(t["chk_bluetooth"])

        self.btn_sys_update.setText(t["btn_sys_update"])
        self.btn_mirrors.setText(t["btn_mirrors"])
        self.btn_orphans.setText(t["btn_orphans"])
        self.btn_vram.setText(t["btn_vram"])
        self.btn_winboat.setText(t["btn_winboat"])
        self.btn_games.setText(t["btn_games"])
        self.btn_dns.setText(t["btn_dns"])

        self.btn_open_installer.setText(t["btn_open_installer"])
        self.btn_open_kernel.setText(t["btn_open_kernel"])

        # Çekirdek Sayfası
        self.kernel_back_btn.setText(t["kernel_back_btn"])
        self.kernel_page_title.setText(t["kernel_page_title"])
        self.kernel_desc_label.setText(t["kernel_desc"].format(kernel=self.kernel_info))

        for item in self.kernel_widgets:
            is_currently_running = (item["id"] == "default")
            active_indicator = " [ AKTİF ]" if lang == "tr" else " [ ACTIVE ]"
            color_theme = '#00f5d4' if self.current_theme == 'dark' else '#00a896'
            if is_currently_running:
                item["k_title"].setText(item["name"] + f" <span style='color: {color_theme}; font-size: 10px; font-weight: bold;'>{active_indicator}</span>")
            else:
                item["k_title"].setText(item["name"])

            # Çekirdek açıklaması çevirisi
            desc_key = "desc_" + item["id"]
            item["k_desc"].setText(t[desc_key])

            if item["status_lbl"]:
                item["status_lbl"].setText(t["running_lbl"])
            if item["install_btn"]:
                item["install_btn"].setText(t["install_lbl"])
            if item["remove_btn"]:
                item["remove_btn"].setText(t["remove_lbl"])

        # Sorun Giderme Sayfası
        self.trouble_back_btn.setText(t["trouble_back_btn"])
        self.trouble_page_title.setText(t["trouble_page_title"])

        self.btn_clear_cache.setText(t["btn_clear_cache"])
        self.btn_db_lock.setText(t["btn_db_lock"])
        self.btn_keyring.setText(t["btn_keyring"])
        self.btn_reinstall_all.setText(t["btn_reinstall_all"])
        self.btn_kwin_debug.setText(t["btn_kwin_debug"])

        # Footer
        self.startup_lbl.setText(t["startup_lbl"])
        self.theme_toggle_btn.setToolTip(t["tooltip_theme"])

    def apply_theme(self):
        if self.current_theme == "dark":
            self.setStyleSheet(DARK_QSS)
        else:
            self.setStyleSheet(LIGHT_QSS)

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title="Pardus Hello", subtitle="Pardus 23.0 - Karşılama Ekranı")
        main_layout.addWidget(self.title_bar)

        self.stacked_widget = QStackedWidget()
        self.create_welcome_page()
        self.create_apps_tweaks_page()
        self.create_kernel_manager_page()
        self.create_troubleshooting_page()
        
        main_layout.addWidget(self.stacked_widget)
        self.create_footer(main_layout)

    def create_footer(self, parent_layout):
        footer_frame = QFrame()
        footer_frame.setFixedHeight(45)
        footer_frame.setObjectName("footerFrame")
        
        if self.current_theme == "dark":
            footer_frame.setStyleSheet("QFrame#footerFrame { background-color: #090b10; border-top: 1px solid #1f2335; }")
        else:
            footer_frame.setStyleSheet("QFrame#footerFrame { background-color: #e6e9ef; border-top: 1px solid #ccd0da; }")

        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(15, 0, 15, 0)
        
        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("footerLangCombo")
        self.lang_combo.addItems(["Türkçe", "English"])
        self.lang_combo.setFixedSize(110, 26)
        footer_layout.addWidget(self.lang_combo)

        footer_layout.addStretch()

        self.theme_toggle_btn = QPushButton("☀️ / 🌙")
        self.theme_toggle_btn.setToolTip("Temayı Değiştir")
        self.theme_toggle_btn.setStyleSheet("font-size: 11px; padding: 4px 10px; font-weight: bold; border-radius: 13px;")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)

        footer_layout.addWidget(self.theme_toggle_btn)

        footer_layout.addStretch()

        self.startup_lbl = QLabel("Başlangıçta aç:")
        self.startup_lbl.setStyleSheet("font-size: 11px; font-weight: bold;" + ("color: #a9b1d6;" if self.current_theme == "dark" else "color: #5c5f77;"))
        self.startup_toggle = ToggleSwitch(main_window=self)
        self.startup_toggle.setChecked(True)
        
        footer_layout.addWidget(self.startup_lbl)
        footer_layout.addWidget(self.startup_toggle)
        
        size_grip = QSizeGrip(self)
        footer_layout.addWidget(size_grip)

        parent_layout.addWidget(footer_frame)

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"
        
        self.apply_theme()
        self.centralWidget().setStyleSheet(self.styleSheet())
        self.update()
        self.diagnostic_logs.append(f"[INFO] Tema değiştirildi: {self.current_theme}")

    def get_cpu_info(self):
        try:
            if platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
            return platform.processor() or "Intel Core i7 / AMD Ryzen 5"
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
            return "16.0 GB"
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

    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def create_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(15)

        self.welcome_title = QLabel()
        self.welcome_title.setObjectName("headerTitle")
        self.welcome_title.setAlignment(Qt.AlignCenter)
        
        self.welcome_subtitle = QLabel()
        self.welcome_subtitle.setObjectName("sectionTitle")
        self.welcome_subtitle.setAlignment(Qt.AlignCenter)
        
        self.intro_text = QLabel()
        self.intro_text.setWordWrap(True)
        self.intro_text.setAlignment(Qt.AlignCenter)
        self.intro_text.setFont(QFont("Inter", 10))
        self.intro_text.setStyleSheet("line-height: 1.5; color: #a9b1d6;" if self.current_theme == "dark" else "color: #5c5f77;")

        layout.addWidget(self.welcome_title)
        layout.addWidget(self.welcome_subtitle)
        layout.addWidget(self.intro_text)
        layout.addSpacing(10)

        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(20)

        columns_data = [
            {
                "title_key": "col_doc",
                "links": [
                    {"key": "link_readme", "url": "https://www.pardus.org.tr"},
                    {"key": "link_release", "url": "https://www.pardus.org.tr/surum-notlari/"},
                    {"key": "link_wiki", "url": "https://wiki.pardus.org.tr"}
                ]
            },
            {
                "title_key": "col_sup",
                "links": [
                    {"key": "link_forum", "url": "https://forum.pardus.org.tr"},
                    {"key": "link_software", "url": "https://talep.pardus.org.tr"},
                    {"key": "", "url": ""}
                ]
            },
            {
                "title_key": "col_prj",
                "links": [
                    {"key": "link_join", "url": "https://gonullu.pardus.org.tr"},
                    {"key": "link_dev", "url": "https://github.com/pardus"},
                    {"key": "link_donate", "url": "https://www.pardus.org.tr/hakkinda/"}
                ]
            }
        ]

        self.col_title_labels = []
        self.link_buttons = []

        for col in columns_data:
            col_box = QFrame()
            col_box.setObjectName("cardFrame")
            col_layout = QVBoxLayout(col_box)
            col_layout.setContentsMargins(15, 15, 15, 15)
            col_layout.setSpacing(10)

            col_title = QLabel()
            col_title.setFont(QFont("Inter", 11, QFont.Bold))
            col_title.setAlignment(Qt.AlignCenter)
            col_title.setStyleSheet("color: #00f5d4;" if self.current_theme == "dark" else "color: #008e7f;")
            col_layout.addWidget(col_title)
            self.col_title_labels.append((col_title, col["title_key"]))

            for link in col["links"]:
                if link["key"] == "":
                    dummy = QLabel()
                    dummy.setFixedHeight(38)
                    col_layout.addWidget(dummy)
                    continue

                btn = QPushButton()
                btn.setObjectName("linkGridBtn")
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda checked, url=link["url"]: webbrowser.open(url))
                col_layout.addWidget(btn)
                self.link_buttons.append((btn, link["key"]))

            col_layout.addStretch()
            grid_layout.addWidget(col_box)

        layout.addWidget(grid_widget)
        layout.addSpacing(10)

        bottom_actions_layout = QHBoxLayout()
        bottom_actions_layout.setSpacing(15)

        self.btn_tweaks = QPushButton()
        self.btn_tweaks.setFixedHeight(44)
        self.btn_tweaks.setFont(QFont("Inter", 10, QFont.Bold))
        self.btn_tweaks.setCursor(Qt.PointingHandCursor)
        self.btn_tweaks.clicked.connect(lambda: self.change_page(1))
        
        self.btn_installer = QPushButton()
        self.btn_installer.setFixedHeight(44)
        self.btn_installer.setFont(QFont("Inter", 10, QFont.Bold))
        self.btn_installer.setCursor(Qt.PointingHandCursor)
        self.btn_installer.clicked.connect(self.open_package_installer)

        self.btn_trouble = QPushButton()
        self.btn_trouble.setFixedHeight(44)
        self.btn_trouble.setFont(QFont("Inter", 10, QFont.Bold))
        self.btn_trouble.setCursor(Qt.PointingHandCursor)
        self.btn_trouble.clicked.connect(lambda: self.change_page(3))

        bottom_actions_layout.addWidget(self.btn_tweaks)
        bottom_actions_layout.addWidget(self.btn_installer)
        bottom_actions_layout.addWidget(self.btn_trouble)
        layout.addLayout(bottom_actions_layout)

        layout.addStretch()
        self.stacked_widget.addWidget(page)

    def create_apps_tweaks_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Üst Bar (Geri butonu ve başlık sabit kalacak)
        top_bar_widget = QWidget()
        top_bar = QHBoxLayout(top_bar_widget)
        top_bar.setContentsMargins(40, 20, 40, 10)
        
        self.tweaks_back_btn = QPushButton()
        self.tweaks_back_btn.setObjectName("backBtn")
        self.tweaks_back_btn.setFixedSize(80, 32)
        self.tweaks_back_btn.setCursor(Qt.PointingHandCursor)
        self.tweaks_back_btn.clicked.connect(lambda: self.change_page(0))
        
        self.tweaks_page_title = QLabel()
        self.tweaks_page_title.setObjectName("sectionTitle")
        self.tweaks_page_title.setFont(QFont("Inter", 14, QFont.Bold))
        
        top_bar.addWidget(self.tweaks_back_btn)
        top_bar.addWidget(self.tweaks_page_title)
        top_bar.addStretch()
        main_layout.addWidget(top_bar_widget)

        # Kaydırma Alanı (Scroll Area)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(40, 0, 40, 25)
        layout.setSpacing(15)

        # 1. BÖLÜM: İnce Ayarlar
        tweaks_box = QFrame()
        tweaks_box.setObjectName("cardFrame")
        tb_layout = QVBoxLayout(tweaks_box)
        tb_layout.setContentsMargins(20, 15, 20, 15)
        tb_layout.setSpacing(10)

        self.tweaks_section_title1 = QLabel()
        self.tweaks_section_title1.setObjectName("groupTitle")
        tb_layout.addWidget(self.tweaks_section_title1)

        checkbox_grid_widget = QWidget()
        checkbox_grid = QGridLayout(checkbox_grid_widget)
        checkbox_grid.setContentsMargins(0, 0, 0, 0)
        checkbox_grid.setSpacing(12)

        self.chk1 = QCheckBox()
        self.chk2 = QCheckBox()
        self.chk2.setChecked(True)
        self.chk3 = QCheckBox()
        self.chk3.setChecked(True)
        self.chk4 = QCheckBox()
        self.chk5 = QCheckBox()
        self.chk6 = QCheckBox()
        self.chk6.setChecked(True)

        checkbox_grid.addWidget(self.chk1, 0, 0)
        checkbox_grid.addWidget(self.chk2, 0, 1)
        checkbox_grid.addWidget(self.chk3, 0, 2)
        checkbox_grid.addWidget(self.chk4, 1, 0)
        checkbox_grid.addWidget(self.chk5, 1, 1)
        checkbox_grid.addWidget(self.chk6, 1, 2)
        
        self.chk6.stateChanged.connect(lambda state: self.simulate_service_toggle("Bluetooth", state, self.chk6))

        tb_layout.addWidget(checkbox_grid_widget)
        layout.addWidget(tweaks_box)

        # 2. BÖLÜM: Araçlar
        tools_box = QFrame()
        tools_box.setObjectName("cardFrame")
        t_layout = QVBoxLayout(tools_box)
        t_layout.setContentsMargins(20, 15, 20, 15)
        t_layout.setSpacing(10)

        self.tweaks_section_title2 = QLabel()
        self.tweaks_section_title2.setObjectName("groupTitle")
        t_layout.addWidget(self.tweaks_section_title2)

        tools_grid_widget = QWidget()
        tools_grid = QGridLayout(tools_grid_widget)
        tools_grid.setContentsMargins(0, 0, 0, 0)
        tools_grid.setSpacing(10)

        self.btn_sys_update = QPushButton()
        self.btn_sys_update.clicked.connect(self.simulate_update_packages)
        self.btn_sys_update.setCursor(Qt.PointingHandCursor)

        self.btn_mirrors = QPushButton()
        self.btn_mirrors.clicked.connect(self.simulate_mirrors)
        self.btn_mirrors.setCursor(Qt.PointingHandCursor)

        self.btn_orphans = QPushButton()
        self.btn_orphans.clicked.connect(self.simulate_remove_orphans)
        self.btn_orphans.setCursor(Qt.PointingHandCursor)

        self.btn_vram = QPushButton()
        self.btn_vram.clicked.connect(self.simulate_vram)
        self.btn_vram.setCursor(Qt.PointingHandCursor)

        self.btn_winboat = QPushButton()
        self.btn_winboat.clicked.connect(self.simulate_winboat)
        self.btn_winboat.setCursor(Qt.PointingHandCursor)

        self.btn_games = QPushButton()
        self.btn_games.clicked.connect(self.simulate_games)
        self.btn_games.setCursor(Qt.PointingHandCursor)

        self.btn_dns = QPushButton()
        self.btn_dns.clicked.connect(self.simulate_dns)
        self.btn_dns.setCursor(Qt.PointingHandCursor)

        tools_grid.addWidget(self.btn_sys_update, 0, 0)
        tools_grid.addWidget(self.btn_mirrors, 0, 1)
        tools_grid.addWidget(self.btn_orphans, 0, 2)
        tools_grid.addWidget(self.btn_vram, 1, 0)
        tools_grid.addWidget(self.btn_winboat, 1, 1)
        tools_grid.addWidget(self.btn_games, 1, 2)
        tools_grid.addWidget(self.btn_dns, 2, 0, 1, 3)

        t_layout.addWidget(tools_grid_widget)
        layout.addWidget(tools_box)

        # 3. BÖLÜM: Uygulamalar
        apps_box = QFrame()
        apps_box.setObjectName("cardFrame")
        a_layout = QVBoxLayout(apps_box)
        a_layout.setContentsMargins(20, 15, 20, 15)
        a_layout.setSpacing(10)

        self.tweaks_section_title3 = QLabel()
        self.tweaks_section_title3.setObjectName("groupTitle")
        a_layout.addWidget(self.tweaks_section_title3)

        apps_btn_layout = QHBoxLayout()
        apps_btn_layout.setSpacing(15)

        self.btn_open_installer = QPushButton()
        self.btn_open_installer.setFixedHeight(38)
        self.btn_open_installer.setCursor(Qt.PointingHandCursor)
        self.btn_open_installer.clicked.connect(self.open_package_installer)

        self.btn_open_kernel = QPushButton()
        self.btn_open_kernel.setFixedHeight(38)
        self.btn_open_kernel.setCursor(Qt.PointingHandCursor)
        self.btn_open_kernel.clicked.connect(lambda: self.change_page(2))

        apps_btn_layout.addWidget(self.btn_open_installer)
        apps_btn_layout.addWidget(self.btn_open_kernel)
        a_layout.addLayout(apps_btn_layout)

        layout.addWidget(apps_box)
        layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.stacked_widget.addWidget(page)

    def create_kernel_manager_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 20, 40, 25)
        layout.setSpacing(15)

        top_bar = QHBoxLayout()
        self.kernel_back_btn = QPushButton()
        self.kernel_back_btn.setObjectName("backBtn")
        self.kernel_back_btn.setFixedSize(80, 32)
        self.kernel_back_btn.setCursor(Qt.PointingHandCursor)
        self.kernel_back_btn.clicked.connect(lambda: self.change_page(1))
        
        self.kernel_page_title = QLabel()
        self.kernel_page_title.setObjectName("sectionTitle")
        
        top_bar.addWidget(self.kernel_back_btn)
        top_bar.addWidget(self.kernel_page_title)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.kernel_desc_label = QLabel()
        self.kernel_desc_label.setObjectName("sectionDesc")
        layout.addWidget(self.kernel_desc_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        scroll_layout.setSpacing(12)

        self.kernels = [
            {"id": "default", "name": "linux-image-amd64", "desc": "Pardus Standart Kararlı Çekirdek (Önerilen)"},
            {"id": "rt", "name": "linux-image-rt-amd64", "desc": "Düşük Gecikmeli Gerçek Zamanlı Çekirdek (Realtime)"},
            {"id": "lts", "name": "linux-image-6.1.0-amd64", "desc": "Uzun Süreli Desteklenen Çekirdek (Debian Stable)"},
            {"id": "liquorix", "name": "linux-image-liquorix-amd64", "desc": "Liquorix Yüksek Performanslı Oyun ve Masaüstü Çekirdeği"}
        ]

        self.kernel_widgets = []

        for k in self.kernels:
            card = QFrame()
            card.setObjectName("cardFrame")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)
            card_layout.setSpacing(16)

            icon_lbl = QLabel()
            icon_lbl.setPixmap(QIcon.fromTheme("utilities-terminal").pixmap(32, 32))
            card_layout.addWidget(icon_lbl)

            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(4)

            k_title = QLabel()
            k_title.setObjectName("cardTitle")
            k_title.setFont(QFont("Inter", 12, QFont.Bold))

            k_desc = QLabel(k["desc"])
            k_desc.setObjectName("cardDesc")

            info_layout.addWidget(k_title)
            info_layout.addWidget(k_desc)
            card_layout.addWidget(info_widget, stretch=1)

            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(8)

            is_currently_running = (k["id"] == "default")
            status_lbl = None
            install_btn = None
            remove_btn = None

            if is_currently_running:
                status_lbl = QLabel()
                status_lbl.setStyleSheet("color: #00f5d4; font-weight: bold;" if self.current_theme == "dark" else "color: #008e7f; font-weight: bold;")
                btn_layout.addWidget(status_lbl)
            else:
                install_btn = QPushButton()
                install_btn.setObjectName("primaryActionBtn")
                install_btn.clicked.connect(lambda checked, kn=k["name"]: self.simulate_kernel_install(kn))
                install_btn.setCursor(Qt.PointingHandCursor)
                
                remove_btn = QPushButton()
                remove_btn.setObjectName("dangerActionBtn")
                remove_btn.clicked.connect(lambda checked, kn=k["name"]: self.simulate_kernel_remove(kn))
                remove_btn.setCursor(Qt.PointingHandCursor)
                
                btn_layout.addWidget(remove_btn)
                btn_layout.addWidget(install_btn)

            card_layout.addWidget(btn_container)
            scroll_layout.addWidget(card)

            self.kernel_widgets.append({
                "id": k["id"],
                "name": k["name"],
                "k_title": k_title,
                "k_desc": k_desc,
                "status_lbl": status_lbl,
                "install_btn": install_btn,
                "remove_btn": remove_btn
            })

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        self.stacked_widget.addWidget(page)

    def create_troubleshooting_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Üst Bar
        top_bar_widget = QWidget()
        top_bar = QHBoxLayout(top_bar_widget)
        top_bar.setContentsMargins(40, 20, 40, 10)
        
        self.trouble_back_btn = QPushButton()
        self.trouble_back_btn.setObjectName("backBtn")
        self.trouble_back_btn.setFixedSize(80, 32)
        self.trouble_back_btn.setCursor(Qt.PointingHandCursor)
        self.trouble_back_btn.clicked.connect(lambda: self.change_page(0))
        
        self.trouble_page_title = QLabel()
        self.trouble_page_title.setObjectName("sectionTitle")
        
        top_bar.addWidget(self.trouble_back_btn)
        top_bar.addWidget(self.trouble_page_title)
        top_bar.addStretch()
        main_layout.addWidget(top_bar_widget)

        # Kaydırma Alanı
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(40, 0, 40, 25)
        layout.setSpacing(20)

        trouble_box = QFrame()
        trouble_box.setObjectName("cardFrame")
        tb_layout = QVBoxLayout(trouble_box)
        tb_layout.setContentsMargins(25, 25, 25, 25)
        tb_layout.setSpacing(15)

        self.btn_clear_cache = QPushButton()
        self.btn_clear_cache.setFixedHeight(40)
        self.btn_clear_cache.setCursor(Qt.PointingHandCursor)
        self.btn_clear_cache.clicked.connect(self.simulate_clean_cache)

        self.btn_db_lock = QPushButton()
        self.btn_db_lock.setFixedHeight(40)
        self.btn_db_lock.setCursor(Qt.PointingHandCursor)
        self.btn_db_lock.clicked.connect(self.simulate_remove_lock)

        self.btn_keyring = QPushButton()
        self.btn_keyring.setFixedHeight(40)
        self.btn_keyring.setCursor(Qt.PointingHandCursor)
        self.btn_keyring.clicked.connect(self.simulate_keyring)

        self.btn_reinstall_all = QPushButton()
        self.btn_reinstall_all.setFixedHeight(40)
        self.btn_reinstall_all.setCursor(Qt.PointingHandCursor)
        self.btn_reinstall_all.clicked.connect(self.simulate_reinstall_all)

        self.btn_kwin_debug = QPushButton()
        self.btn_kwin_debug.setFixedHeight(40)
        self.btn_kwin_debug.setCursor(Qt.PointingHandCursor)
        self.btn_kwin_debug.clicked.connect(self.open_log_viewer)

        tb_layout.addWidget(self.btn_clear_cache)
        tb_layout.addWidget(self.btn_db_lock)
        tb_layout.addWidget(self.btn_keyring)
        tb_layout.addWidget(self.btn_reinstall_all)
        tb_layout.addWidget(self.btn_kwin_debug)

        layout.addWidget(trouble_box)
        layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.stacked_widget.addWidget(page)

    def open_package_installer(self):
        installer = PackageInstallerWindow(self, is_dark_mode=(self.current_theme == "dark"), lang_idx=self.lang_combo.currentIndex())
        installer.setStyleSheet(self.styleSheet())
        installer.exec_()

    def simulate_service_toggle(self, service_name, state, checkbox):
        status_text = "Etkinleştiriliyor" if state == Qt.Checked else "Devre Dışı Bırakılıyor"
        action_cmd = "enable" if state == Qt.Checked else "disable"
        
        auth = AuthDialog(self, action_text=f"{service_name} Servisi ({status_text})", command_text=f"sudo systemctl {action_cmd} {service_name.lower()}")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text=f"Servis Durumu Değiştiriliyor ({service_name})", package_name="systemctl")
            if progress.exec_() == QDialog.Accepted:
                self.diagnostic_logs.append(f"[INFO] Servis durumu değişti: {service_name} -> {status_text} (Komut: sudo systemctl {action_cmd} {service_name.lower()})")
                QMessageBox.information(
                    self,
                    "Servis Yapılandırıldı",
                    f"PoC Sürümü: Arka planda 'sudo systemctl {action_cmd} {service_name.lower()}' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )
        else:
            checkbox.blockSignals(True)
            checkbox.setChecked(not state)
            checkbox.blockSignals(False)

    def simulate_remove_lock(self):
        auth = AuthDialog(self, action_text="Veritabanı Paket Kilidini Kaldırma", command_text="sudo rm -f /var/lib/dpkg/lock-frontend")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Paket Kilidi Temizleniyor", package_name="dpkg")
            if progress.exec_() == QDialog.Accepted:
                self.diagnostic_logs.append("[INFO] Paket veritabanı kilitleri temizlendi (Komut: sudo rm -f /var/lib/dpkg/lock-frontend).")
                QMessageBox.information(
                    self,
                    "Kilit Kaldırıldı",
                    "PoC Sürümü: Arka planda 'sudo rm -f /var/lib/dpkg/lock-frontend' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )

    def simulate_clean_cache(self):
        auth = AuthDialog(self, action_text="Paket Önbellek Temizleme", command_text="sudo apt-get clean && sudo apt-get autoremove")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Paket Önbelleği Temizleniyor", package_name="apt")
            if progress.exec_() == QDialog.Accepted:
                self.diagnostic_logs.append("[INFO] Paket önbelleği temizlendi (Komut: sudo apt-get clean && sudo apt-get autoremove).")
                QMessageBox.information(
                    self,
                    "Önbellek Temizlendi",
                    "PoC Sürümü: Arka planda 'sudo apt-get clean && sudo apt-get autoremove' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )

    def simulate_update_packages(self):
        auth = AuthDialog(self, action_text="Sistem Paketlerini Güncelleme", command_text="sudo apt-get update && sudo apt-get upgrade -y")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Depolar Denetleniyor", package_name="apt-update")
            if progress.exec_() == QDialog.Accepted:
                self.diagnostic_logs.append("[INFO] Sistem depo güncellemeleri tetiklendi (Komut: sudo apt-get update && sudo apt-get upgrade -y).")
                QMessageBox.information(
                    self,
                    "Sistem Güncel",
                    "PoC Sürümü: Arka planda 'sudo apt-get update && sudo apt-get upgrade -y' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )

    def simulate_kernel_install(self, kernel_name):
        auth = AuthDialog(self, action_text=f"Yeni Çekirdek Kurulumu ({kernel_name})", command_text=f"sudo apt install {kernel_name}")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text=f"{kernel_name} İndiriliyor ve Kuruluyor", package_name=kernel_name)
            if progress.exec_() == QDialog.Accepted:
                self.diagnostic_logs.append(f"[INFO] Yeni çekirdek kurulumu tetiklendi: {kernel_name} (Komut: sudo apt install {kernel_name})")
                QMessageBox.information(
                    self,
                    "Çekirdek Kuruldu",
                    f"PoC Sürümü: Arka planda 'sudo apt install {kernel_name}' komutunun çalıştırılması simüle edildi.\n\nSistemi yeniden başlatarak bu çekirdeği aktif edebilirsiniz.",
                    QMessageBox.Ok
                )

    def simulate_kernel_remove(self, kernel_name):
        auth = AuthDialog(self, action_text=f"Çekirdek Kaldırma ({kernel_name})", command_text=f"sudo apt purge {kernel_name}")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text=f"{kernel_name} Sistemden Siliniyor", package_name=kernel_name)
            if progress.exec_() == QDialog.Accepted:
                self.diagnostic_logs.append(f"[INFO] Çekirdek sistemden kaldırıldı: {kernel_name} (Komut: sudo apt purge {kernel_name})")
                QMessageBox.information(
                    self,
                    "Çekirdek Kaldırıldı",
                    f"PoC Sürümü: Arka planda 'sudo apt purge {kernel_name}' komutunun çalıştırılması simüle edildi.",
                    QMessageBox.Ok
                )

    def simulate_mirrors(self):
        auth = AuthDialog(self, action_text="Paket Deposu Ayna Hız Testi", command_text="sudo apt-transport-https mirror-ranker")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Aynalar Pingleniyor", package_name="apt-transport-https")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "Aynalar Sıralandı", "En hızlı ayna sunucusu tespit edildi ve /etc/apt/sources.list dosyasına yazıldı (Simüle).")

    def simulate_remove_orphans(self):
        auth = AuthDialog(self, action_text="Kullanılmayan Bağımlılıkları Kaldırma", command_text="sudo apt autoremove --purge")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Artık Paketler Kaldırılıyor", package_name="apt")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "Paketler Temizlendi", "Sistemdeki tüm gereksiz bağımlılıklar başarıyla kaldırıldı (Simüle).")

    def simulate_vram(self):
        auth = AuthDialog(self, action_text="VRAM Yönetimi Kurulumu", command_text="sudo vram-manager --configure")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="VRAM Ayarları Yapılandırılıyor", package_name="vram-manager")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "Kuruldu", "VRAM yönetimi başarıyla etkinleştirildi (Simüle).")

    def simulate_winboat(self):
        auth = AuthDialog(self, action_text="Winboat Kurulumu", command_text="sudo apt install winboat")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Winboat İndiriliyor", package_name="winboat")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "Kuruldu", "Winboat sisteminize başarıyla kuruldu (Simüle).")

    def simulate_games(self):
        auth = AuthDialog(self, action_text="Oyun Paketlerinin Kurulumu", command_text="sudo apt install steam-devices gamemode")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Gerekli Sürücü ve Paketler Yükleniyor", package_name="gamemode")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "Kuruldu", "Oyun performans paketleri ve kütüphaneleri kuruldu (Simüle).")

    def simulate_dns(self):
        auth = AuthDialog(self, action_text="DNS Sunucusu Değiştirme", command_text="sudo resolvconf -u")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="DNS Ayarları Güncelleniyor", package_name="dns-manager")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "DNS Güncellendi", "Sistem DNS sunucusu 1.1.1.1 (Cloudflare) olarak değiştirildi (Simüle).")

    def simulate_keyring(self):
        auth = AuthDialog(self, action_text="Pardus/Debian Anahtar Halkasını Sıfırlama", command_text="sudo apt-key adv --refresh-keys")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Anahtarlar İndiriliyor ve Kuruluyor", package_name="apt-key")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "Anahtarlar Güncellendi", "Sistem paket imzalama anahtarları başarıyla sıfırlandı (Simüle).")

    def simulate_reinstall_all(self):
        auth = AuthDialog(self, action_text="Tüm Bozuk Paketleri Yeniden Kurma", command_text="sudo apt install --reinstall $(dpkg --get-selections | grep deinstall | cut -f1)")
        if auth.exec_() == QDialog.Accepted:
            progress = ProgressDialog(self, operation_text="Paket Listesi Onarılıyor", package_name="apt")
            if progress.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "Onarım Tamamlandı", "Bozuk veya eksik paketlerin tespiti ve yeniden kurulumu tamamlandı (Simüle).")

    def open_log_viewer(self):
        dialog = LogViewerDialog(self, is_dark_mode=(self.current_theme == "dark"))
        dialog.setStyleSheet(self.styleSheet())
        dialog.exec_()


# ==============================================================================
# SİSTEM VE TANI GÜNLÜK İZLEYİCİSİ (Log Viewer Dialog)
# ==============================================================================

class LogViewerDialog(QDialog):
    """Sistem günlüklerini ve uygulama tanılamalarını okuyup gösteren gelişmiş günlük izleyici."""
    def __init__(self, parent=None, is_dark_mode=True):
        super().__init__(parent)
        self.parent_window = parent
        self.is_dark_mode = is_dark_mode
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setMinimumSize(800, 550)
        self.init_ui()
        self.load_logs()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Başlık Çubuğu
        self.title_bar = CustomTitleBar(self, title="Sistem Günlük İzleyicisi", subtitle="Pardus Log Viewer")
        main_layout.addWidget(self.title_bar)

        # İçerik Alanı
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(12)

        # Kontrol Paneli (Kaynak Seçimi, Arama, Yenile)
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        source_lbl = QLabel("Günlük Kaynağı:")
        source_lbl.setStyleSheet("font-weight: bold;")
        control_layout.addWidget(source_lbl)

        self.source_combo = QComboBox()
        self.source_combo.addItems([
            "Uygulama Tanılama Günlüğü (Pardus Hello)",
            "Paket Yönetim Günlüğü (/var/log/dpkg.log)",
            "Sistem Servis Günlükleri (journalctl)"
        ])
        self.source_combo.currentIndexChanged.connect(self.load_logs)
        self.source_combo.setMinimumWidth(280)
        control_layout.addWidget(self.source_combo)

        control_layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Günlüklerde ara...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_logs)
        control_layout.addWidget(self.search_input)

        self.refresh_btn = QPushButton("Yenile")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.load_logs)
        control_layout.addWidget(self.refresh_btn)

        content_layout.addLayout(control_layout)

        # Metin Alanı (QTextEdit)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Monospace", 9))
        
        # QTextEdit QSS styling
        if self.is_dark_mode:
            self.log_text.setStyleSheet(
                "QTextEdit { background-color: #0c0f17; color: #a9b1d6; border: 1px solid #1f2335; border-radius: 6px; padding: 10px; }"
            )
        else:
            self.log_text.setStyleSheet(
                "QTextEdit { background-color: #eff1f5; color: #4c4f69; border: 1px solid #ccd0da; border-radius: 6px; padding: 10px; }"
            )
        content_layout.addWidget(self.log_text)

        # Alt Çubuk (Satır Sayısı ve Kapat)
        bottom_layout = QHBoxLayout()
        self.status_lbl = QLabel("Hazır.")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #565f89;" if self.is_dark_mode else "font-size: 11px; color: #6c6f85;")
        bottom_layout.addWidget(self.status_lbl)
        
        bottom_layout.addStretch()

        self.close_btn = QPushButton("Kapat")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(self.close_btn)

        content_layout.addLayout(bottom_layout)
        main_layout.addWidget(content_widget)

        self.raw_log_content = ""

    def load_logs(self):
        self.log_text.clear()
        idx = self.source_combo.currentIndex()

        if idx == 0:
            # Diagnostic Log
            if hasattr(self.parent_window, 'diagnostic_logs'):
                self.raw_log_content = "\n".join(self.parent_window.diagnostic_logs)
            else:
                self.raw_log_content = "[INFO] Tanılama günlüğü bulunamadı."
        elif idx == 1:
            # dpkg.log
            try:
                if os.path.exists("/var/log/dpkg.log"):
                    with open("/var/log/dpkg.log", "r") as f:
                        lines = f.readlines()
                        self.raw_log_content = "".join(lines[-150:])
                else:
                    self.raw_log_content = "[HATA] /var/log/dpkg.log dosyası sistemde bulunamadı."
            except Exception as e:
                self.raw_log_content = f"[HATA] dpkg.log okunamadı: {str(e)}"
        elif idx == 2:
            # journalctl
            try:
                res = subprocess.run(["journalctl", "-n", "100", "--no-pager"], capture_output=True, text=True, timeout=2)
                if res.stdout:
                    self.raw_log_content = res.stdout
                else:
                    self.raw_log_content = "[BİLGİ] journalctl çıktısı boş döndü."
            except Exception as e:
                self.raw_log_content = f"[HATA] journalctl okunamadı (Sistem yetkisi eksik olabilir): {str(e)}"

        self.log_text.setPlainText(self.raw_log_content)
        self.filter_logs(self.search_input.text())

    def filter_logs(self, filter_text):
        if not filter_text:
            self.log_text.setPlainText(self.raw_log_content)
            self.log_text.moveCursor(self.log_text.document().lineCount())
            self.status_lbl.setText(f"Toplam satır sayısı: {self.log_text.document().lineCount()}")
            return

        filtered_lines = []
        for line in self.raw_log_content.splitlines():
            if filter_text.lower() in line.lower():
                filtered_lines.append(line)

        self.log_text.setPlainText("\n".join(filtered_lines))
        self.status_lbl.setText(f"Eşleşen satır sayısı: {len(filtered_lines)} / Toplam: {self.raw_log_content.count(chr(10)) + 1}")


# ==============================================================================
# ANA ÇALIŞTIRICI
# ==============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PardusHello")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
