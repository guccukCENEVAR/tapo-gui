#!/usr/bin/env python3
"""Tapo Işık Kontrol — Tapo akıllı ışıklar için masaüstü arayüzü (PySide6 + tapo)."""

from __future__ import annotations

import asyncio
import ipaddress
import json
import math
import os
import socket
import sys
import threading
from pathlib import Path

from tapo import ApiClient
from PySide6.QtCore import QEasingCurve, QEvent, QLocale, QObject, QPoint, QPointF, QRectF, Qt, QTimer, QVariantAnimation, Signal
from PySide6.QtGui import (
    QAction, QColor, QFont, QFontMetrics, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient,
    QKeySequence, QShortcut,
)
from PySide6.QtWidgets import (
    QAbstractButton, QApplication, QColorDialog, QDialog, QDialogButtonBox, QFormLayout, QFrame,
    QGridLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox,
    QPushButton, QScrollArea, QSlider, QStackedWidget, QStyle, QStyleOptionSlider, QVBoxLayout, QWidget,
)

if sys.platform == "win32":
    CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "tapo-gui"
else:
    CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "tapo-gui"
CONFIG_FILE = CONFIG_DIR / "config.json"
# Paketlenmiş (PyInstaller) sürümde dosyalar _MEIPASS altında, betik olarak çalışırken yanında
APP_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
_ICO_FILE = APP_DIR / "assets" / "tapo-gui.ico"
ICON_FILE = _ICO_FILE if (sys.platform == "win32" and _ICO_FILE.exists()) else APP_DIR / "assets" / "tapo-gui.svg"

PRESET_COLORS = [
    ("color_red", 0, 100), ("color_orange", 30, 100), ("color_yellow", 55, 100), ("color_green", 120, 100),
    ("color_cyan", 175, 100), ("color_blue", 230, 100), ("color_purple", 275, 100), ("color_pink", 320, 80),
]

WHITE_PRESETS = [
    ("white_warm", 2700), ("white_natural", 4000), ("white_daylight", 5500), ("white_cool", 6500),
]

STRINGS: dict[str, dict[str, str]] = {
    "tr": {
        "app_title": "Tapo Işık Kontrol",
        "lights": "Işıklar",
        "off": "Kapalı",
        "turn_off_drag": "Kapat",
        "color_red": "Kırmızı",
        "color_orange": "Turuncu",
        "color_yellow": "Sarı",
        "color_green": "Yeşil",
        "color_cyan": "Turkuaz",
        "color_blue": "Mavi",
        "color_purple": "Mor",
        "color_pink": "Pembe",
        "white_warm": "Sıcak",
        "white_natural": "Doğal",
        "white_daylight": "Gün ışığı",
        "white_cool": "Soğuk",
        "value_tooltip": "{name}: {lo}–{hi} {unit} arası bir değer yazıp Enter'a basın",
        "unsupported_value_title": "Desteklenmeyen değer",
        "unsupported_value_body": "{name} için “{raw}” desteklenmiyor.\nBu cihaz {lo}–{hi} {unit} arasını destekliyor.",
        "tile_tooltip": "Tıkla: ayarlar · Sağ tık: hızlı menü · Basılı tutup yukarı/aşağı sürükle: parlaklık",
        "back_lights": "‹  Işıklar",
        "rename_light_tooltip": "Işığı yeniden adlandır",
        "brightness": "Parlaklık",
        "color": "Renk",
        "colors": "Renkler",
        "hue": "Renk tonu",
        "hue_short": "Ton",
        "saturation": "Doygunluk",
        "white_temp": "Beyaz ton",
        "white": "Beyaz",
        "custom_color_hint": " — yeniden adlandırmak/silmek için sağ tıklayın",
        "add_color_tooltip": "Yeni renk ekle (şu anki renkle başlar)",
        "pick_color_btn": "Renk seç…",
        "rename_ellipsis": "Yeniden adlandır…",
        "delete_color": "“{name}” rengini sil",
        "rename_title": "Yeniden adlandır",
        "rename_color_prompt": "Rengin yeni adı:",
        "add_color_dialog": "Eklenecek rengi seç",
        "color_name_title": "Renk adı",
        "color_name_prompt": "Bu renge bir ad verin:",
        "color_default_name": "Renk {n}",
        "color_exists": "Bu renk zaten kayıtlı.",
        "tapo_name_suffix": " · Tapo'daki adı: {name}",
        "cmd_failed": "{alias}: {what} başarısız — {err}",
        "cmd_ok": "{alias}: {what}",
        "turned_on": "açıldı",
        "turned_off": "kapatıldı",
        "cmd_brightness": "parlaklık {pct}",
        "cmd_color": "renk {h}°/{s}%",
        "cmd_white_temp": "beyaz ton {t}K",
        "pick_color_dialog": "Renk seç",
        "quick_rename": "✎  Yeniden adlandır",
        "quick_all_settings": "Tüm ayarlar  ›",
        "login_title": "TP-Link hesabı",
        "login_info": "Tapo ampuller yerel ağda bile TP-Link / Tapo hesabınızla\ndoğrulama ister. Tapo uygulamasındaki e-posta ve şifreyi girin.",
        "email": "E-posta",
        "password": "Şifre",
        "scan_network": "⟳  Ağda ara",
        "scanning": "⟳  Aranıyor…",
        "add_by_ip": "＋  IP ile ekle",
        "account": "Hesap",
        "lang_btn": "EN",
        "lang_tooltip": "Switch language to English",
        "turn_all_on": "Tümünü aç",
        "turn_all_off": "Tümünü kapat",
        "empty_state": "Henüz ışık yok.\n“Ağda ara” ya da “IP ile ekle” ile ekleyin.",
        "summary_count": "{n} ışık · {on} açık",
        "summary_waiting": "Işık bekleniyor",
        "connecting_saved": "Kayıtlı ışıklara bağlanılıyor…",
        "rename_light_title": "Işığı yeniden adlandır",
        "rename_light_prompt": "Yeni ad (boş bırakırsanız Tapo'daki ad kullanılır: “{name}”):",
        "renamed_status": "Ad değiştirildi: {alias}",
        "scanning_status": "Yerel ağda Tapo ışıkları aranıyor…",
        "scan_error": "Arama hatası: {err}",
        "scan_done": "{found} yeni ışık bulundu, {total} ışık listede.",
        "connect_failed": "{host} bağlanamadı: {reason}",
        "no_response_or_not_light": "yanıt yok ya da ışık değil",
        "add_ip_title": "IP ile ekle",
        "add_ip_prompt": "Işığın IP adresi (ör. 192.168.1.50):",
        "connecting_host": "{host} bağlanılıyor…",
    },
    "en": {
        "app_title": "Tapo Light Control",
        "lights": "Lights",
        "off": "Off",
        "turn_off_drag": "Off",
        "color_red": "Red",
        "color_orange": "Orange",
        "color_yellow": "Yellow",
        "color_green": "Green",
        "color_cyan": "Cyan",
        "color_blue": "Blue",
        "color_purple": "Purple",
        "color_pink": "Pink",
        "white_warm": "Warm",
        "white_natural": "Natural",
        "white_daylight": "Daylight",
        "white_cool": "Cool",
        "value_tooltip": "{name}: enter a value between {lo}–{hi} {unit} and press Enter",
        "unsupported_value_title": "Unsupported value",
        "unsupported_value_body": "“{raw}” is not supported for {name}.\nThis device supports {lo}–{hi} {unit}.",
        "tile_tooltip": "Click: settings · Right-click: quick menu · Hold & drag up/down: brightness",
        "back_lights": "‹  Lights",
        "rename_light_tooltip": "Rename light",
        "brightness": "Brightness",
        "color": "Color",
        "colors": "Colors",
        "hue": "Hue",
        "hue_short": "Hue",
        "saturation": "Saturation",
        "white_temp": "White Temperature",
        "white": "White",
        "custom_color_hint": " — right-click to rename/delete",
        "add_color_tooltip": "Add new color (starts with current color)",
        "pick_color_btn": "Pick color…",
        "rename_ellipsis": "Rename…",
        "delete_color": "Delete “{name}”",
        "rename_title": "Rename",
        "rename_color_prompt": "New color name:",
        "add_color_dialog": "Choose a color to add",
        "color_name_title": "Color name",
        "color_name_prompt": "Give this color a name:",
        "color_default_name": "Color {n}",
        "color_exists": "This color is already saved.",
        "tapo_name_suffix": " · Tapo name: {name}",
        "cmd_failed": "{alias}: {what} failed — {err}",
        "cmd_ok": "{alias}: {what}",
        "turned_on": "turned on",
        "turned_off": "turned off",
        "cmd_brightness": "brightness {pct}",
        "cmd_color": "color {h}°/{s}%",
        "cmd_white_temp": "white temp {t}K",
        "pick_color_dialog": "Pick color",
        "quick_rename": "✎  Rename",
        "quick_all_settings": "All settings  ›",
        "login_title": "TP-Link Account",
        "login_info": "Tapo lights require your TP-Link / Tapo account credentials\neven on the local network. Enter the email and password from the Tapo app.",
        "email": "Email",
        "password": "Password",
        "scan_network": "⟳  Scan network",
        "scanning": "⟳  Scanning…",
        "add_by_ip": "＋  Add by IP",
        "account": "Account",
        "lang_btn": "TR",
        "lang_tooltip": "Dili Türkçeye çevir",
        "turn_all_on": "Turn all on",
        "turn_all_off": "Turn all off",
        "empty_state": "No lights yet.\nClick “Scan network” or “Add by IP” to get started.",
        "summary_count": "{n} lights · {on} on",
        "summary_waiting": "Waiting for lights",
        "connecting_saved": "Connecting to saved lights…",
        "rename_light_title": "Rename light",
        "rename_light_prompt": "New name (leave empty to use Tapo name: “{name}”):",
        "renamed_status": "Renamed to: {alias}",
        "scanning_status": "Scanning local network for Tapo lights…",
        "scan_error": "Scan error: {err}",
        "scan_done": "Found {found} new light(s), {total} total.",
        "connect_failed": "Failed to connect to {host}: {reason}",
        "no_response_or_not_light": "no response or not a light",
        "add_ip_title": "Add by IP",
        "add_ip_prompt": "Light IP address (e.g. 192.168.1.50):",
        "connecting_host": "Connecting to {host}…",
    },
}

_LANG = "tr"


def get_lang() -> str:
    return _LANG


def set_lang(lang: str) -> None:
    global _LANG
    _LANG = lang if lang in STRINGS else "en"


def detect_default_lang() -> str:
    return "tr" if QLocale.system().name().lower().startswith("tr") else "en"


def tr(key: str, **kw) -> str:
    text = STRINGS.get(_LANG, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))
    return text.format(**kw) if kw else text


def fmt_pct(v: int) -> str:
    return f"%{v}" if _LANG == "tr" else f"{v}%"


# ---------------------------------------------------------------- yapılandırma
def load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"username": "", "password": "", "hosts": []}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    if os.name != "nt":
        CONFIG_FILE.chmod(0o600)  # şifre içerdiği için yalnızca kullanıcı okuyabilsin


class ColorStore(QObject):
    """Kullanıcının eklediği renkler. Yapılandırma dosyasında "custom_colors" altında saklanır."""

    changed = Signal()

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = cfg

    @property
    def colors(self) -> list[dict]:
        return self.cfg.setdefault("custom_colors", [])

    def add(self, h: int, s: int, name: str) -> bool:
        if any(c["h"] == h and c["s"] == s for c in self.colors):
            return False
        self.colors.append({"name": name, "h": h, "s": s})
        save_config(self.cfg)
        self.changed.emit()
        return True

    def rename(self, index: int, name: str):
        self.colors[index]["name"] = name
        save_config(self.cfg)
        self.changed.emit()

    def remove(self, index: int):
        del self.colors[index]
        save_config(self.cfg)
        self.changed.emit()


# ---------------------------------------------------------------- async köprüsü
class AsyncRunner(QObject):
    """asyncio döngüsünü ayrı bir thread'de çalıştırır, sonuçları Qt sinyaliyle döndürür."""

    _done = Signal(object, object, object)  # callback, sonuç, hata

    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        self._done.connect(self._dispatch)

    def run(self, coro, on_done=None):
        fut = asyncio.run_coroutine_threadsafe(coro, self.loop)

        def finished(f):
            try:
                self._done.emit(on_done, f.result(), None)
            except Exception as e:  # noqa: BLE001
                self._done.emit(on_done, None, e)

        fut.add_done_callback(finished)

    @staticmethod
    def _dispatch(cb, result, err):
        if cb:
            cb(result, err)


TEMP_MIN, TEMP_MAX = 2500, 6500
# discovery sonucunun türü -> renk desteği
COLOR_KINDS = {"ColorLight", "RgbLightStrip", "RgbicLightStrip"}
LIGHT_KINDS = COLOR_KINDS | {"Light"}


class TapoLight:
    """tapo kütüphanesinin handler'ı etrafında, arayüzün kullandığı sade bir sarmalayıcı."""

    def __init__(self, host: str, kind: str, handler):
        self.host = host
        self.kind = kind
        self.handler = handler
        self.info: dict = {}
        self.custom_name: str | None = None  # bu uygulamada verilen ad (cihaza yazılmaz)

    # ---- durum
    @property
    def device_name(self):
        return self.info.get("nickname") or self.host

    @property
    def alias(self):
        return self.custom_name or self.device_name

    @property
    def model(self):
        return self.info.get("model", "")

    @property
    def is_on(self):
        return bool(self.info.get("device_on"))

    @property
    def brightness(self):
        return self.info.get("brightness") or 100

    @property
    def hue(self):
        return self.info.get("hue") or 0

    @property
    def saturation(self):
        return self.info.get("saturation") or 100

    @property
    def color_temp(self):
        return self.info.get("color_temp") or 0  # 0 = renkli modda

    @property
    def has_color(self):
        return self.kind in COLOR_KINDS

    @property
    def has_temp(self):
        return "color_temp" in self.info

    # ---- komutlar
    async def _call(self, fn, *args):
        try:
            return await fn(*args)
        except Exception:  # noqa: BLE001 — oturum düşmüş olabilir, bir kez tazeleyip tekrar dene
            await self.handler.refresh_session()
            return await fn(*args)

    async def update(self):
        info = await self._call(self.handler.get_device_info)
        self.info = info.to_dict()

    async def turn_on(self):
        await self._call(self.handler.on)
        self.info["device_on"] = True

    async def turn_off(self):
        await self._call(self.handler.off)
        self.info["device_on"] = False

    async def set_brightness(self, v):
        await self._call(self.handler.set_brightness, v)

    async def set_hs(self, h, s):
        await self._call(self.handler.set_hue_saturation, h % 360, max(1, s))

    async def set_color_temp(self, t):
        await self._call(self.handler.set_color_temperature, t)


async def probe(client: ApiClient, target: str, timeout_s: int = 3) -> list[TapoLight]:
    """Bir IP'yi (veya yayın adresini) sorgular, bulunan ışıkları bağlanmış halde döndürür."""
    lights = []
    async for r in await client.discover_devices(target, timeout_s):
        try:
            d = r.get()
        except Exception:  # noqa: BLE001
            continue
        kind = type(d).__name__
        if kind not in LIGHT_KINDS:
            continue  # priz, hub vb. ışık olmayan cihazları atla
        ip = d.ip if hasattr(d, "ip") else d.address[0]
        light = TapoLight(ip, kind, d.handler)
        light.info = d.device_info.to_dict()
        lights.append(light)
    return lights


def local_networks() -> list[ipaddress.IPv4Network]:
    """Bilgisayarın bağlı olduğu yerel /24 ağ(lar)ı."""
    nets = set()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sk:
            sk.connect(("10.255.255.255", 1))  # paket gönderilmez, sadece yerel IP öğrenilir
            nets.add(ipaddress.ip_network(f"{sk.getsockname()[0]}/24", strict=False))
    except OSError:
        pass
    return [n for n in nets if n.is_private]


# ---------------------------------------------------------------- tema
BG = "#0f1115"
SURFACE = "#171a21"
SURFACE2 = "#20242d"
BORDER = "#2a2f3a"
TEXT = "#e9ebf1"
MUTED = "#8b91a1"
ACCENT = "#ffb547"

STYLE = f"""
QMainWindow, QStackedWidget, QScrollArea, QScrollArea > QWidget > QWidget, #page {{ background:{BG}; }}
QWidget {{ color:{TEXT}; font-size:13px; }}
QLabel#h1 {{ font-size:26px; font-weight:700; }}
QLabel#h2 {{ font-size:20px; font-weight:700; }}
QLabel#muted {{ color:{MUTED}; }}
QLabel#section {{ color:{MUTED}; font-size:11px; font-weight:600; letter-spacing:1px; }}
QFrame#panel {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:16px; }}
QPushButton {{ background:{SURFACE2}; border:1px solid {BORDER}; border-radius:10px; padding:7px 14px; }}
QPushButton:hover {{ background:#2a2f3a; border-color:#3a4150; }}
QPushButton:pressed {{ background:#323846; }}
QPushButton:disabled {{ color:{MUTED}; }}
QPushButton#ghost {{ background:transparent; border:none; font-size:15px; padding:6px 8px; }}
QPushButton#ghost:hover {{ background:{SURFACE2}; }}
QLineEdit {{ background:{SURFACE2}; border:1px solid {BORDER}; border-radius:8px; padding:4px 6px; selection-background-color:{ACCENT}; selection-color:#000; }}
QLineEdit:focus {{ border-color:{ACCENT}; }}
QSlider::groove:horizontal {{ height:10px; border-radius:5px; background:{SURFACE2}; }}
QSlider::sub-page:horizontal {{ border-radius:5px; background:transparent; }}
QSlider::handle:horizontal {{ background:white; border:2px solid rgba(0,0,0,60); width:18px; height:18px; margin:-6px 0; border-radius:11px; }}
QScrollBar:vertical {{ background:transparent; width:10px; }}
QScrollBar::handle:vertical {{ background:{SURFACE2}; border-radius:5px; min-height:30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height:0; }}
QMenu {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:8px; padding:4px; }}
QMenu::item {{ padding:6px 16px; border-radius:6px; }}
QMenu::item:selected {{ background:{SURFACE2}; }}
QToolTip {{ background:{SURFACE}; color:{TEXT}; border:1px solid {BORDER}; padding:4px; }}
QStatusBar {{ background:{BG}; color:{MUTED}; }}
QDialog {{ background:{SURFACE}; }}
"""


# ---------------------------------------------------------------- renk yardımcıları
def kelvin_to_qcolor(k: int) -> QColor:
    """Renk sıcaklığını (K) yaklaşık RGB'ye çevirir (Tanner Helland yöntemi)."""
    t = k / 100
    if t <= 66:
        r = 255
        g = 99.4708025861 * math.log(t) - 161.1195681661
        b = 0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307
    else:
        r = 329.698727446 * (t - 60) ** -0.1332047592
        g = 288.1221695283 * (t - 60) ** -0.0755148492
        b = 255
    clamp = lambda v: int(max(0, min(255, v)))  # noqa: E731
    return QColor(clamp(r), clamp(g), clamp(b))


def light_qcolor(dev: TapoLight) -> QColor:
    """Işığın şu an yandığı renk (tam parlaklıkta)."""
    if dev.color_temp:
        return kelvin_to_qcolor(dev.color_temp)
    if dev.has_color:
        return QColor.fromHsv(dev.hue % 360, round(dev.saturation * 2.55), 255)
    return kelvin_to_qcolor(2700)


def luminance(c: QColor) -> float:
    return 0.2126 * c.redF() + 0.7152 * c.greenF() + 0.0722 * c.blueF()


def mode_text(dev: TapoLight) -> str:
    if not dev.is_on:
        return tr("off")
    if dev.color_temp:
        return f"{fmt_pct(dev.brightness)} · {dev.color_temp}K"
    if dev.has_color:
        return f"{fmt_pct(dev.brightness)} · {dev.hue}°"
    return fmt_pct(dev.brightness)


# ---------------------------------------------------------------- küçük bileşenler
class JumpSlider(QSlider):
    """Çubuğun herhangi bir yerine tıklanınca tutamaç doğrudan oraya gider (sonra sürüklenebilir)."""

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            handle = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
            pos = ev.position().toPoint()
            if not handle.contains(pos):
                groove = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
                span = max(1, groove.width() - handle.width())
                x = pos.x() - groove.x() - handle.width() // 2
                self.setValue(QStyle.sliderValueFromPosition(
                    self.minimum(), self.maximum(), x, span, opt.upsideDown))
        super().mousePressEvent(ev)  # tutamaç artık imlecin altında: sürükleme devam eder


def make_slider(lo: int, hi: int, groove: str | None = None) -> QSlider:
    s = JumpSlider(Qt.Horizontal)
    s.setRange(lo, hi)
    s.setMinimumHeight(26)
    if groove:
        s.setStyleSheet(f"QSlider::groove:horizontal{{background:{groove};}}")
    return s


class ValueBox(QLineEdit):
    """Sürgüye bağlı, klavyeyle değer girilebilen kutu. Aralık dışı/geçersiz girişte hata gösterir."""

    def __init__(self, slider: QSlider, name_key: str, unit: str):
        super().__init__()
        self.slider, self.name_key, self.unit = slider, name_key, unit
        self.setFixedWidth(64)
        self.setAlignment(Qt.AlignRight)
        self.retranslate()
        slider.valueChanged.connect(self._show)
        self.returnPressed.connect(self._commit)
        self._show(slider.value())

    def retranslate(self):
        self.setToolTip(tr(
            "value_tooltip", name=tr(self.name_key),
            lo=self.slider.minimum(), hi=self.slider.maximum(), unit=self.unit,
        ))

    def _show(self, v):
        if not self.hasFocus():
            self.setText(str(v))

    def focusOutEvent(self, ev):
        super().focusOutEvent(ev)
        self.setText(str(self.slider.value()))  # onaylanmamış yazıyı geri al

    def _commit(self):
        text = self.text().strip().strip("%°Kk ")
        lo, hi = self.slider.minimum(), self.slider.maximum()
        try:
            v = int(text)
        except ValueError:
            v = None
        if v is None or not lo <= v <= hi:
            QMessageBox.warning(
                self, tr("unsupported_value_title"),
                tr("unsupported_value_body", name=tr(self.name_key), raw=self.text(),
                   lo=lo, hi=hi, unit=self.unit))
            self.setText(str(self.slider.value()))
            self.selectAll()
            return
        self.slider.setValue(v)
        self.setText(str(v))
        self.selectAll()


class ToggleSwitch(QAbstractButton):
    """iOS tarzı kaydırmalı aç/kapa düğmesi (QCheckBox ile aynı sinyaller)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(52, 30)
        self.accent = QColor(ACCENT)
        self._pos = 0.0
        self._anim = QVariantAnimation(self, duration=160, easingCurve=QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._set_pos)
        self.toggled.connect(self._animate)

    def _set_pos(self, v):
        self._pos = v
        self.update()

    def _animate(self, on):
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(1.0 if on else 0.0)
        self._anim.start()

    def set_accent(self, c: QColor):
        self.accent = QColor(c)
        self.update()

    def paintEvent(self, _ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(1, 1, -1, -1)
        off = QColor(SURFACE2)
        on = self.accent
        track = QColor(
            round(off.red() + (on.red() - off.red()) * self._pos),
            round(off.green() + (on.green() - off.green()) * self._pos),
            round(off.blue() + (on.blue() - off.blue()) * self._pos))
        p.setPen(QPen(QColor(BORDER), 1))
        p.setBrush(track)
        p.drawRoundedRect(r, r.height() / 2, r.height() / 2)
        d = r.height() - 6
        x = r.x() + 3 + (r.width() - d - 6) * self._pos
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 50))
        p.drawEllipse(QRectF(x, r.y() + 4, d, d))
        p.setBrush(QColor("white"))
        p.drawEllipse(QRectF(x, r.y() + 3, d, d))


class LightOrb(QWidget):
    """Detay sayfasındaki büyük, ışığın renginde parlayan küre."""

    def __init__(self, dev_getter):
        super().__init__()
        self.dev_getter = dev_getter
        self.setFixedSize(190, 190)

    def paintEvent(self, _ev):
        dev = self.dev_getter()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QPointF(self.width() / 2, self.height() / 2)
        core = 58
        if dev.is_on:
            col = light_qcolor(dev)
            k = 0.35 + 0.65 * dev.brightness / 100
            glow = QRadialGradient(c, self.width() / 2)
            g0 = QColor(col)
            g0.setAlphaF(0.55 * k)
            g1 = QColor(col)
            g1.setAlphaF(0.0)
            glow.setColorAt(0.25, g0)
            glow.setColorAt(1.0, g1)
            p.setPen(Qt.NoPen)
            p.setBrush(glow)
            p.drawEllipse(c, self.width() / 2, self.height() / 2)
            body = QRadialGradient(QPointF(c.x() - 18, c.y() - 18), core * 1.6)
            body.setColorAt(0, QColor(255, 255, 255))
            body.setColorAt(0.35, col.lighter(110))
            body.setColorAt(1, col.darker(130))
            p.setBrush(body)
        else:
            p.setPen(QPen(QColor(BORDER), 2))
            p.setBrush(QColor(SURFACE2))
        p.drawEllipse(c, core, core)


class LightTile(QWidget):
    """Ana ekrandaki ışık kutucuğu.

    Işık açıkken kutucuk alttan yukarı, parlaklık yüzdesi kadar ışığın rengiyle dolar.
    Basılı tutup yukarı/aşağı sürüklemek (ya da fare tekerleği) parlaklığı doğrudan ayarlar;
    en alta (%0) çekilirse ışık kapanır.
    """

    clicked = Signal()
    powerClicked = Signal()
    menuRequested = Signal(QPoint)  # sağ tık: hızlı menü (ekran konumu)

    W, H = 196, 168
    DRAG_START = 6  # bu kadar pikselden az hareket tıklama sayılır

    def __init__(self, card: "LightCard"):
        super().__init__()
        self.card = card
        self.setFixedSize(self.W, self.H)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover)
        self.retranslate()
        self._hover = False
        self._press = None  # (y, başlangıç parlaklığı) — sürükleme için
        self._drag = None  # sürüklenirken gösterilen parlaklık (0 = kapat)
        card.changed.connect(self.update)

    def retranslate(self):
        self.setToolTip(tr("tile_tooltip"))
        self.update()

    def power_rect(self) -> QRectF:
        return QRectF(self.W - 50, 14, 36, 36)

    def event(self, ev):
        if ev.type() in (QEvent.HoverEnter, QEvent.HoverLeave):
            self._hover = ev.type() == QEvent.HoverEnter
            self.update()
        return super().event(ev)

    # ---- parlaklık ayarı (sürükleme / tekerlek)
    def _set_level(self, v: int):
        """0–100 arası seviyeyi anında gösterir, cihaza (gecikmeli) gönderir."""
        dev, card = self.card.dev, self.card
        if v >= 1:
            dev.info.update(brightness=v, device_on=True)
            card.bright.setValue(v)  # kartın kendi debounce'u gönderir ve gerekirse ışığı açar
        else:
            t = card._timers.get("bright")
            if t:
                t.stop()  # bekleyen parlaklık komutunu iptal et, bırakınca kapatılacak
            dev.info["device_on"] = False
        card.changed.emit()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton and not self.power_rect().contains(ev.position()):
            dev = self.card.dev
            self._press = (ev.position().y(), dev.brightness if dev.is_on else 0)

    def mouseMoveEvent(self, ev):
        if self._press is None:
            return
        y0, start = self._press
        dy = y0 - ev.position().y()  # yukarı = pozitif
        if self._drag is None and abs(dy) < self.DRAG_START:
            return
        if self._drag is None:
            self.card.external_drag = True
            self.setCursor(Qt.SizeVerCursor)
        v = max(0, min(100, round(start + dy / (self.H * 0.9) * 100)))
        if v != self._drag:
            self._drag = v
            self._set_level(v)

    def mouseReleaseEvent(self, ev):
        if ev.button() != Qt.LeftButton:
            return
        dragged, final = self._drag is not None, self._drag
        self._press = self._drag = None
        self.card.external_drag = False
        self.setCursor(Qt.PointingHandCursor)
        if dragged:
            if final == 0 and self.card.power.isChecked():
                self.card.power.setChecked(False)  # en alta çekildi: kapat
            self.update()
            return
        if self.rect().contains(ev.position().toPoint()):
            if self.power_rect().contains(ev.position()):
                self.powerClicked.emit()
            else:
                self.clicked.emit()

    def contextMenuEvent(self, ev):
        self.menuRequested.emit(ev.globalPos())

    def wheelEvent(self, ev):
        steps = ev.angleDelta().y() / 120
        if not steps:
            return
        dev = self.card.dev
        base = dev.brightness if dev.is_on else 0
        v = max(1, min(100, round(base + steps * 5)))
        self._set_level(v)
        ev.accept()

    # ---- çizim
    def paintEvent(self, _ev):
        dev = self.card.dev
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        on = dev.is_on
        level = self._drag if self._drag is not None else (dev.brightness if on else 0)
        on = on and level > 0
        col = light_qcolor(dev)

        shape = QPainterPath()
        shape.addRoundedRect(r, 22, 22)

        # zemin: koyu; açıkken hafif ışık renginde ton
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(SURFACE))
        p.drawPath(shape)
        fill_top = r.bottom() - r.height() * level / 100 if on else r.bottom() + 1
        if on:
            tint = QColor(col)
            tint.setAlphaF(0.10)
            p.setBrush(tint)
            p.drawPath(shape)
            # parlaklık kadar alttan dolan renk
            p.save()
            p.setClipPath(shape)
            g = QLinearGradient(0, fill_top, 0, r.bottom())
            g.setColorAt(0, col)
            g.setColorAt(1, QColor(col).darker(150))
            p.fillRect(QRectF(r.left(), fill_top, r.width(), r.bottom() - fill_top + 1), g)
            if fill_top > r.top() + 2:  # dolum çizgisinde ince parlak kenar
                p.fillRect(QRectF(r.left(), fill_top, r.width(), 2), QColor(255, 255, 255, 90))
            p.restore()
        p.setPen(QPen(QColor("#4a5263" if self._hover else BORDER), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawPath(shape)

        # Bir öğe renkli dolumun içindeyse metin rengini dolumun rengine göre seç
        dark_on_fill = luminance(col) > 0.6

        def colors_at(y):
            covered = on and y > fill_top
            if covered and dark_on_fill:
                return QColor("#15171c"), QColor(21, 23, 28, 180)
            return QColor(TEXT), QColor("#dfe3ea" if covered else MUTED)

        # simge: ampul ya da şerit
        icon = QRectF(18, 18, 40, 40)
        p.setPen(Qt.NoPen)
        if on:
            glow = QRadialGradient(icon.center(), 30)
            gc = QColor(col)
            gc.setAlphaF(0.7)
            glow.setColorAt(0, gc)
            gc.setAlphaF(0.0)
            glow.setColorAt(1, gc)
            p.setBrush(glow)
            p.drawEllipse(icon.center(), 30, 30)
        p.setBrush(QColor(255, 255, 255, 235) if on else QColor(SURFACE2))
        if "Strip" in dev.kind:
            for i in range(4):
                p.drawRoundedRect(QRectF(icon.x() + i * 10.5, icon.y() + 12 + (i % 2) * 6, 8, 14), 3, 3)
        else:
            p.drawEllipse(icon.adjusted(4, 0, -4, -8))
            p.drawRoundedRect(QRectF(icon.center().x() - 7, icon.bottom() - 9, 14, 8), 3, 3)

        # güç düğmesi
        pr = self.power_rect()
        fg_pw, _ = colors_at(pr.center().y())
        p.setBrush(QColor(255, 255, 255, 50) if on else QColor(SURFACE2))
        p.setPen(QPen(QColor(255, 255, 255, 80) if on else QColor(BORDER), 1))
        p.drawEllipse(pr)
        p.setPen(QPen(fg_pw if on else QColor(MUTED), 2.2, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        c = pr.center()
        p.drawArc(QRectF(c.x() - 8, c.y() - 7, 16, 16), 120 * 16, 300 * 16)
        p.drawLine(QPointF(c.x(), c.y() - 9), QPointF(c.x(), c.y() - 1))

        # sürüklerken büyük yüzde
        if self._drag is not None:
            big = QFont(self.font())
            big.setPixelSize(30)
            big.setBold(True)
            p.setFont(big)
            p.setPen(colors_at(86)[0])
            p.drawText(QRectF(18, 64, self.W - 36, 40), Qt.AlignLeft | Qt.AlignVCenter,
                       fmt_pct(self._drag) if self._drag else tr("turn_off_drag"))

        # yazılar
        name_rect = QRectF(18, self.H - 64, self.W - 36, 24)
        sub_rect = QRectF(18, self.H - 40, self.W - 36, 22)
        f = QFont(self.font())
        f.setPixelSize(15)
        f.setBold(True)
        p.setFont(f)
        p.setPen(colors_at(name_rect.center().y())[0])
        p.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter,
                   QFontMetrics(f).elidedText(dev.alias, Qt.ElideRight, int(name_rect.width())))
        f2 = QFont(self.font())
        f2.setPixelSize(13)
        p.setFont(f2)
        p.setPen(colors_at(sub_rect.center().y())[1])
        p.drawText(sub_rect, Qt.AlignLeft | Qt.AlignVCenter, mode_text(dev) if on else tr("off"))


class FlowGrid(QWidget):
    """Kutucukları pencere genişliğine göre satırlara dizen ızgara."""

    def __init__(self, item_w: int, gap: int = 16):
        super().__init__()
        self.item_w, self.gap = item_w, gap
        self.items: list[QWidget] = []
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(gap)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._cols = 0

    def add(self, w: QWidget):
        self.items.append(w)
        self._relayout(force=True)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._relayout()

    def _relayout(self, force=False):
        cols = max(1, (self.width() + self.gap) // (self.item_w + self.gap))
        if cols == self._cols and not force:
            return
        self._cols = cols
        for w in self.items:
            self.grid.removeWidget(w)
        for i, w in enumerate(self.items):
            self.grid.addWidget(w, i // cols, i % cols)


def panel(title: str | None = None) -> tuple[QFrame, QVBoxLayout]:
    f = QFrame()
    f.setObjectName("panel")
    lay = QVBoxLayout(f)
    lay.setContentsMargins(18, 14, 18, 16)
    lay.setSpacing(10)
    f.title_label = None
    if title:
        t = QLabel(title.upper())
        t.setObjectName("section")
        lay.addWidget(t)
        f.title_label = t
    return f, lay


# ---------------------------------------------------------------- ışık detay sayfası
class LightCard(QWidget):
    """Bir ışığın tüm ayarları. Ana ekrandaki kutucuk bu sayfayı açar."""

    changed = Signal()  # ışığın durumu (yerel ya da cihazdan) değişti
    back = Signal()
    renameRequested = Signal()

    PER_ROW = 10

    def __init__(self, dev: TapoLight, runner: AsyncRunner, status_cb, store: ColorStore):
        super().__init__()
        self.setObjectName("page")
        self.store = store
        self.dev = dev
        self.runner = runner
        self.status = status_cb
        self._syncing = False
        self._timers = {}  # gönderimleri sürgü kısa süre durana kadar beklet (debounce)
        self.external_drag = False  # ana ekrandaki kutucuk sürükleniyor mu
        self._section_labels: list[tuple[QLabel, str]] = []
        self._white_buttons: list[tuple[QPushButton, str]] = []
        self._value_boxes: list[ValueBox] = []

        self.has_color = dev.has_color
        self.has_temp = dev.has_temp
        self.has_dim = True

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        lay = QVBoxLayout(body)
        lay.setContentsMargins(24, 16, 24, 24)
        lay.setSpacing(14)

        # üst çubuk
        head = QHBoxLayout()
        self.btn_back = QPushButton(tr("back_lights"))
        self.btn_back.setObjectName("ghost")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.clicked.connect(self.back.emit)
        head.addWidget(self.btn_back)
        head.addStretch()
        self.power = ToggleSwitch()
        self.power.toggled.connect(self._on_power)
        head.addWidget(self.power)
        lay.addLayout(head)

        # başlık + küre
        self.title = QLabel()
        self.title.setObjectName("h1")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("muted")
        tbox = QVBoxLayout()
        tbox.setSpacing(2)
        trow = QHBoxLayout()
        trow.addWidget(self.title)
        self.btn_rename = QPushButton("✎")
        self.btn_rename.setObjectName("ghost")
        self.btn_rename.setCursor(Qt.PointingHandCursor)
        self.btn_rename.setToolTip(tr("rename_light_tooltip"))
        self.btn_rename.clicked.connect(self.renameRequested.emit)
        trow.addWidget(self.btn_rename)
        trow.addStretch()
        tbox.addLayout(trow)
        tbox.addWidget(self.subtitle)
        lay.addLayout(tbox)
        self.orb = LightOrb(lambda: self.dev)
        self.mode = QLabel()
        self.mode.setObjectName("muted")
        self.mode.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.orb, 0, Qt.AlignHCenter)
        lay.addWidget(self.mode)

        # parlaklık
        if self.has_dim:
            box, bl = panel(tr("brightness"))
            self._section_labels.append((box.title_label, "brightness"))
            self.bright = make_slider(1, 100)
            self.bright_lbl = ValueBox(self.bright, "brightness", "%")
            self._value_boxes.append(self.bright_lbl)
            self.bright.valueChanged.connect(lambda _: self._debounce("bright", self._send_brightness))
            bl.addLayout(self._slider_row(self.bright, self.bright_lbl, "%"))
            lay.addWidget(box)

        # renk
        if self.has_color:
            box, cl = panel(tr("color"))
            self._section_labels.append((box.title_label, "color"))
            self.hue = make_slider(0, 360, "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #f00,stop:0.17 #ff0,"
                                           "stop:0.33 #0f0,stop:0.5 #0ff,stop:0.67 #00f,stop:0.83 #f0f,stop:1 #f00)")
            self.sat = make_slider(1, 100)
            self.hue_lbl = ValueBox(self.hue, "hue", "°")
            self.sat_lbl = ValueBox(self.sat, "saturation", "%")
            self._value_boxes.extend([self.hue_lbl, self.sat_lbl])
            for s in (self.hue, self.sat):
                s.valueChanged.connect(lambda _: self._debounce("hsv", self._send_hsv))
                s.valueChanged.connect(lambda _: self._update_swatch())
            self.lbl_hue = self._caption(tr("hue_short"))
            cl.addWidget(self.lbl_hue)
            cl.addLayout(self._slider_row(self.hue, self.hue_lbl, "°"))
            self.lbl_sat = self._caption(tr("saturation"))
            cl.addWidget(self.lbl_sat)
            cl.addLayout(self._slider_row(self.sat, self.sat_lbl, "%"))

            # Hazır + kullanıcı renkleri; çok renk olursa alt satıra geçer
            cl.addSpacing(4)
            self.presets_box = QWidget()
            self.presets_grid = QGridLayout(self.presets_box)
            self.presets_grid.setContentsMargins(0, 0, 0, 0)
            self.presets_grid.setSpacing(8)
            cl.addWidget(self.presets_box)
            self._build_presets()
            store.changed.connect(self._build_presets)
            lay.addWidget(box)

        # beyaz ton
        if self.has_temp:
            box, tl = panel(tr("white_temp"))
            self._section_labels.append((box.title_label, "white_temp"))
            self.temp = make_slider(TEMP_MIN, TEMP_MAX, "qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                                                          "stop:0 #ff9d3c,stop:0.5 #fff1dc,stop:1 #cddcff)")
            self.temp_lbl = ValueBox(self.temp, "white_temp", "K")
            self._value_boxes.append(self.temp_lbl)
            self.temp.valueChanged.connect(lambda _: self._debounce("temp", self._send_temp))
            tl.addLayout(self._slider_row(self.temp, self.temp_lbl, "K"))
            row = QHBoxLayout()
            for key, k in WHITE_PRESETS:
                b = QPushButton(tr(key))
                b.setCursor(Qt.PointingHandCursor)
                b.clicked.connect(lambda _=False, k=k: self.temp.setValue(k))
                row.addWidget(b)
                self._white_buttons.append((b, key))
            tl.addLayout(row)
            lay.addWidget(box)

        lay.addStretch()
        self.sync_from_device()

    def retranslate(self):
        self.btn_back.setText(tr("back_lights"))
        self.btn_rename.setToolTip(tr("rename_light_tooltip"))
        for lbl, key in self._section_labels:
            lbl.setText(tr(key).upper())
        for vb in self._value_boxes:
            vb.retranslate()
        if self.has_color:
            self.lbl_hue.setText(tr("hue_short"))
            self.lbl_sat.setText(tr("saturation"))
            self._build_presets()
        for btn, key in self._white_buttons:
            btn.setText(tr(key))
        self._refresh_visuals()

    # ---- yerleşim yardımcıları
    @staticmethod
    def _caption(text):
        l = QLabel(text)
        l.setObjectName("muted")
        return l

    @staticmethod
    def _slider_row(slider, box, unit):
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(slider, 1)
        row.addWidget(box)
        u = QLabel(unit)
        u.setObjectName("muted")
        u.setFixedWidth(14)
        row.addWidget(u)
        return row

    # ---- renk düğmeleri
    def _swatch_button(self, name, h, s):
        b = QPushButton()
        b.setToolTip(f"{name} ({h}°, {fmt_pct(s)})")
        b.setFixedSize(34, 34)
        b.setCursor(Qt.PointingHandCursor)
        c = QColor.fromHsv(h % 360, round(s * 2.55), 255)
        b.setStyleSheet(f"QPushButton{{background:{c.name()};border-radius:17px;border:2px solid rgba(255,255,255,40);padding:0;}}"
                        f"QPushButton:hover{{border:2px solid white;}}")
        b.clicked.connect(lambda _=False, h=h, s=s: self._apply_hs(h, s))
        return b

    def _build_presets(self):
        self.fill_swatches(self.presets_grid, self.PER_ROW, self._add_color, self._pick_color)

    def fill_swatches(self, g: QGridLayout, per_row: int, add_slot, pick_slot=None):
        """Hazır + kayıtlı renk düğmelerini verilen ızgaraya dizer (ayar sayfası ve hızlı menü)."""
        while g.count():
            g.takeAt(0).widget().deleteLater()
        buttons = [self._swatch_button(tr(k), h, s) for k, h, s in PRESET_COLORS]
        for i, c in enumerate(self.store.colors):
            b = self._swatch_button(c["name"], c["h"], c["s"])
            b.setToolTip(b.toolTip() + tr("custom_color_hint"))
            b.setContextMenuPolicy(Qt.CustomContextMenu)
            b.customContextMenuRequested.connect(lambda _p, i=i, b=b: self._color_menu(i, b))
            buttons.append(b)
        add = QPushButton("+")
        add.setFixedSize(34, 34)
        add.setCursor(Qt.PointingHandCursor)
        add.setToolTip(tr("add_color_tooltip"))
        add.setStyleSheet(f"QPushButton{{border-radius:17px;border:2px dashed {MUTED};background:transparent;"
                          f"font-size:18px;padding:0;color:{MUTED};}}QPushButton:hover{{color:white;border-color:white;}}")
        add.clicked.connect(add_slot)
        buttons.append(add)
        for i, b in enumerate(buttons):
            g.addWidget(b, i // per_row, i % per_row)
        if pick_slot:
            pick = QPushButton(tr("pick_color_btn"))
            pick.setCursor(Qt.PointingHandCursor)
            pick.clicked.connect(pick_slot)
            g.addWidget(pick, 0, per_row + 1)
        g.setColumnStretch(per_row, 1)

    def _color_menu(self, index, button):
        c = self.store.colors[index]
        menu = QMenu(self)
        ren = QAction(tr("rename_ellipsis"), menu)
        ren.triggered.connect(lambda: self._rename_color(index))
        rm = QAction(tr("delete_color", name=c["name"]), menu)
        rm.triggered.connect(lambda: self.store.remove(index))
        menu.addAction(ren)
        menu.addAction(rm)
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    def _rename_color(self, index):
        old = self.store.colors[index]["name"]
        name, ok = QInputDialog.getText(self, tr("rename_title"), tr("rename_color_prompt"), text=old)
        if ok and name.strip() and name.strip() != old:
            self.store.rename(index, name.strip())

    def _add_color(self):
        start = QColor.fromHsv(self.hue.value() % 360, round(self.sat.value() * 2.55), 255)
        c = QColorDialog.getColor(start, self, tr("add_color_dialog"))
        if not c.isValid():
            return
        h, s8, _v, _a = c.getHsv()
        h, s = max(h, 0), max(1, round(s8 / 2.55))
        default_name = tr("color_default_name", n=len(self.store.colors) + 1)
        name, ok = QInputDialog.getText(self, tr("color_name_title"), tr("color_name_prompt"), text=default_name)
        if not ok:
            return
        if not self.store.add(h, s, name.strip() or default_name):
            self.status(tr("color_exists"))
        self._apply_hs(h, s)

    # ---- durum -> arayüz
    def sync_from_device(self):
        # Kullanıcı sürgüyü sürüklerken ya da gönderim beklerken arayüzü ezme
        if self.external_drag or any(s.isSliderDown() for s in self.findChildren(QSlider)) or \
                any(t.isActive() for t in self._timers.values()):
            return
        self._syncing = True
        dev = self.dev
        self.power.setChecked(dev.is_on)
        if self.has_dim:
            self.bright.setValue(dev.brightness)
        if self.has_color:
            self.hue.setValue(dev.hue)
            self.sat.setValue(dev.saturation)
        if self.has_temp and dev.color_temp:
            self.temp.setValue(dev.color_temp)
        self._syncing = False
        self._refresh_visuals()

    def _refresh_visuals(self):
        dev = self.dev
        self.title.setText(dev.alias)
        extra = tr("tapo_name_suffix", name=dev.device_name) if dev.custom_name else ""
        self.subtitle.setText(f"{dev.model} · {dev.host}{extra}")
        col = light_qcolor(dev)
        self.mode.setText(mode_text(dev))
        self.power.set_accent(col if dev.is_on else QColor(ACCENT))
        if self.has_dim:
            self.bright.setStyleSheet(
                "QSlider::groove:horizontal{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 #1d2027,stop:1 {col.name()});}}")
        if self.has_color:
            pure = QColor.fromHsv(self.hue.value() % 360, 255, 255)
            self.sat.setStyleSheet(
                "QSlider::groove:horizontal{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 #ffffff,stop:1 {pure.name()});}}")
        self.orb.update()
        self.changed.emit()

    def _update_swatch(self):
        # Ton/doygunluk sürgüsü oynarken önizleme anında güncellensin
        if self._syncing:
            return
        self.dev.info.update(hue=self.hue.value(), saturation=self.sat.value(), color_temp=0)
        self._refresh_visuals()

    # ---- arayüz -> cihaz
    def _debounce(self, key, fn):
        if self._syncing:
            return
        t = self._timers.get(key)
        if t is None:
            t = QTimer(self)
            t.setSingleShot(True)
            t.setInterval(180)
            t.timeout.connect(fn)
            self._timers[key] = t
        t.start()

    def _send(self, coro, what):
        self.runner.run(coro, lambda _r, e: self.status(
            tr("cmd_failed", alias=self.dev.alias, what=what, err=e) if e
            else tr("cmd_ok", alias=self.dev.alias, what=what)))

    def _on_power(self, on):
        if self._syncing:
            return
        self.dev.info["device_on"] = on
        self._refresh_visuals()
        self._send(self.dev.turn_on() if on else self.dev.turn_off(), tr("turned_on" if on else "turned_off"))

    def _send_brightness(self):
        v = self.bright.value()
        self._ensure_on()
        self.dev.info["brightness"] = v
        self._refresh_visuals()
        self._send(self.dev.set_brightness(v), tr("cmd_brightness", pct=fmt_pct(v)))

    def _send_hsv(self):
        h, s = self.hue.value(), self.sat.value()
        self._ensure_on()
        self.dev.info.update(hue=h, saturation=s, color_temp=0)
        self._refresh_visuals()
        self._send(self.dev.set_hs(h, s), tr("cmd_color", h=h, s=s))

    def _send_temp(self):
        t = self.temp.value()
        self._ensure_on()
        self.dev.info["color_temp"] = t
        self._refresh_visuals()
        self._send(self.dev.set_color_temp(t), tr("cmd_white_temp", t=t))

    def _ensure_on(self):
        # Ampul kapalıyken ayar değiştirilirse cihaz zaten açılır; düğmeyi de güncelle
        self.dev.info["device_on"] = True
        if not self.power.isChecked():
            self._syncing = True
            self.power.setChecked(True)
            self._syncing = False

    def _apply_hs(self, h, s):
        self._syncing = True
        self.hue.setValue(h)
        self.sat.setValue(s)
        self._syncing = False
        self._send_hsv()

    def _pick_color(self):
        start = QColor.fromHsv(self.hue.value() % 360, int(self.sat.value() * 2.55), 255)
        c = QColorDialog.getColor(start, self, tr("pick_color_dialog"))
        if c.isValid():
            h, s, _v, _a = c.getHsv()
            self._apply_hs(max(h, 0), max(1, round(s / 2.55)))


# ---------------------------------------------------------------- hızlı menü (sağ tık)
class QuickPanel(QWidget):
    """Kutucuğa sağ tıklayınca açılan açılır panel: ayar sayfasına girmeden
    aç/kapat, parlaklık, renkler ve beyaz ton."""

    PER_ROW = 8

    def __init__(self, card: LightCard, on_rename, on_open):
        super().__init__(None, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.card = card
        self.setStyleSheet(STYLE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        box, lay = panel()
        outer.addWidget(box)
        lay.setSpacing(10)

        # başlık + aç/kapat
        head = QHBoxLayout()
        names = QVBoxLayout()
        names.setSpacing(0)
        self.name = QLabel()
        self.name.setStyleSheet("font-size:16px;font-weight:700;")
        self.mode = QLabel()
        self.mode.setObjectName("muted")
        names.addWidget(self.name)
        names.addWidget(self.mode)
        head.addLayout(names, 1)
        self.power = ToggleSwitch()
        self.power.setChecked(card.power.isChecked())
        self.power.toggled.connect(lambda v: card.power.setChecked(v))
        head.addWidget(self.power)
        lay.addLayout(head)

        # parlaklık
        lay.addWidget(self._section(tr("brightness")))
        row = QHBoxLayout()
        self.bright = make_slider(1, 100)
        self.bright.setValue(card.bright.value())
        self.bright.valueChanged.connect(card.bright.setValue)
        self.bright_val = QLabel()
        self.bright_val.setFixedWidth(38)
        self.bright_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(self.bright, 1)
        row.addWidget(self.bright_val)
        lay.addLayout(row)

        # renkler
        if card.has_color:
            lay.addWidget(self._section(tr("colors")))
            self.swatches = QWidget()
            self.grid = QGridLayout(self.swatches)
            self.grid.setContentsMargins(0, 0, 0, 0)
            self.grid.setSpacing(8)
            lay.addWidget(self.swatches)
            self._build_swatches()
            card.store.changed.connect(self._build_swatches)

        # beyaz ton
        if card.has_temp:
            lay.addWidget(self._section(tr("white")))
            wrow = QHBoxLayout()
            wrow.setSpacing(6)
            for key, k in WHITE_PRESETS:
                b = QPushButton(tr(key))
                b.setCursor(Qt.PointingHandCursor)
                kc = kelvin_to_qcolor(k)
                b.setStyleSheet(f"QPushButton{{border-left:4px solid {kc.name()};padding:6px 8px;}}")
                b.clicked.connect(lambda _=False, k=k: card.temp.setValue(k))
                wrow.addWidget(b)
            lay.addLayout(wrow)

        # alt düğmeler
        foot = QHBoxLayout()
        ren = QPushButton(tr("quick_rename"))
        ren.setCursor(Qt.PointingHandCursor)
        ren.clicked.connect(lambda: (self.close(), on_rename()))
        more = QPushButton(tr("quick_all_settings"))
        more.setCursor(Qt.PointingHandCursor)
        more.clicked.connect(lambda: (self.close(), on_open()))
        foot.addWidget(ren)
        foot.addStretch()
        foot.addWidget(more)
        lay.addLayout(foot)

        card.changed.connect(self._sync)
        self._sync()
        self.setFixedWidth(400)

    @staticmethod
    def _section(text):
        l = QLabel(text.upper())
        l.setObjectName("section")
        return l

    def _build_swatches(self):
        def add_color():
            self.close()  # renk seçici açılmadan önce paneli kapat
            self.card._add_color()
        self.card.fill_swatches(self.grid, self.PER_ROW, add_color)

    def _sync(self):
        dev = self.card.dev
        self.name.setText(dev.alias)
        self.mode.setText(mode_text(dev))
        self.power.blockSignals(True)
        self.power.setChecked(dev.is_on)
        self.power.blockSignals(False)
        self.power._set_pos(1.0 if dev.is_on else 0.0)
        self.power.set_accent(light_qcolor(dev) if dev.is_on else QColor(ACCENT))
        if not self.bright.isSliderDown():
            self.bright.blockSignals(True)
            self.bright.setValue(self.card.bright.value())
            self.bright.blockSignals(False)
        self.bright_val.setText(fmt_pct(self.bright.value()))
        col = light_qcolor(dev)
        self.bright.setStyleSheet(
            "QSlider::groove:horizontal{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 #1d2027,stop:1 {col.name()});}}")

    def popup_at(self, pos: QPoint):
        self.adjustSize()
        screen = QApplication.screenAt(pos) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        x = min(max(pos.x(), area.left()), area.right() - self.width())
        y = min(max(pos.y(), area.top()), area.bottom() - self.height())
        self.move(x, y)
        self.show()


# ---------------------------------------------------------------- giriş penceresi
class LoginDialog(QDialog):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("login_title"))
        form = QFormLayout(self)
        form.setContentsMargins(20, 20, 20, 16)
        form.setSpacing(10)
        info = QLabel(tr("login_info"))
        info.setObjectName("muted")
        form.addRow(info)
        self.user = QLineEdit(cfg.get("username", ""))
        self.pw = QLineEdit(cfg.get("password", ""))
        self.pw.setEchoMode(QLineEdit.Password)
        form.addRow(tr("email"), self.user)
        form.addRow(tr("password"), self.pw)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)


# ---------------------------------------------------------------- ana pencere
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        set_lang(self.cfg.get("lang") or detect_default_lang())
        self.setWindowTitle(tr("app_title"))
        self.resize(820, 640)
        self.colors = ColorStore(self.cfg)
        self.runner = AsyncRunner()
        self.cards: dict[str, LightCard] = {}
        self.tiles: dict[str, LightTile] = {}

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ---- ana sayfa: ışık kutucukları
        home = QWidget()
        home.setObjectName("page")
        hl = QVBoxLayout(home)
        hl.setContentsMargins(28, 22, 28, 12)
        hl.setSpacing(14)

        top = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.h1 = QLabel(tr("lights"))
        self.h1.setObjectName("h1")
        self.summary = QLabel()
        self.summary.setObjectName("muted")
        titles.addWidget(self.h1)
        titles.addWidget(self.summary)
        top.addLayout(titles)
        top.addStretch()
        self.btn_scan = self._tool(tr("scan_network"), self.discover)
        self.btn_add_ip = self._tool(tr("add_by_ip"), self.add_by_ip)
        self.btn_account = self._tool(tr("account"), self.edit_account)
        self.btn_lang = self._tool(tr("lang_btn"), self.toggle_language)
        self.btn_lang.setToolTip(tr("lang_tooltip"))
        top.addWidget(self.btn_scan)
        top.addWidget(self.btn_add_ip)
        top.addWidget(self.btn_account)
        top.addWidget(self.btn_lang)
        hl.addLayout(top)

        quick = QHBoxLayout()
        self.btn_all_on = self._tool(tr("turn_all_on"), lambda: self.set_all(True))
        self.btn_all_off = self._tool(tr("turn_all_off"), lambda: self.set_all(False))
        quick.addWidget(self.btn_all_on)
        quick.addWidget(self.btn_all_off)
        quick.addStretch()
        hl.addLayout(quick)

        self.grid = FlowGrid(LightTile.W)
        self.empty = QLabel(tr("empty_state"))
        self.empty.setObjectName("muted")
        self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setMinimumHeight(220)
        holder = QWidget()
        holder_l = QVBoxLayout(holder)
        holder_l.setContentsMargins(0, 6, 0, 6)
        holder_l.addWidget(self.empty)
        holder_l.addWidget(self.grid)
        holder_l.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(holder)
        hl.addWidget(scroll, 1)
        self.stack.addWidget(home)
        self.home = home

        self.setStyleSheet(STYLE)
        self._update_summary()

        # Bağlantılar periyodik olarak tazelensin (Tapo uygulamasından yapılan değişiklikler görünsün)
        self.poll = QTimer(self)
        self.poll.setInterval(15000)
        self.poll.timeout.connect(self.refresh_all)
        self.poll.start()

        # Geri: farenin geri tuşu, Alt+Sol ok ya da Esc ayar sayfasından ana ekrana döner
        QApplication.instance().installEventFilter(self)
        for key in ("Alt+Left", "Esc", "Back"):
            QShortcut(QKeySequence(key), self, activated=self.go_home)

        QTimer.singleShot(0, self.startup)

    # ---- yardımcılar
    @staticmethod
    def _tool(text, slot):
        b = QPushButton(text)
        b.setCursor(Qt.PointingHandCursor)
        b.clicked.connect(slot)
        return b

    def toggle_language(self):
        new_lang = "en" if get_lang() == "tr" else "tr"
        set_lang(new_lang)
        self.cfg["lang"] = new_lang
        save_config(self.cfg)
        self.retranslate()

    def retranslate(self):
        self.setWindowTitle(tr("app_title"))
        app = QApplication.instance()
        if app:
            app.setApplicationName(tr("app_title"))
        self.h1.setText(tr("lights"))
        self.btn_scan.setText(tr("scan_network") if self.btn_scan.isEnabled() else tr("scanning"))
        self.btn_add_ip.setText(tr("add_by_ip"))
        self.btn_account.setText(tr("account"))
        self.btn_lang.setText(tr("lang_btn"))
        self.btn_lang.setToolTip(tr("lang_tooltip"))
        self.btn_all_on.setText(tr("turn_all_on"))
        self.btn_all_off.setText(tr("turn_all_off"))
        self.empty.setText(tr("empty_state"))
        self._update_summary()
        for card in self.cards.values():
            card.retranslate()
        for tile in self.tiles.values():
            tile.retranslate()

    def status(self, msg):
        self.statusBar().showMessage(msg, 6000)

    def _update_summary(self):
        n = len(self.cards)
        on = sum(1 for c in self.cards.values() if c.dev.is_on)
        self.summary.setText(tr("summary_count", n=n, on=on) if n else tr("summary_waiting"))
        self.empty.setVisible(n == 0)

    def client(self) -> ApiClient:
        return ApiClient(self.cfg.get("username", ""), self.cfg.get("password", ""))

    def startup(self):
        if not self.cfg.get("username"):
            if not self.edit_account():
                return
        # Bir ışığa aynı anda iki oturum açılırsa ışık birini reddedebiliyor. Bu yüzden önce
        # kayıtlı ışıklara bağlan, ağ taramasını ondan sonra (yalnızca kalan IP'ler için) yap.
        hosts = list(self.cfg.get("hosts", []))
        if not hosts:
            self.discover()
            return
        self.status(tr("connecting_saved"))
        pending = set(hosts)

        def one_done(host):
            pending.discard(host)
            if not pending:
                self.discover()

        for host in hosts:
            self.connect_host(host, on_finished=one_done)

    def edit_account(self) -> bool:
        dlg = LoginDialog(self.cfg, self)
        if dlg.exec() != QDialog.Accepted:
            return False
        self.cfg["username"] = dlg.user.text().strip()
        self.cfg["password"] = dlg.pw.text()
        save_config(self.cfg)
        return True

    def remember_host(self, host):
        hosts = self.cfg.setdefault("hosts", [])
        if host not in hosts:
            hosts.append(host)
            save_config(self.cfg)

    # ---- gezinme
    def open_light(self, host):
        self.stack.setCurrentWidget(self.cards[host])

    def go_home(self):
        self.stack.setCurrentWidget(self.home)

    def open_quick(self, card: LightCard, pos: QPoint):
        host = card.dev.host
        QuickPanel(card, lambda: self.rename_light(card), lambda: self.open_light(host)).popup_at(pos)

    def rename_light(self, card: LightCard):
        """Işığa bu uygulamada görünecek bir ad verir (Tapo uygulamasındaki ad değişmez)."""
        dev = card.dev
        name, ok = QInputDialog.getText(
            self, tr("rename_light_title"),
            tr("rename_light_prompt", name=dev.device_name), text=dev.alias)
        if not ok:
            return
        name = name.strip()
        names = self.cfg.setdefault("names", {})
        if name and name != dev.device_name:
            names[dev.host] = name
        else:
            names.pop(dev.host, None)
            name = None
        dev.custom_name = name
        save_config(self.cfg)
        card._refresh_visuals()
        self.status(tr("renamed_status", alias=dev.alias))

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.MouseButtonPress and ev.button() == Qt.BackButton \
                and self.stack.currentWidget() is not self.home and self.isActiveWindow():
            self.go_home()
            return True
        return super().eventFilter(obj, ev)

    # ---- cihaz yönetimi
    def add_device(self, dev: TapoLight):
        dev.custom_name = self.cfg.get("names", {}).get(dev.host)
        if dev.host in self.cards:
            self.cards[dev.host].dev = dev
            self.cards[dev.host].sync_from_device()
            return
        card = LightCard(dev, self.runner, self.status, self.colors)
        card.back.connect(self.go_home)
        card.renameRequested.connect(lambda c=card: self.rename_light(c))
        card.changed.connect(self._update_summary)
        self.cards[dev.host] = card
        self.stack.addWidget(card)
        tile = LightTile(card)
        tile.clicked.connect(lambda h=dev.host: self.open_light(h))
        tile.powerClicked.connect(lambda c=card: c.power.setChecked(not c.power.isChecked()))
        tile.menuRequested.connect(lambda pos, c=card: self.open_quick(c, pos))
        self.tiles[dev.host] = tile
        self.grid.add(tile)
        self.remember_host(dev.host)
        self._update_summary()

    def discover(self):
        if not self.btn_scan.isEnabled():
            return  # tarama zaten sürüyor
        known = set(self.cards)
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText(tr("scanning"))
        self.status(tr("scanning_status"))

        async def job():
            # Yayın (broadcast) yanıtları güvenlik duvarına takılabildiği için alt ağdaki
            # her IP ayrıca tek tek sorgulanır.
            client = self.client()
            sem = asyncio.Semaphore(64)

            async def one(target):
                async with sem:
                    try:
                        return await probe(client, target, 3)
                    except Exception:  # noqa: BLE001
                        return []

            # Zaten bağlı ışıkları tekrar sorgulama (ikinci oturum açılmasın)
            targets = [] if known else ["255.255.255.255"]
            for net in local_networks():
                if not known:
                    targets.append(str(net.broadcast_address))
                targets += [str(ip) for ip in net.hosts() if str(ip) not in known]
            found = {}
            for lst in await asyncio.gather(*(one(t) for t in targets)):
                for light in lst:
                    found[light.host] = light
            return list(found.values())

        def done(devs, err):
            self.btn_scan.setEnabled(True)
            self.btn_scan.setText(tr("scan_network"))
            if err:
                self.status(tr("scan_error", err=err))
                return
            for d in devs:
                self.add_device(d)
            self.status(tr("scan_done", found=len(devs), total=len(self.cards)))

        self.runner.run(job(), done)

    def connect_host(self, host, on_finished=None):
        async def job():
            for _ in range(2):  # ışık meşgulse bir kez daha dene
                lights = await probe(self.client(), host, 4)
                if lights:
                    await lights[0].update()
                    return lights[0]
                await asyncio.sleep(1)
            return None

        def done(dev, err):
            if err or dev is None:
                self.status(tr("connect_failed", host=host, reason=err or tr("no_response_or_not_light")))
            else:
                self.add_device(dev)
            if on_finished:
                on_finished(host)

        self.runner.run(job(), done)

    def add_by_ip(self):
        host, ok = QInputDialog.getText(self, tr("add_ip_title"), tr("add_ip_prompt"))
        if ok and host.strip():
            self.status(tr("connecting_host", host=host.strip()))
            self.connect_host(host.strip())

    def refresh_all(self):
        for card in list(self.cards.values()):
            self.runner.run(card.dev.update(),
                            lambda _r, e, c=card: c.sync_from_device() if not e else None)

    def set_all(self, on):
        for card in self.cards.values():
            card.power.setChecked(on)


def main():
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("tapo.gui")
        except Exception:  # noqa: BLE001
            pass
    app = QApplication(sys.argv)
    app.setDesktopFileName("tapo-gui")
    app.setStyle("Fusion")  # tema renklerinin her masaüstünde aynı görünmesi için
    icon = QIcon(str(ICON_FILE))
    app.setWindowIcon(icon if not icon.isNull() else QIcon.fromTheme("lightbulb"))
    w = MainWindow()
    app.setApplicationName(tr("app_title"))
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
