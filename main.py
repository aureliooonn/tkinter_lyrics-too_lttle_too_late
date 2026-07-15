import tkinter as tk
import random
import math
import time

# ─── LIRIK ────────────────────────────────────────────
lyrics_data = [
    ("Too little, too late - Laufey",             0),
    ("To hear you scream my name",              5280),
    ("A clear fucking X-ray",                    3920),
    ("Of if I'd stuck around",                   4050),
    ("I swear to God, I almost drowned",         4000),
    ("You asked me how I've been",               4000),
    ("But how could I begin",                    4000),
    ("To tell you I should've chased you?",      3800),
    ("I should be who you're engaged to",        3820),
    ("Lost my fight with fate",                  3470),
    ("A tug-of-war of leave and stay",           4050),
    ("I give in, I abdicate",                    3620),
    ("I lay my sword down anyway",               3700),
    ("I'll see you at Heaven's gate",            3750),
    ("'Cause it's too little, way too late",     3950),
]

lyrics = [item[0] for item in lyrics_data]
durations = [item[1] for item in lyrics_data]

# ─── PALET ELEGAN DARK (melankolis, moody, elegant) ──
THEMES = [
    ("#0f0e17", "#1a1630", "#2a1f5e", "#e8a87c"),  # midnight violet + warm peach
    ("#0d1321", "#1d2d50", "#3a4f7a", "#f4a261"),  # deep navy + gold
    ("#150d14", "#2c1628", "#4a2040", "#c77dff"),  # dark plum + lavender
    ("#0c1518", "#142b30", "#1f4a54", "#7fc8d8"),  # teal abyss + soft cyan
    ("#16100e", "#2e1a14", "#4a2818", "#d4a373"),  # espresso bronze
    ("#0e1018", "#1d2238", "#303a5e", "#e8c4c4"),  # slate + dusty rose
    ("#120e16", "#221d35", "#38305a", "#a8c4d8"),  # obsidian + steel blue
    ("#0f1410", "#1a2818", "#2a4028", "#a8c4a8"),  # dark forest + sage
]

# ─── UKURAN ────────────────────────────────────────
WIN_W, WIN_H = 540, 540

# ─── KONSTANTA ANIMASI ─────────────────────────────
SLIDE_DURATION       = 900
FADE_DURATION        = 2000
FADE_IN_DURATION     = 700
JEDA_SEBELUM_FADE_PREV = 700
CHAR_DELAY_JUDUL     = 60
JEDA_SETELAH_JUDUL   = 3000
JUMLAH_PARTIKEL      = 35
PARTIKEL_INTERVAL    = 30
CURSOR_BLINK_INTERVAL = 500

# ─── SHARED GLITCH STATE (dibikin sekali, dipakai bareng idx 9-14) ──
_shared_glitch = {
    "active": False,
    "red": None,
    "overlay": None,
    "canvas": None,
    "haze": None,
    "haze_canvas": None,
    "loops_started": False,
}

# ─── SETUP ROOT ─────────────────────────────────────
root = tk.Tk()
root.withdraw()

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()


# ═══════════════════════════════════════════════════════
#  FUNGSI BANTU GRAFIS
# ═══════════════════════════════════════════════════════

def hex_to_rgb(h):
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)

def rgb_to_hex(r, g, b):
    return f"#{max(0,min(255,int(r))):02x}{max(0,min(255,int(g))):02x}{max(0,min(255,int(b))):02x}"

def lerp_color(c1, c2, t):
    r1,g1,b1 = hex_to_rgb(c1)
    r2,g2,b2 = hex_to_rgb(c2)
    return rgb_to_hex(r1+(r2-r1)*t, g1+(g2-g1)*t, b1+(b2-b1)*t)

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_out_quart(t):
    return 1 - (1 - t) ** 4

def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2


# ═══════════════════════════════════════════════════════
#  GRADASI BACKGROUND
# ═══════════════════════════════════════════════════════

def buat_gradient(canvas, w, h, *warna):
    """Gradasi vertikal multi-warna yang halus"""
    n = len(warna)
    if n < 2:
        return
    stops = [hex_to_rgb(c) for c in warna]
    for y in range(h):
        t = y / (h - 1) if h > 1 else 0
        seg = t * (n - 1)
        i = min(int(seg), n - 2)
        lokal = seg - i
        r1,g1,b1 = stops[i]
        r2,g2,b2 = stops[i + 1]
        r = r1 + (r2 - r1) * lokal
        g = g1 + (g2 - g1) * lokal
        b = b1 + (b2 - b1) * lokal
        canvas.create_line(0, y, w, y, fill=rgb_to_hex(r, g, b), width=1)


# ═══════════════════════════════════════════════════════
#  PARTIKEL BINTANG LEMBUT (stardust)
# ═══════════════════════════════════════════════════════

class StarParticle:
    def __init__(self, w, h, accent_color):
        self.w = w
        self.h = h
        self.accent_r, self.accent_g, self.accent_b = hex_to_rgb(accent_color)
        self.reset()

    def reset(self):
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(-self.h * 0.3, self.h)
        self.size = random.uniform(0.8, 3.0)
        self.speed = random.uniform(0.06, 0.25)
        self.drift = random.uniform(-0.08, 0.08)
        self.alpha = random.uniform(0.08, 0.35)
        self.phase = random.uniform(0, math.pi * 2)
        self.float_amp = random.uniform(0, 0.4)
        self.float_freq = random.uniform(0.01, 0.04)
        self.twinkle_speed = random.uniform(0.5, 2.0)

    def update(self, waktu):
        self.y += self.speed
        self.x += self.drift + math.sin(waktu * self.float_freq + self.phase) * self.float_amp
        if self.y > self.h + 5:
            self.reset()
            self.y = -5

    def draw(self, canvas, waktu):
        twinkle = 0.6 + 0.4 * math.sin(waktu * self.twinkle_speed + self.phase)
        ca = self.alpha * twinkle
        s = self.size

        # Warna: campur accent dengan putih sesuai alpha
        cr = self.accent_r + (255 - self.accent_r) * (1 - ca)
        cg = self.accent_g + (255 - self.accent_g) * (1 - ca)
        cb = self.accent_b + (255 - self.accent_b) * (1 - ca)
        col = rgb_to_hex(cr, cg, cb)

        # Outer glow (soft)
        canvas.create_oval(
            self.x - s*2.5, self.y - s*2.5,
            self.x + s*2.5, self.y + s*2.5,
            fill=col, outline="", tags=("partikel",)
        )
        # Inner core (bright)
        canvas.create_oval(
            self.x - s*0.6, self.y - s*0.6,
            self.x + s*0.6, self.y + s*0.6,
            fill=rgb_to_hex(255, 255, 255), outline="", tags=("partikel",)
        )


# ═══════════════════════════════════════════════════════
#  PARTIKEL EMBER — melankolis, jatuh perlahan, memudar
# ═══════════════════════════════════════════════════════

class EmberParticle:
    def __init__(self, w, h, accent_color, bg_color):
        self.w = w
        self.h = h
        self.accent_r, self.accent_g, self.accent_b = hex_to_rgb(accent_color)
        self.bg_r, self.bg_g, self.bg_b = hex_to_rgb(bg_color)
        self.reset()

    def reset(self):
        self.x = random.uniform(self.w * 0.1, self.w * 0.9)
        self.y = random.uniform(-self.h * 0.5, 0)
        self.size = random.uniform(1.5, 4.5)
        self.speed = random.uniform(0.15, 0.5)
        self.drift = random.uniform(-0.3, 0.3)
        self.alpha = random.uniform(0.4, 0.85)
        self.phase = random.uniform(0, math.pi * 2)
        self.swing_amp = random.uniform(0.3, 1.0)
        self.swing_freq = random.uniform(0.008, 0.025)
        self.life = 1.0
        self.decay = random.uniform(0.002, 0.006)

    def update(self, waktu):
        self.y += self.speed
        self.x += self.drift + math.sin(waktu * self.swing_freq + self.phase) * self.swing_amp
        self.life = max(0, self.life - self.decay)
        if self.y > self.h + 10 or self.life <= 0:
            self.reset()
            self.life = 1.0

    def draw(self, canvas, waktu):
        ca = self.alpha * self.life
        if ca <= 0:
            return
        s = self.size * (0.8 + 0.4 * math.sin(waktu * 0.05 + self.phase))

        # Warna: accent → bg (memudar)
        cr = self.accent_r + (self.bg_r - self.accent_r) * (1 - self.life)
        cg = self.accent_g + (self.bg_g - self.accent_g) * (1 - self.life)
        cb = self.accent_b + (self.bg_b - self.accent_b) * (1 - self.life)
        col = rgb_to_hex(cr, cg, cb)

        # Outer glow (soft & besar)
        glow_size = s * 4
        canvas.create_oval(
            self.x - glow_size, self.y - glow_size,
            self.x + glow_size, self.y + glow_size,
            fill=col, outline="", tags=("ember",),
            stipple="gray25"
        )
        # Inner glow
        mid_size = s * 2
        canvas.create_oval(
            self.x - mid_size, self.y - mid_size,
            self.x + mid_size, self.y + mid_size,
            fill=col, outline="", tags=("ember",)
        )
        # Core putih kekuningan
        canvas.create_oval(
            self.x - s * 0.5, self.y - s * 0.5,
            self.x + s * 0.5, self.y + s * 0.5,
            fill=rgb_to_hex(
                min(255, cr + 80),
                min(255, cg + 60),
                min(255, cb + 40)
            ), outline="", tags=("ember",)
        )


# ═══════════════════════════════════════════════════════
#  FUNGSI VIGNETTE
# ═══════════════════════════════════════════════════════

def buat_vignette(canvas, w, h, bg_color, intensitas=0.55):
    """Efek gelap di tepi — gradasi bertahap ke arah pinggir"""
    layers = 10
    step = 0.7 / layers
    for i in range(layers):
        t = 1 - (i / layers)
        dark = lerp_color(bg_color, "#000000", 1.0 - t * t)
        # Top
        canvas.create_rectangle(0, i*3, w, i*3+3, fill=dark, outline="", tags="vignette")
        # Bottom
        canvas.create_rectangle(0, h - i*3 - 3, w, h - i*3, fill=dark, outline="", tags="vignette")
        # Left
        canvas.create_rectangle(i*3, 0, i*3+3, h, fill=dark, outline="", tags="vignette")
        # Right
        canvas.create_rectangle(w - i*3 - 3, 0, w - i*3, h, fill=dark, outline="", tags="vignette")


# ═══════════════════════════════════════════════════════
#  FUNGSI UTAMA — MEMBUAT WINDOW LIRIK
# ═══════════════════════════════════════════════════════

def buat_window(idx, fade_prev=None):
    if fade_prev is not None:
        root.after(JEDA_SEBELUM_FADE_PREV, fade_prev)

    if idx >= len(lyrics):
        return

    baris = lyrics[idx]
    durasi = durations[idx]
    is_judul = (idx == 0)

    # Pilih tema (cyclic)
    tema = THEMES[idx % len(THEMES)]
    bg_dark, bg_mid1, bg_mid2, accent = tema

    # Warna teks utama: putih hangat/ivory untuk elegan
    warna_teks  = "#F0EDE6"
    warna_teks_dim = lerp_color(accent, bg_dark, 0.4)
    is_special = (9 <= idx <= 14)
    overlay_red = None
 
    if is_judul:
        font_teks = ("Georgia", 22, "bold")
        char_delay = CHAR_DELAY_JUDUL
    else:
        font_teks = ("Georgia", 17)
        char_delay = max(8, int(durasi / max(1, len(baris))))

    # ── POSISI ──
    if is_judul:
        target_x = (screen_w - WIN_W) // 2
        target_y = (screen_h - WIN_H) // 2
        start_y = target_y
    else:
        margin = 40
        target_x = random.randint(margin, max(margin, screen_w - WIN_W - margin))
        target_y = random.randint(margin, max(margin, screen_h - WIN_H - margin))
        start_y = screen_h + 50  # mulai sedikit lebih rendah untuk efek dramatis

    # ── BUAT WINDOW ──
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.configure(bg=bg_dark)
    win.attributes("-alpha", 0.0)
    win.attributes("-topmost", True)
    win.lift()
    win.attributes("-transparentcolor", "")  # tidak pakai transparansi warna

    win.geometry(f"{WIN_W}x{WIN_H}+{target_x}+{start_y}")
    win.update_idletasks()
    win.deiconify()

    # ── CANVAS UTAMA ──
    canvas = tk.Canvas(win, width=WIN_W, height=WIN_H, highlightthickness=0)
    canvas.pack()

    # ─── GRADASI BACKGROUND ───
    buat_gradient(canvas, WIN_W, WIN_H, bg_dark, bg_mid1, bg_mid2, accent)

    # ─── ORNAMEN: lingkaran samar di background ───
    for _ in range(2):
        cx = random.randint(80, WIN_W - 80)
        cy = random.randint(80, WIN_H - 80)
        r = random.randint(70, 160)
        col = lerp_color(bg_mid2, accent, 0.12)
        canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline="", fill=col, stipple="gray25"
        )

    # ─── BORDER ELEGAN ───
    # Outer solid line
    canvas.create_rectangle(
        2, 2, WIN_W - 2, WIN_H - 2,
        outline=lerp_color(accent, bg_mid2, 0.3), width=1
    )
    # Inner dotted line
    canvas.create_rectangle(
        7, 7, WIN_W - 7, WIN_H - 7,
        outline=lerp_color(accent, bg_dark, 0.5), width=1, dash=(3, 5)
    )

    # ─── CORNER ORNAMENTS ELEGAN ───
    # Multi-layer corner: glow besar → glow kecil → diamond → inner diamond
    ukuran_sudut = 6
    for corner_idx, (cx, cy) in enumerate([(6, 6), (WIN_W-6, 6), (6, WIN_H-6), (WIN_W-6, WIN_H-6)]):
        # Layer 1: Deep outer glow
        canvas.create_oval(
            cx - 24, cy - 24, cx + 24, cy + 24,
            fill=accent, outline="", tags="corner_glow",
            stipple="gray12"
        )
        # Layer 2: Inner glow
        canvas.create_oval(
            cx - 15, cy - 15, cx + 15, cy + 15,
            fill=accent, outline="", tags="corner_glow",
            stipple="gray25"
        )
        # Layer 3: Outer diamond (accent)
        canvas.create_polygon(
            cx, cy - ukuran_sudut,
            cx + ukuran_sudut, cy,
            cx, cy + ukuran_sudut,
            cx - ukuran_sudut, cy,
            fill=accent, outline=""
        )
        # Layer 4: Inner diamond (putih hangat)
        inner = ukuran_sudut * 0.55
        canvas.create_polygon(
            cx, cy - inner,
            cx + inner, cy,
            cx, cy + inner,
            cx - inner, cy,
            fill=warna_teks, outline=""
        )

    # ─── CORNER RAYS — decorative lines radiating inward ───
    ray_col = lerp_color(accent, bg_mid2, 0.25)
    for (cx, cy), sx, sy in [
        ((6, 6), 1, 1), ((WIN_W-6, 6), -1, 1),
        ((6, WIN_H-6), 1, -1), ((WIN_W-6, WIN_H-6), -1, -1)
    ]:
        for i in range(1, 5):
            ex = cx + sx * i * 9
            ey = cy + sy * i * 9
            canvas.create_line(
                cx + sx * 4, cy + sy * 4, ex, ey,
                fill=ray_col, width=1, tags="filigree"
            )
        # Terminal dot at ray end
        tx = cx + sx * 4 * 9
        ty = cy + sy * 4 * 9
        canvas.create_oval(
            tx - 1.5, ty - 1.5, tx + 1.5, ty + 1.5,
            fill=ray_col, outline="", tags="filigree"
        )

    # ─── BORDER ACCENT DOTS ───
    dot_col = lerp_color(accent, bg_mid2, 0.35)
    for x in range(22, WIN_W - 22, 32):
        for y in (5, WIN_H - 5):
            if abs(x - 6) < 20 or abs(x - (WIN_W - 6)) < 20:
                continue
            canvas.create_oval(x-1.5, y-1.5, x+1.5, y+1.5, fill=dot_col, outline="")
    for y in range(22, WIN_H - 22, 32):
        for x in (5, WIN_W - 5):
            if abs(y - 6) < 20 or abs(y - (WIN_H - 6)) < 20:
                continue
            canvas.create_oval(x-1.5, y-1.5, x+1.5, y+1.5, fill=dot_col, outline="")

    # ─── SUBTLE TEXTURE OVERLAY (khusus special) ───
    if is_special:
        canvas.create_rectangle(
            0, 0, WIN_W, WIN_H,
            fill=lerp_color(accent, bg_dark, 0.75),
            stipple="gray12", outline="", tags="texture_bg"
        )

    # ─── PARTIKEL ───
    partikel_list = [StarParticle(WIN_W, WIN_H, accent) for _ in range(JUMLAH_PARTIKEL)]
    ember_list = []
    if is_special:
        ember_list = [EmberParticle(WIN_W, WIN_H, accent, bg_dark) for _ in range(12)]
    anim_start_time = [time.time()]

    win_aktif = [True]  # flag untuk cek apakah window masih ada

    def animasi_partikel():
        if not win_aktif[0]:
            return
        try:
            waktu = time.time() - anim_start_time[0]
            canvas.delete("partikel")
            canvas.delete("ember")
            for p in partikel_list:
                p.update(waktu)
                p.draw(canvas, waktu)
            for e in ember_list:
                e.update(waktu)
                e.draw(canvas, waktu)
            # Pulse corner glow
            pulse = 0.5 + 0.5 * math.sin(waktu * 0.8 + idx)
            for item in canvas.find_withtag("corner_glow"):
                coords = canvas.coords(item)
                if coords:
                    cx = (coords[0] + coords[2]) / 2
                    cy = (coords[1] + coords[3]) / 2
                    r = 14 + 8 * pulse
                    canvas.coords(item, cx-r, cy-r, cx+r, cy+r)
            canvas.tag_raise("teks")
            root.after(PARTIKEL_INTERVAL, animasi_partikel)
        except tk.TclError:
            pass  # window sudah tidak ada, skip

    animasi_partikel()

    # ─── TEKS DI ATAS CANVAS (TANPA BACKGROUND BOX!) ───
    # Teks di-render langsung di canvas dengan beberapa layer:
    # Layer 1: Glow luar (besar, samar)
    teks_glow = canvas.create_text(
        WIN_W // 2, WIN_H // 2,
        text="",
        font=font_teks,
        fill=lerp_color(accent, bg_dark, 0.6),
        width=WIN_W - 100,
        justify="center",
        tags="teks"
    )
    # Layer 2: Shadow (sedikit offset)
    teks_shadow = canvas.create_text(
        WIN_W // 2 + 1.5, WIN_H // 2 + 1.5,
        text="",
        font=font_teks,
        fill="#000000",
        width=WIN_W - 100,
        justify="center",
        tags="teks"
    )
    # Layer 3: Teks utama (paling atas, warna putih hangat)
    teks_main = canvas.create_text(
        WIN_W // 2, WIN_H // 2,
        text="",
        font=font_teks,
        fill=warna_teks,
        width=WIN_W - 100,
        justify="center",
        tags="teks"
    )

    # Pastikan urutan layer
    canvas.tag_lower(teks_glow)
    canvas.tag_lower(teks_shadow)
    canvas.tag_raise(teks_main)

    # Simpan ID untuk akses cepat
    teks_ids = (teks_main, teks_shadow, teks_glow)

    # ── ANIMASI SLIDE + FADE IN ──
    anim_mulai = [0.0]

    def slide_fade_in():
        now = time.perf_counter() * 1000
        if anim_mulai[0] == 0:
            anim_mulai[0] = now

        elapsed = now - anim_mulai[0]
        t = min(1.0, elapsed / SLIDE_DURATION)

        if is_judul:
            eased = 1.0
            win.attributes("-alpha", min(1.0, t * 1.5))
        else:
            eased = ease_out_quart(t)
            y = start_y + (target_y - start_y) * eased
            win.geometry(f"{WIN_W}x{WIN_H}+{target_x}+{int(y)}")
            win.attributes("-alpha", min(1.0, eased * 1.3))

        if t < 1.0 and not is_judul:
            root.after(16, slide_fade_in)
        else:
            if not is_judul:
                win.geometry(f"{WIN_W}x{WIN_H}+{target_x}+{target_y}")
            win.attributes("-alpha", 1.0)

    slide_fade_in()

    # ── ANIMASI KETIK + CURSOR BERKEDIP ──
    teks_bersih = [""]          # teks lirik tanpa cursor
    cursor_tampak = [True]
    cursor_after_id = [None]
    typing_done = [False]

    def update_cursor():
        if not win_aktif[0]:
            return
        cursor_tampak[0] = not cursor_tampak[0]
        dasar = teks_bersih[0]
        if dasar:
            if cursor_tampak[0]:
                simbol = "  |" if typing_done[0] else "  _"
            else:
                simbol = ""
            tampil = dasar + simbol
            try:
                canvas.itemconfig(teks_main, text=tampil)
                canvas.itemconfig(teks_shadow, text=tampil)
                canvas.itemconfig(teks_glow, text=tampil)
            except tk.TclError:
                return
        cursor_after_id[0] = root.after(CURSOR_BLINK_INTERVAL, update_cursor)

    update_cursor()

    def berhenti_cursor():
        if cursor_after_id[0] is not None:
            try:
                root.after_cancel(cursor_after_id[0])
            except tk.TclError:
                pass
            cursor_after_id[0] = None
        # Teks bersih tanpa cursor
        try:
            canvas.itemconfig(teks_main, text=teks_bersih[0])
            canvas.itemconfig(teks_shadow, text=teks_bersih[0])
            canvas.itemconfig(teks_glow, text=teks_bersih[0])
        except tk.TclError:
            pass

    # ── BREATHING GLOW (detak halus pada teks) ──
    breathing_active = [False]

    def breathing_anim():
        if not breathing_active[0] or not win_aktif[0]:
            return
        try:
            waktu = time.time()
            # Pulse lembut pada glow
            pulse = 0.5 + 0.3 * math.sin(waktu * 1.2)
            glow_col = lerp_color(accent, bg_dark, 1.0 - pulse * 0.5)
            canvas.itemconfig(teks_glow, fill=glow_col)
            # Teks utama juga sedikit berdenyut (perubahan warna subtle)
            warm = 0.97 + 0.03 * math.sin(waktu * 1.5 + 1.0)
            r, g, b = 240, 237, 230
            canvas.itemconfig(teks_main, fill=rgb_to_hex(
                r * warm, g * warm, b * (0.98 + 0.02 * math.sin(waktu * 1.3))
            ))
            root.after(50, breathing_anim)
        except tk.TclError:
            pass

    # ── SPECIAL EFFECTS for emotional climax (indices 9-14) ──
    glitch_overlay = None
    glitch_canvas_full = None

    if is_special:
        if not _shared_glitch["active"]:
            _shared_glitch["active"] = True

            # Red transparent overlay fullscreen
            overlay_red = tk.Toplevel(root)
            overlay_red.overrideredirect(True)
            overlay_red.configure(bg="#2a0000")
            overlay_red.attributes("-alpha", 0.0)
            overlay_red.attributes("-topmost", True)
            overlay_red.geometry(f"{screen_w}x{screen_h}+0+0")
            _shared_glitch["red"] = overlay_red

            # Full-screen glitch overlay
            glitch_overlay = tk.Toplevel(root)
            glitch_overlay.overrideredirect(True)
            glitch_overlay.configure(bg="black")
            glitch_overlay.attributes("-alpha", 0.0)
            glitch_overlay.attributes("-topmost", True)
            glitch_overlay.geometry(f"{screen_w}x{screen_h}+0+0")
            glitch_canvas_full = tk.Canvas(glitch_overlay, width=screen_w, height=screen_h,
                                            highlightthickness=0, bg="black")
            glitch_canvas_full.pack()
            _shared_glitch["overlay"] = glitch_overlay
            _shared_glitch["canvas"] = glitch_canvas_full

            # Subtle persistent haze overlay
            glitch_haze = tk.Toplevel(root)
            glitch_haze.overrideredirect(True)
            glitch_haze.configure(bg="black")
            glitch_haze.attributes("-alpha", 0.0)
            glitch_haze.attributes("-topmost", True)
            glitch_haze.geometry(f"{screen_w}x{screen_h}+0+0")
            haze_canvas = tk.Canvas(glitch_haze, width=screen_w, height=screen_h,
                                    highlightthickness=0, bg="black")
            haze_canvas.pack()
            _shared_glitch["haze"] = glitch_haze
            _shared_glitch["haze_canvas"] = haze_canvas

            # Position below this window
            glitch_overlay.lower(win)
            overlay_red.lower(win)
            glitch_haze.lower(win)

            # ── SHARED HAZE LOOP — lebih ringan ──
            def haze_loop():
                if not _shared_glitch["active"]:
                    return
                try:
                    hc = _shared_glitch["haze_canvas"]
                    ho = _shared_glitch["haze"]
                    if hc is None or ho is None:
                        return
                    hc.delete("all")
                    for _ in range(random.randint(15, 40)):
                        hx = random.randint(0, screen_w)
                        hy = random.randint(0, screen_h)
                        hs = random.randint(1, 2)
                        col = random.choice(["#ffffff", "#ff0000", "#0044ff"])
                        hc.create_rectangle(hx, hy, hx + hs, hy + hs, fill=col, outline="")
                    for _ in range(random.randint(2, 5)):
                        sy = random.randint(0, screen_h)
                        hc.create_line(0, sy, screen_w, sy,
                            fill=random.choice(["#ffffff", "#ff0000"]), width=1)
                    ho.attributes("-alpha", random.uniform(0.012, 0.03))
                    root.after(random.randint(400, 900), haze_loop)
                except tk.TclError:
                    pass
            haze_loop()
        else:
            # Reuse shared overlays
            overlay_red = _shared_glitch["red"]
            glitch_overlay = _shared_glitch["overlay"]
            glitch_canvas_full = _shared_glitch["canvas"]
            glitch_haze = _shared_glitch["haze"]
            haze_canvas = _shared_glitch["haze_canvas"]
            # Position below this window too
            glitch_overlay.lower(win)
            overlay_red.lower(win)
            glitch_haze.lower(win)

    def fade_red_start():
        if not is_special or overlay_red is None:
            return
        alpha_val = [0.0]
        def _fade():
            if not win_aktif[0]:
                return
            alpha_val[0] = min(0.3, alpha_val[0] + 0.005)
            try:
                overlay_red.attributes("-alpha", alpha_val[0])
            except tk.TclError:
                return
            if alpha_val[0] < 0.3:
                root.after(30, _fade)
        _fade()
    
    def glitch_loop():
        if not is_special or not win_aktif[0]:
            return
        try:
            if random.random() < 0.25:
                choice = random.randint(0, 3)
                if choice == 0:
                    # Text position offset
                    ox, oy = random.randint(-5,5), random.randint(-3,3)
                    canvas.coords(teks_main, WIN_W//2+ox, WIN_H//2+oy)
                    canvas.coords(teks_shadow, WIN_W//2+ox+1.5, WIN_H//2+oy+1.5)
                    canvas.coords(teks_glow, WIN_W//2+ox, WIN_H//2+oy)
                    root.after(60, lambda: (
                        canvas.coords(teks_main, WIN_W//2, WIN_H//2),
                        canvas.coords(teks_shadow, WIN_W//2+1.5, WIN_H//2+1.5),
                        canvas.coords(teks_glow, WIN_W//2, WIN_H//2),
                    ))
                elif choice == 1:
                    # Screen tear strips
                    for _ in range(random.randint(1,3)):
                        yy = random.randint(30, WIN_H-30)
                        hh = random.randint(2, 6)
                        tear_col = random.choice([
                            rgb_to_hex(180,0,0),
                            rgb_to_hex(120,0,0),
                            lerp_color(bg_dark, "#ff0000", 0.2)
                        ])
                        canvas.create_rectangle(0, yy, WIN_W, yy+hh,
                            fill=tear_col, outline="", tags="glitch", stipple="gray25")
                    root.after(80, lambda: canvas.delete("glitch"))
                elif choice == 2:
                    # RGB color channel split
                    off = random.randint(3, 6)
                    txt = teks_bersih[0]
                    if txt:
                        canvas.create_text(WIN_W//2+off, WIN_H//2, text=txt,
                            font=font_teks, fill="#ff0000", width=WIN_W-100,
                            justify="center", tags="glitch_r")
                        canvas.create_text(WIN_W//2-off, WIN_H//2, text=txt,
                            font=font_teks, fill="#00ffff", width=WIN_W-100,
                            justify="center", tags="glitch_b")
                        root.after(70, lambda: (canvas.delete("glitch_r"), canvas.delete("glitch_b")))
                elif choice == 3:
                    # Character corruption
                    if typing_done[0] and teks_bersih[0]:
                        txt = list(teks_bersih[0])
                        n = random.randint(1, min(3, len(txt)))
                        for _ in range(n):
                            ci = random.randint(0, len(txt)-1)
                            txt[ci] = random.choice("@#$%&+={}[]|\\/<>")
                        corr = "".join(txt)
                        canvas.itemconfig(teks_main, text=corr)
                        canvas.itemconfig(teks_shadow, text=corr)
                        canvas.itemconfig(teks_glow, text=corr)
                        root.after(50, lambda: (
                            canvas.itemconfig(teks_main, text=teks_bersih[0]),
                            canvas.itemconfig(teks_shadow, text=teks_bersih[0]),
                            canvas.itemconfig(teks_glow, text=teks_bersih[0]),
                        ))
            # Additional tear strip on text area
            if is_special and typing_done[0] and random.random() < 0.08:
                y_tear = random.randint(WIN_H//2 - 30, WIN_H//2 + 30)
                h_tear = random.randint(3, 8)
                canvas.create_rectangle(40, y_tear, WIN_W-40, y_tear+h_tear,
                    fill=bg_mid1, outline="", tags="glitch_tear")
                root.after(60, lambda: canvas.delete("glitch_tear"))
        except tk.TclError:
            pass
        root.after(random.randint(150, 400), glitch_loop)
    
    # ── FULL-SCREEN GLITCH LOOP (dramatis & intens) ──
    def glitch_fade_in(target_alpha, hold_dur, fade_steps=7, fade_interval=25):
        """Fade in glitch alpha secara perlahan dari 0 ke target_alpha,
           lalu hold selama hold_dur, lalu reset ke 0."""
        def _step(s=0):
            try:
                a = target_alpha * (s + 1) / fade_steps
                glitch_overlay.attributes("-alpha", a)
            except tk.TclError:
                return
            if s + 1 < fade_steps:
                root.after(fade_interval, _step, s + 1)
            else:
                root.after(hold_dur, lambda: glitch_overlay.attributes("-alpha", 0.0))
        _step(0)

    def screen_glitch_loop():
        if not is_special or not win_aktif[0] or glitch_overlay is None:
            return
        try:
            glitch_canvas_full.delete("all")

            # Intensitas meningkat berdasarkan idx (10=ringan, 14=brutal)
            intensitas = (idx - 8) / 6  # 0.33 → 1.0
            efek = random.randint(0, 9)
            flash_dur = random.randint(30, 100) + int(20 * intensitas)

            if efek == 0:
                # INTENSE full-screen color flash
                flash_color = random.choice([
                    "#ff0000", "#ff2200", "#cc0022",
                    "#4400ff", "#8800ff", "#ff00aa"
                ])
                glitch_canvas_full.create_rectangle(
                    0, 0, screen_w, screen_h,
                    fill=flash_color, outline=""
                )
                # Double flash with offset
                if random.random() < 0.3 + 0.2 * intensitas:
                    glitch_canvas_full.create_rectangle(
                        random.randint(-80, 80), random.randint(-80, 80),
                        screen_w + random.randint(-80, 80), screen_h + random.randint(-80, 80),
                        fill=random.choice(["#ffffff", "#000000"]),
                        stipple="gray25", outline=""
                    )
                # Kadang2 efek burn-in (kotak putih menyala)
                if intensitas > 0.6 and random.random() < 0.25:
                    for _ in range(random.randint(2, 5)):
                        bx = random.randint(0, screen_w)
                        by = random.randint(0, screen_h)
                        bw = random.randint(30, 150)
                        bh = random.randint(30, 150)
                        glitch_canvas_full.create_rectangle(
                            bx, by, bx+bw, by+bh,
                            fill="#ffffff", stipple="gray50", outline=""
                        )
                glitch_fade_in(random.uniform(0.2, 0.35 + 0.25 * intensitas), flash_dur)

            elif efek == 1:
                # MASSIVE screen tearing — puluhan strip across entire screen
                n_strips = random.randint(20, 30 + int(20 * intensitas))
                for _ in range(n_strips):
                    yy = random.randint(0, screen_h)
                    hh = random.randint(2, 8 + int(6 * intensitas))
                    col = random.choice([
                        "#ffffff", "#000000", "#ff0000", "#0044ff",
                        "#ff0044", "#00ff44", "#ff4400", "#4400ff"
                    ])
                    glitch_canvas_full.create_rectangle(
                        0, yy, screen_w, yy + hh,
                        fill=col, outline=""
                    )
                    # Kadang strip dengan shadow offset
                    if random.random() < 0.3:
                        off = random.randint(3, 10)
                        glitch_canvas_full.create_rectangle(
                            off, yy+1, screen_w+off, yy+hh-1,
                            fill=random.choice(["#000000", "#ffffff"]),
                            stipple="gray50", outline=""
                        )
                glitch_fade_in(random.uniform(0.2, 0.35 + 0.15 * intensitas),
                              flash_dur + random.randint(20, 40))

            elif efek == 2:
                # HORIZONTAL DISPLACEMENT — seolah layar bergeser
                chunks = random.randint(6, 10 + int(6 * intensitas))
                for _ in range(chunks):
                    yy = random.randint(0, screen_h)
                    hh = random.randint(20, 50 + int(30 * intensitas))
                    col = random.choice(["#ffffff", "#000000", "#ff0000", "#0044ff"])
                    glitch_canvas_full.create_rectangle(
                        0, yy, screen_w, yy + hh,
                        fill=col, outline=""
                    )
                    # offset shadow
                    offset = random.randint(5, 15 + int(15 * intensitas))
                    shadow_col = random.choice(["#000000", "#ff0000", "#0044ff"])
                    glitch_canvas_full.create_rectangle(
                        offset, yy + 2, screen_w + offset, yy + hh - 2,
                        fill=shadow_col, stipple="gray25", outline=""
                    )
                    # Kadang RGB split di displacement
                    if intensitas > 0.5 and random.random() < 0.3:
                        glitch_canvas_full.create_rectangle(
                            offset + 3, yy + 4, screen_w // 2, yy + hh - 4,
                            fill="#ff0000", stipple="gray50", outline=""
                        )
                        glitch_canvas_full.create_rectangle(
                            screen_w // 2, yy + 4, screen_w + offset - 3, yy + hh - 4,
                            fill="#0044ff", stipple="gray50", outline=""
                        )
                glitch_fade_in(random.uniform(0.25, 0.4 + 0.15 * intensitas),
                              flash_dur + random.randint(30, 60))

            elif efek == 3:
                # RGB CHANNEL SPLIT — aberasi kromatik screen-level
                n_bands = random.randint(4, 7 + int(5 * intensitas))
                for _ in range(n_bands):
                    yy = random.randint(0, screen_h)
                    hh = random.randint(40, screen_h // 3)
                    off_amt = random.randint(5, 10 + int(10 * intensitas))
                    # Red block
                    glitch_canvas_full.create_rectangle(
                        off_amt, yy, screen_w + off_amt, yy + hh,
                        fill="#ff0000", stipple="gray25", outline=""
                    )
                    # Blue block
                    glitch_canvas_full.create_rectangle(
                        -off_amt, yy, screen_w - off_amt, yy + hh,
                        fill="#0044ff", stipple="gray25", outline=""
                    )
                    # Kadang green channel jg
                    if random.random() < 0.3:
                        glitch_canvas_full.create_rectangle(
                            0, yy + 2, screen_w, yy + hh - 2,
                            fill="#00ff44", stipple="gray50", outline=""
                        )
                glitch_fade_in(random.uniform(0.2, 0.3 + 0.15 * intensitas),
                              flash_dur + random.randint(40, 80))

            elif efek == 4:
                # STATIC NOISE BURST — random blocks di seluruh layar
                n_blocks = random.randint(60, 100 + int(80 * intensitas))
                for _ in range(n_blocks):
                    bx = random.randint(0, screen_w)
                    by = random.randint(0, screen_h)
                    bw = random.randint(3, 30 + int(30 * intensitas))
                    bh = random.randint(2, 6 + int(4 * intensitas))
                    col = random.choice([
                        "#ffffff", "#000000", "#ff0000", "#0044ff",
                        "#ff00ff", "#00ff44", "#ffff00", "#ff4400"
                    ])
                    glitch_canvas_full.create_rectangle(
                        bx, by, bx + bw, by + bh, fill=col, outline=""
                    )
                glitch_fade_in(random.uniform(0.12, 0.2 + 0.15 * intensitas), flash_dur)

            elif efek == 5:
                # SCANLINE + FLICKER OVERLAY — efek VHS
                step = random.randint(2, 4)
                for y in range(0, screen_h, step):
                    col = random.choice(["#ffffff", "#ff0000", "#0044ff", "#000000"])
                    glitch_canvas_full.create_line(0, y, screen_w, y, fill=col, width=1)
                # Flash putih kadang2
                if random.random() < 0.3 + 0.2 * intensitas:
                    glitch_canvas_full.create_rectangle(
                        0, 0, screen_w, screen_h,
                        fill="#ffffff", stipple="gray12", outline=""
                    )
                # Wave distortion lines
                if random.random() < 0.4:
                    for _ in range(random.randint(3, 6)):
                        wy = random.randint(0, screen_h)
                        ampl = random.randint(5, 15)
                        glitch_canvas_full.create_line(
                            0, wy, screen_w, wy + random.randint(-ampl, ampl),
                            fill=random.choice(["#ff0000", "#ffffff", "#0044ff"]),
                            width=random.randint(1, 2)
                        )
                glitch_fade_in(random.uniform(0.15, 0.25 + 0.15 * intensitas),
                              flash_dur + random.randint(20, 50))

            elif efek == 6:
                # VERTICAL SPLIT + GLITCH BAR
                tear_x = random.randint(50, screen_w - 50)
                # Big vertical tear
                glitch_canvas_full.create_rectangle(
                    tear_x - 3, 0, tear_x + 3, screen_h,
                    fill="#ffffff", outline=""
                )
                # Radiating cracks from tear
                for _ in range(random.randint(3, 6)):
                    start_y = random.randint(0, screen_h)
                    end_x = tear_x + random.randint(-80, 80)
                    end_y = random.randint(0, screen_h)
                    glitch_canvas_full.create_line(
                        tear_x, start_y, end_x, end_y,
                        fill=random.choice(["#ffffff", "#ff0000"]), width=1
                    )
                # Displaced horizontal chunks
                for _ in range(random.randint(8, 12 + int(8 * intensitas))):
                    yy = random.randint(0, screen_h)
                    hh = random.randint(3, 8 + int(4 * intensitas))
                    col = random.choice(["#ff0000", "#0044ff", "#ffffff", "#000000"])
                    glitch_canvas_full.create_rectangle(
                        random.randint(-40, 40), yy,
                        screen_w + random.randint(-40, 40), yy + hh,
                        fill=col, outline=""
                    )
                glitch_fade_in(random.uniform(0.18, 0.3 + 0.15 * intensitas),
                              flash_dur + random.randint(30, 60))

            elif efek == 7:
                # HEARTQUAKE — concentric shockwave rings
                cx = random.randint(100, screen_w - 100)
                cy = random.randint(100, screen_h - 100)
                max_r = max(screen_w, screen_h)
                n_rings = random.randint(3, 6 + int(4 * intensitas))
                for i in range(n_rings):
                    r = max_r * (i + 1) / n_rings
                    glitch_canvas_full.create_oval(
                        cx - r, cy - r, cx + r, cy + r,
                        outline=random.choice([
                            "#ff0000", "#ffffff", "#0044ff",
                            "#ff00aa", "#4400ff"
                        ]),
                        width=random.randint(1, 3),
                        stipple="gray50" if i % 2 == 0 else ""
                    )
                # Fill flash inside rings
                if random.random() < 0.5:
                    glitch_canvas_full.create_oval(
                        cx - max_r * 0.3, cy - max_r * 0.3,
                        cx + max_r * 0.3, cy + max_r * 0.3,
                        fill=random.choice(["#ffffff", "#ff0000"]),
                        stipple="gray25", outline=""
                    )
                # Extra jagged lines
                for _ in range(random.randint(4, 10)):
                    ax = cx + random.randint(-max_r, max_r)
                    ay = cy + random.randint(-max_r, max_r)
                    glitch_canvas_full.create_line(
                        cx, cy, ax, ay,
                        fill=random.choice(["#ff0000", "#ffffff", "#0044ff"]),
                        width=random.randint(1, 2)
                    )
                glitch_fade_in(random.uniform(0.15, 0.3 + 0.15 * intensitas),
                              flash_dur + random.randint(40, 80))

            elif efek == 8:
                # DRIP DISTORTION — vertical dripping glitch
                n_drips = random.randint(8, 15 + int(10 * intensitas))
                for _ in range(n_drips):
                    dx = random.randint(0, screen_w)
                    dy = random.randint(0, screen_h)
                    length = random.randint(20, 80 + int(60 * intensitas))
                    wide = random.randint(2, 6 + int(4 * intensitas))
                    col = random.choice([
                        "#ff0000", "#0044ff", "#ffffff", "#ff0044",
                        "#4400ff", "#00ff44"
                    ])
                    glitch_canvas_full.create_rectangle(
                        dx, dy, dx + wide, dy + length,
                        fill=col, outline=""
                    )
                    # Shadow drip
                    if random.random() < 0.4:
                        glitch_canvas_full.create_rectangle(
                            dx - wide - 2, dy + 2, dx - 2, dy + length - 2,
                            fill="#000000", stipple="gray50", outline=""
                        )
                # Horizontal "smear" lines
                for _ in range(random.randint(3, 8)):
                    sy = random.randint(0, screen_h)
                    smear_len = random.randint(20, 200)
                    sx = random.randint(0, screen_w - smear_len)
                    glitch_canvas_full.create_rectangle(
                        sx, sy, sx + smear_len, sy + random.randint(2, 5),
                        fill=random.choice(["#ff0000", "#ffffff"]),
                        stipple="gray25", outline=""
                    )
                glitch_fade_in(random.uniform(0.15, 0.3 + 0.15 * intensitas),
                              flash_dur + random.randint(40, 70))

            elif efek == 9:
                # SHATTER — random polygon shards
                n_shards = random.randint(8, 14 + int(8 * intensitas))
                for _ in range(n_shards):
                    # Random triangle/polygon
                    cx = random.randint(0, screen_w)
                    cy = random.randint(0, screen_h)
                    pts = []
                    n_pts = random.choice([3, 4])
                    for _ in range(n_pts):
                        pts.append(cx + random.randint(-60, 60))
                        pts.append(cy + random.randint(-60, 60))
                    col = random.choice([
                        "#ff0000", "#0044ff", "#ffffff", "#4400ff",
                        "#ff0044", "#ff4400", "#000000"
                    ])
                    glitch_canvas_full.create_polygon(
                        pts, fill=col, outline=""
                    )
                    # Outline fragment
                    if random.random() < 0.4:
                        glitch_canvas_full.create_polygon(
                            pts, fill="", outline="#ffffff",
                            width=1, stipple="gray50"
                        )
                # Connecting crack lines
                for _ in range(random.randint(3, 6)):
                    x1 = random.randint(0, screen_w)
                    y1 = random.randint(0, screen_h)
                    x2 = x1 + random.randint(-150, 150)
                    y2 = y1 + random.randint(-150, 150)
                    glitch_canvas_full.create_line(
                        x1, y1, x2, y2,
                        fill=random.choice(["#ffffff", "#ff0000"]),
                        width=random.randint(1, 2)
                    )
                glitch_fade_in(random.uniform(0.15, 0.25 + 0.15 * intensitas),
                              flash_dur + random.randint(50, 90))

            # Schedule next — semakin cepat mendekati akhir
            delay = random.randint(40, 120) - int(30 * intensitas)
            delay = max(20, delay)
            root.after(delay, screen_glitch_loop)

        except tk.TclError:
            pass

    # ── CRACKS ELEGAN — retak halus di border window ──
    def elegant_cracks(iterasi, max_iter):
        """Gambar retak kaca elegan dari tepi window — dipanggil tiap iterasi shake"""
        if iterasi < 6 or iterasi % 2 != 0:
            return
        try:
            progress = iterasi / max_iter  # 0→1
            crack_col = lerp_color(accent, bg_dark, 0.6 + 0.3 * (1 - progress))

            edge = random.randint(0, 3)
            if edge == 0:
                sx, sy = random.randint(25, WIN_W - 25), 5
            elif edge == 1:
                sx, sy = WIN_W - 5, random.randint(25, WIN_H - 25)
            elif edge == 2:
                sx, sy = random.randint(25, WIN_W - 25), WIN_H - 5
            else:
                sx, sy = 5, random.randint(25, WIN_H - 25)

            x, y = sx, sy
            for _ in range(random.randint(2, 4)):
                # Bergerak natural ke arah dalam dengan sedikit acak
                dx = (WIN_W / 2 - x) * random.uniform(0.08, 0.22) + random.randint(-10, 10)
                dy = (WIN_H / 2 - y) * random.uniform(0.08, 0.22) + random.randint(-10, 10)
                nx = max(6, min(WIN_W - 6, int(x + dx)))
                ny = max(6, min(WIN_H - 6, int(y + dy)))

                # Glow subtle di belakang retak
                canvas.create_line(x + 1, y + 1, nx + 1, ny + 1,
                    fill=lerp_color(accent, bg_dark, 0.75), width=3,
                    tags="crack", stipple="gray25")
                # Garis retak utama
                canvas.create_line(x, y, nx, ny,
                    fill=crack_col, width=1, tags="crack")

                # Cabang halus (30%)
                if random.random() < 0.3:
                    bx = x + random.randint(-12, 12)
                    by = y + random.randint(-12, 12)
                    bx = max(6, min(WIN_W - 6, bx))
                    by = max(6, min(WIN_H - 6, by))
                    canvas.create_line(x, y, bx, by,
                        fill=crack_col, width=1, tags="crack")
                x, y = nx, ny
        except tk.TclError:
            pass

    # ── CONTINUOUS SHAKE — goyang halus dari awal sampai idx 14 ──
    _crack_timer = [0.0]  # mutable container untuk tracking waktu crack

    def _draw_crack():
        """Gambar 1 retak baru di border window (dipanggil periodik)"""
        try:
            waktu = time.time() - anim_start_time[0]
            progress = min(1.0, waktu / 25)
            crack_col = lerp_color(accent, bg_dark, 0.6 + 0.3 * (1 - progress))
            edge = random.randint(0, 3)
            if edge == 0:
                sx, sy = random.randint(25, WIN_W - 25), 5
            elif edge == 1:
                sx, sy = WIN_W - 5, random.randint(25, WIN_H - 25)
            elif edge == 2:
                sx, sy = random.randint(25, WIN_W - 25), WIN_H - 5
            else:
                sx, sy = 5, random.randint(25, WIN_H - 25)
            x, y = sx, sy
            for _ in range(random.randint(2, 4)):
                dx = (WIN_W / 2 - x) * random.uniform(0.08, 0.22) + random.randint(-10, 10)
                dy = (WIN_H / 2 - y) * random.uniform(0.08, 0.22) + random.randint(-10, 10)
                nx = max(6, min(WIN_W - 6, int(x + dx)))
                ny = max(6, min(WIN_H - 6, int(y + dy)))
                canvas.create_line(x + 1, y + 1, nx + 1, ny + 1,
                    fill=lerp_color(accent, bg_dark, 0.75), width=3,
                    tags="crack", stipple="gray25")
                canvas.create_line(x, y, nx, ny, fill=crack_col, width=1, tags="crack")
                if random.random() < 0.3:
                    bx = x + random.randint(-12, 12)
                    by = y + random.randint(-12, 12)
                    bx = max(6, min(WIN_W - 6, bx))
                    by = max(6, min(WIN_H - 6, by))
                    canvas.create_line(x, y, bx, by, fill=crack_col, width=1, tags="crack")
                x, y = nx, ny
        except tk.TclError:
            pass

    def continuous_shake():
        """Gentle continuous oscillation — smooth, nggak alay"""
        if not win_aktif[0]:
            return
        try:
            waktu = time.time() - anim_start_time[0]
            base_intensity = 2.5 + max(0, (idx - 8)) * 1.3
            breath = 0.7 + 0.3 * math.sin(waktu * 0.45)
            intensity = base_intensity * breath
            ox = int(math.sin(waktu * 4.5 + idx * 0.7) * intensity)
            oy = int(math.sin(waktu * 2.9 + idx * 1.1) * intensity * 0.5)
            win.geometry(f"{WIN_W}x{WIN_H}+{target_x+ox}+{target_y+oy}")
            # Cracks periodik
            if waktu - _crack_timer[0] > random.uniform(0.8, 1.8):
                _crack_timer[0] = waktu
                _draw_crack()
            root.after(16, continuous_shake)
        except tk.TclError:
            pass

    # ── SHAKE OUT (shake + destroy + cleanup) ──
    def shake_out(iterasi=0):
        breathing_active[0] = False
        max_iter = 50
        if iterasi < max_iter:
            ox = random.randint(-18, 18)
            oy = random.randint(-18, 18)
            try:
                win.geometry(f"{WIN_W}x{WIN_H}+{target_x+ox}+{target_y+oy}")
            except tk.TclError:
                pass
            elegant_cracks(iterasi, max_iter)
            root.after(20, shake_out, iterasi + 1)
        else:
            try:
                win.geometry(f"{WIN_W}x{WIN_H}+{target_x}+{target_y}")
            except tk.TclError:
                pass
            berhenti_cursor()
            win_aktif[0] = False
            if overlay_red is not None:
                try:
                    overlay_red.destroy()
                except tk.TclError:
                    pass
            if glitch_overlay is not None:
                try:
                    glitch_overlay.destroy()
                except tk.TclError:
                    pass
            try:
                glitch_haze.destroy()
            except (tk.TclError, NameError, AttributeError):
                pass
            # Reset shared glitch state
            _shared_glitch["active"] = False
            _shared_glitch["loops_started"] = False
            _shared_glitch["red"] = None
            _shared_glitch["overlay"] = None
            _shared_glitch["canvas"] = None
            _shared_glitch["haze"] = None
            _shared_glitch["haze_canvas"] = None
            try:
                win.destroy()
            except tk.TclError:
                pass
            if idx == len(lyrics) - 1:
                try:
                    root.destroy()
                except tk.TclError:
                    pass

    # ── KETIK ──
    def ketik(karakter_idx=0, teks_sekarang=""):
        if karakter_idx < len(baris):
            teks_sekarang += baris[karakter_idx]
            teks_bersih[0] = teks_sekarang
            # Update semua layer teks
            canvas.itemconfig(teks_main, text=teks_sekarang)
            canvas.itemconfig(teks_shadow, text=teks_sekarang)
            canvas.itemconfig(teks_glow, text=teks_sekarang)

            root.after(char_delay, ketik, karakter_idx + 1, teks_sekarang)
        else:
            typing_done[0] = True
            breathing_active[0] = True
            breathing_anim()

            if is_judul:
                root.after(JEDA_SETELAH_JUDUL, lambda: [
                    berhenti_cursor(),
                    buat_window(idx + 1, fade_out)
                ])
            else:
                # Special section (9-14)
                if is_special and idx < len(lyrics) - 1:
                    # idx 9-13: continuous shake dari sekarang sampai akhir
                    continuous_shake()
                    effect_out = None          # jangan destroy
                elif is_special and idx == len(lyrics) - 1:
                    effect_out = shake_out     # idx 14: shake + cleanup
                else:
                    effect_out = fade_out
                root.after(400, lambda: [
                    berhenti_cursor(),
                    buat_window(idx + 1, effect_out)
                ])

    # ── FADE OUT ──
    def fade_out(alpha=1.0):
        breathing_active[0] = False
        step = 1.0 / (FADE_DURATION / 30)
        alpha_baru = alpha - step
        if alpha_baru > 0:
            try:
                win.attributes("-alpha", alpha_baru)
                root.after(30, fade_out, alpha_baru)
            except tk.TclError:
                pass
        else:
            berhenti_cursor()
            win_aktif[0] = False
            try:
                win.destroy()
            except tk.TclError:
                pass
            if idx == len(lyrics) - 1:
                root.destroy()

    if is_special:
        glitch_loop()  # per-window text glitch, selalu jalan
        if not _shared_glitch.get("loops_started"):
            _shared_glitch["loops_started"] = True
            fade_red_start()
            screen_glitch_loop()
    ketik()

buat_window(0)
root.mainloop()
