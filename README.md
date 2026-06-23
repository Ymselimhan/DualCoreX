# DualCoreX - Pardus Performans, Güvenlik ve Sistem Yönetim Mimarisi

**DualCoreX**, Debian tabanlı milli işletim sistemimiz **Pardus** üzerinde yüksek güvenlik izolasyonu, veri bütünlüğü koruması ve gelişmiş sistem performansı sunmak amacıyla geliştirilmiş bütünleşik bir sistem yönetim ve yapılandırma mimarisidir. 

Bu depo, Teknofest jürisine sunulmak üzere hazırlanmış kavram kanıtı (PoC) araçlarını, özelleştirilmiş sistem politikalarını ve gelecek hedeflere yönelik planlanan modül yapılarını içerir.

---

## 🚀 Proje Mimarisi ve Bileşenleri

Sistem, son kullanıcının ve sistem yöneticilerinin Pardus'u en verimli şekilde kullanabilmesi için modüler bir yapıda tasarlanmıştır:

### 1. Aktif ve Çalışan Araçlar (Implemented Modules)

*   **`1-BTRFS_Snapshot_Araci` (BTRFS Anlık Görüntü Yöneticisi):**
    *   Sistem bütünlüğünü korumak adına BTRFS dosya sistemi alt birimlerinin (subvolumes) yedeklerini (snapshot) alır.
    *   Olası bir sistem çökmesi veya kararsızlık durumunda sistemi güvenli bir yedek noktasına geri döndürmeyi (rollback) sağlar.
    *   *Çalıştırma:* `python3 "1-BTRFS_Snapshot_Araci/main.py"`

*   **`2-Pardus_Kernel_Manager` (Pardus Çekirdek Yöneticisi):**
    *   Sistemin performans ve donanım uyumluluğunu artırmak amacıyla farklı Linux çekirdeklerinin (standart, low-latency/realtime, LTS, liquorix vb.) kurulmasını, kaldırılmasını ve etkinleştirilmesini sağlar.
    *   Sistem yetkilendirme (Polkit/sudo) ve paket kurulum süreçlerini görsel olarak simüle eder.
    *   *Çalıştırma:* `python3 "2-Pardus_Kernel_Manager/main.py"`

*   **`5-Pardus Hello` (Pardus Karşılama ve Hızlı Yapılandırma Portalı):**
    *   CachyOS Hello tasarım dili ve estetiğini referans alan modern, koyu tema ve aydınlık tema destekli karşılama ekranıdır.
    *   Sistemin donanım bilgilerini (OS, CPU, RAM, Kernel) otomatik okur ve sunar.
    *   Canlı sistem kurulumu (Calamares) başlatılmasını, sistem servislerinin (Bluetooth, AppArmor, DNSCrypt, Systemd-OOMD) yapılandırılmasını ve paket depo bakımlarının yapılmasını simüle eder.
    *   Sık kullanılan popüler uygulamaları (Chrome, Firefox, VS Code, Docker, Steam, Spotify vb.) tek tıkla kurmayı sağlar.
    *   *Çalıştırma:* `python3 "5-Pardus Hello/main.py"`

---

### 2. Gelecek Yol Haritası ve Planlanan Modüller (Planned Extensions)

*   **`3-Pardus_KDE_Surumu` (Masaüstü Özelleştirme Şablonları):**
    *   Pardus KDE masaüstü ortamı için DualCoreX performans ve görsel standartlarına uygun ön tanımlı widget ve görünüm konfigürasyonları.
*   **`4-Calamares_Entegrasyonu` (Calamares Canlı Kurulum Yapılandırması):**
    *   Canlı sistem üzerinden diski BTRFS formatında otomatik bölümleyip DualCoreX koruma katmanlarıyla kurmayı hedefleyen kurulum betikleri.
*   **`6-AppImage_Baslaticisi` (Masaüstü Entegrasyon Servisi):**
    *   Sistem genelinde AppImage uzantılı paketlerin masaüstü menüsüne (.desktop) otomatik kaydedilmesini ve çalıştırılmasını kolaylaştıran arka plan servisi.
*   **`7-Pardus_Flatpak_Destegi` (Flatpak Entegrasyonu ve Paket Depo Yöneticisi):**
    *   Flatpak/Flathub desteğinin ve izin yöneticisinin Pardus Hello içerisine entegre edilmesi planı.
*   **`8-Akilli_Surucu_Yoneticisi` (Otomatik Sürücü Yükleme Sihirbazı):**
    *   Donanım taraması (LSPCI/LSUSB) yaparak eksik ekran kartı (Nvidia/AMD), ağ kartı veya çevre birimi sürücülerini tespit edip kuran akıllı sihirbaz.
*   **`9-Sistem_Bakim_Asistani` (Disk Temizleme ve Performans Optimizasyonu):**
    *   Gereksiz sistem günlüklerini (logs), geçici dosyaları (/tmp) ve artık paketleri temizleyerek sistem disk sağlığını koruyan araç.
*   **`10-Tek_Tikla_Sorun_Giderici` (Otomatik Hata Onarım Sihirbazı):**
    *   Kırık paket bağımlılıkları, ses aygıtı sorunları, ağ bağlantısı kopmaları gibi yaygın kullanıcı hatalarını analiz edip onaran akıllı problem çözücü.

---

## 🛠️ Sistem Gereksinimleri ve Kurulum

Araçları yerel ortamınızda test etmek için sisteminizde Python 3 ve PyQt5 kütüphanelerinin bulunması yeterlidir.

### Bağımlılıkların Yüklenmesi
Debian/Pardus tabanlı sisteminizde gerekli kütüphaneleri yüklemek için terminalde aşağıdaki komutu çalıştırabilirsiniz:
```bash
sudo apt update
sudo apt install python3 python3-pyqt5 python3-pip
```

---

## 💻 Çalıştırma Talimatları

Dilediğiniz aktif aracı çalıştırmak için ana dizindeyken terminalden ilgili python betiğini tetikleyebilirsiniz:

```bash
# 1. BTRFS Snapshot Aracını Çalıştır
python3 "1-BTRFS_Snapshot_Araci/main.py"

# 2. Pardus Çekirdek Yöneticisini Çalıştır
python3 "2-Pardus_Kernel_Manager/main.py"

# 3. Pardus Hello Karşılama Ekranını Çalıştır
python3 "5-Pardus Hello/main.py"
```

*Not: Yetki (sudo) gerektiren işlemler kavram kanıtı (PoC) amacıyla güvenli diyalog kutularıyla simüle edilmiş olup, sisteminizde herhangi bir yetkisiz dosya değişikliği veya paket kurulumu yapmamaktadır.*

---

## 📝 Lisans ve Katkı
Bu proje Teknofest Havacılık, Uzay ve Teknoloji Festivali kapsamında geliştirilen bir kavram kanıtı çalışmasıdır. Açık kaynak kodlu olup, geliştirilmeye açıktır.
