# PasaParola Oyunu (Python & PyQt5)

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)

Popüler TV yarışması **Pasaparola**'nın, Python ve PyQt5 kullanılarak geliştirilmiş, tamamen özelleştirilebilir masaüstü uygulama versiyonudur. 

Bu uygulama sayesinde eğlenceli bilgi yarışmaları oluşturabilir ya da oluşturulmuş olanları oynayabilirsiniz.

## 📸 Ekran Görüntüleri
### Ana menü
<img width="1280" height="720" alt="image" src="https://github.com/user-attachments/assets/d8159321-3484-49e9-9036-26418c6ee47b" />

### Oynanış
<img width="1277" height="720" alt="image" src="https://github.com/user-attachments/assets/328a567d-e820-47fe-8b3f-01ad8989f9e0" />
<img width="1280" height="720" alt="image" src="https://github.com/user-attachments/assets/f8d8677d-3e15-467c-b2ac-7aaf8a53b4b8" />
<img width="1280" height="720" alt="image" src="https://github.com/user-attachments/assets/667f77ef-076b-4227-8db5-b9cb35b70895" />

### Skor Tablosu
<img width="904" height="647" alt="image" src="https://github.com/user-attachments/assets/fb318e0a-046a-4e26-a762-7b8caac1eef0" />



## ✨ Özellikler

* Tam ekran arayüz, koyu tema ve dairesel tasarım.

* **İki Farklı Oyun Modu:**
    1. **Normal Oyun:** Veritabanından (`sorular.json`) sırayla veya seçerek anında oynanabilir setler
    2. **Özel Oyun:** Kendi hazırladığınız dilediğiniz harf sayısında ve dizilişinde `.txt` dosyalarıyla oynama imkanı → _format 'ozel_oyun.txt' dosyasında belirtilen şekilde olmalıdır_

* **Oyun Mantığı:**
    * "Pas" geçilen sorulara tur sonunda tekrar dönülür.
    * Renk kodları: Doğru (Yeşil), Yanlış (Kırmızı), Pas (Sarı).

* **Dinamik Puanlama Sistemi:**
    * Doğru: **+25 Puan**
    * Yanlış: **-10 Puan**
    * Artan Süre: **Saniye başına +1 Puan**
    
* **Detaylı Skor Tablosu:** İsim, puan, doğru/yanlış sayıları ve kalan süre istatistiklerini kaydeder.
  
* **Fon Müziği:** İstediğiniz bir `music.mp3` dosyasını uygulama ile aynı yola taşıyıp arka plan müziğinin kefini çıkarabilirsiniz.
