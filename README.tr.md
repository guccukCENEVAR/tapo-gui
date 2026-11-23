# Tapo Işık Kontrol

> 🇬🇧 For English documentation: [README.md](README.md)

Tapo akıllı ışıkları (L510, L520, L530, L535, L610, L630, L900/L920/L930 şerit vb.) **Windows 11** ve **Linux** üzerinden kontrol etmek için masaüstü arayüzü.

Tüm komutlar doğrudan **yerel ağ (LAN)** üzerinden gönderilir; buluta gitmez.

---

## Özellikler

- **Yerel ağ kontrolü:** [`tapo`](https://github.com/mihai-dinculescu/tapo) kütüphanesi sayesinde yeni Tapo yazılımlarının TPAP şifrelemesini destekler.
- **Canlı ışık kutucukları:** Işık açıkken kutucuk, ışığın yandığı renkte parlar ve alttan yukarı parlaklık yüzdesi kadar dolar.
- **Hızlı fare ve sürükleme kontrolü:**
  - **Basılı tutup yukarı/aşağı sürükleyerek** (ya da fare tekerleğiyle) parlaklığı doğrudan ayarlayın; en alta çekmek ışığı kapatır.
  - **Sağ tıklama** ile hızlı menüyü açın: aç/kapat, parlaklık, hazır ve kayıtlı renkler, beyaz tonlar, yeniden adlandırma.
  - **Tıklama** ile tam ayar sayfasını açın: ton, doygunluk, beyaz sıcaklık (K), renk seçici ve klavyeden doğrudan sayısal giriş.
- **Özel renkler:** **+** düğmesiyle kendi renklerinizi kaydedin; sağ tıklayıp yeniden adlandırın veya silin.
- **Yerel yeniden adlandırma:** Işıklara yalnızca bu uygulamada görünecek özel adlar verin (Tapo uygulamasındaki ad değişmez).
- **Türkçe / İngilizce dil desteği:** Sağ üstteki **EN / TR** düğmesiyle yeniden başlatmadan anında dil değiştirin.
- **Çoklu platform:** Windows 11 ve Linux için bağımsız derleme desteği.

---

## Kurulum ve Derleme

### Windows 11

[Python 3.10+](https://www.python.org/downloads/) gerektirir.

**Bağımsız uygulama olarak derleme (önerilen):**

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Bu betik `.venv-win` ortamını kurar, `assets\tapo-gui.ico` ikonunu üretir ve `dist\tapo-gui\tapo-gui.exe` dosyasını oluşturur.

Tek bir `.exe` (`--onefile`) olarak derlemek için:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1 -OneFile
```

**Kaynak koddan çalıştırma:**

```powershell
python -m venv .venv-win
.\.venv-win\Scripts\pip install -r requirements.txt
.\.venv-win\Scripts\python tapo_gui.py
```

### Linux

**Bağımsız uygulama olarak:**

```sh
./build.sh           # dist/tapo-gui/ altında programı üretir
./install-app.sh     # ~/.local altına kurar, uygulama menüsüne ekler
```

Kaldırmak için:

```sh
./install-app.sh --uninstall
```

**Kaynak koddan çalıştırma (geliştirme):**

```sh
./install.sh         # uv ile .venv kurar ve kısayol ekler
./tapo-gui
```

---

## Kullanım

1. İlk açılışta Tapo uygulamasında kullandığınız **TP-Link e-posta ve şifrenizi** girin (ampuller yerel bağlantıda da bu bilgilerle doğrulama ister).
2. **Ağda ara** ile yerel ağdaki ışıkları tarayın veya **IP ile ekle** ile doğrudan IP adresi girin.
3. Sağ üstteki **EN / TR** düğmesiyle arayüz dilini dilediğiniz zaman değiştirebilirsiniz.
4. Detay sayfasından ana ekrana dönmek için `Esc`, `Alt+Sol` veya farenin **Geri** tuşunu kullanabilirsiniz.

---

## Yapılandırma

Ayarlar, kayıtlı cihazlar, özel renkler, adlar ve dil tercihi şu konumda saklanır:

- **Windows:** `%APPDATA%\tapo-gui\config.json`
- **Linux:** `~/.config/tapo-gui/config.json` (dosya izni `600`)

---

## Sorun Giderme

- **Ağda ara:** Önce yayın (broadcast) sorgusu gönderilir; güvenlik duvarı engelleyebildiği için yerel `/24` ağdaki her IP ayrıca tek tek sorgulanır. Tarama yaklaşık 10–15 saniye sürer.
- **Doğrulama hatası:** E-posta ve şifrenin Tapo uygulamasındakiyle aynı olduğundan emin olun (*Hesap* düğmesi). Sorun devam ederse Tapo uygulamasında *Ben → Üçüncü taraf hizmetleri → Üçüncü taraf uyumluluğu* seçeneğini kapatıp yeniden açın.
- **Windows Güvenlik Duvarı:** İlk açılışta izin penceresi çıkarsa yerel ağdaki cihazlarla iletişim için **Özel ağlar** iznini verin.

---

## Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
