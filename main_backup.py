import tkinter as tk
import random

# Lirik + durasi tiap baris (ms), diambil dari timestamp LRC lagu aslinya
# (Laufey - Too Little, Too Late) -- bagian Chorus 2 + Bridge
# durasi = jarak waktu dari baris ini mulai sampai baris berikutnya mulai di lagu
lyrics_data = [
    ("Too little, too late - Laufey",             0),  # judul, ditangani khusus
    ("To hear you scream my name",              5280),  # 02:03.76 -> 02:09.04
    ("A clear fucking X-ray",                    4520),  # 02:09.04 -> 02:13.56
    ("Of if I'd stuck around",                   4500),  # 02:13.56 -> 02:18.06
    ("I swear to God, I almost drowned",         4510),  # 02:18.06 -> 02:22.57
    ("You asked me how I've been",               4400),  # 02:22.57 -> 02:26.97
    ("But how could I begin",                    4500),  # 02:26.97 -> 02:31.47
    ("To tell you I should've chased you?",      4990),  # 02:31.47 -> 02:36.46
    ("I should be who you're engaged to",        4390),  # 02:36.46 -> 02:40.85
    ("Lost my fight with fate",                  4140),  # 02:40.85 -> 02:44.99
    ("A tug-of-war of leave and stay",           4430),  # 02:44.99 -> 02:49.42
    ("I give in, I abdicate",                    4250),  # 02:49.42 -> 02:53.67
    ("I lay my sword down anyway",               4100),  # 02:53.67 -> 02:57.77
    ("I'll see you at Heaven's gate",             4250),  # 02:57.77 -> 03:02.02
    ("'Cause it's too little, way too late",     7940),  # 03:02.02 -> 03:09.96
]

lyrics = [item[0] for item in lyrics_data]
durations = [item[1] for item in lyrics_data]   # ms, jeda antar baris sesuai lagu asli

WIN_W, WIN_H = 500, 500

slide_step = 15          # kecepatan geser naik (px per langkah)
slide_interval = 10      # interval animasi slide (ms)
fade_step = 0.02         # pengurangan opacity tiap langkah fade (lebih kecil = fade lebih lama)
fade_interval = 40       # interval animasi fade (ms)

# fade khusus judul, dibuat lebih cepat dari lirik biasa
fade_step_judul = 0.1
fade_interval_judul = 20

# begitu window BERIKUTNYA muncul, window SEBELUMNYA baru mulai fade out
# setelah nunggu sekian ms ini.
jeda_sebelum_fade_prev = 1000   # ms

char_delay_judul = 60      # kecepatan ngetik khusus baris judul (ms per karakter)
jeda_setelah_judul = 3000  # ms, jeda setelah judul selesai diketik sebelum lirik mulai

root = tk.Tk()
root.withdraw()  # root utama disembunyikan, cuma jadi induk semua window

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()


def posisi_acak():
    # pastikan window tetap sepenuhnya kelihatan di dalam layar
    x = random.randint(0, max(0, screen_w - WIN_W))
    y = random.randint(0, max(0, screen_h - WIN_H))
    return x, y


def buat_window(idx, fade_prev=None):
    # fade_prev: fungsi fade_out milik window SEBELUMNYA (kalau ada).
    # Begitu window baru ini muncul, kita jadwalkan window sebelumnya
    # untuk mulai fade out setelah jeda_sebelum_fade_prev.
    if fade_prev is not None:
        root.after(jeda_sebelum_fade_prev, fade_prev)

    if idx >= len(lyrics):
        return

    baris = lyrics[idx]
    durasi = durations[idx]
    is_judul = (idx == 0)

    # char_delay dihitung supaya ngetik baris ini selesai
    # sesuai jeda asli antar baris di lagu (judul pakai kecepatan sendiri)
    if is_judul:
        char_delay = char_delay_judul
        this_fade_step = fade_step_judul
        this_fade_interval = fade_interval_judul
    else:
        char_delay = max(10, int(durasi / max(1, len(baris))))
        this_fade_step = fade_step
        this_fade_interval = fade_interval

    win = tk.Toplevel(root)
    win.overrideredirect(True)          # tanpa title bar biar mirip "kotak lirik"
    win.configure(bg="white")
    win.attributes("-alpha", 1.0)
    win.attributes("-topmost", True)    # paksa selalu di depan
    win.lift()

    if is_judul:
        # judul langsung muncul DI TENGAH layar, tanpa sliding
        target_x = (screen_w - WIN_W) // 2
        target_y = (screen_h - WIN_H) // 2
        current_y = target_y  # posisi awal = posisi akhir -> tidak ada slide
    else:
        target_x, target_y = posisi_acak()
        # posisi awal: di bawah layar (belum kelihatan), x sudah di posisi acak
        current_y = screen_h

    win.geometry(f"{WIN_W}x{WIN_H}+{target_x}+{current_y}")
    win.update_idletasks()
    win.deiconify()

    label = tk.Label(
        win,
        text="",
        font=("Consolas", 20),
        fg="black",
        bg="white",
        wraplength=WIN_W - 50,
        justify="left"
    )
    label.pack(expand=True, padx=20, pady=20)

    def slide_naik(y=current_y):
        if y > target_y:
            y_baru = max(target_y, y - slide_step)
            win.geometry(f"{WIN_W}x{WIN_H}+{target_x}+{y_baru}")
            win.after(slide_interval, slide_naik, y_baru)

    def ketik(karakter_idx=0, teks_sekarang=""):
        if karakter_idx < len(baris):
            teks_sekarang += baris[karakter_idx]
            label.config(text=teks_sekarang)
            win.after(char_delay, ketik, karakter_idx + 1, teks_sekarang)
        else:
            if is_judul:
                # judul selesai diketik -> tunggu dulu, baru lirik pertama muncul
                win.after(jeda_setelah_judul, buat_window, idx + 1, fade_out)
            else:
                # ketikan selesai -> langsung buat window bait berikutnya,
                # sambil "menitipkan" fade_out window ini ke window baru itu
                win.after(0, buat_window, idx + 1, fade_out)

    def fade_out(alpha=1.0):
        alpha_baru = alpha - this_fade_step
        if alpha_baru > 0:
            win.attributes("-alpha", alpha_baru)
            win.after(this_fade_interval, fade_out, alpha_baru)
        else:
            win.destroy()
            if idx == len(lyrics) - 1:
                root.destroy()

    # jalankan slide dan ketik bersamaan
    slide_naik()
    ketik()


buat_window(0)
root.mainloop()