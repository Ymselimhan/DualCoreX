# DualCoreX - İlerleme Durumu (Progress)

## Mevcut Durum (Current Status)
**`1-BTRFS_Snapshot_Araci` ve `5-Pardus Hello` modülleri tamamlandı.** İlgili araçlar ekran görüntüleriyle tam uyumlu, kararlı ve görsel olarak zenginleştirilmiş halde teslim edilmiştir.

## Çalışan Özellikler (What Works)

### Hafıza Bankası (Memory Bank)
- Temel 6 dokümantasyon dosyası güncel.

### 1-BTRFS_Snapshot_Araci ✅ TAMAMLANDI
- BTRFS sistem tespiti, yedek alma, silme, geri yükleme ve otomatik timer entegrasyonu tamamlandı.

### 2-Pardus_Kernel_Manager ✅ TAMAMLANDI
- Çekirdek listeleme, yükleme/kaldırma ve QSS arayüzü tamamlandı.

### 5-Pardus Hello ✅ TAMAMLANDI
| Özellik | Durum |
|---|---|
| CachyOS Hello grid arayüz tasarımı | ✅ Çalışıyor |
| Özel bütünleşik başlık çubuğu (`CustomTitleBar`) | ✅ Sürükleme ve pencere kontrolleri aktif |
| Gelişmiş koyu/aydınlık tema şablonları | ✅ Tam entegre |
| Kaydırılabilir sayfalar (`QScrollArea`) | ✅ Sığma/taşma sorunları yok |
| Doğru Polkit komut simülasyonları | ✅ Aktif (systemctl, rm vb.) |
| Gelişmiş Paket Kurucu Penceresi (`QTreeWidget`) | ✅ Arama, kategoriler ve yükle/kaldır eylemleri aktif |
| Özel resimsiz Toggle Switch | ✅ Tam entegre |

## Yapılacaklar (What's Left to Build)
- [ ] **3-Pardus_KDE_Surumu:** KDE Plasma entegrasyonu ve Pardus teması aracı.
- [ ] Ağ izolasyon kuralları (`nftables`).
- [ ] Güvenli katman köprü mekanizması (DualCoreX ana mimari).

## Bilinen Sorunlar (Known Issues)
- Yok.

## Kararların Gelişimi (Evolution of Decisions)
- **2026-06-23 (Başlangıç):** Mimari kararlar alındı ve `1-BTRFS_Snapshot_Araci` tamamlandı.
- **2026-06-23:** `2-Pardus_Kernel_Manager` bileşeni tamamlandı.
- **2026-06-24:** `5-Pardus Hello` modülü ekran görüntülerindeki CachyOS Hello düzenine ve temasına göre yeniden yazıldı. Arayüzün küçük ekranlarda sıkışmasını engellemek için kaydırma alanları (`QScrollArea`) kullanıldı.
- **2026-06-24:** İptal butonlarında signal-slot kilitlenmelerini engellemek için lambdalarda `checkbox` nesnesi parametre olarak geçildi. Yetki diyaloglarında sahte paket kurulum komutları yerine gerçek komutların gösterilmesi sağlandı. Altbilgideki (footer) sosyal medya ikonları temizlendi.

