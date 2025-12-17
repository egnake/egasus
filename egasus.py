import os
import datetime
from colorama import Fore, Style, init
import deviceops

init(autoreset=True)

LOG_FILE = "egasus.log"
CONFIG_FILE = "egasus.conf"

def log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def ascii_banner():
    print(Fore.CYAN + """
    _____________   _____    __ __ ______
   / ____/ ____/ | / /   |  / //_// ____/
  / __/ / / __/  |/ / /| | / ,<  / __/   
 / /___/ /_/ / /|  / ___ |/ /| |/ /___   
/_____/\____/_/ |_/_/  |_/_/ |_/_____/   
    """)

def banner(device_info=None):
    ascii_banner()
    if device_info:
        print(Fore.YELLOW + f"Cihaz: {device_info.get('model', 'Yok')} | Android: {device_info.get('android', 'Yok')} | Pil: {device_info.get('battery', 'Yok')}")
    else:
        print(Fore.RED + "Cihaz bağlı değil!")

def help_menu():
    print(Fore.CYAN + "\n--- Yardım Menüsü ---")
    print(Fore.YELLOW + """
Her fonksiyon alt menülerde gruplanmıştır:
- Ekran İşlemleri: Ekranı Kaydet / Yansıt / Görüntü Al
- Dosya İşlemleri: Gönder (push) / Çek (pull) / Gez (file manager)
- APK İşlemleri: Listele / Yükle / Kaldır / Yedekle / Toplu Yükle/Kaldır

Alt menüye girerken cihazı bir kez seçersiniz; çıkana kadar aynı cihaz kullanılır.
Kritik işlemlerde girdilerinizi dikkatli girin (paket adı, yollar).
""")

# -------------
# ALT MENÜLER
# -------------
def ensure_device_selected():
    dev = deviceops.select_device()
    if not dev:
        print(Fore.RED + "Cihaz seçilmedi.")
    return dev

def screen_menu():
    device = ensure_device_selected()
    if not device:
        return
    while True:
        clear()
        info = deviceops.get_device_info(device)
        banner(info)
        print(Fore.CYAN + "\n--- Ekran İşlemleri ---")
        print(Fore.YELLOW + """
[1] Ekran Kaydı
[2] Ekran Yansıt (scrcpy)
[3] Ekran Görüntüsü
[0] Geri Dön
""")
        choice = input("Seçiminiz: ").strip()
        if choice == "1":
            deviceops.screen_record(device)
        elif choice == "2":
            deviceops.mirror_screen(device)
        elif choice == "3":
            deviceops.screenshot(device)
        elif choice == "0":
            break
        else:
            print(Fore.RED + "Geçersiz seçim!")
        input(Fore.MAGENTA + "\nDevam etmek için Enter'a basın...")

def files_menu():
    device = ensure_device_selected()
    if not device:
        return
    while True:
        clear()
        info = deviceops.get_device_info(device)
        banner(info)
        print(Fore.CYAN + "\n--- Dosya İşlemleri ---")
        print(Fore.YELLOW + """
[1] Dosya Gönder (push)
[2] Dosya Çek (pull)
[3] Dosya Gez (file manager)
[0] Geri Dön
""")
        choice = input("Seçiminiz: ").strip()
        if choice == "1":
            deviceops.push_file(device)
        elif choice == "2":
            deviceops.pull_file(device)
        elif choice == "3":
            deviceops.file_manager(device)
        elif choice == "0":
            break
        else:
            print(Fore.RED + "Geçersiz seçim!")
        input(Fore.MAGENTA + "\nDevam etmek için Enter'a basın...")

def apk_menu():
    device = ensure_device_selected()
    if not device:
        return
    while True:
        clear()
        info = deviceops.get_device_info(device)
        banner(info)
        print(Fore.CYAN + "\n--- APK İşlemleri ---")
        print(Fore.YELLOW + """
[1] APK Listesi
[2] APK Yükle
[3] APK Kaldır
[4] APK Yedekle
[5] Toplu APK Yükle
[6] Toplu APK Kaldır
[0] Geri Dön
""")
        choice = input("Seçiminiz: ").strip()
        if choice == "1":
            deviceops.list_apks(device)
        elif choice == "2":
            deviceops.install_apk(device)
        elif choice == "3":
            deviceops.uninstall_apk(device)
        elif choice == "4":
            deviceops.backup_apk(device)
        elif choice == "5":
            deviceops.batch_install_apks(device)
        elif choice == "6":
            deviceops.batch_uninstall_apks(device)
        elif choice == "0":
            break
        else:
            print(Fore.RED + "Geçersiz seçim!")
        input(Fore.MAGENTA + "\nDevam etmek için Enter'a basın...")

# -------------
# ANA MENÜ
# -------------
def main_menu():
    while True:
        clear()
        # varsa ilk cihaza ait özet göster
        device_info = None
        devices = deviceops.get_connected_devices()
        if devices:
            device_info = deviceops.get_device_info(devices[0])
        banner(device_info)
        print(Fore.YELLOW + """
[1] Cihazı Kontrol Et
[2] Wi-Fi ile Bağlan
[3] Bağlantıyı Kes
[4] Ekran İşlemleri
[5] Dosya İşlemleri
[6] APK İşlemleri
[7] Cihazı Yeniden Başlat
[8] Cihaz Konsolu (Shell)
[9] Logcat Göster
[10] Ekran Kilitle/Aç
[11] Cihazı Uyandır
[12] Sık Kullanılan ADB Komutları
[13] Yardım Menüsü
[14] İşlem Geçmişini Göster (log)
[0] Çıkış
""")
        choice = input("Seçiminiz: ").strip()
        try:
            if choice == "1":
                deviceops.check_device()
            elif choice == "2":
                deviceops.connect_wifi()
            elif choice == "3":
                deviceops.disconnect()
            elif choice == "4":
                screen_menu()
            elif choice == "5":
                files_menu()
            elif choice == "6":
                apk_menu()
            elif choice == "7":
                # alt menü gibi cihaz seçtir, aynı anda tek işlem
                dev = deviceops.select_device()
                if dev:
                    deviceops.reboot_device(dev)
            elif choice == "8":
                dev = deviceops.select_device()
                if dev:
                    deviceops.device_console(dev)
            elif choice == "9":
                dev = deviceops.select_device()
                if dev:
                    deviceops.show_logcat(dev)
            elif choice == "10":
                dev = deviceops.select_device()
                if dev:
                    deviceops.lock_screen(dev)
            elif choice == "11":
                dev = deviceops.select_device()
                if dev:
                    deviceops.wake_device(dev)
            elif choice == "12":
                deviceops.show_adb_commands()
            elif choice == "13":
                help_menu()
            elif choice == "14":
                deviceops.show_log()
            elif choice == "0":
                print(Fore.CYAN + "Çıkılıyor...")
                log("Uygulamadan çıkıldı.")
                break
            else:
                print(Fore.RED + "Geçersiz seçim!")
        except Exception as e:
            print(Fore.RED + f"Beklenmeyen hata: {e}")
            log(f"Beklenmeyen hata: {e}")
        input(Fore.MAGENTA + "\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main_menu()
