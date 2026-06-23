# DualCoreX - Aktif Bağlam (Active Context)

## Mevcut Odak Noktası (Current Work Focus)
- **Pardus Kernel Manager Tamamlandı:** `2-Pardus_Kernel_Manager` bileşeni, şık Dark/Light QSS arayüzü, süzülmüş çekirdek tabloları, Pardus 25 temalı Pars logo/ikon tasarımı ve yetkilendirme simülasyonu ile tamamlandı. Sonraki odak noktası `3-Pardus_KDE_Surumu`.

## Son Değişiklikler (Recent Changes)
- **Çekirdek Yöneticisi Geliştirildi:** `2-Pardus_Kernel_Manager` sıfırdan yazılarak tamamlandı.
- **Yerleşim ve Ölçeklenme Düzeltmeleri:** QTableWidget satır yükseklikleri `38px` değerine sabitlendi, sol dikey dizin başlıkları gizlendi ve hücre içi butonlar dikey kırpılmaya uğramadan `90x26px` boyutlarında düzgün ölçeklendi. Sekme genişlikleri `min-width: 180px;` ile sabitlendi.
- **Pardus 25 Temalı Pars İkonu:** `generate_image` ile tasarlanan Pardus 25 temalı modern Anadolu Leoparı (Pars) logosu `icon.png` olarak kaydedildi; pencere ikonu ve banner logosu olarak entegre edildi.
- **Simülasyon Entegrasyonu:** Polkit şifre ekranı ve paket yükleme ilerleme barı simüle edildi.

## Sonraki Adımlar (Next Steps)
1. **`3-Pardus_KDE_Surumu`:** KDE Plasma entegrasyonu ve Pardus teması ayarlama aracı.

## Aktif Kararlar ve Değerlendirmeler
- **Layout Ölçeklemesi:** Hücre içi butonların bozulmasını engellemek için doğrudan buton eklemek yerine, layoutlu bir `QWidget` wrapper (kapsayıcı) kullanıldı. Bu sayede buton boyutu ve hizalaması QSS/Table kısıtlamalarından bağımsız olarak korundu.
- **Pardus 25 Markalama:** PoC tasarımının jüride maksimum etkiyi bırakması adına simge tasarımlarında Pardus 25 kurumsal kimliğine sadık kalındı.
