import os
import subprocess
import datetime
from colorama import Fore, Style, init
init(autoreset=True)

LOG_FILE = "egasus.log"

def log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

# --------------------------
# CİHAZ SEÇİMİ / BİLGİLERİ
# --------------------------
def get_connected_devices():
    try:
        result = subprocess.getoutput("adb devices")
        devices = []
        for line in result.splitlines()[1:]:
            # satır "serial\tstate" şeklinde gelir, state == "device" olanları al
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])
        return devices
    except Exception as e:
        log(f"Bağlı cihazları alma hatası: {e}")
        return []

def select_device():
    devices = get_connected_devices()
    if not devices:
        print(Fore.RED + "Hiçbir cihaz bağlı değil! Lütfen cihazı bağlayın ve tekrar deneyin.")
        log("Cihaz bağlı değil.")
        return None
    if len(devices) == 1:
        return devices[0]
    print(Fore.YELLOW + "Birden fazla cihaz bağlı. Lütfen bir cihaz seçin:")
    for idx, dev in enumerate(devices, 1):
        print(f"[{idx}] {dev}")
    while True:
        choice = input("Seçiminiz: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(devices):
            return devices[int(choice)-1]
        print(Fore.RED + "Geçersiz seçim!")

def _adb(device, cmd):
    """Seçilen cihaza özel adb komutu hazırla."""
    prefix = f"adb -s {device} " if device else "adb "
    return prefix + cmd

def get_device_info(device=None):
    info = {}
    try:
        prefix = f"adb -s {device} " if device else "adb "
        # Model / Android / Üretici
        info['model'] = subprocess.getoutput(f"{prefix}shell getprop ro.product.model").strip()
        info['android'] = subprocess.getoutput(f"{prefix}shell getprop ro.build.version.release").strip()
        info['manufacturer'] = subprocess.getoutput(f"{prefix}shell getprop ro.product.manufacturer").strip()

        # Pil (dumpsys battery)
        battery_dump = subprocess.getoutput(f"{prefix}shell dumpsys battery")
        level = None
        for line in battery_dump.splitlines():
            if "level" in line:
                try:
                    level = int(line.split(":")[-1].strip())
                    break
                except Exception:
                    pass
        info['battery'] = f"%{level}" if level is not None else "Bilinmiyor"

        # RAM (MemTotal)
        meminfo = subprocess.getoutput(f"{prefix}shell cat /proc/meminfo")
        ram_line = next((l for l in meminfo.splitlines() if l.lower().startswith("memtotal")), "")
        info['ram'] = ram_line.strip() or "Bilinmiyor"

        # Depolama (/data)
        df_out = subprocess.getoutput(f"{prefix}shell df -k /data")
        # genelde başlık + bir satır olur; son satırı alan/boş vb. çekelim
        lines = [l for l in df_out.splitlines() if l.strip()]
        storage = "Bilinmiyor"
        if len(lines) >= 2:
            cols = lines[-1].split()
            # bazı cihazlarda: Filesystem 1K-blocks Used Available Use% Mounted on
            if len(cols) >= 6:
                total_k, avail_k = cols[1], cols[3]
                try:
                    total_mb = int(total_k) // 1024
                    avail_mb = int(avail_k) // 1024
                    storage = f"{total_mb}MB toplam, {avail_mb}MB boş"
                except Exception:
                    storage = "Bilinmiyor"
        info['storage'] = storage

        # Çözünürlük
        wm = subprocess.getoutput(f"{prefix}shell wm size").strip()
        info['resolution'] = wm

        # IMEI (her cihazda çalışmayabilir)
        try:
            imei_raw = subprocess.getoutput(f"{prefix}shell service call iphonesubinfo 1")
            digits = "".join(ch for ch in imei_raw if ch.isdigit())
            info['imei'] = digits[:15] if len(digits) >= 15 else "Yok"
        except Exception:
            info['imei'] = "Yok"

    except Exception as e:
        log(f"Cihaz bilgi hatası: {e}")
        info = {'model': 'Yok', 'android': 'Yok', 'battery': 'Yok'}
    return info

def check_device(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    try:
        result = subprocess.getoutput("adb devices")
        print(Fore.YELLOW + "\nBağlı cihazlar:\n" + result)
        info = get_device_info(device)
        print(Fore.GREEN + (
            f"\nModel: {info['model']}\nAndroid: {info['android']}\nPil: {info['battery']}"
            f"\nÜretici: {info.get('manufacturer','Yok')}\nRAM: {info.get('ram','Yok')}"
            f"\nDepolama: {info.get('storage','Yok')}\nÇözünürlük: {info.get('resolution','Yok')}"
            f"\nIMEI: {info.get('imei','Yok')}"
        ))
        log(f"Cihaz kontrol edildi: {info}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Cihaz kontrol hatası: {e}")

# --------------------------
# BAĞLANTI
# --------------------------
def connect_wifi(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    ip = input("Telefon IP adresini gir (örn: 192.168.1.5): ").strip()
    try:
        subprocess.call(_adb(device, "tcpip 5555"), shell=True)
        subprocess.call(f"adb connect {ip}:5555", shell=True)
        print(Fore.GREEN + "Kablosuz bağlantı denendi.")
        log(f"Wi-Fi bağlantı denendi: {ip}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Wi-Fi bağlantı hatası: {e}")

def disconnect():
    try:
        subprocess.call("adb disconnect", shell=True)
        print(Fore.GREEN + "Tüm bağlantılar kesildi.")
        log("Bağlantılar kesildi.")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Bağlantı kesme hatası: {e}")

# --------------------------
# EKRAN İŞLEMLERİ
# --------------------------
def screen_record(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    duration = input("Kayıt süresi (saniye, max 180): ").strip()
    if not duration.isdigit():
        print(Fore.RED + "Geçersiz süre!")
        return
    duration = max(1, min(int(duration), 180))
    filename = f"record_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    try:
        subprocess.call(_adb(device, f"shell screenrecord /sdcard/{filename} --time-limit {duration}"), shell=True)
        subprocess.call(_adb(device, f"pull /sdcard/{filename} ./"), shell=True)
        print(Fore.GREEN + f"Kayıt tamamlandı: {filename}")
        log(f"Ekran kaydı alındı ({duration} sn) -> {filename}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Ekran kaydı hatası: {e}")

def screenshot(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    filename = f"screen_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    try:
        subprocess.call(_adb(device, f"shell screencap -p /sdcard/{filename}"), shell=True)
        subprocess.call(_adb(device, f"pull /sdcard/{filename} ./"), shell=True)
        print(Fore.GREEN + f"Ekran görüntüsü kaydedildi: {filename}")
        log(f"Ekran görüntüsü alındı -> {filename}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Ekran görüntüsü hatası: {e}")

def mirror_screen(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    print(Fore.CYAN + "scrcpy başlatılıyor (kurulu olmalı)...")
    try:
        subprocess.call(f"scrcpy -s {device}", shell=True)
        log("scrcpy ile ekran yansıtıldı.")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Ekran yansıtma hatası: {e}")

# --------------------------
# DOSYA İŞLEMLERİ
# --------------------------
def push_file(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    local = input("Gönderilecek dosyanın yolu: ").strip()
    remote = input("Cihazdaki hedef yol (örn: /sdcard/): ").strip()
    if not os.path.isfile(local):
        print(Fore.RED + "Dosya bulunamadı!")
        log(f"Dosya gönderme hatası: {local} bulunamadı.")
        return
    try:
        subprocess.call(_adb(device, f'push "{local}" "{remote}"'), shell=True)
        print(Fore.GREEN + "Dosya cihaza gönderildi.")
        log(f"Dosya gönderildi: {local} -> {remote}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Dosya gönderme hatası: {e}")

def pull_file(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    remote = input("Cihazdaki dosya yolu: ").strip()
    local = input("Bilgisayardaki hedef yol: ").strip()
    local_dir = os.path.dirname(local) or "."
    if local_dir and not os.path.exists(local_dir):
        print(Fore.RED + "Hedef klasör bulunamadı!")
        log(f"Dosya çekme hatası: {local_dir} bulunamadı.")
        return
    try:
        subprocess.call(_adb(device, f'pull "{remote}" "{local}"'), shell=True)
        print(Fore.GREEN + "Dosya bilgisayarına çekildi.")
        log(f"Dosya çekildi: {remote} -> {local}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Dosya çekme hatası: {e}")

def file_manager(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    path = input("Cihazda gezilecek klasör yolu (örn: /sdcard/): ").strip()
    try:
        result = subprocess.getoutput(_adb(device, f'shell ls -l "{path}"'))
        print(Fore.YELLOW + f"\n{path} içeriği:\n{result}")
        log(f"Dosya yöneticisi: {path}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Dosya yöneticisi hatası: {e}")

# --------------------------
# APK İŞLEMLERİ
# --------------------------
def list_apks(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    try:
        result = subprocess.getoutput(_adb(device, "shell pm list packages"))
        print(Fore.YELLOW + "\nYüklü APK'lar:\n" + result)
        log("APK listesi gösterildi.")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"APK listesi hatası: {e}")

def install_apk(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    apk_path = input("Yüklenecek APK dosyasının yolu: ").strip()
    if not os.path.isfile(apk_path):
        print(Fore.RED + "APK dosyası bulunamadı!")
        log(f"APK yükleme hatası: {apk_path} bulunamadı.")
        return
    try:
        subprocess.call(_adb(device, f'install "{apk_path}"'), shell=True)
        print(Fore.GREEN + "APK yüklendi.")
        log(f"APK yüklendi: {apk_path}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"APK yükleme hatası: {e}")

def uninstall_apk(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    package = input("Kaldırılacak paket adı (örn: com.android.chrome): ").strip()
    if not package:
        print(Fore.RED + "Paket adı boş olamaz!")
        log("APK kaldırma hatası: paket adı boş.")
        return
    try:
        subprocess.call(_adb(device, f'uninstall "{package}"'), shell=True)
        print(Fore.GREEN + "APK kaldırıldı.")
        log(f"APK kaldırıldı: {package}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"APK kaldırma hatası: {e}")

def backup_apk(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    package = input("Yedeklenecek paket adı: ").strip()
    try:
        apk_path_raw = subprocess.getoutput(_adb(device, f"shell pm path {package}")).strip()
        apk_path = apk_path_raw.replace("package:", "").strip()
        if not apk_path:
            print(Fore.RED + "APK yolu bulunamadı!")
            log(f"APK yedekleme hatası: {package} yolu bulunamadı.")
            return
        subprocess.call(_adb(device, f'pull "{apk_path}" ./'), shell=True)
        print(Fore.GREEN + f"{package} APK yedeklendi.")
        log(f"APK yedeklendi: {package}")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"APK yedekleme hatası: {e}")

def batch_install_apks(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    folder = input("APK klasörü yolu: ").strip()
    if not os.path.isdir(folder):
        print(Fore.RED + "Klasör bulunamadı!")
        log(f"Toplu APK yükleme hatası: {folder} bulunamadı.")
        return
    for apk in os.listdir(folder):
        if apk.lower().endswith(".apk"):
            try:
                subprocess.call(_adb(device, f'install "{os.path.join(folder, apk)}"'), shell=True)
                print(Fore.GREEN + f"{apk} yüklendi.")
                log(f"Toplu APK yüklendi: {apk}")
            except Exception as e:
                print(Fore.RED + f"{apk} yüklenemedi: {e}")
                log(f"Toplu APK yükleme hatası: {apk} - {e}")

def batch_uninstall_apks(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    packages = input("Kaldırılacak paket adlarını virgülle ayırarak girin: ").strip().split(",")
    for package in packages:
        package = package.strip()
        if package:
            try:
                subprocess.call(_adb(device, f'uninstall "{package}"'), shell=True)
                print(Fore.GREEN + f"{package} kaldırıldı.")
                log(f"Toplu APK kaldırıldı: {package}")
            except Exception as e:
                print(Fore.RED + f"{package} kaldırılamadı: {e}")
                log(f"Toplu APK kaldırma hatası: {package} - {e}")

# --------------------------
# DİĞERLERİ
# --------------------------
def reboot_device(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    print(Fore.YELLOW + "Yeniden başlatma türünü seçin:")
    print("[1] Normal\n[2] Bootloader\n[3] Recovery")
    choice = input("Seçiminiz: ").strip()
    try:
        if choice == "1":
            subprocess.call(_adb(device, "reboot"), shell=True)
            log("Cihaz normal şekilde yeniden başlatıldı.")
        elif choice == "2":
            subprocess.call(_adb(device, "reboot bootloader"), shell=True)
            log("Cihaz bootloader ile yeniden başlatıldı.")
        elif choice == "3":
            subprocess.call(_adb(device, "reboot recovery"), shell=True)
            log("Cihaz recovery ile yeniden başlatıldı.")
        else:
            print(Fore.RED + "Geçersiz seçim!")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Yeniden başlatma hatası: {e}")

def device_console(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    print(Fore.YELLOW + "Cihaz shell konsolu. Çıkmak için 'exit' yazın.")
    while True:
        cmd = input("adb shell> ")
        if cmd.strip().lower() == "exit":
            break
        try:
            result = subprocess.getoutput(_adb(device, f"shell {cmd}"))
            print(result)
            log(f"Konsol komutu: {cmd} -> {result}")
        except Exception as e:
            print(Fore.RED + f"Hata: {e}")
            log(f"Konsol hatası: {e}")

def show_logcat(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    print(Fore.YELLOW + "Logcat çıktısı (son 100 satır):")
    try:
        all_log = subprocess.getoutput(_adb(device, "logcat -d"))
        tail = "\n".join(all_log.splitlines()[-100:])
        print(tail)
        log("Logcat gösterildi.")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Logcat hatası: {e}")

def lock_screen(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    try:
        subprocess.call(_adb(device, "shell input keyevent 26"), shell=True)
        print(Fore.GREEN + "Ekran kilitlendi/açıldı.")
        log("Ekran kilitlendi/açıldı.")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Ekran kilitleme hatası: {e}")

def wake_device(device=None):
    if not device:
        device = select_device()
        if not device:
            return
    try:
        subprocess.call(_adb(device, "shell input keyevent 224"), shell=True)
        print(Fore.GREEN + "Cihaz uyandırıldı.")
        log("Cihaz uyandırıldı.")
    except Exception as e:
        print(Fore.RED + f"Hata: {e}")
        log(f"Cihaz uyandırma hatası: {e}")

def show_adb_commands():
    print(Fore.CYAN + "\n--- Sık Kullanılan ADB Komutları ---")
    commands = [
        ("adb devices", "Bağlı cihazları listeler"),
        ("adb shell", "Cihazda shell açar"),
        ("adb install <apk>", "APK yükler"),
        ("adb uninstall <paket>", "APK kaldırır"),
        ("adb push <dosya> <hedef>", "Dosya gönderir"),
        ("adb pull <dosya> <hedef>", "Dosya çeker"),
        ("adb reboot", "Cihazı yeniden başlatır"),
        ("adb logcat", "Logcat çıktısı"),
        ("adb tcpip 5555", "Wi-Fi bağlantı portu açar"),
        ("adb connect <ip>:5555", "Wi-Fi ile bağlanır"),
        ("adb shell screencap -p <yol>", "Ekran görüntüsü alır"),
        ("adb shell screenrecord <yol>", "Ekran kaydı alır"),
    ]
    for cmd, desc in commands:
        print(Fore.YELLOW + f"{cmd} -> {desc}")

def show_log():
    print(Fore.MAGENTA + "\n--- İşlem Geçmişi ---")
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            print(f.read())
    except FileNotFoundError:
        print(Fore.RED + "Henüz log kaydı yok.")
