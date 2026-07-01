# -*- coding: utf-8 -*-
"""
Mao Quote Wallpaper Generator (毛选语录艺术壁纸生成器)

Cross-platform calligraphic desktop wallpaper from Mao Zedong's Selected Works.
Works on Windows, macOS, and Linux.

Usage:
    python gen_wallpaper.py --quote "星星之火，可以燎原" \
        --volume "《毛泽东选集》第一卷" \
        --article "《星星之火，可以燎原》" \
        --date "一九三〇年一月五日" \
        --year "一九三〇" \
        --note "毛泽东致林彪的复信..." \
        --output wallpaper.png [--set-wallpaper]

Author: WorkBuddy AI (penapinner)
License: MIT
"""
import argparse, math, random, os, sys, subprocess, platform, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


# ======================== Font Detection ========================

_FONT_DIRS = []

_sys = platform.system()
if _sys == "Windows":
    _FONT_DIRS = [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"),
        r"C:\Windows\Fonts",
    ]
elif _sys == "Darwin":
    _FONT_DIRS = [
        os.path.expanduser("~/Library/Fonts"),
        "/Library/Fonts",
        "/System/Library/Fonts",
    ]
else:  # Linux
    _FONT_DIRS = [
        os.path.expanduser("~/.fonts"),
        os.path.expanduser("~/.local/share/fonts"),
        "/usr/share/fonts",
        "/usr/local/share/fonts",
    ]


def _find_font(keywords, fallback_keywords=None):
    """Search font directories for a font matching any of the keywords.
    Primary keywords are searched first; fallback only if nothing found."""
    # Phase 1: search primary keywords only
    for d in _FONT_DIRS:
        if not os.path.isdir(d):
            continue
        for root, _dirs, files in os.walk(d):
            for f in files:
                lower = f.lower()
                if not lower.endswith((".ttf", ".ttc", ".otf")):
                    continue
                for kw in keywords:
                    if kw in lower:
                        return os.path.join(root, f)
    # Phase 2: search fallback keywords only if primary yielded nothing
    if fallback_keywords:
        for d in _FONT_DIRS:
            if not os.path.isdir(d):
                continue
            for root, _dirs, files in os.walk(d):
                for f in files:
                    lower = f.lower()
                    if not lower.endswith((".ttf", ".ttc", ".otf")):
                        continue
                    for kw in fallback_keywords:
                        if kw in lower:
                            return os.path.join(root, f)
    # Last resort: find any CJK-capable font
    for d in _FONT_DIRS:
        if not os.path.isdir(d):
            continue
        for root, _dirs, files in os.walk(d):
            for f in files:
                lower = f.lower()
                if not lower.endswith((".ttf", ".ttc", ".otf")):
                    continue
                if any(k in lower for k in ["msyh", "yahei", "simhei", "simsun", "songti",
                                            "kaiti", "xing", "fang", "hei", "deng",
                                            "kaiu", "kai", "ming", "yuan"]):
                    return os.path.join(root, f)
    raise FileNotFoundError(
        "No Chinese font found.\n"
        "Install one of: 微软雅黑, 黑体, 宋体, 楷体, or any CJK font."
    )


@functools.lru_cache(maxsize=None)
def detect_screen_resolution():
    """Auto-detect primary monitor resolution. Returns (width, height)."""
    try:
        if platform.system() == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            # GetDeviceCaps DESKTOPHORZRES/DESKTOPVERTRES = actual physical pixels
            gdi32 = ctypes.windll.gdi32
            hdc = user32.GetDC(0)
            w = gdi32.GetDeviceCaps(hdc, 118)
            h = gdi32.GetDeviceCaps(hdc, 117)
            user32.ReleaseDC(0, hdc)
            if w > 0 and h > 0:
                return w, h
            return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        elif platform.system() == "Darwin":
            import subprocess
            out = subprocess.check_output(
                ["system_profiler", "SPDisplaysDataType"], text=True, timeout=5
            )
            for line in out.splitlines():
                if "Resolution" in line:
                    for part in line.split():
                        if "x" in part and part.replace("x", "").strip().isdigit():
                            w_s, h_s = part.split("x")
                            return int(w_s), int(h_s)
            return 1920, 1080
        else:  # Linux
            import subprocess
            out = subprocess.check_output(
                ["xrandr", "--current"], text=True, timeout=5
            )
            for line in out.splitlines():
                if "*" in line:
                    for part in line.split():
                        if "x" in part:
                            w_s = part.split("x")[0]
                            # Handle "x1080" or "1920x1080"
                            h_part = part.split("x")[1].split("+")[0].split()[0]
                            if w_s.lstrip("+-").isdigit() and h_part.lstrip("+-").isdigit():
                                return int(w_s), int(h_part)
            return 1920, 1080
    except Exception:
        return 1920, 1080


@functools.lru_cache(maxsize=None)
def detect_calligraphy_font():
    # 指定: 项目目录下的汉仪黄科行书简
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_font = os.path.join(script_dir, "hanyihuangkexingshujian.ttf")
    if os.path.isfile(local_font):
        return local_font
    return _find_font(
        ["huangkexingshu", "hanyihuang", "hyhuang"],
        ["xingkai", "xingka", "stxing", "kaiti", "simkai", "songti", "simsun"],
    )


@functools.lru_cache(maxsize=None)
def detect_kaiti_font():
    # 指定: Windows 楷体
    if platform.system() == "Windows":
        for p in [r"C:\Windows\Fonts\simkai.ttf", r"C:\Windows\Fonts\kaiu.ttf",
                  r"C:\Windows\Fonts\STKAITI.TTF"]:
            if os.path.isfile(p):
                return p
    return _find_font(["kaiti", "simkai", "kaiu"], ["xingkai", "stxing", "songti"])


@functools.lru_cache(maxsize=None)
def detect_hei_font():
    # 指定: Windows 微软雅黑
    if platform.system() == "Windows":
        for p in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf",
                  r"C:\Windows\Fonts\simsun.ttc", r"C:\Windows\Fonts\deng.ttf"]:
            if os.path.isfile(p):
                return p
    return _find_font(
        ["msyh", "yahei", "simhei", "hei", "deng"],
        ["simsun", "songti", "fang", "ming", "sans"],
    )


# ======================== Argument Parsing ========================

def parse_args():
    p = argparse.ArgumentParser(
        description="毛选语录艺术壁纸生成器 — Mao Quote Calligraphic Wallpaper Generator"
    )
    p.add_argument("--quote", required=True, help="主语录文本 (quote text)")
    p.add_argument("--volume", required=True, help="出处卷次 (volume)")
    p.add_argument("--article", required=True, help="出处篇名 (article title)")
    p.add_argument("--date", required=True, help="日期，如 一九三〇年一月五日")
    p.add_argument("--year", help="左下角竖排年份，如 一九三〇（与 --vertical-year 同义）")
    p.add_argument("--vertical-year", help="左下角竖排年份，如 一九三〇（与 --year 同义）")
    p.add_argument("--note", required=True, help="段落注释 (annotation)")
    p.add_argument("--output", default="mao_quote_wallpaper.png", help="输出PNG路径")
    p.add_argument("--font", default=None, help="主书法字体路径 (auto-detect)")
    p.add_argument("--font-kaiti", default=None, help="楷体路径")
    p.add_argument("--font-hei", default=None, help="黑体路径")
    p.add_argument("--font-size", type=int, default=None, help="主文字号 (auto-calc)")
    p.add_argument("--width", type=int, default=0, help="宽度 (default: 自动检测屏幕分辨率)")
    p.add_argument("--height", type=int, default=0, help="高度 (default: 自动检测屏幕分辨率)")
    p.add_argument("--seed", type=int, default=None, help="随机种子")
    p.add_argument("--set-wallpaper", action="store_true", help="生成后设为桌面壁纸")
    return p.parse_args()


# ======================== Layout ========================

def calc_font_size(quote, max_width, font_path):
    char_count = len(quote)
    if char_count <= 6:
        return 220
    elif char_count <= 10:
        return 190
    elif char_count <= 15:
        return 150
    elif char_count <= 20:
        return 110
    elif char_count <= 30:
        return 80
    else:
        return 60


# ======================== Wallpaper Setter ========================

def set_wallpaper(image_path):
    """Set the given image as desktop wallpaper (cross-platform)."""
    abs_path = os.path.abspath(image_path)
    _sys = platform.system()

    if _sys == "Windows":
        import ctypes
        result = ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
        if not result:
            raise RuntimeError("Failed to set wallpaper on Windows")
        print(f"[OK] Wallpaper set on Windows")

    elif _sys == "Darwin":
        # macOS: use osascript to tell Finder
        script = f'''
        tell application "Finder"
            set desktop picture to POSIX file "{abs_path}"
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", script], check=True)
            print(f"[OK] Wallpaper set on macOS")
        except subprocess.CalledProcessError:
            # Fallback: try systemevents for all spaces
            script2 = f'''
            tell application "System Events"
                set picture of every desktop to "{abs_path}"
            end tell
            '''
            subprocess.run(["osascript", "-e", script2], check=True)
            print(f"[OK] Wallpaper set on macOS (all spaces)")

    elif _sys == "Linux":
        # Try various desktop environments
        env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        tried = []
        success = False

        # GNOME
        if not success:
            try:
                subprocess.run(
                    ["gsettings", "set", "org.gnome.desktop.background",
                     "picture-uri", f"file://{abs_path}"],
                    check=True, capture_output=True,
                )
                print(f"[OK] Wallpaper set on GNOME")
                success = True
            except Exception:
                tried.append("gsettings (GNOME)")

        # KDE
        if not success:
            try:
                subprocess.run(
                    ["plasma-apply-wallpaperimage", abs_path],
                    check=True, capture_output=True,
                )
                print(f"[OK] Wallpaper set on KDE")
                success = True
            except Exception:
                tried.append("plasma-apply-wallpaperimage (KDE)")

        # XFCE
        if not success:
            try:
                monitors = subprocess.check_output(
                    ["xfconf-query", "-c", "xfce4-desktop", "-l"],
                    text=True,
                ).strip().split("\n")
                for m in monitors:
                    if "image-path" in m or "last-image" in m:
                        subprocess.run(
                            ["xfconf-query", "-c", "xfce4-desktop",
                             "-p", m, "-s", abs_path],
                            check=True,
                        )
                print(f"[OK] Wallpaper set on XFCE")
                success = True
            except Exception:
                tried.append("xfconf-query (XFCE)")

        # feh (generic)
        if not success:
            try:
                subprocess.run(
                    ["feh", "--bg-fill", abs_path],
                    check=True, capture_output=True,
                )
                print(f"[OK] Wallpaper set via feh")
                success = True
            except Exception:
                tried.append("feh")

        if not success:
            print(f"[WARN] Could not set wallpaper automatically on Linux.")
            print(f"   Tried: {', '.join(tried)}")
            print(f"   Image saved to: {abs_path}")


# ======================== Generator ========================

def generate(args):
    W, H = args.width, args.height
    if W <= 0 or H <= 0:
        detected = detect_screen_resolution()
        if W <= 0:
            W = detected[0]
        if H <= 0:
            H = detected[1]
        print(f">>> 自动检测屏幕分辨率: {W}x{H}")
    if args.seed is not None:
        random.seed(args.seed)

    # Fonts
    FONT_MAIN = args.font or detect_calligraphy_font()
    FONT_KAITI = args.font_kaiti or detect_kaiti_font()
    FONT_HEI = args.font_hei or detect_hei_font()
    font_size = args.font_size or calc_font_size(args.quote, W * 0.75, FONT_MAIN)

    # Resolve year (either --year or --vertical-year)
    year = args.year or args.vertical_year
    if not year:
        raise ValueError("必须提供 --year 或 --vertical-year 参数")

    # ---- Color palette (bright / parchment style) ----
    BG_CENTER = (250, 245, 232)
    BG_EDGE   = (225, 215, 195)
    INK_TOP   = (200, 35, 35)
    INK_MID   = (160, 20, 20)
    INK_BOT   = (110, 16, 16)
    GLOW_WARM = (230, 180, 40)
    GLOW_AMBER = (210, 145, 25)
    SEAL_RED  = (200, 30, 30)
    LINE_GOLD = (160, 120, 50)
    NOTE_TITLE = (140, 100, 40)
    NOTE_BODY  = (80, 55, 30)

    print(f"{'='*60}")
    print(f"  语录: {args.quote}")
    print(f"  字体: {os.path.basename(FONT_MAIN)}")
    print(f"  字号: {font_size}px | 尺寸: {W}x{H}")
    print(f"{'='*60}")

    # --- 1. Background ---
    print(">>> 1/6  Background...")
    img = Image.new('RGB', (W, H), BG_EDGE)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = abs(y - H * 0.46) / (H * 0.52)
        t = min(t, 1.0)
        ease = 3 * t*t - 2 * t*t*t
        r = int(BG_CENTER[0] * (1 - ease) + BG_EDGE[0] * ease)
        g = int(BG_CENTER[1] * (1 - ease) + BG_EDGE[1] * ease)
        b = int(BG_CENTER[2] * (1 - ease) + BG_EDGE[2] * ease)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Paper texture
    tex = Image.new('L', (W, H), 128)
    tex_draw = ImageDraw.Draw(tex)
    for _ in range(3000):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        tex_draw.point((x, y), fill=random.randint(124, 132))
    tex = tex.filter(ImageFilter.GaussianBlur(0.8))
    img = Image.blend(img, Image.merge('RGB', (tex, tex, tex)), 0.06)

    # --- 2. Warm glow ---
    print(">>> 2/6  Glow...")
    cx, cy = W // 2, int(H * 0.46)
    glow = Image.new('RGB', (W, H), BG_CENTER)
    glow_draw = ImageDraw.Draw(glow)
    for r in range(550, 0, -10):
        progress = 1 - r / 550
        intensity = progress ** 2
        cr = int(255 * (1 - intensity) + 235 * intensity)
        cg = int(245 * (1 - intensity) + 200 * intensity)
        cb = int(232 * (1 - intensity) + 130 * intensity)
        glow_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.blend(img, glow, 0.6)

    # --- 3. Spark particles ---
    print(">>> 3/6  Particles...")
    spark = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    spark_draw = ImageDraw.Draw(spark)
    for _ in range(60):
        x = random.randint(0, W)
        y = random.randint(int(H * 0.35), H)
        size = random.uniform(1.5, 4)
        b = random.uniform(0.25, 0.75)
        cr = int(220 * b + 35 * (1 - b))
        cg = int(150 * b + 180 * (1 - b))
        cb = int(30 * b + 200 * (1 - b))
        spark_draw.ellipse([x - size, y - size, x + size, y + size], fill=(cr, cg, cb, int(150 * b)))
        spark_draw.ellipse([x - size*3, y - size*3, x + size*3, y + size*3], fill=(cr, cg, cb, int(40 * b)))
    spark = spark.filter(ImageFilter.GaussianBlur(1.5))
    img = Image.alpha_composite(img.convert('RGBA'), spark).convert('RGB')

    # --- 4. Main quote ---
    print(">>> 4/6  Quote text...")
    quote = args.quote
    font_main = ImageFont.truetype(FONT_MAIN, font_size)
    bbox = font_main.getbbox(quote)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_x = (W - text_w) // 2 - bbox[0]
    text_y = cy - text_h // 2 - bbox[1]

    # Outer glow
    gm = Image.new('L', (W, H), 0)
    ImageDraw.Draw(gm).text((text_x, text_y), quote, font=font_main, fill=255)
    gb = gm.filter(ImageFilter.GaussianBlur(25))
    img = Image.composite(Image.new('RGB', (W, H), GLOW_WARM), img, ImageEnhance.Brightness(gb).enhance(0.3))
    gb2 = gm.filter(ImageFilter.GaussianBlur(10))
    img = Image.composite(Image.new('RGB', (W, H), GLOW_AMBER), img, ImageEnhance.Brightness(gb2).enhance(0.15))

    # Cinnabar gradient
    grad = Image.new('RGB', (W, H), BG_CENTER)
    for y in range(H):
        t = (y - text_y) / text_h
        t = max(0, min(1, t))
        if t < 0.35:
            tt = t / 0.35
            r = int(INK_TOP[0] * (1 - tt) + INK_MID[0] * tt)
            g = int(INK_TOP[1] * (1 - tt) + INK_MID[1] * tt)
            b = int(INK_TOP[2] * (1 - tt) + INK_MID[2] * tt)
        else:
            tt = (t - 0.35) / 0.65
            r = int(INK_MID[0] * (1 - tt) + INK_BOT[0] * tt)
            g = int(INK_MID[1] * (1 - tt) + INK_BOT[1] * tt)
            b = int(INK_MID[2] * (1 - tt) + INK_BOT[2] * tt)
        ImageDraw.Draw(grad).line([(0, y), (W, y)], fill=(r, g, b))
    img.paste(grad, (0, 0), gm)

    # Drop shadow
    sm = Image.new('L', (W, H), 0)
    ImageDraw.Draw(sm).text((text_x + 2, text_y + 2), quote, font=font_main, fill=60)
    sm = sm.filter(ImageFilter.GaussianBlur(2))
    img = Image.composite(Image.new('RGB', (W, H), BG_EDGE), img, ImageEnhance.Brightness(sm).enhance(0.4))

    # --- 5. Decorations ---
    print(">>> 5/6  Decorations...")
    draw = ImageDraw.Draw(img)

    # Separator line
    line_y = text_y + text_h + 55
    lcx, lhalf = W // 2, 140
    for x in range(lcx - lhalf, lcx + lhalf):
        t = abs(x - lcx) / lhalf
        a = int(140 * (1 - t))
        if a > 0:
            draw.point((x, line_y), fill=LINE_GOLD)
    draw.ellipse([lcx - 4, line_y - 4, lcx + 4, line_y + 4], fill=LINE_GOLD)

    # Seal stamp
    sx, sy, ss = W - 130, 70, 80
    seal = Image.new('RGBA', (ss + 20, ss + 20), (0, 0, 0, 0))
    seal_draw = ImageDraw.Draw(seal)
    seal_draw.rounded_rectangle([5, 5, ss + 10, ss + 10], radius=8, outline=(*SEAL_RED, 210), width=3)
    seal_draw.text((ss // 2 + 5, ss // 2 + 5), "毛选", font=ImageFont.truetype(FONT_MAIN, 28), fill=(*SEAL_RED, 210), anchor='mm')
    img.paste(seal, (sx, sy), seal)

    # Top-left label
    fdl = ImageFont.truetype(FONT_HEI, 14)
    draw.line([(80, 93), (115, 93)], fill=(160, 120, 60), width=1)
    draw.text((128, 85), "毛  主  席  语  录", font=fdl, fill=(160, 120, 60))

    # Bottom-left vertical year
    font_year = ImageFont.truetype(FONT_KAITI, 15)
    for i, ch in enumerate(year):
        draw.text((85, H - 180 + i * 24), ch, font=font_year, fill=(130, 95, 55))

    # --- 6. Source & annotation ---
    print(">>> 6/6  Citation...")
    font_src = ImageFont.truetype(FONT_KAITI, 22)
    font_src_book = ImageFont.truetype(FONT_KAITI, 24)
    font_nl = ImageFont.truetype(FONT_HEI, 16)
    font_note = ImageFont.truetype(FONT_HEI, 17)

    nx = W - 80
    maxw = 360

    def wrap(text, font, mw):
        lines, cur = [], ""
        for ch in text:
            test = cur + ch
            if font.getbbox(test)[2] - font.getbbox(test)[0] > mw and cur:
                lines.append(cur)
                cur = ch
            else:
                cur = test
        if cur:
            lines.append(cur)
        return lines

    # Calculate total note section height to prevent bottom overflow
    note_h = 0
    for txt, fnt in [(args.volume, font_src_book), (args.article, font_src), (args.date, font_src)]:
        bb = fnt.getbbox(txt)
        note_h += bb[3] - bb[1] + 10
    note_h += 8 + 1 + 16  # separator line and padding
    bb = font_nl.getbbox("段  落  注  释")
    note_h += bb[3] - bb[1] + 25
    for ln in wrap(args.note, font_note, maxw):
        bb = font_note.getbbox(ln)
        note_h += bb[3] - bb[1] + 8

    # Position: leave 50px bottom margin; don't overlap the separator line
    ny = min(H - 280, H - note_h - 50)
    ny = max(ny, line_y + 40)

    src_lines = [
        (args.volume, font_src_book, LINE_GOLD),
        (args.article, font_src, NOTE_TITLE),
        (args.date, font_src, NOTE_TITLE),
    ]
    cy2 = ny
    for txt, fnt, clr in src_lines:
        bb = fnt.getbbox(txt)
        draw.text((nx - (bb[2] - bb[0]), cy2), txt, font=fnt, fill=clr)
        cy2 += bb[3] - bb[1] + 10

    cy2 += 8
    draw.line([(nx - maxw, cy2), (nx, cy2)], fill=LINE_GOLD, width=1)
    cy2 += 16

    lbl = "段  落  注  释"
    bbl = font_nl.getbbox(lbl)
    draw.text((nx - (bbl[2] - bbl[0]), cy2), lbl, font=font_nl, fill=LINE_GOLD)
    cy2 += 25

    for ln in wrap(args.note, font_note, maxw):
        bb = font_note.getbbox(ln)
        draw.text((nx - (bb[2] - bb[0]), cy2), ln, font=font_note, fill=NOTE_BODY)
        cy2 += bb[3] - bb[1] + 8

    # --- Vignette ---
    vignette = Image.new('L', (W, H), 0)
    vd = ImageDraw.Draw(vignette)
    vd.rectangle([0, 0, W, H], fill=255)
    for r in range(0, 500, 5):
        vd.rectangle([r, int(r * H / W), W - r, H - int(r * H / W)], outline=255 - int(r / 500 * 100))
    vignette = vignette.filter(ImageFilter.GaussianBlur(200))
    img = Image.composite(img, Image.new('RGB', (W, H), (210, 195, 165)), vignette)

    # --- Save ---
    img.save(args.output, 'PNG', quality=95)
    print(f"\n[Done] {os.path.abspath(args.output)}  ({W}x{H})")
    return args.output


if __name__ == "__main__":
    args = parse_args()
    output = generate(args)
    if args.set_wallpaper:
        set_wallpaper(output)
