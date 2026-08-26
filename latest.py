# ★made by lowkeyy★
# GG Klanı — Riot Account Generator  |  latest.py  |  single-file build

import sys
import os
import threading
import time
import uuid
import json
import random
import string
import shutil
import logging
import base64
import subprocess
from datetime import datetime

# ── Qt ──────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QCheckBox, QTextEdit, QTabWidget,
    QFrame, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QMessageBox, QDialog, QFormLayout,
    QGraphicsOpacityEffect, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QObject, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QPalette, QTextCursor

# ── Third-party (optional) ───────────────────────────────────────────────────
try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

HAS_WIN32 = False
try:
    import win32gui, win32con
    HAS_WIN32 = True
except ImportError:
    pass

HAS_PYAUTOGUI = False
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    HAS_PYAUTOGUI = True
except ImportError:
    pass

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    HAS_DRISSION = True
except ImportError:
    HAS_DRISSION = False

# ════════════════════════════════════════════════════════════════════════════
#  LOGGING
# ════════════════════════════════════════════════════════════════════════════
logging.basicConfig(
    filename="worker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
#  ACCOUNT CREATOR
# ════════════════════════════════════════════════════════════════════════════
def _slow_type(ele, text, delay=0.05):
    ele.click()
    for ch in text:
        ele.input(ch)
        time.sleep(delay)


def _random_email():
    local = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"{local}@gmail.com"


def create_riot_account(task_id, user_data_dir, proxy=None, headless=False,
                        log_callback=None, status_callback=None):
    def emit(msg, level="info"):
        tag = f"[Task-{task_id[-6:]}] {msg}"
        if log_callback:
            log_callback(tag, level)
        getattr(logger, "warning" if level == "warn" else level, logger.info)(tag)

    if not HAS_DRISSION:
        emit("DrissionPage kurulu değil — hesap oluşturulamıyor.", "error")
        return False

    emit(f"İşlem başladı. Dizin: {user_data_dir}")
    os.makedirs(user_data_dir, exist_ok=True)
    result  = {"task_id": task_id, "status": "failed", "account_info": {}, "error": None}
    page    = None
    success = False

    try:
        opts = ChromiumOptions()
        opts.set_user_data_path(user_data_dir)
        opts.set_argument("--mute-audio")
        opts.set_argument("--no-sandbox")
        opts.set_argument("--disable-dev-shm-usage")
        opts.set_argument("--disable-gpu")
        opts.set_argument("--window-size=1920,1080")

        if headless:
            opts.set_argument("--headless=new")
            emit("Headless modu aktif.")
        else:
            opts.no_imgs()

        if proxy:
            opts.set_argument(f"--proxy-server={proxy}")

        opts.set_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        opts.set_argument("--disable-blink-features=AutomationControlled")
        opts.set_argument("--disable-web-security")
        opts.set_argument("--allow-running-insecure-content")
        opts.set_argument("--lang=tr-TR,tr;q=0.9")

        emit("Tarayıcı başlatılıyor...")
        page = ChromiumPage(opts)
        page.run_cdp("Page.addScriptToEvaluateOnNewDocument", source="""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins',   {get: () => [1,2,3,4,5]});
        """)

        emit("Riot Games hesap sayfasına gidiliyor...")
        if not page.get("https://account.riotgames.com/", timeout=15):
            raise Exception("Sayfa yüklenemedi — bağlantı hatası.")

        page.ele("xpath:/html/body/div[2]/div/main/div/form/div/div/div[3]/span[2]", timeout=15).click()
        emit("İlk adım geçildi.")

        account_info          = {}
        account_info["email"] = _random_email()

        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div[1]/div/input",
                 timeout=10).input(account_info["email"])
        emit(f"E-posta: {account_info['email']}")
        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button/div").click()

        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[1]/input",
                 timeout=10).input("12")
        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[2]/input").input("12")
        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[3]/input").input("2002")
        emit("Doğum tarihi girildi.")
        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button/div").click()

        account_info["username"] = ("tyex" + "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)))[:20]
        account_info["password"] = ".gg/ggklani" + "".join(random.choices(string.digits, k=8))

        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div/input",
                 timeout=10).input(account_info["username"])
        emit(f"Kullanıcı adı: {account_info['username']}")
        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button/div").click()

        _slow_type(page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[1]/div/input",
                             timeout=10), account_info["password"])
        time.sleep(0.2)
        pw2 = page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[4]/div[1]/input")
        pw2.clear()
        _slow_type(pw2, account_info["password"])
        emit("Şifreler girildi.")
        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button/div").click()

        tos = page.ele("xpath://*[@id='tos-scrollable-area']", timeout=10)
        page.run_js("arguments[0].scrollTop = arguments[0].scrollHeight", tos)
        emit("TOS kaydırıldı.")
        cooldown = random.uniform(2.0, 3.0)
        emit(f"Cooldown ({cooldown:.1f}s)...")
        time.sleep(cooldown)
        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[3]/div/div/div/input").click()
        page.ele("xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button").click()
        emit("Form gönderildi, tamamlanma bekleniyor...")
        time.sleep(2)
        emit("Kayıt için 6 saniye bekleniyor...")
        time.sleep(6)

        # Persist to TXT
        with open("created_accounts.txt", "a", encoding="utf-8") as f:
            f.write(f"{account_info['email']}:{account_info['username']}:{account_info['password']}\n")

        # Persist to JSON
        try:
            jf = "created_accounts.json"
            accs = json.load(open(jf, encoding="utf-8")) if os.path.exists(jf) else []
            accs.append({
                "email":      account_info["email"],
                "username":   account_info["username"],
                "password":   account_info["password"],
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status":     "Created",
            })
            json.dump(accs, open(jf, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        except Exception as je:
            logger.warning(f"JSON kayıt hatası: {je}")

        result["status"] = "success"
        result["account_info"] = account_info
        success = True
        emit("Hesap başarıyla oluşturuldu!", "info")
        if status_callback:
            status_callback("success", account_info)

    except Exception as e:
        result["error"] = str(e)
        emit(f"Hata: {e}", "error")
        if status_callback and str(e) != "CAPTCHA_DETECTED":
            status_callback("failed", {"error": str(e)})
        if str(e) == "CAPTCHA_DETECTED":
            raise

    finally:
        if page:
            try:
                page.quit()
                emit("Tarayıcı kapatıldı.")
            except Exception as e:
                emit(f"Tarayıcı kapatma hatası: {e}", "error")

        if success:
            try:
                shutil.rmtree(user_data_dir)
            except Exception:
                pass
        os.makedirs("results", exist_ok=True)
        with open(f"results/{task_id}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    return success


# ════════════════════════════════════════════════════════════════════════════
#  RIOT LOGIN MANAGER
# ════════════════════════════════════════════════════════════════════════════
class RiotLoginManager:

    STANDARD_CLIENT_PATHS = [
        r"C:\Riot Games\Riot Client\RiotClientServices.exe",
        os.path.join(os.getenv("LOCALAPPDATA", ""), r"Riot Games\Riot Client\RiotClientServices.exe"),
        os.path.join(os.getenv("ALLUSERSPROFILE", r"C:\ProgramData"),
                     r"Riot Games\Riot Client\RiotClientServices.exe"),
        r"D:\Riot Games\Riot Client\RiotClientServices.exe",
        r"E:\Riot Games\Riot Client\RiotClientServices.exe",
    ]
    LOCKFILE_PATHS = [
        os.path.join(os.getenv("LOCALAPPDATA", ""), r"Riot Games\Riot Client\Config\lockfile"),
        r"C:\Riot Games\Riot Client\Config\lockfile",
    ]

    @classmethod
    def find_riot_client_path(cls):
        for p in cls.STANDARD_CLIENT_PATHS:
            if os.path.exists(p):
                return p
        return None

    @classmethod
    def find_lockfile(cls):
        for p in cls.LOCKFILE_PATHS:
            if os.path.exists(p):
                return p
        return None

    @classmethod
    def is_riot_client_running(cls):
        try:
            out = subprocess.check_output(
                'tasklist /FI "IMAGENAME eq RiotClientServices.exe" /NH',
                shell=True, text=True)
            return "RiotClientServices.exe" in out
        except Exception:
            return False

    @classmethod
    def find_riot_window_handle(cls):
        if not HAS_WIN32:
            return None
        found = []
        def cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd) and "Riot Client" in win32gui.GetWindowText(hwnd):
                found.append(hwnd)
        win32gui.EnumWindows(cb, None)
        return found[0] if found else None

    @classmethod
    def focus_riot_window(cls):
        if not HAS_WIN32:
            return False
        hwnd = cls.find_riot_window_handle()
        if hwnd:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                return True
            except Exception as e:
                logger.warning(f"SetForegroundWindow: {e}")
        return False

    @classmethod
    def login_riot_client_api(cls, username, password, log_callback=None):
        def log(msg, level="info"):
            if log_callback:
                log_callback(f"[API] {msg}", level)

        if not HAS_REQUESTS:
            return False, "requests modülü yok"

        lock = cls.find_lockfile()
        if not lock:
            return False, "Lockfile bulunamadı"

        try:
            parts = open(lock, encoding="utf-8").read().strip().split(":")
            if len(parts) < 5:
                return False, "Lockfile formatı geçersiz"
            _, _, port, auth_token, _ = parts[:5]
            log(f"API port: {port}")

            sess = requests.Session()
            sess.verify = False
            hdrs = {
                "Authorization": "Basic " + base64.b64encode(
                    f"riot:{auth_token}".encode()).decode(),
                "Content-Type": "application/json",
            }
            # Birden fazla endpoint dene — Riot farklı versiyonlarda farklı yollar kullanıyor
            endpoints = [
                ("POST", f"https://127.0.0.1:{port}/rso-auth/v2/authorizations",
                 {"type": "auth", "username": username, "password": password, "remember": True}),
                ("PUT",  f"https://127.0.0.1:{port}/rso-auth/v2/authorizations",
                 {"type": "auth", "username": username, "password": password, "remember": True}),
                ("POST", f"https://127.0.0.1:{port}/rso-auth/v1/session",
                 {"username": username, "password": password, "persistLogin": False}),
            ]
            for method, url, payload in endpoints:
                try:
                    fn = sess.put if method == "PUT" else sess.post
                    r  = fn(url, json=payload, headers=hdrs, timeout=5)
                    log(f"[{method}] {url.split('/')[-1]} → {r.status_code}", "info")
                    if r.status_code in (200, 201, 204):
                        log(f"'{username}' API ile giriş yapıldı!", "success")
                        return True, "API Login Successful"
                    if r.status_code == 400 and "invalid_client" in r.text:
                        log(f"Endpoint desteklenmiyor, sonraki deneniyor...", "warn")
                        continue
                    log(f"API yanıtı {r.status_code}: {r.text}", "warn")
                except Exception as ep:
                    log(f"Endpoint hatası: {ep}", "warn")
                    continue
            return False, "Tüm API endpointleri başarısız"
        except Exception as e:
            log(f"API hatası: {e}", "warn")
            return False, str(e)

    @classmethod
    def _force_logout(cls, log=None):
        def _l(msg, level="info"):
            if log:
                log(f"[Logout] {msg}", level)

        lock = cls.find_lockfile()
        if lock and HAS_REQUESTS:
            try:
                parts = open(lock, encoding="utf-8").read().strip().split(":")
                if len(parts) >= 5:
                    port, auth_token = parts[2], parts[3]
                    sess = requests.Session()
                    sess.verify = False
                    hdrs = {"Authorization": "Basic " + base64.b64encode(
                        f"riot:{auth_token}".encode()).decode()}
                    res = sess.delete(
                        f"https://127.0.0.1:{port}/rso-auth/v1/session",
                        headers=hdrs, timeout=5)
                    if res.status_code in (200, 204):
                        _l("Oturum API ile kapatıldı.")
                        time.sleep(1)
                        return
                    _l(f"API logout {res.status_code}, process kapatılıyor...", "warn")
            except Exception as e:
                _l(f"API logout hatası: {e}", "warn")

        try:
            subprocess.run(["taskkill", "/F", "/IM", "RiotClientServices.exe"],
                           capture_output=True, check=False)
            subprocess.run(["taskkill", "/F", "/IM", "RiotClientUx.exe"],
                           capture_output=True, check=False)
            _l("Process sonlandırıldı.")
            time.sleep(2)
        except Exception as e:
            _l(f"Process sonlandırma hatası: {e}", "error")

    @classmethod
    def login_riot_client_desktop(cls, username, password,
                                   custom_path=None, log_callback=None):
        # Based on denagnon/Riot-Manager — pygetwindow + direct paste, no API
        def log(msg, level='info'):
            if log_callback:
                log_callback(f'[RiotClient] {msg}', level)
            logger.info(msg)

        path = custom_path or cls.find_riot_client_path()

        # Step 1 — calisiyor mu, calisiyorsa oldur
        if cls.is_riot_client_running():
            log('Riot Client calisuyor, kapatiliyor...', 'info')
            cls._force_logout(log)
            time.sleep(2)

        # Step 2 — kapali ise ac
        if not cls.is_riot_client_running():
            if not path or not os.path.exists(path):
                err = f'Riot Client bulunamadi: {path}'
                log(err, 'error')
                return False, err
            log(f'Baslatiliyor: {path}', 'info')
            subprocess.Popen([path, '--launch-product=league_of_legends',
                               '--launch-patchline=live'])

        # Step 3 — pygetwindow ile pencere gorununce devam et (Riot-Manager yontemi)
        try:
            import pygetwindow as gw
            HAS_GW = True
        except ImportError:
            HAS_GW = False
            log('pygetwindow bulunamadi. pip install pygetwindow', 'warn')

        log('Riot Client penceresi bekleniyor (max 60s)...', 'info')
        window = None
        for elapsed in range(60):
            time.sleep(1)
            if HAS_GW:
                wins = gw.getWindowsWithTitle('Riot Client')
                if wins:
                    window = wins[0]
                    log(f'Pencere {elapsed + 1}. saniyede bulundu.', 'info')
                    break
            else:
                if cls.is_riot_client_running():
                    log(f'Process {elapsed + 1}. saniyede acildi, 4s bekleniyor...', 'info')
                    time.sleep(4)
                    break
            if (elapsed + 1) % 5 == 0:
                log(f'Bekleniyor... {elapsed + 1}s', 'info')

        if HAS_GW and window is None:
            return False, 'Riot Client penceresi 60s icinde acilamadi'

        if not HAS_PYAUTOGUI:
            return False, 'pyautogui yok -- pip install pyautogui'

        try:
            import pyperclip
            HAS_PYPERCLIP = True
        except ImportError:
            HAS_PYPERCLIP = False
            log('pyperclip bulunamadi -- pip install pyperclip', 'warn')

        try:
            # Pencereyi one getir
            if window:
                try:
                    window.activate()
                    log('Pencere aktiflestirildi.', 'info')
                except Exception as e:
                    log(f'window.activate uyarisi: {e}', 'warn')
            time.sleep(1)

            pyautogui.PAUSE = 0.05

            # ── Ekran taramasi ile input kutularini bul ──────────────────────
            # Riot Client login formu: USERNAME ve PASSWORD alanlari
            # altin/bej arka plan rengi (#c8a870 civari) ile ayirt edilebilir.
            # Pencere siniri icinde soldan %5-%30 yatay bant, dikey olarak taran.
            def find_input_boxes(win):
                """
                Ekran goruntu sundan Riot Client login formundaki
                USERNAME ve PASSWORD kutularinin merkez Y koordinatini dondurur.
                (x koordinati: sol panelin ortasi)
                Bulamazsa None, None dondurur.
                """
                try:
                    from PIL import Image
                    import pyautogui as _pa

                    # Sadece pencere alanini yakala
                    left   = win.left
                    top    = win.top
                    width  = win.width
                    height = win.height

                    shot = _pa.screenshot(region=(left, top, width, height))
                    img  = shot  # PIL Image

                    # Sol panel x araligi: %3 - %27
                    x_start = int(width * 0.03)
                    x_end   = int(width * 0.27)
                    x_mid   = (x_start + x_end) // 2

                    # Input kutusu rengi: bej/altin --- R:190-220, G:160-190, B:90-130
                    # Her satiri tara, o renk araliginda yatay cizgi varsa input kutusu
                    input_rows = []
                    for y in range(int(height * 0.15), int(height * 0.70)):
                        matches = 0
                        for x in range(x_start, x_end, 4):
                            r, g, b = img.getpixel((x, y))[:3]
                            if 175 <= r <= 230 and 150 <= g <= 200 and 80 <= b <= 145:
                                matches += 1
                        if matches > 8:
                            input_rows.append(y)

                    if not input_rows:
                        return None, None

                    # Ardindan gelen satirlari grupla (her grup bir input kutusu)
                    groups = []
                    grp    = [input_rows[0]]
                    for row in input_rows[1:]:
                        if row - grp[-1] <= 3:
                            grp.append(row)
                        else:
                            if len(grp) >= 4:
                                groups.append(grp)
                            grp = [row]
                    if len(grp) >= 4:
                        groups.append(grp)

                    if len(groups) < 2:
                        return None, None

                    # Ilk grup USERNAME, ikinci grup PASSWORD
                    uy_local = sum(groups[0]) // len(groups[0])
                    py_local = sum(groups[1]) // len(groups[1])

                    # Ekran koordinatina cevir
                    uy_screen = top  + uy_local
                    py_screen = top  + py_local
                    x_screen  = left + x_mid

                    return (x_screen, uy_screen), (x_screen, py_screen)

                except Exception as e:
                    log(f'Ekran tarama hatasi: {e}', 'warn')
                    return None, None

            user_pos = None
            pass_pos = None
            if window:
                log('Ekran taranarak input kutulari aranıyor...', 'info')
                user_pos, pass_pos = find_input_boxes(window)

            if user_pos and pass_pos:
                log(f'Input kutulari bulundu — username: {user_pos}  password: {pass_pos}', 'info')
            else:
                # Fallback: pencere oranlarindan hesapla
                log('Ekran taramasi basarisiz, oran hesabi kullaniliyor...', 'warn')
                if window:
                    px_x   = window.left + int(window.width  * 0.13)
                    user_pos = (px_x, window.top + int(window.height * 0.32))
                    pass_pos = (px_x, window.top + int(window.height * 0.40))
                else:
                    sw2, sh2 = pyautogui.size()
                    user_pos = (sw2 // 2, sh2 // 2 - 45)
                    pass_pos = (sw2 // 2, sh2 // 2 + 15)

            ux, uy = user_pos
            px2, py2 = pass_pos

            # ── Username ────────────────────────────────────────────────────
            log(f'Kullanici adi giriliyor: {username}', 'info')
            pyautogui.click(x=ux, y=uy)
            time.sleep(0.4)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.05)
            pyautogui.press('delete')
            time.sleep(0.1)
            if HAS_PYPERCLIP:
                pyperclip.copy(username)
                time.sleep(0.15)
                pyautogui.hotkey('ctrl', 'v')
            else:
                for ch in username:
                    pyautogui.typewrite(ch, interval=0.04)
            time.sleep(0.2)

            # ── Password ────────────────────────────────────────────────────
            log('Sifre giriliyor...', 'info')
            pyautogui.click(x=px2, y=py2)
            time.sleep(0.4)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.05)
            pyautogui.press('delete')
            time.sleep(0.1)
            if HAS_PYPERCLIP:
                pyperclip.copy(password)
                time.sleep(0.15)
                pyautogui.hotkey('ctrl', 'v')
            else:
                for ch in password:
                    pyautogui.typewrite(ch, interval=0.04)
            time.sleep(0.15)

            # Enter
            pyautogui.hotkey('enter')
            log(f'Giris bilgileri gonderildi: {username}!', 'success')
            return True, 'Login Completed'

        except Exception as e:
            err = f'UI automation hatasi: {e}'
            log(err, 'error')
            return False, err



# ════════════════════════════════════════════════════════════════════════════
#  SIGNALS
# ════════════════════════════════════════════════════════════════════════════
class Signals(QObject):
    log           = Signal(str, str)
    status        = Signal(str, dict)
    stopped       = Signal()
    account_added = Signal(dict)


# ════════════════════════════════════════════════════════════════════════════
#  STYLESHEET
# ════════════════════════════════════════════════════════════════════════════
STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0d0d12;
    color: #e0e0e8;
    font-family: 'Segoe UI', sans-serif;
}
QWidget#titleBar {
    background-color: #0d0d12;
    border-bottom: 1px solid #1e1e2e;
}
QTabWidget::pane { border: none; background: transparent; }
QTabBar { background: transparent; }
QTabBar::tab {
    background: transparent; color: #6b6b88;
    font-size: 12px; font-weight: 600;
    padding: 10px 28px; border: none;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected { color: #ffffff; border-bottom: 2px solid #7c3aed; }
QTabBar::tab:hover:!selected { color: #a0a0c0; }
QWidget#card {
    background-color: #13131f; border: 1px solid #1e1e2e; border-radius: 10px;
}
QLabel#cardTitle { color: #9ca3af; font-size: 11px; font-weight: 600; }
QLabel#cardValue { color: #ffffff; font-size: 15px; font-weight: 700; }
QPushButton {
    font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700;
    border-radius: 8px; padding: 9px 20px; border: none; letter-spacing: 0.5px;
}
QPushButton#btnPrimary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6d28d9, stop:1 #7c3aed);
    color: #ffffff;
}
QPushButton#btnPrimary:hover { background: #7c3aed; }
QPushButton#btnPrimary:disabled { background: #27272a; color: #52525b; }
QPushButton#btnDanger {
    background-color: #7f1d1d; color: #fca5a5; border: 1px solid #991b1b;
}
QPushButton#btnDanger:hover { background-color: #991b1b; color: #ffffff; }
QPushButton#btnStop {
    background-color: #1a1a2e; color: #ef4444; border: 1px solid #ef4444;
}
QPushButton#btnStop:hover { background-color: #ef4444; color: #ffffff; }
QPushButton#btnStop:disabled { background-color: #1a1a2e; color: #52525b; border-color: #3f3f46; }
QPushButton#btnGhost {
    background-color: transparent; color: #9ca3af; border: 1px solid #2d2d42;
}
QPushButton#btnGhost:hover { background-color: #1e1e2e; color: #ffffff; border-color: #7c3aed; }
QPushButton#btnAutoLogin {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #6d28d9);
    color: #ffffff; font-size: 12px; font-weight: 800;
    letter-spacing: 1px; padding: 10px 24px;
}
QPushButton#btnAutoLogin:hover { background: #8b5cf6; }
QLineEdit, QSpinBox, QComboBox {
    background-color: #1a1a2e; color: #e0e0e8;
    border: 1px solid #2d2d42; border-radius: 7px;
    padding: 8px 12px; font-size: 12px;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border-color: #7c3aed; }
QSlider::groove:horizontal { height: 4px; background: #1e1e2e; border-radius: 2px; }
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6d28d9, stop:1 #a78bfa);
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #ffffff; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: #a78bfa; }
QCheckBox { color: #9ca3af; font-size: 11px; spacing: 8px; font-weight: 600; }
QCheckBox:hover { color: #e0e0e8; }
QCheckBox::indicator {
    width: 15px; height: 15px; border: 1px solid #3d3d56;
    border-radius: 4px; background: #1a1a2e;
}
QCheckBox::indicator:checked { background: #7c3aed; border-color: #7c3aed; }
QTableWidget {
    background-color: #0f0f1a; color: #e0e0e8;
    gridline-color: #1e1e2e; border: 1px solid #1e1e2e; border-radius: 8px;
}
QTableWidget::item { padding: 8px 12px; }
QTableWidget::item:selected { background-color: #2d1f5e; color: #c4b5fd; }
QHeaderView::section {
    background-color: #13131f; color: #6b7280;
    font-size: 10px; font-weight: 800; letter-spacing: 1px;
    padding: 10px; border: none; border-bottom: 1px solid #1e1e2e;
}
QWidget#termPanel {
    background-color: #0a0a12; border: 1px solid #1e1e2e; border-radius: 8px;
}
QWidget#termHeader {
    background-color: #111118; border-radius: 8px 8px 0 0;
    border-bottom: 1px solid #1e1e2e; min-height: 30px; max-height: 30px;
}
QTextEdit#termOutput {
    background-color: #0a0a12; color: #c0c0d0; border: none;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    font-size: 11px; padding: 10px 14px;
}
QFrame#sep { background-color: #1e1e2e; max-height: 1px; min-height: 1px; }
QScrollBar:vertical { background: #0d0d12; width: 6px; border-radius: 3px; }
QScrollBar::handle:vertical { background: #3d3d56; border-radius: 3px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QWidget#sidebar { background-color: #0b0b14; border-right: 1px solid #1e1e2e; }
QLabel#logoText { color: #a78bfa; font-size: 22px; font-weight: 900; letter-spacing: 1px; }
QLabel#logoSub  { color: #6b6b88; font-size: 9px; letter-spacing: 3px; font-weight: 700; }
QLabel#secLabel { color: #7c3aed; font-size: 9px; letter-spacing: 2px; font-weight: 800; }
QLabel#sliderVal { color: #a78bfa; font-size: 22px; font-weight: 800; }
"""


def _sep(parent=None):
    f = QFrame(parent)
    f.setObjectName("sep")
    f.setFrameShape(QFrame.HLine)
    return f


# ════════════════════════════════════════════════════════════════════════════
#  WIDGETS
# ════════════════════════════════════════════════════════════════════════════
class StatCard(QWidget):
    def __init__(self, title, value="0", color="#ffffff", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumWidth(140)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)

        self._dot = QLabel("●")
        self._dot.setStyleSheet("color:#f59e0b; font-size:10px;")
        self._dot.setAlignment(Qt.AlignRight)

        tr = QHBoxLayout()
        tl = QLabel(title)
        tl.setObjectName("cardTitle")
        tr.addWidget(tl)
        tr.addStretch()
        tr.addWidget(self._dot)

        self._val = QLabel(value)
        self._val.setObjectName("cardValue")
        self._val.setStyleSheet(f"color:{color}; font-size:15px; font-weight:700;")
        self._fx = QGraphicsOpacityEffect(self._val)
        self._val.setGraphicsEffect(self._fx)

        lay.addLayout(tr)
        lay.addWidget(self._val)

    def set_value(self, v):
        self._val.setText(str(v))
        a = QPropertyAnimation(self._fx, b"opacity")
        a.setDuration(260)
        a.setStartValue(0.2)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.start()
        self._anim = a

    def set_dot(self, color):
        self._dot.setStyleSheet(f"color:{color}; font-size:10px;")


class StatusCard(QWidget):
    def __init__(self, label, value, dot_color="#f59e0b", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumWidth(160)
        self.setMinimumHeight(80)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)

        top = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setObjectName("cardTitle")
        self._dot = QLabel("●")
        self._dot.setStyleSheet(f"color:{dot_color}; font-size:10px;")
        top.addWidget(lbl)
        top.addStretch()
        top.addWidget(self._dot)

        self._val = QLabel(value)
        self._val.setObjectName("cardValue")
        lay.addLayout(top)
        lay.addWidget(self._val)

    def set_value(self, v):
        self._val.setText(v)

    def set_dot(self, color):
        self._dot.setStyleSheet(f"color:{color}; font-size:10px;")


class AddAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hesap Ekle")
        self.setFixedSize(380, 240)
        self.setStyleSheet(STYLESHEET)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)

        title = QLabel("HESAP EKLE")
        title.setObjectName("secLabel")
        lay.addWidget(title)
        lay.addSpacing(10)

        form = QFormLayout()
        form.setSpacing(10)
        self.ie = QLineEdit(); self.ie.setPlaceholderText("user@gmail.com")
        self.iu = QLineEdit(); self.iu.setPlaceholderText("Riot Kullanıcı Adı")
        self.ip = QLineEdit(); self.ip.setEchoMode(QLineEdit.Password)
        self.ip.setPlaceholderText("Riot Şifresi")
        form.addRow("E-posta:", self.ie)
        form.addRow("Kullanıcı:", self.iu)
        form.addRow("Şifre:", self.ip)
        lay.addLayout(form)
        lay.addSpacing(14)

        br = QHBoxLayout()
        bc = QPushButton("İptal"); bc.setObjectName("btnGhost"); bc.clicked.connect(self.reject)
        bs = QPushButton("Kaydet"); bs.setObjectName("btnPrimary"); bs.clicked.connect(self.accept)
        br.addWidget(bc); br.addWidget(bs)
        lay.addLayout(br)

    def get_data(self):
        return {
            "email":      self.ie.text().strip(),
            "username":   self.iu.text().strip(),
            "password":   self.ip.text().strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status":     "Saved",
        }


# ════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ════════════════════════════════════════════════════════════════════════════
class App(QMainWindow):
    JSON_DB = "created_accounts.json"
    TXT_DB  = "created_accounts.txt"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GG Klanı — Account Generator")
        self.setMinimumSize(1060, 720)
        self.resize(1240, 780)
        self.setStyleSheet(STYLESHEET)

        self.running        = False
        self.worker_thread  = None
        self.success_count  = 0
        self.fail_count     = 0
        self.captcha_count  = 0
        self.accounts_list  = []
        self.term_collapsed = False

        self._sig = Signals()
        self._sig.log.connect(self._on_log)
        self._sig.status.connect(self._on_status)
        self._sig.stopped.connect(self._on_stopped)
        self._sig.account_added.connect(self._on_account_added)

        root = QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_sidebar())
        outer.addWidget(self._build_main(), stretch=1)

        self.load_accounts_from_storage()
        self.write_log("GG Klanı İçin Tasarlandı!", "info")

        self._rc_timer = QTimer(self)
        self._rc_timer.timeout.connect(self._poll_riot_client)
        self._rc_timer.start(3000)
        self._poll_riot_client()

    # ── Riot Client poller ───────────────────────────────────────────────────
    def _poll_riot_client(self):
        running = RiotLoginManager.is_riot_client_running()
        if running:
            self._sc_riot.set_value("Çalışıyor")
            self._sc_riot.set_dot("#22c55e")
        else:
            self._sc_riot.set_value("Kapalı")
            self._sc_riot.set_dot("#ef4444")

    # ── Sidebar ─────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = QWidget(); sb.setObjectName("sidebar"); sb.setFixedWidth(268)
        lay = QVBoxLayout(sb)
        lay.setContentsMargins(20, 26, 20, 22)
        lay.setSpacing(0)

        logo = QLabel("GG Klanı"); logo.setObjectName("logoText")
        sub  = QLabel("ACCOUNT GENERATOR"); sub.setObjectName("logoSub")
        lay.addWidget(logo); lay.addWidget(sub)
        lay.addSpacing(22); lay.addWidget(_sep()); lay.addSpacing(18)

        lay.addWidget(self._slabel("HESAP AYARLARI")); lay.addSpacing(10)

        row = QHBoxLayout()
        lbl = QLabel("Hesap Sayısı"); lbl.setStyleSheet("color:#6b7280; font-size:11px;")
        self.target_count_label = QLabel("1"); self.target_count_label.setObjectName("sliderVal")
        self.target_count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(lbl); row.addWidget(self.target_count_label)
        lay.addLayout(row); lay.addSpacing(6)

        self.target_count_slider = QSlider(Qt.Horizontal)
        self.target_count_slider.setMinimum(1); self.target_count_slider.setMaximum(200)
        self.target_count_slider.setValue(1)
        self.target_count_slider.valueChanged.connect(self.update_target_label)
        lay.addWidget(self.target_count_slider); lay.addSpacing(10)

        self.infinite_var = QCheckBox("Sonsuz Mod")
        self.infinite_var.stateChanged.connect(self.toggle_slider)
        lay.addWidget(self.infinite_var)
        lay.addSpacing(18); lay.addWidget(_sep()); lay.addSpacing(18)

        lay.addWidget(self._slabel("AYARLAR")); lay.addSpacing(10)
        self.headless_var = QCheckBox("Arka Plan Modu"); lay.addWidget(self.headless_var)
        lay.addSpacing(8)
        self.use_warp_var = QCheckBox("WARP (Otomatik IP Rotasyonu)")
        self.use_warp_var.setChecked(True); lay.addWidget(self.use_warp_var)
        lay.addSpacing(18); lay.addWidget(_sep()); lay.addSpacing(18)

        lay.addWidget(self._slabel("RİOT CLIENT YOLU")); lay.addSpacing(8)
        pr = QHBoxLayout(); pr.setSpacing(6)
        self.input_riot_path = QLineEdit()
        det = RiotLoginManager.find_riot_client_path()
        if det:
            self.input_riot_path.setText(det)
        else:
            self.input_riot_path.setPlaceholderText("RiotClientServices.exe...")
        bb = QPushButton("📁"); bb.setObjectName("btnGhost")
        bb.setFixedWidth(38); bb.setFixedHeight(34)
        bb.clicked.connect(self.browse_riot_client_path)
        pr.addWidget(self.input_riot_path, stretch=1); pr.addWidget(bb)
        lay.addLayout(pr)

        lay.addStretch(); lay.addWidget(_sep()); lay.addSpacing(14)

        self.start_btn = QPushButton("▶  Başlat"); self.start_btn.setObjectName("btnPrimary")
        self.start_btn.setFixedHeight(42); self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_tasks)
        lay.addWidget(self.start_btn); lay.addSpacing(8)

        self.stop_btn = QPushButton("■  Durdur"); self.stop_btn.setObjectName("btnStop")
        self.stop_btn.setFixedHeight(42); self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setEnabled(False); self.stop_btn.clicked.connect(self.stop_tasks)
        lay.addWidget(self.stop_btn)
        return sb

    def _slabel(self, text):
        l = QLabel(text); l.setObjectName("secLabel"); return l

    # ── Main area ────────────────────────────────────────────────────────────
    def _build_main(self):
        panel = QWidget()
        ml = QVBoxLayout(panel); ml.setContentsMargins(0, 0, 0, 0); ml.setSpacing(0)

        tb = QWidget(); tb.setObjectName("titleBar"); tb.setFixedHeight(52)
        tl = QHBoxLayout(tb); tl.setContentsMargins(22, 0, 22, 0)
        an = QLabel("GGKlan"); an.setStyleSheet("color:#a78bfa;font-size:16px;font-weight:900;")
        as_ = QLabel("Account Generator")
        as_.setStyleSheet("color:#4b4b6a;font-size:10px;margin-left:8px;margin-top:4px;")
        od = QLabel("●"); od.setStyleSheet("color:#22c55e;font-size:10px;")
        ol = QLabel("ONLINE"); ol.setStyleSheet("color:#22c55e;font-size:10px;font-weight:800;")
        tl.addWidget(an); tl.addWidget(as_); tl.addStretch()
        tl.addWidget(od); tl.addSpacing(4); tl.addWidget(ol)
        ml.addWidget(tb)

        self.tabs = QTabWidget(); self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._build_dashboard_tab(), "Dashboard")
        self.tabs.addTab(self._build_accounts_tab(), "Hesaplar")
        ml.addWidget(self.tabs, stretch=1)
        return panel

    def _build_dashboard_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab); lay.setContentsMargins(20, 18, 20, 18); lay.setSpacing(14)

        sc = QHBoxLayout(); sc.setSpacing(10)
        self._sc_status = StatusCard("Status",      "Ready to Launch", "#f59e0b")
        self._sc_riot   = StatusCard("Riot Client", "Kontrol...",      "#6b7280")
        self._sc_warp   = StatusCard("WARP",        "Kapalı",          "#6b7280")
        sc.addWidget(self._sc_status); sc.addWidget(self._sc_riot); sc.addWidget(self._sc_warp)
        lay.addLayout(sc)

        sr = QHBoxLayout(); sr.setSpacing(10)
        self.card_success = StatCard("Başarılı", "0", "#22c55e")
        self.card_fail    = StatCard("Başarısız", "0", "#ef4444")
        self.card_captcha = StatCard("Captcha",  "0", "#f59e0b")
        self.card_total   = StatCard("Toplam",   "0", "#a78bfa")
        sr.addWidget(self.card_success); sr.addWidget(self.card_fail)
        sr.addWidget(self.card_captcha); sr.addWidget(self.card_total)
        lay.addLayout(sr)

        ar = QHBoxLayout(); ar.setSpacing(10)
        b1 = QPushButton("▶  BAŞLAT"); b1.setObjectName("btnPrimary")
        b1.setFixedHeight(40); b1.clicked.connect(self.start_tasks)
        b2 = QPushButton("🔁  WARP BAĞLAN"); b2.setObjectName("btnGhost")
        b2.setFixedHeight(40)
        b2.clicked.connect(lambda: threading.Thread(target=self.warp_connect, daemon=True).start())
        b3 = QPushButton("🚀  AUTO LOGIN"); b3.setObjectName("btnAutoLogin")
        b3.setFixedHeight(40); b3.clicked.connect(self._trigger_login_from_dashboard)
        b4 = QPushButton("■  DURDUR"); b4.setObjectName("btnDanger")
        b4.setFixedHeight(40); b4.clicked.connect(self.stop_tasks)
        ar.addWidget(b1); ar.addWidget(b2); ar.addWidget(b3); ar.addWidget(b4)
        lay.addLayout(ar)

        lay.addWidget(self._build_terminal_panel(), stretch=1)
        return tab

    def _build_accounts_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab); lay.setContentsMargins(20, 18, 20, 18); lay.setSpacing(10)

        top = QHBoxLayout(); top.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Kullanıcı adı veya e-posta ile ara...")
        self.search_input.textChanged.connect(self.filter_accounts_table)
        top.addWidget(self.search_input, stretch=1)
        ba = QPushButton("➕  Manuel Ekle"); ba.setObjectName("btnGhost")
        ba.clicked.connect(self.open_add_account_dialog)
        br = QPushButton("🔄  Yenile"); br.setObjectName("btnGhost")
        br.clicked.connect(self.load_accounts_from_storage)
        top.addWidget(ba); top.addWidget(br)
        lay.addLayout(top)

        self.acc_table = QTableWidget()
        self.acc_table.setColumnCount(5)
        self.acc_table.setHorizontalHeaderLabels(["E-POSTA", "KULLANICI ADI", "ŞİFRE", "TARİH", "DURUM"])
        self.acc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5):
            self.acc_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.acc_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.acc_table.setSelectionMode(QTableWidget.SingleSelection)
        lay.addWidget(self.acc_table, stretch=1)

        bot = QHBoxLayout(); bot.setSpacing(8)
        bal = QPushButton("🚀  RIOT CLIENT AUTO-LOGIN"); bal.setObjectName("btnAutoLogin")
        bal.setFixedHeight(36); bal.clicked.connect(self.trigger_riot_client_desktop_login)
        bwb = QPushButton("🌐  Tarayıcı Girişi"); bwb.setObjectName("btnGhost")
        bwb.setFixedHeight(36); bwb.clicked.connect(self.trigger_riot_web_login)
        bcp = QPushButton("📋  Kopyala"); bcp.setObjectName("btnGhost")
        bcp.setFixedHeight(36); bcp.clicked.connect(self.copy_selected_credentials)
        bdl = QPushButton("🗑️  Sil"); bdl.setObjectName("btnDanger")
        bdl.setFixedHeight(36); bdl.clicked.connect(self.delete_selected_account)
        bex = QPushButton("💾  TXT Aktar"); bex.setObjectName("btnGhost")
        bex.setFixedHeight(36); bex.clicked.connect(self.export_accounts_txt)
        bot.addWidget(bal); bot.addWidget(bwb); bot.addWidget(bcp); bot.addWidget(bdl)
        bot.addStretch(); bot.addWidget(bex)
        lay.addLayout(bot)
        return tab

    def _build_terminal_panel(self):
        self.terminal_panel = QWidget(); self.terminal_panel.setObjectName("termPanel")
        tl = QVBoxLayout(self.terminal_panel); tl.setContentsMargins(0, 0, 0, 0); tl.setSpacing(0)

        hdr = QWidget(); hdr.setObjectName("termHeader")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(12, 0, 12, 0); hl.setSpacing(8)
        hl.addWidget(QLabel("💻"))
        ttl = QLabel("LIVE ACTIVITY")
        ttl.setStyleSheet("color:#9ca3af;font-size:11px;font-weight:800;letter-spacing:1.5px;font-family:Consolas;")
        stl = QLabel("service and process events")
        stl.setStyleSheet("color:#4b5563;font-size:10px;font-family:Consolas;")
        hl.addWidget(ttl); hl.addWidget(stl); hl.addStretch()

        bcl = QPushButton("Clear"); bcl.setObjectName("btnGhost")
        bcl.setFixedHeight(22); bcl.setStyleSheet("font-size:10px;padding:2px 8px;")
        bcl.clicked.connect(lambda: self.log_box.clear())
        self.btn_toggle_term = QPushButton("▼"); self.btn_toggle_term.setObjectName("btnGhost")
        self.btn_toggle_term.setFixedHeight(22); self.btn_toggle_term.setFixedWidth(28)
        self.btn_toggle_term.setStyleSheet("font-size:10px;padding:0;")
        self.btn_toggle_term.clicked.connect(self.toggle_terminal)
        hl.addWidget(bcl); hl.addWidget(self.btn_toggle_term)
        tl.addWidget(hdr)

        self.log_box = QTextEdit(); self.log_box.setObjectName("termOutput")
        self.log_box.setReadOnly(True); self.log_box.setLineWrapMode(QTextEdit.NoWrap)
        self.log_box.setMinimumHeight(140)
        tl.addWidget(self.log_box, stretch=1)
        return self.terminal_panel

    def toggle_terminal(self):
        if self.term_collapsed:
            self.log_box.setVisible(True); self.btn_toggle_term.setText("▼")
            self.term_collapsed = False
        else:
            self.log_box.setVisible(False); self.btn_toggle_term.setText("▲")
            self.term_collapsed = True

    # ── Storage ──────────────────────────────────────────────────────────────
    def load_accounts_from_storage(self):
        self.accounts_list = []
        if os.path.exists(self.JSON_DB):
            try:
                self.accounts_list = json.load(open(self.JSON_DB, encoding="utf-8"))
            except Exception as e:
                self.write_log(f"JSON okuma hatası: {e}", "error")

        if os.path.exists(self.TXT_DB):
            try:
                existing = {a.get("username") for a in self.accounts_list if "username" in a}
                for line in open(self.TXT_DB, encoding="utf-8"):
                    parts = line.strip().split(":")
                    if len(parts) == 3:
                        email, user, pwd = parts
                        if user not in existing:
                            self.accounts_list.append({
                                "email": email, "username": user, "password": pwd,
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "status": "Synced",
                            })
                            existing.add(user)
            except Exception as e:
                self.write_log(f"TXT sync hatası: {e}", "error")

        self.populate_accounts_table()

    def populate_accounts_table(self):
        self.acc_table.setRowCount(0)
        q = self.search_input.text().lower().strip() if hasattr(self, "search_input") else ""
        for acc in self.accounts_list:
            u, e = acc.get("username", ""), acc.get("email", "")
            if q and q not in u.lower() and q not in e.lower():
                continue
            r = self.acc_table.rowCount()
            self.acc_table.insertRow(r)
            self.acc_table.setItem(r, 0, QTableWidgetItem(e))
            self.acc_table.setItem(r, 1, QTableWidgetItem(u))
            self.acc_table.setItem(r, 2, QTableWidgetItem(acc.get("password", "")))
            self.acc_table.setItem(r, 3, QTableWidgetItem(acc.get("created_at", "-")))
            self.acc_table.setItem(r, 4, QTableWidgetItem(acc.get("status", "Saved")))
        self.card_total.set_value(len(self.accounts_list))

    def filter_accounts_table(self):
        self.populate_accounts_table()

    def _on_account_added(self, acc):
        self.accounts_list.append(acc)
        self.save_accounts_json()
        self.populate_accounts_table()
        self.write_log(f"Yeni hesap: {acc.get('username')}", "success")

    def save_accounts_json(self):
        try:
            json.dump(self.accounts_list, open(self.JSON_DB, "w", encoding="utf-8"),
                      indent=2, ensure_ascii=False)
        except Exception as e:
            self.write_log(f"JSON kayıt hatası: {e}", "error")

    # ── Login actions ────────────────────────────────────────────────────────
    def _trigger_login_from_dashboard(self):
        if not self.accounts_list:
            QMessageBox.information(self, "Hesap Yok", "Henüz hesap yok.")
            return
        acc  = self.accounts_list[-1]
        user = acc.get("username", "").strip()
        pwd  = acc.get("password", "").strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Eksik Bilgi", "Son hesapta bilgi eksik.")
            return
        path = self.input_riot_path.text().strip()
        self.write_log(f"Dashboard auto-login → '{user}'", "info")

        def _run():
            ok, msg = RiotLoginManager.login_riot_client_desktop(
                username=user, password=pwd,
                custom_path=path or None, log_callback=self.write_log)
            self.write_log(f"Sonuç: {msg}", "success" if ok else "error")

        threading.Thread(target=_run, daemon=True).start()

    def trigger_riot_client_desktop_login(self):
        sel = self.acc_table.currentRow()
        if sel < 0:
            QMessageBox.information(self, "Hesap Seçin", "Tabloda bir hesap seçin.")
            return
        user = self.acc_table.item(sel, 1).text()
        pwd  = self.acc_table.item(sel, 2).text()
        if not user or not pwd:
            QMessageBox.warning(self, "Eksik", "Kullanıcı adı/şifre eksik.")
            return
        path = self.input_riot_path.text().strip()
        self.write_log(f"Auto-login: '{user}'...", "info")

        def _run():
            ok, msg = RiotLoginManager.login_riot_client_desktop(
                username=user, password=pwd,
                custom_path=path or None, log_callback=self.write_log)
            self.write_log(f"Sonuç: {msg}", "success" if ok else "error")

        threading.Thread(target=_run, daemon=True).start()

    def trigger_riot_web_login(self):
        sel = self.acc_table.currentRow()
        if sel < 0:
            QMessageBox.information(self, "Hesap Seçin", "Tabloda bir hesap seçin.")
            return
        user = self.acc_table.item(sel, 1).text()
        pwd  = self.acc_table.item(sel, 2).text()
        self.write_log(f"Tarayıcı giriş: '{user}'...", "info")

        def _run():
            if hasattr(RiotLoginManager, "login_riot_browser"):
                ok, msg = RiotLoginManager.login_riot_browser(
                    username=user, password=pwd,
                    headless=False, log_callback=self.write_log)
                self.write_log(f"Sonuç: {msg}", "success" if ok else "error")
            else:
                self.write_log("login_riot_browser metodu bulunamadı.", "error")

        threading.Thread(target=_run, daemon=True).start()

    def copy_selected_credentials(self):
        sel = self.acc_table.currentRow()
        if sel < 0:
            return
        u = self.acc_table.item(sel, 1).text()
        p = self.acc_table.item(sel, 2).text()
        QApplication.clipboard().setText(f"{u}:{p}")
        self.write_log(f"Kopyalandı: '{u}:{p}'", "info")

    def open_add_account_dialog(self):
        dlg = AddAccountDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if d.get("username") and d.get("password"):
                self._sig.account_added.emit(d)

    def delete_selected_account(self):
        sel = self.acc_table.currentRow()
        if sel < 0:
            return
        u = self.acc_table.item(sel, 1).text()
        if QMessageBox.question(self, "Sil", f"'{u}' silinsin mi?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.accounts_list = [a for a in self.accounts_list if a.get("username") != u]
            self.save_accounts_json()
            self.populate_accounts_table()
            self.write_log(f"Silindi: '{u}'.", "info")

    def export_accounts_txt(self):
        if not self.accounts_list:
            self.write_log("Aktarılacak hesap yok.", "error"); return
        ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join(os.path.expanduser("~"), "Desktop", f"riot_accounts_{ts}.txt")
        try:
            with open(fname, "w", encoding="utf-8") as f:
                for a in self.accounts_list:
                    f.write(f"{a.get('email')}:{a.get('username')}:{a.get('password')}\n")
            self.write_log(f"Masaüstüne aktarıldı: riot_accounts_{ts}.txt", "success")
        except Exception as e:
            self.write_log(f"Aktar hatası: {e}", "error")

    def browse_riot_client_path(self):
        fn, _ = QFileDialog.getOpenFileName(self, "RiotClientServices.exe Seç", "", "Executable (*.exe)")
        if fn:
            self.input_riot_path.setText(fn)

    # ── Worker ───────────────────────────────────────────────────────────────
    def update_target_label(self, v):
        self.target_count_label.setText(str(v))

    def toggle_slider(self):
        if self.infinite_var.isChecked():
            self.target_count_slider.setEnabled(False)
            self.target_count_label.setText("∞")
        else:
            self.target_count_slider.setEnabled(True)
            self.target_count_label.setText(str(self.target_count_slider.value()))

    def write_log(self, msg, level="info"):
        self._sig.log.emit(msg, level)

    def _on_log(self, msg, level):
        ts = time.strftime("%H:%M:%S")
        c  = {"info": "#38bdf8", "error": "#f87171", "success": "#34d399", "warn": "#fbbf24"}
        tc, mc, pc = "#4b5563", c.get(level, "#c0c0d0"), c.get(level, "#38bdf8")
        html = (
            f'<span style="color:{tc};font-family:Consolas,monospace;">[{ts}]</span> '
            f'<span style="color:{pc};font-weight:bold;font-family:Consolas,monospace;">[{level.upper()}]</span> '
            f'<span style="color:{mc};font-family:Consolas,monospace;">{msg}</span><br>'
        )
        self.log_box.moveCursor(QTextCursor.End)
        self.log_box.insertHtml(html)
        self.log_box.moveCursor(QTextCursor.End)

    def update_status(self, status, data):
        self._sig.status.emit(status, data)

    def _on_status(self, status, data):
        if status == "success":
            self.success_count += 1
            self.card_success.set_value(self.success_count)
            if all(k in data for k in ("email", "username", "password")):
                self._sig.account_added.emit({
                    "email": data["email"], "username": data["username"],
                    "password": data["password"],
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Created",
                })
        elif status == "failed":
            self.fail_count += 1; self.card_fail.set_value(self.fail_count)
        elif status == "captcha":
            self.captcha_count += 1; self.card_captcha.set_value(self.captcha_count)

    def _on_stopped(self):
        self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False)
        self._sc_status.set_value("Ready to Launch"); self._sc_status.set_dot("#f59e0b")

    def warp_connect(self):
        try:
            self.write_log("WARP bağlanıyor...", "info")
            self._sc_warp.set_value("Bağlanıyor"); self._sc_warp.set_dot("#f59e0b")
            subprocess.run(["warp-cli", "connect"], check=False, capture_output=True)
            time.sleep(4)
            self.write_log("WARP bağlandı.", "info")
            self._sc_warp.set_value("Bağlı"); self._sc_warp.set_dot("#22c55e")
            return True
        except Exception as e:
            self.write_log(f"WARP hatası: {e}", "error")
            self._sc_warp.set_value("Hata"); self._sc_warp.set_dot("#ef4444")
            return False

    def warp_disconnect(self):
        try:
            subprocess.run(["warp-cli", "disconnect"], check=False, capture_output=True)
            self.write_log("WARP kesildi.", "info")
            self._sc_warp.set_value("Kapalı"); self._sc_warp.set_dot("#6b7280")
            time.sleep(1)
        except Exception as e:
            self.write_log(f"WARP kesme hatası: {e}", "error")

    def worker(self):
        created = 0
        self._sc_status.set_value("Çalışıyor"); self._sc_status.set_dot("#22c55e")
        while self.running:
            if not self.infinite_var.isChecked():
                if created >= self.target_count_slider.value():
                    self.write_log("Hedef sayıya ulaşıldı.", "info")
                    self.running = False; self._sig.stopped.emit(); break

            task_id       = str(uuid.uuid4())[:8]
            user_data_dir = f"data_{task_id}"
            headless      = self.headless_var.isChecked()

            if self.use_warp_var.isChecked():
                self.warp_connect()

            try:
                ok = create_riot_account(
                    task_id=task_id, user_data_dir=user_data_dir,
                    proxy=None, headless=headless,
                    log_callback=self.write_log,
                    status_callback=self.update_status,
                )
                if ok:
                    created += 1
                    self.write_log(f"İlerleme: {created} hesap.", "info")
            except Exception as e:
                self.write_log(f"Worker hatası: {e}", "error")
            finally:
                if self.use_warp_var.isChecked():
                    self.warp_disconnect()
            time.sleep(2)

    def start_tasks(self):
        if self.running:
            return
        self.running = True
        mode   = "WARP" if self.use_warp_var.isChecked() else "Standart"
        target = "∞" if self.infinite_var.isChecked() else self.target_count_slider.value()
        self.write_log(f"Başlatılıyor — {mode} · Hedef: {target}", "info")
        self.start_btn.setEnabled(False); self.stop_btn.setEnabled(True)
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.worker_thread.start()

    def stop_tasks(self):
        self.running = False
        self.write_log("Durduruluyor...", "warn")
        self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False)


# ════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor("#0d0d12"))
    pal.setColor(QPalette.WindowText,      QColor("#e0e0e8"))
    pal.setColor(QPalette.Base,            QColor("#0f0f1a"))
    pal.setColor(QPalette.AlternateBase,   QColor("#13131f"))
    pal.setColor(QPalette.Text,            QColor("#e0e0e8"))
    pal.setColor(QPalette.Button,          QColor("#1a1a2e"))
    pal.setColor(QPalette.ButtonText,      QColor("#e0e0e8"))
    pal.setColor(QPalette.Highlight,       QColor("#7c3aed"))
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)
    w = App()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
