# DualCoreX - İlerleme Durumu (Progress)

## Mevcut Durum (Current Status)
**`1-BTRFS_Snapshot_Araci` modülü tamamlandı.** Tüm özellikler geliştirilmiş, hatalar giderilmiş ve sisteme kurulmuştur.

## Çalışan Özellikler (What Works)

### Hafıza Bankası (Memory Bank)
- Temel 6 dokümantasyon dosyası güncel.

### 1-BTRFS_Snapshot_Araci ✅ TAMAMLANDI
| Özellik | Durum |
|---|---|
| BTRFS sistem tespiti (`findmnt`) | ✅ Çalışıyor |
| Snapshot listeleme | ✅ Çalışıyor |
| Manuel yedek alma (GUI) | ✅ Çalışıyor |
| Yedek silme (güvenlik kontrolüyle) | ✅ Çalışıyor |
| Geri yükleme (`set-default` + reboot) | ✅ Çalışıyor |
| X11 Polkit yetki yükseltme | ✅ Çalışıyor |
| Wayland Polkit yetki yükseltme | ✅ Çalışıyor |
| 2 saatlik otomatik yedek (Systemd Timer) | ✅ `active (waiting)` |
| CLI modu (`btrfs_helper.py --auto`) | ✅ Çalışıyor |
| Koyu/Aydınlık tema geçişi | ✅ Çalışıyor |
| Uygulama ikonu (`icon.png`) | ✅ Kurulu |
| Masaüstü kısayolu (.desktop) | ✅ Kurulu |
| Uygulama menüsü kaydı | ✅ Kurulu |

## Yapılacaklar (What's Left to Build)
- [x] **2-Pardus_Kernel_Manager:** Çekirdek listeleme, yükleme/kaldırma ve QSS arayüzü tamamlandı.
- [ ] **3-Pardus_KDE_Surumu:** KDE Plasma entegrasyonu ve Pardus teması aracı.
- [ ] Ağ izolasyon kuralları (`nftables`).
- [ ] Güvenli katman köprü mekanizması (DualCoreX ana mimari).

## Bilinen Sorunlar (Known Issues)
- `QStandardPaths: runtime directory '/run/user/1000' is not owned by UID 0` uyarısı: Root ile çalışırken `/run/user/` dizininin UID uyuşmazlığından kaynaklanan zararsız bir uyarı mesajı. İşlevselliği etkilemiyor.

## Kararların Gelişimi (Evolution of Decisions)
- **2026-06-23 (Başlangıç):** Memory Bank kuruldu.
- **2026-06-23:** `1-BTRFS_Snapshot_Araci` temel işlevleri tamamlandı.
- **2026-06-23:** X11/Wayland çift ekran sunucusu desteği ve Systemd Timer eklendi.
- **2026-06-23:** Koyu/Aydınlık tema, uygulama ikonu ve .desktop dosyası eklendi. `toggle_theme` hata düzeltmesi yapıldı.
- **2026-06-23:** IDE üzerindeki sahte/geçersiz CSS hata bildirimlerini (gradient syntax vb.) temizlemek için `style.css` dosyası `style.qss` olarak yeniden adlandırıldı, `main.py` güncellendi ve eski CSS silindi.
- **2026-06-23:** `2-Pardus_Kernel_Manager` bileşeni; şık Dark/Light QSS arayüzü, süzülmüş çekirdek tabloları, Pardus 25 temalı Pars logo/ikon tasarımı ve yetkilendirme simülasyonu ile tamamlandı.
