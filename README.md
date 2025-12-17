# Egasus 🐎

Egasus, Python ve ADB (Android Debug Bridge) altyapısını kullanarak geliştirilmiş, terminal tabanlı gelişmiş bir Android cihaz yönetim ve otomasyon aracıdır. Karmaşık ADB komutlarıyla uğraşmak yerine, kullanıcı dostu menüler üzerinden cihazınızı yönetmenizi sağlar.

## 🚀 Özellikler

Egasus, cihaz yönetimi için hepsi bir arada (All-in-One) çözümler sunar:

* **📱 Cihaz Bilgileri:** Model, Android sürümü, pil durumu, RAM, depolama ve çözünürlük bilgilerini anlık görüntüleme.
* **🎥 Ekran Araçları:**
    * Ekran kaydı alma (Süre sınırlı/sınırsız).
    * Anlık ekran görüntüsü (Screenshot) alma.
    * Ekran yansıtma (Scrcpy entegrasyonu).
* **📂 Dosya Yönetimi:**
    * Bilgisayardan telefona dosya gönderme (Push).
    * Telefondan bilgisayara dosya çekme (Pull).
    * Terminal üzerinden dosya gezgini.
* **📦 APK Yönetimi:**
    * Yüklü uygulamaları listeleme.
    * Tekli veya toplu APK yükleme/kaldırma.
    * Yüklü uygulamaları APK olarak yedekleme (Extract).
* **📡 Bağlantı:** Wi-Fi üzerinden kablosuz ADB bağlantısı kurma.

## 🛠️ Kurulum

Proje dosyalarını bilgisayarınıza indirin ve gerekli kütüphaneleri kurun.

1.  **Repoyu Klonlayın:**
    ```bash
    git clone https://github.com/egnake/egasus.git
    cd egasus
    ```

2.  **Gereksinimleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Gereklilikler:**
    * Bilgisayarınızda **ADB** (Android Debug Bridge) kurulu ve PATH'e ekli olmalıdır.
    * Ekran yansıtma özelliği için **scrcpy** kurulu olmalıdır.

## ▶️ Kullanım

Cihazınızı USB ile bağlayın (veya aynı ağdaysanız Wi-Fi menüsünü kullanın) ve aracı başlatın:

```bash
python egasus.py
```
## 🤝 Contributing
```text
Bu projeyi geliştirmek için katkılarınızı bekliyoruz! Hata düzeltmeleri, yeni özellikler veya dokümantasyon iyileştirmeleri yapabilirsiniz.

Bu repoyu Fork'layın.

Yeni bir özellik dalı (branch) oluşturun: git checkout -b feature/YeniOzellik

Değişikliklerinizi yapın ve commit'leyin: git commit -m 'feat: Yeni özellik eklendi'

Branch'inizi push'layın: git push origin feature/YeniOzellik

GitHub üzerinden bir Pull Request (PR) oluşturun.
```
## 👤 Author
```text
[egnake] (https://github.com/egnake) - Geliştirici & Tasarımcı
```
## 📄 License
```text
Bu proje MIT Lisansı ile lisanslanmıştır.
```
