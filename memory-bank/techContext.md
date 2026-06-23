# DualCoreX - Teknik Bağlam (Tech Context)

## Kullanılan Teknolojiler (Technologies Used)

| Teknoloji | Kullanım Amacı |
|---|---|
| Python 3.13 | Ana geliştirme dili |
| PyQt5 5.15.11 | GUI kütüphanesi |
| Qt Style Sheets (QSS) | Koyu/Aydınlık tema sistemi |
| Polkit / `pkexec` | Grafiksel yetki yükseltme (X11 + Wayland) |
| Systemd Timers | GUI bağımsız 2 saatlik otomatik yedekleme |
| `btrfs-progs` | BTRFS disk işlemleri |
| `xhost` | X11/Wayland root GUI yetkilendirme köprüsü |
| `.desktop` + XDG | Uygulama menüsü entegrasyonu |
| GRUB2 / EFI | Önyükleme yönetimi |
| LUKS / `cryptsetup` | Disk şifreleme |

## Geliştirme Ortamı

- **İşletim Sistemi:** Pardus 25 (Debian tabanlı, VirtualBox VM)
- **Python:** `/usr/bin/python3` (3.13)
- **PyQt5:** `5.15.11+dfsg-2` (APT ile kuruldu)
- **Git:** Remote `origin` → `github.com:Ymselimhan/DualCoreX.git` (main branch)
- **Çalışma Dizini:** `/home/yms/Masaüstü/pardus/`

## Kurulu Sistem Dosyaları

| Dosya | Konum |
|---|---|
| Uygulama ikonu | `~/.local/share/icons/btrfs-snapshot-manager.png` |
| Desktop kısayolu (menü) | `~/.local/share/applications/btrfs-snapshot-manager.desktop` |
| Desktop kısayolu (masaüstü) | `~/Masaüstü/btrfs-snapshot-manager.desktop` |
| Systemd Servis | `/etc/systemd/system/btrfs-autosnap.service` |
| Systemd Timer | `/etc/systemd/system/btrfs-autosnap.timer` |

## Teknik Kısıtlamalar

- **Wayland root GUI:** Root uygulamalar `WAYLAND_DISPLAY`, `XDG_RUNTIME_DIR`, `XAUTHORITY` ve `xhost +local:` kombinasyonu ile Wayland oturumunda çalıştırılabilir.
- **BTRFS zorunluluğu:** Tüm disk işlemleri yalnızca `/` dizini BTRFS ise çalışır.
- **Systemd root servisi:** `btrfs-autosnap.service` root yetkisiyle `/etc/systemd/system/` altında çalışır.

## Bağımlılıklar

```
python3-pyqt5    >= 5.15
btrfs-progs      (yüklü)
policykit-1      (yüklü - pkexec için)
x11-xserver-utils (xhost için)
systemd          (yüklü)
```
