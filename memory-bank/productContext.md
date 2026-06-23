# DualCoreX - Ürün Bağlamı (Product Context)

## Neden Bu Proje Var? (Why It Exists)
Bilişim dünyasında kullanıcılar sürekli olarak **Performans** ve **Güvenlik** arasında bir seçim yapmaya zorlanırlar. 
- Yüksek performans gerektiren işler (geliştirme araçları, oyunlar, test ortamları) genellikle sistemi dış tehditlere daha açık hale getirir.
- Maksimum güvenlik gerektiren işler (bankacılık işlemleri, kurumsal yönetim, hassas veri işleme) ise katı kısıtlamalar ve ek yükler getirerek performansı düşürür.

**DualCoreX**, bu iki dünyayı birbirinden izole ederek aynı fiziksel makinede hem maksimum performansı hem de maksimum güvenliği bir arada sunmayı amaçlar.

## Çözdüğü Sorunlar (Problems It Solves)
1. **Güvenlik İhlallerinin Yayılması:** Günlük kullanımda veya performans gerektiren işlerde bulaşabilecek zararlı yazılımların, hassas kurumsal bilgilere veya kişisel verilere ulaşmasını engeller.
2. **Performans Kayıpları:** Güvenlik yazılımlarının veya kısıtlamalarının (örn. ağır antivirüsler, kısıtlayıcı firewall'lar) performansa ihtiyaç duyulan işleri yavaşlatmasının önüne geçer.
3. **Kullanım Zorluğu:** Geleneksel çift önyükleme (dual-boot) sistemlerindeki yavaş geçiş ve kopuk çalışma deneyimini optimize eder.

## Nasıl Çalışır? (How It Works)
Sistem iki ana katmandan oluşur:
1. **Güvenli Katman (Secure Domain):** Pardus tabanlı, minimum servis içeren, sadece güvenli ve hassas işlemler için yapılandırılmış, dış dünyayla kontrollü iletişim kuran katman.
2. **Performans Katmanı (Performance Domain):** Geliştirme, günlük kullanım ve kaynak tüketen işlemler için ayrılmış, esnek yapılandırılmış katman.

Bu iki katman arasındaki geçişler ve veri akışları önceden tanımlanmış güvenlik politikaları ve izole köprüler aracılığıyla gerçekleştirilir.

## Kullanıcı Deneyimi Hedefleri (UX Goals)
- **Hızlı Geçiş:** İki ortam arasında minimum kesintiyle geçiş yapabilmek.
- **Net Durum Göstergesi:** Kullanıcının o anda hangi ortamda (Güvenli vs. Performans) çalıştığını her an kolayca anlayabilmesi.
- **Güvenli Paylaşım:** Ortamlar arasında dosya veya veri aktarırken kullanıcının güvenliği tehlikeye atmayacak kadar basit ama denetlenebilir bir akış sunulması.
