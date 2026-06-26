#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║      PARDUS HELLO — SİSTEM KONTROL MERKEZİ  (Gerçek Komut Sürümü)         ║
║  Tüm işlemler pkexec ile root yetkisiyle, QThread üzerinde çalışır.        ║
║  Light / Dark tema, 6 sekme, tam YETKİLENDİRME + gerçek komut motoru.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ==============================================================================
# 0. IMPORTS
# ==============================================================================
import os
import sys
import platform
import subprocess

from PyQt5.QtCore import (
    Qt, QSize, QUrl, QThread, pyqtSignal, QObject
)
from PyQt5.QtGui import QIcon, QDesktopServices, QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget,
    QListWidget, QListWidgetItem, QScrollArea,
    QLabel, QPushButton, QMessageBox, QGroupBox,
    QSizePolicy, QProgressBar, QDialog, QTextEdit
)

# ==============================================================================
# 1. TEMA QSS
# ==============================================================================

def qss_dark() -> str:
    return """
/* ══ DARK THEME ══════════════════════════════════════════════════════════ */
QWidget          { background-color:#181825; color:#cdd6f4;
                   font-family:'Inter','Segoe UI','Ubuntu',sans-serif; font-size:13px; }
QMainWindow      { background-color:#181825; }

QListWidget      { background-color:#11111b; border:none; outline:none;
                   padding:8px 0; }
QListWidget::item          { color:#a6adc8; padding:12px 20px; border-radius:8px;
                              margin:2px 8px; font-size:13px; font-weight:500; }
QListWidget::item:hover    { background-color:#1e1e2e; color:#cdd6f4; }
QListWidget::item:selected { background-color:#313244; color:#89b4fa;
                              font-weight:700; border-left:3px solid #89b4fa; }

QScrollArea { background:transparent; border:none; }
QScrollBar:vertical { background:#1e1e2e; width:6px; border-radius:3px; }
QScrollBar::handle:vertical { background:#45475a; border-radius:3px; min-height:30px; }
QScrollBar::handle:vertical:hover { background:#585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background:transparent; }

QPushButton { background-color:#313244; color:#cdd6f4; border:none;
              border-radius:6px; padding:8px 18px; font-size:12px; font-weight:600; }
QPushButton:hover   { background-color:#45475a; color:#fff; }
QPushButton:pressed { background-color:#6c7086; }
QPushButton:disabled { background-color:#1e1e2e; color:#45475a; }

QPushButton#btnAccent  { background-color:#89b4fa; color:#1e1e2e; }
QPushButton#btnAccent:hover  { background-color:#b4d0fb; }
QPushButton#btnAccent:pressed { background-color:#74a7f8; }
QPushButton#btnAccent:disabled { background-color:#313244; color:#585b70; }

QPushButton#btnDanger  { background-color:#f38ba8; color:#1e1e2e; }
QPushButton#btnDanger:hover  { background-color:#f5a3b8; }
QPushButton#btnDanger:disabled { background-color:#313244; color:#585b70; }

QPushButton#btnSuccess { background-color:#a6e3a1; color:#1e1e2e; }
QPushButton#btnSuccess:hover { background-color:#b8e8b4; }

QPushButton#btnWarning { background-color:#f9e2af; color:#1e1e2e; }
QPushButton#btnWarning:hover { background-color:#fbe9c2; }

QPushButton#btnTheme   { background-color:#313244; color:#89b4fa;
                          border:1px solid #45475a; border-radius:6px; padding:6px 14px; }
QPushButton#btnTheme:hover { background-color:#45475a; }

QPushButton#btnLink { background-color:transparent; color:#89b4fa;
                       border:1px solid #45475a; border-radius:8px;
                       padding:10px 16px; font-size:12px; font-weight:600; }
QPushButton#btnLink:hover { background-color:#1e1e2e; border-color:#89b4fa; }

QGroupBox { background-color:#181825; border:1px solid #45475a;
            border-radius:10px; margin-top:22px; font-size:13px;
            font-weight:700; color:#6c7086; }
QGroupBox::title { subcontrol-origin:margin; left:16px; top:-11px;
                   padding:2px 10px; color:#cdd6f4; background-color:#313244;
                   border-radius:4px; font-size:13px; font-weight:700; }

QFrame#Card    { background-color:#181825; border:1px solid #313244; border-radius:10px; }
QFrame#CardBlue{ background-color:#1e2030; border:1px solid #89b4fa; border-radius:10px; }
QFrame#SideBar { background-color:#11111b; }

QLabel#LblTitle    { color:#89b4fa; font-size:28px; font-weight:700; }
QLabel#LblSubtitle { color:#a6adc8; font-size:14px; }
QLabel#LblSection  { color:#89b4fa; font-size:15px; font-weight:700; }
QLabel#LblMuted    { color:#6c7086; font-size:11px; }
QLabel#LblKey      { color:#6c7086; font-size:12px; }
QLabel#LblVal      { color:#cdd6f4; font-size:12px; font-weight:600; }

QProgressBar { background:#313244; border:none; border-radius:4px; height:6px; }
QProgressBar::chunk { background:#89b4fa; border-radius:4px; }

QMessageBox { background-color:#1e1e2e; color:#cdd6f4; }
QMessageBox QLabel { color:#cdd6f4; font-size:13px; }
QMessageBox QPushButton { min-width:80px; padding:8px 16px; }

QTextEdit { background-color:#11111b; color:#cdd6f4; border:1px solid #313244;
            border-radius:6px; font-family:monospace; font-size:12px; }
"""


def qss_light() -> str:
    return """
/* ══ LIGHT THEME ═════════════════════════════════════════════════════════ */
QWidget          { background-color:#f5f5f7; color:#1c1c1e;
                   font-family:'Inter','Segoe UI','Ubuntu',sans-serif; font-size:13px; }
QMainWindow      { background-color:#f5f5f7; }

QListWidget      { background-color:#e8e8ed; border:none; outline:none; padding:8px 0; }
QListWidget::item          { color:#3c3c43; padding:12px 20px; border-radius:8px;
                              margin:2px 8px; font-size:13px; font-weight:500; }
QListWidget::item:hover    { background-color:#d1d1d6; color:#1c1c1e; }
QListWidget::item:selected { background-color:#007aff; color:#ffffff;
                              font-weight:700; border-left:3px solid #0051a8; }

QScrollArea { background:transparent; border:none; }
QScrollBar:vertical { background:#e8e8ed; width:6px; border-radius:3px; }
QScrollBar::handle:vertical { background:#aeaeb2; border-radius:3px; min-height:30px; }
QScrollBar::handle:vertical:hover { background:#8e8e93; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background:transparent; }

QPushButton { background-color:#d1d1d6; color:#1c1c1e; border:none;
              border-radius:6px; padding:8px 18px; font-size:12px; font-weight:600; }
QPushButton:hover   { background-color:#aeaeb2; }
QPushButton:pressed { background-color:#8e8e93; }
QPushButton:disabled { background-color:#e8e8ed; color:#aeaeb2; }

QPushButton#btnAccent  { background-color:#007aff; color:#ffffff; }
QPushButton#btnAccent:hover  { background-color:#0051d0; }
QPushButton#btnAccent:pressed { background-color:#003fa8; }
QPushButton#btnAccent:disabled { background-color:#d1d1d6; color:#8e8e93; }

QPushButton#btnDanger  { background-color:#ff3b30; color:#ffffff; }
QPushButton#btnDanger:hover  { background-color:#d62b20; }
QPushButton#btnDanger:disabled { background-color:#d1d1d6; color:#8e8e93; }

QPushButton#btnSuccess { background-color:#34c759; color:#ffffff; }
QPushButton#btnSuccess:hover { background-color:#28a045; }

QPushButton#btnWarning { background-color:#ff9500; color:#ffffff; }
QPushButton#btnWarning:hover { background-color:#d07d00; }

QPushButton#btnTheme   { background-color:#e8e8ed; color:#007aff;
                          border:1px solid #d1d1d6; border-radius:6px; padding:6px 14px; }
QPushButton#btnTheme:hover { background-color:#d1d1d6; }

QPushButton#btnLink { background-color:transparent; color:#007aff;
                       border:1px solid #d1d1d6; border-radius:8px;
                       padding:10px 16px; font-size:12px; font-weight:600; }
QPushButton#btnLink:hover { background-color:#e8e8ed; border-color:#007aff; }

QGroupBox { background-color:#ffffff; border:1px solid #c0c0c8;
            border-radius:10px; margin-top:22px; font-size:13px;
            font-weight:700; color:#8e8e93; }
QGroupBox::title { subcontrol-origin:margin; left:16px; top:-11px;
                   padding:2px 10px; color:#1c1c1e; background-color:#d1d1d6;
                   border-radius:4px; font-size:13px; font-weight:700; }

QFrame#Card    { background-color:#ffffff; border:1px solid #d1d1d6; border-radius:10px; }
QFrame#CardBlue{ background-color:#e8f0ff; border:1px solid #007aff; border-radius:10px; }
QFrame#SideBar { background-color:#e8e8ed; }

QLabel#LblTitle    { color:#007aff; font-size:28px; font-weight:700; }
QLabel#LblSubtitle { color:#3c3c43; font-size:14px; }
QLabel#LblSection  { color:#007aff; font-size:15px; font-weight:700; }
QLabel#LblMuted    { color:#8e8e93; font-size:11px; }
QLabel#LblKey      { color:#8e8e93; font-size:12px; }
QLabel#LblVal      { color:#1c1c1e; font-size:12px; font-weight:600; }

QProgressBar { background:#d1d1d6; border:none; border-radius:4px; height:6px; }
QProgressBar::chunk { background:#007aff; border-radius:4px; }

QMessageBox { background-color:#f5f5f7; }
QMessageBox QLabel { color:#1c1c1e; font-size:13px; }
QMessageBox QPushButton { min-width:80px; padding:8px 16px; }

QTextEdit { background-color:#ffffff; color:#1c1c1e; border:1px solid #d1d1d6;
            border-radius:6px; font-family:monospace; font-size:12px; }
"""


# ==============================================================================
# 2. SİSTEM BİLGİSİ (salt okuma — subprocess.check_output)
# ==============================================================================

# ── Pardus logosu yükleyici ───────────────────────────────────────────────────
def _pardus_icon() -> QIcon:
    """
    Sistemdeki Pardus emblem PNG dosyalarını kullanarak çok çözünürlüklü
    bir QIcon oluşturur. Görev çubuğu, pencere başlığı ve Alt+Tab için
    en yüksek kaliteli ikonu sağlar.
    """
    _base = "/usr/share/icons/desktop-base"
    _hico = "/usr/share/icons/hicolor"
    candidates = [
        (256, f"{_base}/256x256/emblems/emblem-pardus.png"),
        (128, f"{_base}/128x128/emblems/emblem-pardus.png"),
        (64,  f"{_base}/64x64/emblems/emblem-pardus.png"),
        (256, f"{_hico}/256x256/emblems/emblem-pardus.png"),
        (128, f"{_hico}/128x128/emblems/emblem-pardus.png"),
    ]
    icon = QIcon()
    for size, path in candidates:
        if os.path.exists(path):
            icon.addFile(path, QSize(size, size))
    if icon.isNull():
        # Hiçbir dosya bulunamazsa tema ikonuna dön
        icon = QIcon.fromTheme("emblem-pardus",
               QIcon.fromTheme("distributor-logo",
               QIcon.fromTheme("start-here-symbolic")))
    return icon

def get_os_name() -> str:
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return f"{platform.system()} {platform.release()}"


def get_kernel() -> str:
    return platform.release()


def get_cpu() -> str:
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or "Bilinmiyor"


def get_ram() -> str:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return f"{kb // 1024} MB  (~{kb // (1024 * 1024)} GB)"
    except Exception:
        pass
    return "Bilinmiyor"


def get_hostname() -> str:
    try:
        return subprocess.check_output(["hostname"], text=True).strip()
    except Exception:
        return "pardus"


def get_desktop() -> str:
    de = os.environ.get("XDG_CURRENT_DESKTOP", "")
    return de if de else os.environ.get("DESKTOP_SESSION", "Bilinmiyor")


# ==============================================================================
# 3. ARKA PLAN KOMUT ÇALIŞTIRICI (QThread)
# ==============================================================================

class CommandWorker(QObject):
    """
    Komutları arka planda (UI donmadan) çalıştırır.
    pkexec ile root yetkisi alır; Polkit şifre penceresi otomatik açılır.
    """
    started  = pyqtSignal()
    progress = pyqtSignal(str)          # anlık çıktı satırı
    finished = pyqtSignal(int, str)     # (return_code, full_output)

    def __init__(self, cmd: list, use_pkexec: bool = True):
        super().__init__()
        self.cmd       = cmd
        self.use_pkexec = use_pkexec

    def run(self):
        self.started.emit()
        final_cmd = (["pkexec"] + self.cmd) if self.use_pkexec else self.cmd
        try:
            proc = subprocess.Popen(
                final_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            output_lines = []
            for line in proc.stdout:
                output_lines.append(line)
                self.progress.emit(line.rstrip())
            proc.wait()
            self.finished.emit(proc.returncode, "".join(output_lines))
        except FileNotFoundError:
            msg = f"[HATA] Komut bulunamadı: {final_cmd[0]}"
            self.finished.emit(127, msg)
        except Exception as e:
            self.finished.emit(1, str(e))


class CommandThread(QThread):
    def __init__(self, worker: CommandWorker):
        super().__init__()
        self.worker = worker
        self.worker.moveToThread(self)
        self.started.connect(self.worker.run)


# ==============================================================================
# 4. ÇIKTI PENCERESİ (QDialog)
# ==============================================================================

class OutputDialog(QDialog):
    """Komut çıktısını ve ilerleme çubuğunu gösteren modal pencere."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(620, 380)
        self.setModal(True)

        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(20, 20, 20, 20)

        self.lbl_status = QLabel("⏳  İşlem başlatılıyor…")
        self.lbl_status.setStyleSheet("font-weight:700; font-size:13px;")
        lay.addWidget(self.lbl_status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)   # belirsiz (dönen) mod
        self.progress.setFixedHeight(6)
        lay.addWidget(self.progress)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        lay.addWidget(self.output, 1)

        self.btn_close = QPushButton("⏳  Çalışıyor…")
        self.btn_close.setEnabled(False)
        self.btn_close.setObjectName("btnAccent")
        self.btn_close.clicked.connect(self.accept)
        lay.addWidget(self.btn_close)

    def append_line(self, line: str):
        self.output.append(line)

    def set_done(self, success: bool, summary: str):
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        if success:
            self.lbl_status.setText("✅  İşlem başarıyla tamamlandı.")
            self.lbl_status.setStyleSheet("font-weight:700; font-size:13px; color:#a6e3a1;")
            self.btn_close.setText("✔  Kapat")
        else:
            self.lbl_status.setText("❌  Hata oluştu.")
            self.lbl_status.setStyleSheet("font-weight:700; font-size:13px; color:#f38ba8;")
            self.btn_close.setText("✖  Kapat")
        self.btn_close.setEnabled(True)
        self.output.append(f"\n{'─'*50}\n{summary}")


# ==============================================================================
# 5. KOMUT ÇALIŞTIRMA YARDIMCISI
# ==============================================================================

def run_command(parent, title: str, cmd: list, use_pkexec: bool = True):
    """
    Verilen komutu bir QThread üzerinde çalıştırır,
    çıktıyı OutputDialog'da gösterir.
    use_pkexec=True → komutun önüne 'pkexec' eklenir.
    """
    dlg = OutputDialog(title, parent)

    worker = CommandWorker(cmd, use_pkexec)
    thread = CommandThread(worker)

    worker.progress.connect(dlg.append_line)
    worker.finished.connect(
        lambda code, out: dlg.set_done(code == 0, out[-500:] if out else "")
    )

    # Thread nesnesini diyalog kapanana kadar canlı tut
    dlg._thread = thread
    thread.start()
    dlg.exec_()
    thread.quit()
    thread.wait()


# ==============================================================================
# 6. YENİDEN KULLANILABİLİR BİLEŞENLER
# ==============================================================================

class SectionHeader(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("LblSection")
        self.setContentsMargins(0, 16, 0, 4)


class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setStyleSheet("color:#313244; border:none; background:#313244; max-height:1px;")
        self.setFixedHeight(1)


class InfoRow(QWidget):
    def __init__(self, key, value, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(32)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 5, 4, 5)
        lay.setSpacing(12)
        lbl_k = QLabel(key)
        lbl_k.setObjectName("LblKey")
        lbl_k.setFixedWidth(180)           # ← 160→180px
        lbl_v = QLabel(value)
        lbl_v.setObjectName("LblVal")
        lbl_v.setWordWrap(True)
        lay.addWidget(lbl_k)
        lay.addWidget(lbl_v, 1)


class AppCard(QFrame):
    """Yazılım Merkezi / Sürücü Yöneticisi kartı."""

    def __init__(self, icon_char, title, subtitle,
                 btn_text, btn_style, cmd, use_pkexec=True, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._cmd        = cmd
        self._title      = title
        self._use_pkexec = use_pkexec
        self._parent_win = None

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(14)

        icon_lbl = QLabel(icon_char)
        icon_lbl.setFixedSize(42, 42)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            "font-size:22px; background:#313244; border-radius:8px; color:#89b4fa;"
        )

        txt = QVBoxLayout()
        txt.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet("font-size:13px; font-weight:700;")
        s = QLabel(subtitle)
        s.setObjectName("LblMuted")
        txt.addWidget(t)
        txt.addWidget(s)

        self.btn = QPushButton(btn_text)
        self.btn.setObjectName(btn_style)
        self.btn.setFixedSize(106, 34)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self._run)

        lay.addWidget(icon_lbl)
        lay.addLayout(txt, 1)
        lay.addWidget(self.btn)

    def set_parent_window(self, w):
        self._parent_win = w

    def _run(self):
        self.btn.setEnabled(False)
        run_command(self._parent_win, self._title, self._cmd, self._use_pkexec)
        self.btn.setEnabled(True)


class BigActionCard(QFrame):
    """Sistem Bakımı / Sorun Giderici büyük aksiyon kartı."""

    def __init__(self, icon_char, title, description,
                 cmd, btn_style="btnAccent", use_pkexec=True, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._cmd        = cmd
        self._title      = title
        self._use_pkexec = use_pkexec
        self._parent_win = None

        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(14)

        icon_lbl = QLabel(icon_char)
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            "font-size:24px; background:#313244; border-radius:8px;"
        )

        txt = QVBoxLayout()
        txt.setSpacing(3)
        t = QLabel(title)
        t.setStyleSheet("font-size:13px; font-weight:700;")
        d = QLabel(description)
        d.setObjectName("LblMuted")
        d.setWordWrap(True)
        txt.addWidget(t)
        txt.addWidget(d)

        self.btn = QPushButton("▶  Çalıştır")
        self.btn.setObjectName(btn_style)
        self.btn.setFixedSize(110, 34)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self._run)

        lay.addWidget(icon_lbl)
        lay.addLayout(txt, 1)
        lay.addWidget(self.btn)

    def set_parent_window(self, w):
        self._parent_win = w

    def _run(self):
        self.btn.setEnabled(False)
        run_command(self._parent_win, self._title, self._cmd, self._use_pkexec)
        self.btn.setEnabled(True)


# ==============================================================================
# 7. SEKMELER
# ==============================================================================

# ── SEKME 1 : Ana Sayfa ────────────────────────────────────────────────────────
def build_home_page(win) -> QWidget:
    page = QWidget()
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    content = QWidget()
    lay = QVBoxLayout(content)
    lay.setContentsMargins(36, 36, 36, 36)
    lay.setSpacing(20)

    # ── Hero kartı ─────────────────────────────────────────────────────────
    hero = QFrame()
    hero.setObjectName("CardBlue")
    h_lay = QVBoxLayout(hero)
    h_lay.setContentsMargins(32, 28, 32, 28)
    h_lay.setSpacing(10)

    top_row = QHBoxLayout()
    top_row.setSpacing(14)
    # ── Pardus logosu (hero) ─────────────────────────────────────────
    _LOGO_PATHS = [
        "/usr/share/icons/desktop-base/128x128/emblems/emblem-pardus.png",
        "/usr/share/icons/hicolor/128x128/emblems/emblem-pardus.png",
    ]
    penguin = QLabel()
    penguin.setFixedSize(68, 68)
    penguin.setAlignment(Qt.AlignCenter)
    penguin.setStyleSheet("background:transparent;")
    _logo_px = QPixmap()
    for _p in _LOGO_PATHS:
        if os.path.exists(_p):
            _logo_px = QPixmap(_p)
            break
    if not _logo_px.isNull():
        penguin.setPixmap(_logo_px.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    else:
        penguin.setText("🐧")
        penguin.setStyleSheet("font-size:52px; background:transparent;")

    t_col = QVBoxLayout()
    t_col.setSpacing(4)
    lbl_main = QLabel("Pardus'a Hoş Geldiniz")
    lbl_main.setObjectName("LblTitle")
    lbl_sub = QLabel("Sistem Kontrol Merkezi  ·  Pardus / Debian")
    lbl_sub.setObjectName("LblSubtitle")
    t_col.addWidget(lbl_main)
    t_col.addWidget(lbl_sub)
    top_row.addWidget(penguin)
    top_row.addLayout(t_col, 1)

    desc = QLabel(
        "Bu araç; yazılım kurulumu, donanım sürücü yönetimi, sistem bakımı ve "
        "sorun giderme işlemlerini tek merkezden yönetmenizi sağlar. "
        "Tüm yetkili işlemler pkexec (Polkit) aracılığıyla güvenli biçimde çalıştırılır."
    )
    desc.setObjectName("LblSubtitle")
    desc.setWordWrap(True)

    h_lay.addLayout(top_row)
    h_lay.addWidget(desc)
    lay.addWidget(hero)

    # ── Sistem bilgisi kartı (QFrame — başlık her zaman görünür) ──────────
    info_frame = QFrame()
    info_frame.setObjectName("Card")
    info_outer = QVBoxLayout(info_frame)
    info_outer.setContentsMargins(0, 0, 0, 0)
    info_outer.setSpacing(0)

    # Başlık bandı
    hdr_band = QFrame()
    hdr_band.setStyleSheet(
        "background-color:#313244; border-radius:8px 8px 0 0; border:none;"
    )
    hdr_band.setFixedHeight(42)
    hdr_inner = QHBoxLayout(hdr_band)
    hdr_inner.setContentsMargins(20, 0, 20, 0)
    hdr_inner.setSpacing(10)
    hdr_icon = QLabel("💻")
    hdr_icon.setStyleSheet("font-size:18px; background:transparent;")
    hdr_title = QLabel("Donanım & Sistem Bilgisi")
    hdr_title.setStyleSheet(
        "color:#cdd6f4; font-size:14px; font-weight:700; background:transparent;"
    )
    hdr_inner.addWidget(hdr_icon)
    hdr_inner.addWidget(hdr_title, 1)
    info_outer.addWidget(hdr_band)

    # İçerik alanı
    ig_content = QWidget()
    ig_lay = QVBoxLayout(ig_content)
    ig_lay.setContentsMargins(20, 8, 20, 12)
    ig_lay.setSpacing(0)

    rows_data = [
        ("İşletim Sistemi",   get_os_name()),
        ("Kernel Sürümü",     get_kernel()),
        ("Bilgisayar Adı",    get_hostname()),
        ("Masaüstü Ortamı",   get_desktop()),
        ("İşlemci (CPU)",     get_cpu()),
        ("RAM",               get_ram()),
        ("Python Sürümü",     platform.python_version()),
        ("Mimari",            platform.machine()),
    ]
    for i, (k, v) in enumerate(rows_data):
        ig_lay.addWidget(InfoRow(k, v))
        if i < len(rows_data) - 1:
            ig_lay.addWidget(Divider())

    info_outer.addWidget(ig_content)
    lay.addWidget(info_frame)


    # ── Hızlı erişim ──────────────────────────────────────────────────────
    lay.addWidget(SectionHeader("Hızlı Erişim"))
    btn_row = QHBoxLayout()
    btn_row.setSpacing(12)
    quick = [
        ("🖥️ Yazılım Merkezi", 1),
        ("⚙️ Sürücü Yöneticisi", 2),
        ("🛠️ Sistem Bakımı", 3),
        ("🔍 Sorun Giderici", 4),
        ("🌐 Topluluk", 5),
    ]
    for label, idx in quick:
        b = QPushButton(label)
        b.setObjectName("btnAccent")
        b.setCursor(Qt.PointingHandCursor)
        b.setMinimumHeight(40)
        b.clicked.connect(lambda _, i=idx: win.nav_to(i))
        btn_row.addWidget(b)
    lay.addLayout(btn_row)
    lay.addStretch()

    scroll.setWidget(content)
    outer.addWidget(scroll)
    return page


# ── SEKME 2 : Yazılım Merkezi ─────────────────────────────────────────────────
SOFTWARE_DATA = {
    "🌐  Tarayıcılar": [
        ("🟡", "Google Chrome",
         "Hızlı ve güvenli Google tarayıcısı",
         ["apt-get", "install", "-y", "google-chrome-stable"]),
        ("🦊", "Mozilla Firefox",
         "Gizlilik odaklı açık kaynak tarayıcı",
         ["apt-get", "install", "-y", "firefox"]),
        ("🔵", "Chromium",
         "Chrome'un açık kaynak temeli",
         ["apt-get", "install", "-y", "chromium"]),
    ],
    "🎮  Oyun": [
        ("🕹️", "Steam",
         "Valve'ın oyun platformu",
         ["apt-get", "install", "-y", "steam"]),
        ("🍷", "Wine",
         "Windows uygulamalarını Linux'ta çalıştırır",
         ["apt-get", "install", "-y", "wine"]),
        ("🎲", "Lutris",
         "Linux oyun yöneticisi",
         ["apt-get", "install", "-y", "lutris"]),
    ],
    "💻  Geliştirme": [
        ("🐍", "Python3 + pip",
         "Python programlama dili araçları",
         ["apt-get", "install", "-y", "python3", "python3-pip"]),
        ("🐳", "Docker",
         "Konteyner platformu",
         ["apt-get", "install", "-y", "docker.io"]),
        ("🌿", "Git",
         "Dağıtık sürüm kontrol sistemi",
         ["apt-get", "install", "-y", "git"]),
        ("🖥️", "Build Essential",
         "GCC ve temel derleme araçları",
         ["apt-get", "install", "-y", "build-essential"]),
    ],
    "🎵  Medya & Araçlar": [
        ("🎬", "VLC Media Player",
         "Evrensel medya oynatıcı",
         ["apt-get", "install", "-y", "vlc"]),
        ("🖼️", "GIMP",
         "Profesyonel görüntü düzenleyici",
         ["apt-get", "install", "-y", "gimp"]),
        ("📄", "LibreOffice",
         "Açık kaynak ofis paketi",
         ["apt-get", "install", "-y", "libreoffice"]),
        ("📺", "OBS Studio",
         "Canlı yayın ve ekran kaydı",
         ["apt-get", "install", "-y", "obs-studio"]),
    ],
}


def build_software_page(win) -> QWidget:
    page = QWidget()
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    content = QWidget()
    lay = QVBoxLayout(content)
    lay.setContentsMargins(36, 36, 36, 36)
    lay.setSpacing(14)

    lbl = QLabel("Yazılım Merkezi")
    lbl.setObjectName("LblTitle")
    lay.addWidget(lbl)

    sub = QLabel(
        "Kategorilere göre popüler uygulamaları kurun. "
        "Yükleme işlemleri pkexec (Polkit) aracılığıyla root yetkisiyle çalıştırılır."
    )
    sub.setObjectName("LblSubtitle")
    sub.setWordWrap(True)
    lay.addWidget(sub)
    lay.addSpacing(8)

    for category, apps in SOFTWARE_DATA.items():
        lay.addWidget(SectionHeader(category))
        for icon, name, desc, cmd in apps:
            card = AppCard(icon, name, desc, "📦  Kur", "btnAccent", cmd, use_pkexec=True)
            card.set_parent_window(win)
            lay.addWidget(card)
        lay.addSpacing(4)

    lay.addStretch()
    scroll.setWidget(content)
    outer.addWidget(scroll)
    return page


# ── SEKME 3 : Sürücü Yöneticisi ──────────────────────────────────────────────
DRIVER_DATA = [
    ("🟢", "NVIDIA Grafik Kartı (Proprietary)",
     "Kapalı kaynak NVIDIA sürücüsü — yüksek performans",
     ["apt-get", "install", "-y", "nvidia-driver"]),
    ("🔴", "AMD Radeon (firmware)",
     "AMD GPU firmware ve açık kaynak sürücü paketi",
     ["apt-get", "install", "-y", "firmware-amd-graphics"]),
    ("🔵", "Intel Grafik Mikrokodu",
     "Intel integrated GPU mikro kodu",
     ["apt-get", "install", "-y", "intel-microcode"]),
    ("📶", "Realtek Wi-Fi Adaptörü",
     "RTL8xxx serisi kablosuz sürücüsü",
     ["apt-get", "install", "-y", "firmware-realtek"]),
    ("📡", "Broadcom Wi-Fi Adaptörü",
     "BCM serisi kablosuz sürücüsü",
     ["apt-get", "install", "-y", "firmware-b43-installer"]),
    ("🖨️", "Yazıcı Sürücüleri (CUPS)",
     "Evrensel yazıcı destek paketi",
     ["apt-get", "install", "-y", "cups", "printer-driver-all"]),
    ("🔊", "PipeWire Ses Sunucusu",
     "Modern gelişmiş ses sunucusu",
     ["apt-get", "install", "-y", "pipewire", "pipewire-pulse"]),
]


def build_driver_page(win) -> QWidget:
    page = QWidget()
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    content = QWidget()
    lay = QVBoxLayout(content)
    lay.setContentsMargins(36, 36, 36, 36)
    lay.setSpacing(14)

    lbl = QLabel("Sürücü Yöneticisi")
    lbl.setObjectName("LblTitle")
    lay.addWidget(lbl)
    sub = QLabel(
        "Donanımınız için uygun sürücüleri kurun. "
        "Polkit aracılığıyla güvenli root yetkisiyle çalıştırılır."
    )
    sub.setObjectName("LblSubtitle")
    sub.setWordWrap(True)
    lay.addWidget(sub)
    lay.addSpacing(8)

    for icon, name, desc, cmd in DRIVER_DATA:
        card = AppCard(icon, name, desc, "⬇  Kur", "btnAccent", cmd, use_pkexec=True)
        card.set_parent_window(win)
        lay.addWidget(card)

    lay.addStretch()
    scroll.setWidget(content)
    outer.addWidget(scroll)
    return page


# ── SEKME 4 : Sistem Bakımı ───────────────────────────────────────────────────
MAINTENANCE_DATA = [
    (
        "🧹", "Paket Önbelleğini Temizle",
        "apt önbelleğini boşaltarak disk alanı açar",
        ["apt-get", "clean"],
        "btnAccent", True,
    ),
    (
        "🗑️", "Gereksiz Bağımlılıkları Sil",
        "Artık kullanılmayan paketleri kaldırır",
        ["apt-get", "autoremove", "-y"],
        "btnWarning", True,
    ),
    (
        "📋", "Eski Sistem Günlüklerini Temizle",
        "3 günden eski journald günlüklerini siler",
        ["journalctl", "--vacuum-time=3d"],
        "btnWarning", True,
    ),
    (
        "🔄", "Sistem Paketlerini Güncelle",
        "Tüm kurulu paketleri en son sürüme günceller",
        ["apt-get", "update"],
        "btnAccent", True,
    ),
    (
        "🔧", "APT Veritabanını Onar",
        "Bozuk paket veritabanını yeniden yapılandırır",
        ["dpkg", "--configure", "-a"],
        "btnDanger", True,
    ),
    (
        "💾", "Takas Alanını Yenile (Swap)",
        "RAM kullanımını optimize etmek için swap yenilenir",
        ["bash", "-c", "swapoff -a && swapon -a"],
        "btnSuccess", True,
    ),
]


def build_maintenance_page(win) -> QWidget:
    page = QWidget()
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    content = QWidget()
    lay = QVBoxLayout(content)
    lay.setContentsMargins(36, 36, 36, 36)
    lay.setSpacing(14)

    lbl = QLabel("Sistem Bakımı")
    lbl.setObjectName("LblTitle")
    lay.addWidget(lbl)
    sub = QLabel("Sisteminizi hızlandırın, disk alanı açın, gereksiz dosyaları temizleyin.")
    sub.setObjectName("LblSubtitle")
    lay.addWidget(sub)
    lay.addSpacing(8)

    for icon, title, desc, cmd, style, pkexec in MAINTENANCE_DATA:
        card = BigActionCard(icon, title, desc, cmd, style, pkexec)
        card.set_parent_window(win)
        lay.addWidget(card)

    lay.addStretch()
    scroll.setWidget(content)
    outer.addWidget(scroll)
    return page


# ── SEKME 5 : Sorun Giderici ──────────────────────────────────────────────────
TROUBLESHOOT_DATA = [
    (
        "🌐", "Ağ Bağlantısını Sıfırla",
        "NetworkManager servisini yeniden başlatır",
        ["systemctl", "restart", "NetworkManager"],
        "btnAccent", True,
    ),
    (
        "🔊", "Ses Sunucusunu Onar",
        "PulseAudio/PipeWire oturumunu yeniler (root gerektirmez)",
        ["bash", "-c",
         "systemctl --user restart pipewire pipewire-pulse 2>/dev/null "
         "|| pulseaudio -k && pulseaudio --start"],
        "btnAccent", False,         # kullanıcı servisi — pkexec KULLANILMAZ
    ),
    (
        "📦", "Kilitli Paket Yöneticisini Kurtar",
        "dpkg kilit dosyalarını kaldırır",
        ["bash", "-c",
         "rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock "
         "/var/cache/apt/archives/lock && dpkg --configure -a"],
        "btnDanger", True,
    ),
    (
        "🖥️", "Ekran Çözünürlüğünü Sıfırla",
        "xrandr ile birincil ekranı otomatik moda alır (root gerektirmez)",
        ["xrandr", "--auto"],
        "btnWarning", False,
    ),
    (
        "📡", "DNS Önbelleğini Temizle",
        "systemd-resolved önbelleğini sıfırlar",
        ["systemd-resolve", "--flush-caches"],
        "btnSuccess", True,
    ),
    (
        "⏱️", "Yavaş Başlangıcı Analiz Et",
        "Açılışı yavaşlatan servisleri listeler (root gerektirmez)",
        ["bash", "-c", "systemd-analyze blame | head -20"],
        "btnSuccess", False,
    ),
    (
        "🔥", "Güvenlik Duvarını Etkinleştir",
        "UFW güvenlik duvarını etkinleştirir",
        ["ufw", "enable"],
        "btnWarning", True,
    ),
    (
        "🔓", "SSH Hizmetini Yeniden Başlat",
        "sshd servisini restart eder",
        ["systemctl", "restart", "ssh"],
        "btnAccent", True,
    ),
]


def build_troubleshoot_page(win) -> QWidget:
    page = QWidget()
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    content = QWidget()
    lay = QVBoxLayout(content)
    lay.setContentsMargins(36, 36, 36, 36)
    lay.setSpacing(14)

    lbl = QLabel("Sorun Giderici")
    lbl.setObjectName("LblTitle")
    lay.addWidget(lbl)
    sub = QLabel(
        "Sık karşılaşılan sistem sorunlarını hızla çözün. "
        "Root gerektiren işlemler Polkit ile güvenli şekilde yürütülür."
    )
    sub.setObjectName("LblSubtitle")
    sub.setWordWrap(True)
    lay.addWidget(sub)
    lay.addSpacing(8)

    grid = QGridLayout()
    grid.setSpacing(12)
    for i, (icon, title, desc, cmd, style, pkexec) in enumerate(TROUBLESHOOT_DATA):
        card = BigActionCard(icon, title, desc, cmd, style, pkexec)
        card.set_parent_window(win)
        grid.addWidget(card, i // 2, i % 2)
    lay.addLayout(grid)
    lay.addStretch()

    scroll.setWidget(content)
    outer.addWidget(scroll)
    return page


# ── SEKME 6 : Topluluk ────────────────────────────────────────────────────────
COMMUNITY_LINKS = [
    ("💬", "Pardus Forum",           "Toplulukla iletişim, sorular ve tartışmalar",       "https://forum.pardus.org.tr"),
    ("📖", "Pardus Wiki",            "Kapsamlı Türkçe belgeler ve kılavuzlar",             "https://wiki.pardus.org.tr"),
    ("🐛", "Hata / Talep Portalı",   "Yazılım isteklerinizi ve hatalarınızı bildirin",    "https://talep.pardus.org.tr"),
    ("📦", "Pardus Paket Deposu",    "Mevcut paketleri listeleyin ve arayın",             "https://paketler.pardus.org.tr"),
    ("💻", "Pardus GitHub",          "Açık kaynak projelerine katkıda bulunun",           "https://github.com/pardus"),
    ("📰", "Pardus Resmi Web Sitesi","İndirmeler, sürüm notları ve daha fazlası",         "https://www.pardus.org.tr"),
    ("🎓", "TÜBİTAK BİLGEM",        "Pardus'u geliştiren kurumun resmi sayfası",         "https://bilgem.tubitak.gov.tr"),
    ("🛡️", "USOM (Siber Güvenlik)", "Türkiye Ulusal Siber Olaylara Müdahale Merkezi",    "https://www.usom.gov.tr"),
]


def build_community_page(win) -> QWidget:
    page = QWidget()
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    content = QWidget()
    lay = QVBoxLayout(content)
    lay.setContentsMargins(36, 36, 36, 36)
    lay.setSpacing(20)

    lbl = QLabel("Topluluk")
    lbl.setObjectName("LblTitle")
    lay.addWidget(lbl)
    sub = QLabel("Pardus topluluğuna katılın, belgelerden faydalanın, geri bildirimde bulunun.")
    sub.setObjectName("LblSubtitle")
    lay.addWidget(sub)
    lay.addSpacing(8)

    grid = QGridLayout()
    grid.setSpacing(14)
    for i, (icon, name, desc, url) in enumerate(COMMUNITY_LINKS):
        card = QFrame()
        card.setObjectName("Card")
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(18, 16, 18, 16)
        c_lay.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(8)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size:20px;")
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("font-size:13px; font-weight:700;")
        top.addWidget(icon_lbl)
        top.addWidget(name_lbl, 1)

        desc_lbl = QLabel(desc)
        desc_lbl.setObjectName("LblMuted")
        desc_lbl.setWordWrap(True)

        btn = QPushButton("🌍  Aç →")
        btn.setObjectName("btnLink")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))

        c_lay.addLayout(top)
        c_lay.addWidget(desc_lbl)
        c_lay.addWidget(btn)
        grid.addWidget(card, i // 2, i % 2)

    lay.addLayout(grid)
    lay.addStretch()
    scroll.setWidget(content)
    outer.addWidget(scroll)
    return page


# ==============================================================================
# 8. SOL MENÜ LOGO BİLEŞENİ
# ==============================================================================

class SidebarLogo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 10)
        lay.setSpacing(2)

        row = QHBoxLayout()
        row.setSpacing(10)

        # ── Pardus logosu (sidebar) ────────────────────────────────────
        _LOGO_PATHS_S = [
            "/usr/share/icons/desktop-base/128x128/emblems/emblem-pardus.png",
            "/usr/share/icons/hicolor/128x128/emblems/emblem-pardus.png",
        ]
        em = QLabel()
        em.setFixedSize(38, 38)
        em.setAlignment(Qt.AlignCenter)
        em.setStyleSheet("background:transparent;")
        _logo_px_s = QPixmap()
        for _p in _LOGO_PATHS_S:
            if os.path.exists(_p):
                _logo_px_s = QPixmap(_p)
                break
        if not _logo_px_s.isNull():
            em.setPixmap(_logo_px_s.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            em.setText("🐧")
            em.setStyleSheet("font-size:30px; background:transparent;")

        t_col = QVBoxLayout()
        t_col.setSpacing(0)
        name_lbl = QLabel("Pardus Hello")
        name_lbl.setStyleSheet("color:#89b4fa; font-size:15px; font-weight:700; background:transparent;")
        ver_lbl = QLabel("Sistem Kontrol Merkezi  v2.0")
        ver_lbl.setStyleSheet("color:#585b70; font-size:10px; background:transparent;")
        t_col.addWidget(name_lbl)
        t_col.addWidget(ver_lbl)

        row.addWidget(em)
        row.addLayout(t_col, 1)
        lay.addLayout(row)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background:#1e1e2e; max-height:1px; border:none;")
        div.setFixedHeight(1)
        lay.addWidget(div)


# ==============================================================================
# 9. ANA PENCERE
# ==============================================================================

MENU_ITEMS = [
    "🏠  Ana Sayfa",
    "🖥️  Yazılım Merkezi",
    "⚙️  Sürücü Yöneticisi",
    "🛠️  Sistem Bakımı",
    "🔍  Sorun Giderici",
    "🌐  Topluluk",
]


class PardusHello(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pardus Hello — Sistem Kontrol Merkezi")
        self.setMinimumSize(1060, 680)
        self.resize(1240, 760)
        # Pardus logosu — görev çubuğu ikonu
        self.setWindowIcon(_pardus_icon())
        self._dark_mode = True     # varsayılan: karanlık tema
        self._build_ui()
        self._apply_theme()

    # ── Arayüz inşası ─────────────────────────────────────────────────────
    def _build_ui(self):
        # Central widget — temel arka plan rengi zorunlu
        central = QWidget()
        central.setObjectName("CentralBg")
        central.setAutoFillBackground(True)
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Sol panel ──────────────────────────────────────────────────────
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(270)
        self.sidebar.setObjectName("SideBar")
        self.sidebar.setAutoFillBackground(True)   # ← arka plan sızmasını önler

        side_lay = QVBoxLayout(self.sidebar)
        side_lay.setContentsMargins(0, 0, 0, 0)
        side_lay.setSpacing(0)

        side_lay.addWidget(SidebarLogo())

        self.menu = QListWidget()
        self.menu.setFocusPolicy(Qt.NoFocus)
        self.menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for label in MENU_ITEMS:
            item = QListWidgetItem(label)
            item.setSizeHint(QSize(248, 46))
            self.menu.addItem(item)
        self.menu.currentRowChanged.connect(self._on_nav)
        side_lay.addWidget(self.menu, 1)

        # ── Tema değiştir butonu (sol alt köşe) ───────────────────────────
        self.btn_theme = QPushButton("☀️  Aydınlık Mod")
        self.btn_theme.setObjectName("btnTheme")
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.setFixedHeight(36)
        self.btn_theme.clicked.connect(self._toggle_theme)

        self.footer_wrap = QWidget()
        self.footer_wrap.setObjectName("SideBar")
        self.footer_wrap.setAutoFillBackground(True)
        fw_lay = QVBoxLayout(self.footer_wrap)
        fw_lay.setContentsMargins(10, 6, 10, 10)
        fw_lay.setSpacing(6)
        fw_lay.addWidget(self.btn_theme)
        self.footer_lbl = QLabel("TÜBİTAK BİLGEM  ·  Pardus")
        self.footer_lbl.setAlignment(Qt.AlignCenter)
        self.footer_lbl.setObjectName("FooterLbl")
        fw_lay.addWidget(self.footer_lbl)
        side_lay.addWidget(self.footer_wrap)

        main_lay.addWidget(self.sidebar)

        # ── Sağ içerik ─────────────────────────────────────────────────────
        self.right = QWidget()
        self.right.setObjectName("RightPanel")
        self.right.setAutoFillBackground(True)     # ← arka plan sızmasını önler
        r_lay = QVBoxLayout(self.right)
        r_lay.setContentsMargins(0, 0, 0, 0)
        r_lay.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setObjectName("MainStack")
        self.stack.setAutoFillBackground(True)
        self.stack.addWidget(build_home_page(self))          # 0
        self.stack.addWidget(build_software_page(self))      # 1
        self.stack.addWidget(build_driver_page(self))        # 2
        self.stack.addWidget(build_maintenance_page(self))   # 3
        self.stack.addWidget(build_troubleshoot_page(self))  # 4
        self.stack.addWidget(build_community_page(self))     # 5

        r_lay.addWidget(self.stack, 1)
        main_lay.addWidget(self.right, 1)

        self.menu.setCurrentRow(0)

    # ── Navigasyon ────────────────────────────────────────────────────────
    def _on_nav(self, index: int):
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)

    def nav_to(self, index: int):
        self.menu.setCurrentRow(index)

    # ── Tema yönetimi ─────────────────────────────────────────────────────
    def _toggle_theme(self):
        self._dark_mode = not self._dark_mode
        self._apply_theme()

    def _apply_theme(self):
        app = QApplication.instance()
        if self._dark_mode:
            app.setStyleSheet(qss_dark())
            self.btn_theme.setText("☀️  Aydınlık Mod")
            # Inline stil — QSS'in ulaşamadığı native widget'lar için
            _sb  = "background-color:#11111b;"
            _rp  = "background-color:#1e1e2e;"
            _fl  = "color:#313244; font-size:10px;"
        else:
            app.setStyleSheet(qss_light())
            self.btn_theme.setText("🌙  Karanlık Mod")
            _sb  = "background-color:#e8e8ed;"
            _rp  = "background-color:#f0f0f5;"
            _fl  = "color:#aeaeb2; font-size:10px;"

        self.sidebar.setStyleSheet(f"QWidget#SideBar {{ {_sb} }}")
        self.footer_wrap.setStyleSheet(f"QWidget#SideBar {{ {_sb} }}")
        self.right.setStyleSheet(f"QWidget#RightPanel {{ {_rp} }}")
        self.stack.setStyleSheet(f"QStackedWidget#MainStack {{ {_rp} }}")
        self.footer_lbl.setStyleSheet(_fl)


# ==============================================================================
# 10. GİRİŞ NOKTASI
# ==============================================================================

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("PardusHello")
    app.setApplicationDisplayName("Pardus Hello")
    app.setOrganizationName("TÜBİTAK BİLGEM")
    app.setOrganizationDomain("pardus.org.tr")
    app.setWindowIcon(_pardus_icon())

    win = PardusHello()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
