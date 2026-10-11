# ==============================================================================
#                      نرم‌افزار Clock Plus (ابزار پیشرفته تبدیل ساعت)
# ==============================================================================
# این ماژول رابط کاربری گرافیکی مدرن (Tkinter) و منطق تبدیل زمان برنامه Clock Plus را پیاده‌سازی می‌کند.
# ویژگی‌های کلیدی:
#   ۱. خواندن و پیست مستقیم ساعت از کلیپ‌بورد با کلید فیزیکی Ctrl+V (مستقل از زبان کیبورد)
#   ۲. محاسبه آنی جمع یا تفریق ساعت پایه با مقدار تنظیمی ثابت
#   ۳. کپی فوری ساعت تبدیل‌شده با Ctrl+C
#   ۴. طراحی مدرن با گوشه‌های گرد (Rounded Corners) برای کارت‌ها، دکمه‌ها و فیلدهای ورودی
#   ۵. آیکون‌های وکتور اختصاصی رندر شده با Pillow برای تغییر تم و پین کردن پنجره
#   ۶. پایداری تنظیمات و ذخیره دقیق آخرین موقعیت و ابعاد پنجره در فایل JSON
# ==============================================================================

import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime, timedelta
import sys
import os
import json
import math
from PIL import Image, ImageDraw, ImageTk

# ==============================================================================
# ۱. بهینه‌سازی DPI و تنظیمات سیستم‌عامل ویندوز
# ==============================================================================
# در مانیتورهای با مقیاس‌بندی بالا (High DPI مثل ۱۲۵٪ یا ۱۵۰٪)، برنامه‌های Tkinter به طور پیش‌فرض
# ممکن است تار (Blurry) به نظر برسند. با فراخوانی توابع زیر از shcore/user32، برنامه به صورت
# Per-Monitor DPI Aware اجرا می‌شود تا فونت‌ها و خطوط کاملاً شفاف (Crisp) باشند.
if sys.platform == "win32":
    try:
        from ctypes import windll
        # تنظیم آگاهی از مقیاس نمایشگر برای هر مانیتور (Per Monitor DPI Aware V2)
        windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # روش جایگزین برای ویندوزهای قدیمی‌تر
            windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    try:
        from ctypes import windll
        # تفکیک پروسه در تسک‌بار ویندوز تا آیکون اختصاصی در نوار وظیفه ثبت و نمایش داده شود
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("ClockPlus.TimeCalculator.App.1")
    except Exception:
        pass

# ==============================================================================
# ۲. بارگذاری کتابخانه کمکی کلیپ‌بورد (pyperclip)
# ==============================================================================
# اگر pyperclip موجود باشد به عنوان لایه اول خواندن کلیپ‌بورد استفاده می‌شود.
# در صورت عدم وجود، لایه‌های بومی Tkinter و Win32 API وارد عمل می‌شوند.
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


# ==============================================================================
# ۳. پالت‌های رنگی تم تاریک (Dark) و تم روشن (Light)
# ==============================================================================
# تمام رنگ‌ها بر اساس استانداردهای مدرن رابط کاربری (تضاد نوری و کنتراست بالا) انتخاب شده‌اند.
DARK = {
    "bg":           "#0f0f1a",   # پس‌زمینه اصلی پنجره
    "titlebar":     "#15152b",   # پس‌زمینه تایتل‌بار سفارشی
    "card":         "#1a1a2e",   # پس‌زمینه کارت‌های ساعت پایه و مقدار اضافه
    "card2":        "#16162a",   # پس‌زمینه کارت بزرگ نتیجه
    "accent":       "#00e5a0",   # رنگ سبز نئونی اصلی (برای ساعت پایه و نتیجه)
    "accent2":      "#5c6cff",   # رنگ ایندیگو/آبی مکمل (برای بخش مقدار اضافه)
    "accent_h":     "#00ffb3",   # رنگ هایلایت هنگام هاور ماوس
    "accent2_h":    "#7a88ff",   # رنگ هایلایت دکمه‌ها در هاور
    "danger":       "#ff5566",   # رنگ قرمز برای نمایش خطاها
    "close_h":      "#ff4466",   # رنگ دکمه بستن در هاور
    "text":         "#ffffff",   # رنگ متن اصلی (سفید خالص با کنتراست حداکثری)
    "text_dim":     "#9a9ab0",   # رنگ متون راهنما و ثانویه
    "border":       "#2a2a44",   # رنگ خطوط مرزی کارت‌ها
    "entry_bg":     "#202036",   # پس‌زمینه داخل فیلدهای ورودی اعداد
    "entry_border": "#32324f",   # حاشیه فیلد ورودی عدد در حالت عادی
    "min_h":        "#3a3a5c",   # رنگ دکمه مینی‌مایز در هاور
    "btn_gray":     "#23233c",   # پس‌زمینه دکمه‌های آیکونی
    "btn_gray_h":   "#343456",   # پس‌زمینه دکمه‌های آیکونی در هاور
    "btn_purple":   "#6a3a8a",   # رنگ بنفش دکمه Paste دستی
    "btn_purple_h": "#8246a8",   # رنگ بنفش دکمه Paste در هاور
    "result_bg":    "#16162a",   # پس‌زمینه کارت نهایی
}

LIGHT = {
    "bg":           "#f0f0f5",   # پس‌زمینه خاکستری ملایم
    "titlebar":     "#e0e0ea",   # تایتل‌بار روشن
    "card":         "#ffffff",   # کارت‌های سفید خالص
    "card2":        "#fafafa",   # کارت نتیجه با پس‌زمینه بسیار روشن
    "accent":       "#00a878",   # سبز زمردی با کنتراست عالی روی سفید
    "accent2":      "#4455dd",   # آبی رویال برای بخش اضافه
    "accent_h":     "#00c78f",   # هایلایت سبز
    "accent2_h":    "#6677ff",   # هایلایت آبی
    "danger":       "#dd3344",   # رنگ قرمز هشدار
    "close_h":      "#ff4466",   # قرمز بستن
    "text":         "#1a1a2e",   # متن تیره خوانا
    "text_dim":     "#666680",   # متون فرعی خاکستری
    "border":       "#d4d4e2",   # مرز کارت‌ها در حالت لایت
    "entry_bg":     "#f2f2fa",   # پس‌زمینه فیلد ورودی عدد
    "entry_border": "#d8d8e6",   # حاشیه ورودی عدد
    "min_h":        "#c5c5d5",   # هاور دکمه کمینه
    "btn_gray":     "#dedee8",   # دکمه‌های آیکونی لایت
    "btn_gray_h":   "#cecede",   # هاور دکمه‌های آیکونی
    "btn_purple":   "#8844aa",   # دکمه پیست بنفش لایت
    "btn_purple_h": "#aa66cc",   # هاور دکمه پیست
    "result_bg":    "#fafafa",   # کادر نتیجه روشن
}

# متغیر سراسری نگه‌دارنده رنگ‌های تم فعلی برنامه
COLORS = dict(DARK)

# جدول ترجمه ارقام فارسی و عربی به معادل‌های انگلیسی (ASCII)
DIGIT_MAP = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_digits(text: str) -> str:
    """
    تبدیل ارقام فارسی و عربی درون رشته متنی به ارقام استاندارد انگلیسی.
    ورودی: متن حاوی هر نوع رقم
    خروجی: متن با ارقام انگلیسی خالص (0-9)
    """
    if not text:
        return ""
    return str(text).translate(DIGIT_MAP)


def clean_clipboard_text(text: str) -> str:
    """
    پاک‌سازی نویسه‌های زائد و پنهان کلیپ‌بورد:
    - حذف نیم‌فاصله (Zero-width non-joiner)
    - تبدیل Non-breaking space به فاصله عادی
    - حذف کوتیشن، کاراکترهای تب و خط جدید
    - استانداردسازی ارقام فارسی به انگلیسی
    """
    if not text:
        return ""
    text = str(text).replace("\u200c", "").replace("\xa0", " ").strip()
    strip_chars = ' "' + "'" + '\t\r\n'
    text = text.strip(strip_chars)
    return normalize_digits(text)


def resource_path(relative_path: str) -> str:
    """
    یافتن مسیر واقعی فایل‌های منبع (مثل آیکون) چه در حالت اسکریپت و چه پس از پکیج شدن با PyInstaller:
    در حالت One-file PyInstaller، فایل‌ها در پوشه موقت sys._MEIPASS باز می‌شوند.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# ==============================================================================
# ۴. موتور رندر گوشه‌های گرد برای کادرها و دکمه‌ها
# ==============================================================================
class RoundedFrame(tk.Canvas):
    """
    کادر مدرن با گوشه‌های نرم و گرد (Rounded Frame):
    به جای استفاده از فریم مستطیلی تیز، یک Canvas دو لایه ایجاد می‌کند.
    یک تصویر Pillow با گوشه‌های گرد و آنتی‌الیاسینگ (Anti-Aliasing) در مقیاس دوبرابر (Super-sampling)
    رندر شده و یک فریم داخلی در مرکز آن برای قرارگیری سایر ویجت‌ها ایجاد می‌گردد.
    """
    def __init__(self, parent, bg_parent: str, fill_color: str, border_color: str = None,
                 radius: int = 16, border_w: int = 1, **kwargs):
        super().__init__(parent, bg=bg_parent, highlightthickness=0, bd=0, **kwargs)
        self.bg_parent = bg_parent
        self.fill_color = fill_color
        self.border_color = border_color
        self.radius = radius
        self.border_w = border_w
        self._img_ref = None
        self._img_id = None
        self._win_id = None

        # فریم داخلی که ویجت‌های فرزند درون آن Pack یا Grid می‌شوند
        self.container = tk.Frame(self, bg=fill_color)
        # اتصال به رویداد تغییر اندازه برای رندر مجدد انحناها متناسب با ابعاد واقعی
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        """رندر تصویر گوشه گرد هنگام تغییر ابعاد کادر"""
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return
        scale = 2  # رندر در رزولوشن دوبرابر جهت حذف دندانه‌دار شدن لبه‌ها
        W = w * scale
        H = h * scale
        R = self.radius * scale
        bw = int(self.border_w * scale)

        img = Image.new("RGBA", (W, H), self.bg_parent)
        draw = ImageDraw.Draw(img)
        if self.border_color:
            draw.rounded_rectangle([0, 0, W - 1, H - 1], radius=R, fill=self.fill_color,
                                   outline=self.border_color, width=bw)
        else:
            draw.rounded_rectangle([0, 0, W - 1, H - 1], radius=R, fill=self.fill_color)

        # تبدیل به تصویر Tkinter با فیلتر Bilinear
        self._img_ref = ImageTk.PhotoImage(img.resize((w, h), Image.Resampling.BILINEAR))
        if self._img_id is None:
            self._img_id = self.create_image(0, 0, anchor="nw", image=self._img_ref)
        else:
            self.itemconfig(self._img_id, image=self._img_ref)

        # تنظیم پدینگ و موقعیت فریم داخلی روی کادر گرد
        pad_x = max(10, self.radius // 2)
        pad_y = max(8, self.radius // 2)
        cw = max(10, w - 2 * pad_x)
        ch = max(10, h - 2 * pad_y)

        if self._win_id is None:
            self._win_id = self.create_window(pad_x, pad_y, anchor="nw", window=self.container,
                                              width=cw, height=ch)
        else:
            self.coords(self._win_id, pad_x, pad_y)
            self.itemconfigure(self._win_id, width=cw, height=ch)

    def set_border(self, border_color: str, border_w: int = 1):
        """تغییر رنگ و ضخامت خط حاشیه (جهت افکت فوکوس یا هاور)"""
        self.border_color = border_color
        self.border_w = border_w
        self._redraw()


def make_rounded_rect_img(w: int, h: int, radius: int, parent_bg: str, fill_color: str,
                          border_color: str = None, scale: int = 3):
    """
    تولید یک تصویر مستطیل گوشه‌گرد برای پس‌زمینه دکمه‌ها با استفاده از Pillow و Lanczos Anti-aliasing.
    """
    W = w * scale
    H = h * scale
    R = radius * scale
    img = Image.new("RGBA", (W, H), parent_bg)
    draw = ImageDraw.Draw(img)
    if border_color:
        draw.rounded_rectangle([0, 0, W - 1, H - 1], radius=R, fill=fill_color,
                               outline=border_color, width=max(1, scale))
    else:
        draw.rounded_rectangle([0, 0, W - 1, H - 1], radius=R, fill=fill_color)
    return ImageTk.PhotoImage(img.resize((w, h), Image.Resampling.LANCZOS))


def make_slot_bg(w: int, h: int, r: int, parent_bg: str, fill_color: str,
                 border_color: str, border_w: int = 1, scale: int = 3):
    """
    تولید پس‌زمینه کادر اختصاصی ورودی عدد با لبه‌های خمیده و بردر مشخص.
    """
    W = w * scale
    H = h * scale
    R = r * scale
    bw = int(border_w * scale)
    img = Image.new("RGBA", (W, H), parent_bg)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, W - 1, H - 1], radius=R, fill=fill_color,
                           outline=border_color, width=bw)
    return ImageTk.PhotoImage(img.resize((w, h), Image.Resampling.LANCZOS))


# ==============================================================================
# ۵. جایگاه ورودی عدد با کادر خمیده و ایزوله (CurvedEntrySlot)
# ==============================================================================
class CurvedEntrySlot(tk.Canvas):
    """
    جایگاه اختصاصی ورودی ارقام (ساعت و دقیقه) با لبه‌های گرد:
    نکته فنی بسیار مهم:
      در Tkinter روی ویندوز، اگر ورودی Entry روی tk.Label قرار گیرد، با رندر مجدد Label در FocusIn،
      موتور GDI ویندوز تصویر پس‌زمینه را روی متن Entry می‌اندازد و متن محو می‌شود.
      برای حل قطعی این باگ، از یک tk.Canvas استفاده شده و ویجت Entry با متد create_window
      درون آن نشانده شده است؛ بدین ترتیب لایه‌بندی Z-Order کاملاً استاندارد و ایزوله باقی می‌ماند.
    """
    def __init__(self, parent, default: str, parent_bg: str, fill_bg: str,
                 border_color: str, focus_border_color: str,
                 fg_color: str, select_bg: str, select_fg: str,
                 w: int = 82, h: int = 50, radius: int = 10, font=None):
        super().__init__(parent, width=w, height=h, bg=parent_bg, highlightthickness=0, bd=0)
        self.w = w
        self.h = h
        self.radius = radius
        self.parent_bg = parent_bg
        self.fill_bg = fill_bg
        self.border_color = border_color
        self.focus_border_color = focus_border_color

        # رندر تصاویر حالت عادی و حالت فوکوس
        self.img_norm = make_slot_bg(w, h, radius, parent_bg, fill_bg, border_color, 1)
        self.img_focus = make_slot_bg(w, h, radius, parent_bg, fill_bg, focus_border_color, 2)

        self.bg_img_id = self.create_image(0, 0, anchor="nw", image=self.img_norm)

        # ویجت ورودی متنی داخل کادر گرد
        self.entry = tk.Entry(self, width=3, justify="center", font=font,
                              bg=fill_bg, fg=fg_color,
                              selectbackground=select_bg, selectforeground=select_fg,
                              insertbackground=focus_border_color,
                              exportselection=False,  # جلوگیری از پاک شدن کلیپ‌بورد در تغییر فوکوس
                              relief="flat", bd=0, highlightthickness=0)
        self.win_id = self.create_window(w // 2, h // 2, anchor="center", window=self.entry)
        self.entry.insert(0, default)
        self.entry.slot = self

        # مدیریت رویدادهای فوکوس و تغییر ظاهر کادر
        self.entry.bind("<FocusIn>", self._on_focus_in, add="+")
        self.entry.bind("<FocusOut>", self._on_focus_out, add="+")
        self.bind("<Button-1>", lambda e: self.entry.focus_set())

    def _on_focus_in(self, event=None):
        """هنگام فوکوس: کادر به رنگ هایلایت نئونی تغییر کرده و ارقام انتخاب می‌شوند"""
        self.itemconfig(self.bg_img_id, image=self.img_focus)
        self.entry.select_range(0, tk.END)

    def _on_focus_out(self, event=None):
        """هنگام خروج فوکوس: کادر به حاشیه عادی برمی‌گردد"""
        self.itemconfig(self.bg_img_id, image=self.img_norm)


# ==============================================================================
# ۶. رندرر آیکون‌های برداری با کیفیت بالا (Vector Icons with Pillow)
# ==============================================================================
def create_sun_pil(size: int = 20, scale: int = 4, color: str = "#f59e0b"):
    """
    تولید وکتور خورشید برای دکمه تغییر تم به حالت روز:
    شامل یک دایره مرکزی و ۸ شعاع نوری با محاسبات مثلثاتی sin/cos.
    """
    S = size * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = S / 2, S / 2
    r_core = S * 0.22

    ray_in = S * 0.32
    ray_out = S * 0.44
    ray_w = max(2, int(S * 0.075))
    for i in range(8):
        ang = i * (math.pi / 4)
        x1 = cx + ray_in * math.cos(ang)
        y1 = cy + ray_in * math.sin(ang)
        x2 = cx + ray_out * math.cos(ang)
        y2 = cy + ray_out * math.sin(ang)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=ray_w)

    draw.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=color)
    return img


def create_moon_pil(size: int = 20, scale: int = 4, color: str = "#6366f1"):
    """
    تولید وکتور هلال ماه برای دکمه تغییر تم به حالت شب:
    از طریق ترسیم یک دایره اصلی و برش هندسی (Subtractive Boolean) با دایره دوم شفاف.
    """
    S = size * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = S / 2, S / 2
    r = S * 0.38

    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    cut_r = S * 0.33
    ox = S * 0.21
    oy = -S * 0.13
    draw.ellipse([cx - cut_r + ox, cy - cut_r + oy, cx + cut_r + ox, cy + cut_r + oy], fill=(0, 0, 0, 0))
    return img


def create_pin_pil(size: int = 20, scale: int = 4, color: str = "#94a3b8"):
    """
    تولید وکتور سوزن پین (Pushpin) برای دکمه Always-on-Top:
    شامل کلاهک بالایی، بدنه مخروطی، حلقه نگهدارنده و سوزن پایینی.
    """
    S = size * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = S / 2

    # کلاهک گرد بالا
    top_w = S * 0.46
    top_h = S * 0.10
    top_y = S * 0.14
    draw.rounded_rectangle([cx - top_w/2, top_y, cx + top_w/2, top_y + top_h],
                           radius=int(S*0.04), fill=color)

    # بدنه مخروطی میانی
    body_top_w = S * 0.30
    body_bot_w = S * 0.16
    body_y1 = top_y + top_h
    body_y2 = S * 0.54
    poly = [
        (cx - body_top_w/2, body_y1),
        (cx + body_top_w/2, body_y1),
        (cx + body_bot_w/2, body_y2),
        (cx - body_bot_w/2, body_y2),
    ]
    draw.polygon(poly, fill=color)

    # رینگ یا طوقه اتصال
    collar_w = S * 0.38
    collar_h = S * 0.08
    collar_y = body_y2
    draw.rounded_rectangle([cx - collar_w/2, collar_y, cx + collar_w/2, collar_y + collar_h],
                           radius=int(S*0.03), fill=color)

    # نوک سوزن
    needle_w = max(2, int(S * 0.055))
    draw.line([(cx, collar_y + collar_h), (cx, S * 0.88)], fill=color, width=needle_w)
    return img


def make_rounded_icon_img(w: int, h: int, radius: int, parent_bg: str, btn_bg: str,
                          icon_pil: Image.Image, border_color: str = None, scale: int = 3):
    """
    ترکیب کادر دکمه گوشه‌گرد با آیکون وکتور در مرکز آن جهت استفاده به عنوان تصویر دکمه.
    """
    W = w * scale
    H = h * scale
    R = radius * scale
    base = Image.new("RGBA", (W, H), parent_bg)
    draw = ImageDraw.Draw(base)
    if border_color:
        draw.rounded_rectangle([0, 0, W - 1, H - 1], radius=R, fill=btn_bg,
                               outline=border_color, width=max(1, scale))
    else:
        draw.rounded_rectangle([0, 0, W - 1, H - 1], radius=R, fill=btn_bg)

    icon_resized = icon_pil.resize((int(20 * scale), int(20 * scale)), Image.Resampling.LANCZOS)
    iw, ih = icon_resized.size
    ox = (W - iw) // 2
    oy = (H - ih) // 2
    base.paste(icon_resized, (ox, oy), icon_resized)

    return ImageTk.PhotoImage(base.resize((w, h), Image.Resampling.LANCZOS))


# ==============================================================================
# ۷. مدیریت پایداری تنظیمات و ذخیره موقعیت پنجره (JSON Persistence)
# ==============================================================================
def get_settings_file() -> str:
    """
    تعیین مسیر فایل timecalc_settings.json:
    - در صورت داشتن دسترسی نوشتن، کنار خود فایل اجرایی ذخیره می‌شود (پورتابل واقعی).
    - در صورت محدودیت دسترسی، در پوشه کاربر سیستم (~/.timecalc_settings.json) قرار می‌گیرد.
    """
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        test_file = os.path.join(exe_dir, ".test_perm")
        try:
            with open(test_file, "w") as f:
                f.write("1")
            os.remove(test_file)
            return os.path.join(exe_dir, "timecalc_settings.json")
        except Exception:
            pass
    return os.path.join(os.path.expanduser("~"), ".timecalc_settings.json")


def load_settings() -> dict:
    """خواندن تنظیمات پیشین (تم، مقادیر افزایشی، و آخرین ابعاد پنجره)"""
    settings_file = get_settings_file()
    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {"theme": "dark", "add_hour": "0", "add_minute": "0", "geometry": ""}


def save_settings(settings: dict):
    """ذخیره تنظیمات روی دیسک با فرمت JSON و فرمت مرتب"""
    settings_file = get_settings_file()
    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ==============================================================================
# ۸. سیستم خواندن و نوشتن ۳ لایه در کلیپ‌بورد ویندوز (Robust Clipboard Fallback)
# ==============================================================================
def get_clipboard_text(root=None) -> str:
    """
    دریافت متن از کلیپ‌بورد با مکانیزم تضمینی ۳ مرحله‌ای:
      لایه ۱: کتابخانه استاندارد pyperclip
      لایه ۲: سیستم داخلی Tkinter (clipboard_get)
      لایه ۳: دسترسی مستقیم به Win32 API با فرمت CF_UNICODETEXT
    """
    # ۱. تلاش لایه اول
    if HAS_PYPERCLIP:
        try:
            txt = pyperclip.paste()
            if txt and txt.strip():
                return txt
        except Exception:
            pass

    # ۲. تلاش لایه دوم
    if root is not None:
        try:
            txt = root.clipboard_get()
            if txt and txt.strip():
                return txt
        except Exception:
            pass

    # ۳. تلاش لایه سوم: استفاده مستقیم از Win32 API
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            user32.OpenClipboard.argtypes = [wintypes.HWND]
            user32.OpenClipboard.restype = wintypes.BOOL
            user32.CloseClipboard.argtypes = []
            user32.CloseClipboard.restype = wintypes.BOOL
            user32.GetClipboardData.argtypes = [wintypes.UINT]
            user32.GetClipboardData.restype = wintypes.HANDLE
            kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
            kernel32.GlobalLock.restype = ctypes.c_void_p
            kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
            kernel32.GlobalUnlock.restype = wintypes.BOOL

            if user32.OpenClipboard(None):
                try:
                    CF_UNICODETEXT = 13
                    h_data = user32.GetClipboardData(CF_UNICODETEXT)
                    if h_data:
                        ptr = kernel32.GlobalLock(h_data)
                        if ptr:
                            try:
                                return ctypes.c_wchar_p(ptr).value
                            finally:
                                kernel32.GlobalUnlock(h_data)
                finally:
                    user32.CloseClipboard()
        except Exception:
            pass

    return None


def copy_to_clipboard(text: str, root=None):
    """کپی کردن رشته خروجی در کلیپ‌بورد سیستم"""
    if not text:
        return
    try:
        if HAS_PYPERCLIP:
            pyperclip.copy(text)
        elif root is not None:
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
    except Exception:
        pass


def set_dark_titlebar(hwnd):
    """
    فعال‌سازی تم تاریک بومی ویندوز برای فریم پنجره از طریق Win32 DwmSetWindowAttribute.
    """
    if sys.platform != "win32":
        return
    try:
        from ctypes import windll, c_int, byref
        value = c_int(1)
        windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, byref(value), 4)
    except Exception:
        try:
            from ctypes import windll, c_int, byref
            value = c_int(1)
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, byref(value), 4)
        except Exception:
            pass


# ==============================================================================
# ۹. کلاس اصلی برنامه (ModernTimeCalculator)
# ==============================================================================
class ModernTimeCalculator:
    """
    کنترل‌کننده مرکزی و رابط گرافیکی برنامه تبدیل ساعت.
    مدیریت کننده رویدادها، تایتل‌بار اختصاصی، کارت‌های زمان، کلیدهای میانبر، و تعامل با کلیپ‌بورد.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Clock Plus - Time Calculator")
        self.root.minsize(440, 560)

        # بارگذاری تنظیمات ذخیره‌شده قبلی
        self.settings = load_settings()
        self.current_theme = self.settings.get("theme", "dark")
        self._apply_theme_colors()

        self._setup_window_icon()

        # متغیرهای مربوط به جابجایی درگ پنجره بدون تایتل‌بار سنتی
        self._drag_x = 0
        self._drag_y = 0
        self.is_pinned = False
        self._toast_after_id = None
        self._auto_calc_id = None

        self._build_fonts()
        self._build_ui()
        self._restore_geometry()

        # حذف فریم سفید پیش‌فرض ویندوز و ساخت تایتل‌بار بدون حاشیه با WinAPI
        self.root.after(50, self._remove_titlebar_winapi)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # هوک هوشمند رویدادهای فیزیکی کلیدها (تشخیص Keycode سخت‌افزاری مستقل از زبان کیبورد)
        self.root.bind_all("<KeyPress>", self._on_global_key)

        # بایندهای استاندارد کمکی برای پیست و کپی
        self.root.bind_all("<Control-v>", lambda e: self._on_ctrl_v(e))
        self.root.bind_all("<Control-V>", lambda e: self._on_ctrl_v(e))
        self.root.bind_all("<Shift-Insert>", lambda e: self._on_ctrl_v(e))
        self.root.bind_all("<Control-c>", lambda e: self._on_ctrl_c(e))
        self.root.bind_all("<Control-C>", lambda e: self._on_ctrl_c(e))
        self.root.bind_all("<Return>", lambda e: self._on_enter_pressed())
        self.root.bind_all("<KP_Enter>", lambda e: self._on_enter_pressed())

        # قابلیت پیست سریع با کلیک راست در هر کجای صفحه
        self.root.bind("<Button-3>", lambda e: self._on_ctrl_v(e))
        self.content.bind("<Button-3>", lambda e: self._on_ctrl_v(e))

        # اتصال به رویداد بستن پنجره برای ذخیره پایدار ابعاد و مقادیر
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # محاسبه و فوکوس اولیه در زمان راه‌اندازی
        self.root.after(100, self.calculate)
        self.root.after(200, lambda: self.base_hour.focus_set())

    def _setup_window_icon(self):
        """تنظیم آیکون پنجره از فایل icon.ico"""
        try:
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
        except Exception:
            pass

    def _restore_geometry(self):
        """بازیابی آخرین موقعیت مکانی و اندازه پنجره روی صفحه نمایش"""
        geom = self.settings.get("geometry")
        default_w, default_h = 560, 720
        restored = False
        if geom and isinstance(geom, str) and ("x" in geom):
            try:
                self.root.geometry(geom)
                restored = True
            except Exception:
                pass

        if not restored:
            self.root.update_idletasks()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            x = max(0, (sw - default_w) // 2)
            y = max(0, (sh - default_h) // 2)
            self.root.geometry(f"{default_w}x{default_h}+{x}+{y}")

    def _apply_theme_colors(self):
        """بارگذاری متغیر رنگ‌های فعال بر اساس تم انتخاب‌شده"""
        global COLORS
        COLORS.clear()
        COLORS.update(LIGHT if self.current_theme == "light" else DARK)

    def toggle_theme(self):
        """جابجایی بین تم دارک و تم لایت و ساخت مجدد المان‌های گرافیکی"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self._apply_theme_colors()
        self.settings["theme"] = self.current_theme
        save_settings(self.settings)

        for widget in self.root.winfo_children():
            widget.destroy()

        self._build_ui()
        self.root.after(50, self._remove_titlebar_winapi)
        self.root.after(100, self.calculate)
        theme_name = "روشن" if self.current_theme == "light" else "تاریک"
        self._show_toast(f"تم {theme_name} فعال شد")

    def _on_global_key(self, event):
        """
        مدیریت سراسری کلیدهای کیبورد بر پایه کد سخت‌افزاری (Hardware Keycode):
        نکته فنی:
          وقتی کیبورد ویندوز روی حالت فارسی قرار دارد، زدن کلید فیزیکی V کاراکتر 'ر' می‌فرستد
          و کلید C کاراکتر 'و' می‌فرستد؛ بنابراین بایند معمولی <Control-v> تحریک نمی‌شود!
          این متد با بررسی مستقیم Keycode (کد ۸۶ برای V و کد ۶۷ برای C) باعث می‌شود
          زدن Ctrl+V و Ctrl+C در هر دو زبان انگلیسی و فارسی ۱۰۰٪ بدون باگ کار کند.
        """
        is_ctrl = bool(event.state & 0x0004) or bool(event.state & 4)

        if is_ctrl:
            sym = str(event.keysym).lower()
            # تشخیص کلید فیزیکی V (پیست و محاسبه)
            if event.keycode == 86 or sym in ("v", "arabic_ra", "ra", "quoteright"):
                self._on_ctrl_v(event)
                return "break"
            # تشخیص کلید فیزیکی C (کپی نتیجه ساعت نهایی)
            if event.keycode == 67 or sym in ("c", "arabic_waw", "waw"):
                self._on_ctrl_c(event)
                return "break"

        # فشردن کلید اینتر برای اجرای محاسبه
        if event.keycode == 13 or event.keysym in ("Return", "KP_Enter"):
            self._on_enter_pressed()
            return "break"

        return None

    def _on_ctrl_v(self, event=None):
        """رویداد پیست ساعت از کلیپ‌بورد، نشاندن در فیلدها و انجام محاسبه"""
        text = get_clipboard_text(self.root)
        if not text:
            self._show_toast("کلیپ‌بورد خالی است")
            return "break"
        cleaned = clean_clipboard_text(text)
        if not cleaned:
            self._show_toast("کلیپ‌بورد خالی است")
            return "break"
        self._apply_pasted_text(cleaned)
        return "break"

    def _on_ctrl_c(self, event=None):
        """رویداد کپی کردن نتیجه نهایی ساعت تبدیل‌شده در کلیپ‌بورد"""
        res_time = self.result_label.cget("text")
        if ":" in res_time and res_time not in ("--:--", ""):
            copy_to_clipboard(res_time, self.root)
            self._show_toast(f"✓ کپی شد: {res_time}")
        else:
            self.calculate()
            res_time = self.result_label.cget("text")
            if ":" in res_time:
                copy_to_clipboard(res_time, self.root)
                self._show_toast(f"✓ کپی شد: {res_time}")
        return "break"

    def _apply_pasted_text(self, text: str):
        """
        تفسیر هوشمند متن کپی‌شده:
        - اگر با + یا - شروع شده باشد، در بخش مقدار اضافه درج می‌شود.
        - اگر فرمت ساعت معتبر باشد، در بخش ساعت پایه درج و نتیجه فوراً حساب می‌شود.
        - اگر یک عدد خام باشد، در فیلد تحت فوکوس قرار می‌گیرد.
        """
        text = clean_clipboard_text(text)
        is_add = text.startswith("+")
        is_sub = text.startswith("-")

        # اگر متن مربوط به مقدار اضافه باشد
        if is_add or is_sub:
            clean = text[1:].strip()
            parsed = self._parse_hhmm(clean)
            if parsed:
                h, m = parsed
                sign = "-" if is_sub else ""
                self.add_hour.delete(0, tk.END)
                self.add_hour.insert(0, f"{sign}{h}")
                self.add_minute.delete(0, tk.END)
                self.add_minute.insert(0, f"{m:02d}")
                self._save_add_values()
                self.calculate()
                res = self.result_label.cget("text")
                self._show_toast(f"✓ مقدار اضافه: {sign}{h:02d}:{m:02d} | نتیجه: {res}")
                return

        # بررسی فرمت ساعت پایه
        parsed = self._parse_hhmm(text)
        if parsed:
            h, m = parsed
            self.base_hour.delete(0, tk.END)
            self.base_hour.insert(0, f"{h:02d}")
            self.base_minute.delete(0, tk.END)
            self.base_minute.insert(0, f"{m:02d}")
            self.calculate()
            res = self.result_label.cget("text")
            self._show_toast(f"✓ ساعت پایه: {h:02d}:{m:02d} | تبدیل شد: {res}")
            return

        # در صورت عدد ساده، در فیلد جاری می‌نشیند
        clean_digits = text.lstrip("-")
        if clean_digits.isdigit():
            widget = self.root.focus_get()
            target = widget if isinstance(widget, tk.Entry) else self.base_hour
            target.delete(0, tk.END)
            target.insert(0, text)
            self.calculate()
            return

        self._show_toast(f"فرمت نامعتبر: {text[:15]}")

    def _parse_hhmm(self, text: str):
        """
        پارسر چندوجهی زمان با پشتیبانی از انواع فرمت‌های متنی و زبان‌ها:
        - فرمت‌های جداکننده‌دار: 14:30:00 ، 14:30 ، 14-30 ، 14/30 ، 14.30
        - پشتیبانی از AM و PM انگلیسی و ق.ظ و ب.ظ فارسی
        - پشتیبانی از اعداد سه رقمی و چهار رقمی به هم چسبیده (مانند 1430 یا 930)
        خروجی: تاپل (ساعت, دقیقه) یا None در صورت نامعتبر بودن
        """
        text = clean_clipboard_text(text)
        is_pm = False
        is_am = False
        lower = text.lower()
        if "pm" in lower or "ب.ظ" in text:
            is_pm = True
        if "am" in lower or "ق.ظ" in text:
            is_am = True
        for token in ("am", "pm", "ق.ظ", "ب.ظ"):
            text = text.lower().replace(token, "").strip()

        # بررسی انواع جداکننده‌های متداول زمان
        for sep in (":", "-", " ", "،", ".", "؛", "/"):
            if sep in text:
                parts = [p.strip() for p in text.split(sep) if p.strip()]
                if len(parts) >= 2:
                    h_str, m_str = parts[0], parts[1]
                    if h_str.isdigit() and m_str.isdigit():
                        h, m = int(h_str), int(m_str)
                        if is_pm and h < 12:
                            h += 12
                        elif is_am and h == 12:
                            h = 0
                        if 0 <= h <= 23 and 0 <= m <= 59:
                            return (h, m)

        # بررسی اعداد پیوسته (مثلاً 1430 به معنی ۱۴:۳۰)
        if text.isdigit():
            if len(text) == 4:
                h, m = int(text[:2]), int(text[2:])
                if 0 <= h <= 23 and 0 <= m <= 59:
                    return (h, m)
            elif len(text) == 3:
                h, m = int(text[:1]), int(text[1:])
                if 0 <= h <= 23 and 0 <= m <= 59:
                    return (h, m)

        return None

    def _remove_titlebar_winapi(self):
        """
        حذف تایتل‌بار و استایل پیش‌فرض ویندوز بدون استفاده از overrideredirect:
        با اعمال فلگ WS_CAPTION روی هندل HWND از طریق Win32 API، پنجره بدون تایتل‌بار سنتی
        می‌شود اما تمام ویژگی‌های پنجره‌های استاندارد ویندوز (مثل مینی‌مایز در تسک‌بار و انیمیشن) حفظ می‌گردد.
        """
        if sys.platform != "win32":
            self.root.overrideredirect(True)
            return
        try:
            from ctypes import windll
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()

            if self.current_theme == "dark":
                set_dark_titlebar(hwnd)

            GWL_STYLE = -16
            WS_CAPTION = 0x00C00000
            style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            style = style & ~WS_CAPTION
            windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)

            SWP_FRAMECHANGED = 0x0020
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                                        SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE)
        except Exception as e:
            print("WinAPI error:", e)
            self.root.overrideredirect(True)

    def _build_fonts(self):
        """تعریف فونت‌های یکپارچه و بهینه‌شده برنامه با خانواده Segoe UI"""
        self.f_title    = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.f_h1       = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.f_subtitle = tkfont.Font(family="Segoe UI", size=10)
        self.f_label    = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.f_entry    = tkfont.Font(family="Segoe UI", size=24, weight="bold")
        self.f_colon    = tkfont.Font(family="Segoe UI", size=24, weight="bold")
        self.f_btn      = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.f_result   = tkfont.Font(family="Segoe UI", size=54, weight="bold")
        self.f_error    = tkfont.Font(family="Segoe UI", size=15, weight="bold")
        self.f_small    = tkfont.Font(family="Segoe UI", size=9)
        self.f_close    = tkfont.Font(family="Segoe UI", size=11, weight="bold")

    def _create_rounded_button(self, parent, text: str, command, bg_color: str,
                               hover_color: str, fg_color: str,
                               width: int = 100, height: int = 38, radius: int = 10):
        """ساخت دکمه با گوشه‌های گرد و افکت بصری هاور با رندر آنتی‌الیاس Pillow"""
        img_norm = make_rounded_rect_img(width, height, radius, COLORS["bg"], bg_color)
        img_hov  = make_rounded_rect_img(width, height, radius, COLORS["bg"], hover_color)

        btn = tk.Label(parent, image=img_norm, text=text, compound="center",
                       fg=fg_color, font=self.f_btn, bg=COLORS["bg"],
                       bd=0, cursor="hand2")
        btn.img_norm = img_norm
        btn.img_hov  = img_hov

        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.config(image=btn.img_hov))
        btn.bind("<Leave>", lambda e: btn.config(image=btn.img_norm))
        return btn

    def _make_curved_entry(self, parent, default: str, field_type: str = "hour", is_base: bool = True):
        """ساخت کادر اختصاصی ارقام با لبه خمیده و پشتیبانی از اسکرول و کلیدهای جهت‌نما"""
        accent_color = COLORS["accent"] if is_base else COLORS["accent2"]
        select_bg = accent_color
        select_fg = "#0f0f1a" if self.current_theme == "dark" else "#ffffff"

        slot = CurvedEntrySlot(parent, default=default,
                               parent_bg=COLORS["card"],
                               fill_bg=COLORS["entry_bg"],
                               border_color=COLORS["border"],
                               focus_border_color=accent_color,
                               fg_color=COLORS["text"],
                               select_bg=select_bg,
                               select_fg=select_fg,
                               w=82, h=50, radius=10,
                               font=self.f_entry)

        e = slot.entry

        # اتصالات میانبرهای کلیپ‌بورد روی فیلد
        e.bind("<Control-v>", lambda ev: self._on_ctrl_v(ev))
        e.bind("<Control-V>", lambda ev: self._on_ctrl_v(ev))
        e.bind("<Control-c>", lambda ev: self._on_ctrl_c(ev))
        e.bind("<Control-C>", lambda ev: self._on_ctrl_c(ev))
        e.bind("<Button-3>", lambda ev: self._on_ctrl_v(ev))
        slot.bind("<Button-3>", lambda ev: self._on_ctrl_v(ev))

        # تغییر اعداد با کلیدهای بالا/پایین و چرخ ماوس
        e.bind("<Up>", lambda ev: self._adjust_entry(e, field_type, 1))
        e.bind("<Down>", lambda ev: self._adjust_entry(e, field_type, -1))
        e.bind("<MouseWheel>", lambda ev: self._on_mousewheel_entry(ev, e, field_type))

        e.bind("<FocusOut>", lambda ev: self._on_entry_focus_out(e), add="+")

        return e

    def _build_ui(self):
        """چیدمان ساختار رابط کاربری برنامه"""
        self.root.configure(bg=COLORS["bg"])
        self._build_titlebar()

        self.content = tk.Frame(self.root, bg=COLORS["bg"])
        self.content.pack(fill="both", expand=True)

        for i in range(5):
            self.content.grid_rowconfigure(i, weight=(1 if i == 4 else 0))
        self.content.grid_columnconfigure(0, weight=1)

        # بخش بالای صفحه (عنوان و راهنمای کلیدها)
        header = tk.Frame(self.content, bg=COLORS["bg"])
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 6))

        tk.Label(header, text="Clock Plus", bg=COLORS["bg"],
                 fg=COLORS["accent"], font=self.f_h1).pack(anchor="w")
        tk.Label(header,
                 text="Ctrl+V = پیست ساعت • Ctrl+C = کپی نتیجه تبدیل‌شده • Enter = محاسبه",
                 bg=COLORS["bg"], fg=COLORS["text_dim"],
                 font=self.f_subtitle).pack(anchor="w", pady=(3, 0))

        # --- ۱. کارت ساعت پایه با لبه‌های کاملاً گرد ---
        base_card = RoundedFrame(self.content, bg_parent=COLORS["bg"], fill_color=COLORS["card"],
                                 border_color=COLORS["border"], radius=16, border_w=1, height=135)
        base_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(12, 8))
        self._card_title(base_card.container, "ساعت پایه", "ساعت و دقیقه")

        base_row = tk.Frame(base_card.container, bg=COLORS["card"])
        base_row.pack(pady=(10, 16))

        self.base_hour = self._make_curved_entry(base_row, "12", field_type="hour", is_base=True)
        self.base_hour.slot.pack(side="left", padx=8)

        tk.Label(base_row, text=":", bg=COLORS["card"], fg=COLORS["accent"],
                 font=self.f_colon).pack(side="left")

        self.base_minute = self._make_curved_entry(base_row, "00", field_type="minute", is_base=True)
        self.base_minute.slot.pack(side="left", padx=8)

        # --- ۲. کارت مقدار اضافه با لبه‌های کاملاً گرد ---
        add_card = RoundedFrame(self.content, bg_parent=COLORS["bg"], fill_color=COLORS["card"],
                                border_color=COLORS["border"], radius=16, border_w=1, height=135)
        add_card.grid(row=2, column=0, sticky="ew", padx=30, pady=(4, 8))
        self._card_title(add_card.container, "مقدار اضافه", "ذخیره در حافظه")

        add_row = tk.Frame(add_card.container, bg=COLORS["card"])
        add_row.pack(pady=(10, 16))

        saved_ah = self.settings.get("add_hour", "0")
        saved_am = self.settings.get("add_minute", "0")

        self.add_hour = self._make_curved_entry(add_row, saved_ah, field_type="add_hour", is_base=False)
        self.add_hour.slot.pack(side="left", padx=8)

        tk.Label(add_row, text=":", bg=COLORS["card"], fg=COLORS["accent2"],
                 font=self.f_colon).pack(side="left")

        self.add_minute = self._make_curved_entry(add_row, saved_am, field_type="minute", is_base=False)
        self.add_minute.slot.pack(side="left", padx=8)

        # پیوند پرش خودکار (Auto-Tab) بین فیلد ساعت و دقیقه پس از درج دو رقم
        self.base_hour.bind("<KeyRelease>", lambda ev: self._on_entry_key_release(ev, self.base_hour, self.base_minute))
        self.add_hour.bind("<KeyRelease>", lambda ev: self._on_entry_key_release(ev, self.add_hour, self.add_minute))

        # --- ۳. ردیف دکمه‌های کنترل با گوشه‌های گرد ---
        btn_row = tk.Frame(self.content, bg=COLORS["bg"])
        btn_row.grid(row=3, column=0, pady=(14, 10))

        # دکمه محاسبه
        self._create_rounded_button(
            btn_row, "محاسبه", self.calculate,
            COLORS["accent"], COLORS["accent_h"], "#0f0f1a",
            width=106, height=38, radius=10
        ).grid(row=0, column=0, padx=3)

        # دکمه الان (نشاندن ساعت فعلی سیستم)
        self._create_rounded_button(
            btn_row, "الان", self.now_time,
            COLORS["accent2"], COLORS["accent2_h"], "white",
            width=68, height=38, radius=10
        ).grid(row=0, column=1, padx=3)

        # دکمه Paste دستی
        self._create_rounded_button(
            btn_row, "Paste", lambda: self._on_ctrl_v(),
            COLORS["btn_purple"], COLORS["btn_purple_h"], "white",
            width=78, height=38, radius=10
        ).grid(row=0, column=2, padx=3)

        # دکمه تغییر تم با آیکون وکتور خورشید/ماه
        if self.current_theme == "dark":
            theme_pil = create_sun_pil(size=20, color="#f59e0b")
        else:
            theme_pil = create_moon_pil(size=20, color="#6366f1")

        self.theme_img_norm = make_rounded_icon_img(40, 38, 10, COLORS["bg"], COLORS["btn_gray"], theme_pil)
        self.theme_img_hov  = make_rounded_icon_img(40, 38, 10, COLORS["bg"], COLORS["btn_gray_h"], theme_pil)

        self.theme_btn = tk.Label(btn_row, image=self.theme_img_norm,
                                   bg=COLORS["bg"], bd=0, cursor="hand2")
        self.theme_btn.grid(row=0, column=3, padx=3)
        self.theme_btn.bind("<Button-1>", lambda e: self.toggle_theme())
        self.theme_btn.bind("<Enter>", lambda e: self.theme_btn.config(image=self.theme_img_hov))
        self.theme_btn.bind("<Leave>", lambda e: self.theme_btn.config(image=self.theme_img_norm))

        # دکمه سنجاق پنجره (Always on top) با آیکون وکتور پین
        pin_inact_pil = create_pin_pil(size=20, color=("#94a3b8" if self.current_theme == "dark" else "#64748b"))
        pin_act_pil   = create_pin_pil(size=20, color=COLORS["accent"])

        self.pin_img_norm = make_rounded_icon_img(40, 38, 10, COLORS["bg"], COLORS["btn_gray"], pin_inact_pil)
        self.pin_img_hov  = make_rounded_icon_img(40, 38, 10, COLORS["bg"], COLORS["btn_gray_h"], pin_inact_pil)
        self.pin_img_act  = make_rounded_icon_img(40, 38, 10, COLORS["bg"], COLORS["card2"], pin_act_pil,
                                                 border_color=COLORS["accent"])
        self.pin_img_act_hov = make_rounded_icon_img(40, 38, 10, COLORS["bg"], COLORS["card"], pin_act_pil,
                                                     border_color=COLORS["accent_h"])

        cur_pin_img = self.pin_img_act if self.is_pinned else self.pin_img_norm
        self.pin_btn = tk.Label(btn_row, image=cur_pin_img,
                                 bg=COLORS["bg"], bd=0, cursor="hand2")
        self.pin_btn.grid(row=0, column=4, padx=3)
        self.pin_btn.bind("<Button-1>", lambda e: self.toggle_pin())
        self.pin_btn.bind("<Enter>", lambda e: self._pin_hover_in())
        self.pin_btn.bind("<Leave>", lambda e: self._pin_hover_out())

        # --- ۴. کارت بزرگ نتیجه نهایی با قابلیت کلیک برای کپی ---
        result_wrap = tk.Frame(self.content, bg=COLORS["bg"])
        result_wrap.grid(row=4, column=0, sticky="nsew", padx=30, pady=(10, 25))

        self.result_card = RoundedFrame(result_wrap, bg_parent=COLORS["bg"], fill_color=COLORS["card2"],
                                        border_color=COLORS["accent"], radius=18, border_w=2)
        self.result_card.pack(fill="both", expand=True)

        tk.Label(self.result_card.container, text="نتیجه تبدیل‌شده   (Ctrl+C یا کلیک = کپی)",
                 bg=COLORS["card2"], fg=COLORS["text_dim"],
                 font=self.f_small).pack(pady=(12, 0))

        self.result_label = tk.Label(self.result_card.container, text="--:--",
                                      bg=COLORS["card2"], fg=COLORS["accent"],
                                      font=self.f_result, cursor="hand2")
        self.result_label.pack(expand=True, fill="both", padx=10, pady=8)

        # بایند کلیک و هاور روی کارت نتیجه برای کپی سریع
        for widget in (self.result_card, self.result_card.container, self.result_label):
            widget.bind("<Button-1>", self._on_ctrl_c)
            widget.bind("<Enter>", self._result_hover_on)
            widget.bind("<Leave>", self._result_hover_off)

        # --- ۵. کادر پیام شناور (Toast Notification) ---
        self._toast_frame = tk.Frame(self.root, bg=COLORS["accent"], padx=16, pady=8,
                                     highlightbackground=COLORS["border"], highlightthickness=1)
        self._toast_label = tk.Label(self._toast_frame, text="", bg=COLORS["accent"],
                                     fg="#0f0f1a", font=("Segoe UI", 10, "bold"))
        self._toast_label.pack()

    def _pin_hover_in(self):
        """افکت هاور دکمه پین پنجره"""
        if self.is_pinned:
            self.pin_btn.config(image=self.pin_img_act_hov)
        else:
            self.pin_btn.config(image=self.pin_img_hov)

    def _pin_hover_out(self):
        """خروج موس از روی دکمه پین پنجره"""
        if self.is_pinned:
            self.pin_btn.config(image=self.pin_img_act)
        else:
            self.pin_btn.config(image=self.pin_img_norm)

    def toggle_pin(self):
        """تغییر وضعیت سنجاق بودن پنجره روی سایر برنامه‌ها (Always-on-Top)"""
        self.is_pinned = not self.is_pinned
        self.root.attributes("-topmost", self.is_pinned)
        if self.is_pinned:
            self.pin_btn.config(image=self.pin_img_act)
            self._show_toast("پنجره روی سایر برنامه‌ها پین شد")
        else:
            self.pin_btn.config(image=self.pin_img_norm)
            self._show_toast("حالت پین غیرفعال شد")

    def _build_titlebar(self):
        """ساخت نوار عنوان اختصاصی با دکمه‌های بستن، مینی‌مایز و قابلیت درگ با ماوس"""
        bar = tk.Frame(self.root, bg=COLORS["titlebar"], height=38)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        title = tk.Label(bar, text="Clock Plus",
                         bg=COLORS["titlebar"], fg=COLORS["text"],
                         font=self.f_title)
        title.pack(side="left", padx=14)

        close_btn = tk.Label(bar, text="✕", bg=COLORS["titlebar"],
                             fg=COLORS["text_dim"], font=self.f_close,
                             width=4, cursor="hand2")
        close_btn.pack(side="right", fill="y")
        close_btn.bind("<Button-1>", lambda e: self._on_close())
        close_btn.bind("<Enter>", lambda e: close_btn.config(
            bg=COLORS["close_h"], fg="white"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(
            bg=COLORS["titlebar"], fg=COLORS["text_dim"]))

        min_btn = tk.Label(bar, text="—", bg=COLORS["titlebar"],
                           fg=COLORS["text_dim"], font=self.f_close,
                           width=4, cursor="hand2")
        min_btn.pack(side="right", fill="y")
        min_btn.bind("<Button-1>", lambda e: self.root.iconify())
        min_btn.bind("<Enter>", lambda e: min_btn.config(
            bg=COLORS["min_h"], fg="white"))
        min_btn.bind("<Leave>", lambda e: min_btn.config(
            bg=COLORS["titlebar"], fg=COLORS["text_dim"]))

        for widget in (bar, title):
            widget.bind("<Button-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._do_drag)

    def _start_drag(self, event):
        """ثبت نقطه شروع کلیک برای کشیدن پنجره"""
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_drag(self, event):
        """جابجایی پنجره همگام با حرکت ماوس روی تایتل‌بار"""
        x = self.root.winfo_x() + (event.x - self._drag_x)
        y = self.root.winfo_y() + (event.y - self._drag_y)
        self.root.geometry(f"+{x}+{y}")

    def _card_title(self, parent, text: str, hint: str = None):
        """رندر هدر داخل کارت‌ها شامل نشانگر رنگی عمودی، عنوان و زیرعنوان"""
        row = tk.Frame(parent, bg=COLORS["card"])
        row.pack(anchor="w", padx=14, pady=(10, 0), fill="x")

        tk.Frame(row, bg=COLORS["accent"], width=3, height=18).pack(side="left")

        tk.Label(row, text=f"  {text}", bg=COLORS["card"],
                 fg=COLORS["text"], font=self.f_label).pack(side="left")

        if hint:
            tk.Label(row, text=f"  —  {hint}", bg=COLORS["card"],
                     fg=COLORS["text_dim"], font=self.f_small).pack(side="left")

    def _on_entry_key_release(self, event, current_entry, next_entry):
        """
        رویداد پس از تایپ کاراکتر در فیلد ورودی:
        - تبدیل خودکار ارقام فارسی به انگلیسی در لحظه
        - پرش خودکار به فیلد بعدی (Auto-Tab) پس از ورود ۲ رقم
        - راه‌اندازی تایمر محاسبه خودکار
        """
        raw = current_entry.get()
        converted = normalize_digits(raw)
        if raw != converted:
            pos = current_entry.index(tk.INSERT)
            current_entry.delete(0, tk.END)
            current_entry.insert(0, converted)
            current_entry.icursor(pos)

        self._on_entry_change()

        # پرش هوشمند به فیلد دقیقه پس از درج دو رقم ساعت
        if event.keysym not in ("BackSpace", "Delete", "Left", "Right", "Tab", "Return", "KP_Enter", "Up", "Down"):
            val = current_entry.get().strip().lstrip("-")
            if len(val) >= 2 and next_entry is not None:
                next_entry.focus_set()
                next_entry.select_range(0, tk.END)

    def _on_entry_focus_out(self, entry):
        """هنگام خروج فوکوس: ذخیره‌سازی مقادیر و تصحیح ارقام فارسی"""
        raw = entry.get()
        converted = normalize_digits(raw)
        if raw != converted:
            entry.delete(0, tk.END)
            entry.insert(0, converted)
        self._on_entry_change()

    def _adjust_entry(self, entry, field_type: str, delta: int):
        """
        افزایش یا کاهش عدد فیلد با کلیدهای جهت‌نما یا چرخ ماوس:
        - فیلد ساعت: چرخه ۲۴ ساعته (۰ تا ۲۳)
        - فیلد دقیقه: چرخه ۶۰ دقیقه‌ای (۰ تا ۵۹)
        - فیلد ساعت اضافه: اعداد صحیح دلخواه حتی منفی
        """
        val_str = normalize_digits(entry.get()).strip()
        try:
            val = int(val_str) if val_str not in ("", "-") else 0
        except ValueError:
            val = 0

        val += delta

        if field_type == "hour":
            val = val % 24
            formatted = f"{val:02d}"
        elif field_type == "minute":
            val = val % 60
            formatted = f"{val:02d}"
        elif field_type == "add_hour":
            formatted = str(val)
        else:
            formatted = str(val)

        entry.delete(0, tk.END)
        entry.insert(0, formatted)
        entry.select_range(0, tk.END)

        self._save_add_values()
        self.calculate()
        return "break"

    def _on_mousewheel_entry(self, event, entry, field_type: str):
        """پاسخ به چرخ ماوس روی فیلدهای ورودی عدد"""
        delta = 1 if event.delta > 0 else -1
        return self._adjust_entry(entry, field_type, delta)

    def _on_enter_pressed(self, event=None):
        """محاسبه فوری زمان با فشردن کلید اینتر"""
        self.calculate()
        return "break"

    def _on_entry_change(self):
        """ذخیره مقادیر و تنظیم زمان‌بند برای محاسبه با تاخیر کم (Debounce)"""
        self._save_add_values()
        self._auto_calculate()

    def _save_add_values(self):
        """ذخیره مقادیر افزایشی در تنظیمات JSON جهت ماندگاری بین دفعات باز شدن برنامه"""
        try:
            ah = normalize_digits(self.add_hour.get()).strip() or "0"
            am = normalize_digits(self.add_minute.get()).strip() or "0"
            self.settings["add_hour"] = ah
            self.settings["add_minute"] = am
            save_settings(self.settings)
        except Exception:
            pass

    def _auto_calculate(self):
        """محاسبه خودکار با ایجاد وقفه ۳۵۰ میلی‌ثانیه‌ای حین تایپ"""
        if self._auto_calc_id:
            try:
                self.root.after_cancel(self._auto_calc_id)
            except Exception:
                pass
        self._auto_calc_id = self.root.after(350, self.calculate)

    def parse_entry(self, entry) -> int:
        """تبدیل محتوای متنی فیلد ورودی به عدد صحیح با در نظر گرفتن خالی بودن"""
        val = normalize_digits(entry.get()).strip()
        if val == "" or val == "-":
            return 0
        return int(val)

    def calculate(self):
        """
        منطق محاسباتی اصلی برنامه:
        - دریافت ساعت و دقیقه پایه و اعتبارسنجی بازه مجاز (۰ تا ۲۳ و ۰ تا ۵۹)
        - دریافت ساعت و دقیقه افزایشی
        - اعمال جمع یا تفریق زمانی بر مبنای timedelta
        - به‌روزرسانی نمایشگر بزرگ نتیجه با فرمت HH:MM
        """
        try:
            bh = self.parse_entry(self.base_hour)
            bm = self.parse_entry(self.base_minute)
            ah = self.parse_entry(self.add_hour)
            am = self.parse_entry(self.add_minute)

            if not (0 <= bh <= 23):
                self._show_error("ساعت باید بین ۰ تا ۲۳ باشد")
                return
            if not (0 <= bm <= 59):
                self._show_error("دقیقه باید بین ۰ تا ۵۹ باشد")
                return

            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            base_time = today + timedelta(hours=bh, minutes=bm)

            # اگر مقدار ساعت افزایشی منفی باشد، تفریق زمان انجام می‌شود
            if ah < 0:
                final_time = base_time - timedelta(hours=abs(ah), minutes=am)
            else:
                final_time = base_time + timedelta(hours=ah, minutes=am)

            self.result_label.config(text=final_time.strftime("%H:%M"),
                                      fg=COLORS["accent"],
                                      font=self.f_result)
            self._save_add_values()
        except ValueError:
            self._show_error("لطفاً عدد معتبر وارد کنید")

    def _show_error(self, msg: str):
        """نمایش پیام خطا درون کادر نتیجه با رنگ قرمز"""
        self.result_label.config(text=msg, fg=COLORS["danger"], font=self.f_error)

    def now_time(self):
        """نشاندن ساعت و دقیقه جاری سیستم در فیلدهای ساعت پایه و اجرای محاسبه"""
        now = datetime.now()
        self.base_hour.delete(0, tk.END)
        self.base_hour.insert(0, f"{now.hour:02d}")
        self.base_minute.delete(0, tk.END)
        self.base_minute.insert(0, f"{now.minute:02d}")
        self.calculate()

    def _result_hover_on(self, event=None):
        """روشن شدن کادر هایلایت نتیجه هنگام حرکت ماوس روی آن"""
        self.result_card.set_border(COLORS["accent_h"], border_w=2)
        if ":" in self.result_label.cget("text"):
            self.result_label.config(fg=COLORS["accent_h"])

    def _result_hover_off(self, event=None):
        """بازگشت کادر نتیجه به حالت عادی پس از خروج ماوس"""
        self.result_card.set_border(COLORS["accent"], border_w=2)
        if ":" in self.result_label.cget("text"):
            self.result_label.config(fg=COLORS["accent"])

    def _show_toast(self, msg: str):
        """نمایش پیام شناور درون‌پنجره‌ای (Toast) با انیمیشن محو خودکار پس از ۱.۶ ثانیه"""
        if self._toast_after_id is not None:
            try:
                self.root.after_cancel(self._toast_after_id)
            except Exception:
                pass
            self._toast_after_id = None

        self._toast_frame.config(bg=COLORS["accent"])
        self._toast_label.config(text=msg, bg=COLORS["accent"], fg="#0f0f1a")
        self._toast_frame.place(relx=0.5, rely=0.95, anchor="s")
        self._toast_frame.lift()
        self._toast_after_id = self.root.after(1600, self._hide_toast)

    def _hide_toast(self):
        """مخفی کردن پیام شناور Toast"""
        self._toast_frame.place_forget()
        self._toast_after_id = None

    def _on_close(self):
        """رویداد بسته شدن پنجره: ذخیره قطعی آخرین ابعاد و موقعیت مکانی و خروج تمیز"""
        try:
            self._save_add_values()
            if self.root.state() == "normal":
                self.settings["geometry"] = self.root.geometry()
            save_settings(self.settings)
        except Exception:
            pass
        self.root.destroy()


# ==============================================================================
# ۱۰. نقطه شروع اجرای برنامه (Main Entry Point)
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernTimeCalculator(root)
    root.mainloop()
