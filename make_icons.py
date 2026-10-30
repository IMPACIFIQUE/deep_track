import math
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons")
os.makedirs(OUT, exist_ok=True)

W = (255, 255, 255, 255)
S = 256  # draw big, then shrink for smooth edges


def canvas():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def save(img, name):
    img.resize((64, 64), Image.LANCZOS).save(os.path.join(OUT, f"{name}.png"))


def home():
    img, d = canvas()
    d.line([(30, 125), (128, 35), (226, 125)], fill=W, width=18, joint="curve")
    d.line([(55, 110), (55, 225), (201, 225), (201, 110)], fill=W, width=18, joint="curve")
    d.rectangle((108, 160, 148, 225), fill=W)
    save(img, "home")


def task():
    img, d = canvas()
    d.rounded_rectangle((40, 40, 216, 216), radius=24, outline=W, width=16)
    d.line([(80, 130), (115, 165), (180, 90)], fill=W, width=18, joint="curve")
    save(img, "task")


def hacking():
    img, d = canvas()
    d.rounded_rectangle((24, 48, 232, 208), radius=20, outline=W, width=16)
    d.line([(70, 100), (110, 128), (70, 156)], fill=W, width=16, joint="curve")
    d.line([(130, 160), (185, 160)], fill=W, width=16)
    save(img, "hacking")


def control():
    img, d = canvas()
    for y, x in ((70, 90), (128, 165), (186, 115)):
        d.line([(40, y), (216, y)], fill=W, width=12)
        d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=W)
    save(img, "control")


def admin():
    img, d = canvas()
    pts = [(128, 25), (220, 60), (220, 130), (128, 232), (36, 130), (36, 60)]
    d.line(pts + [pts[0]], fill=W, width=16, joint="curve")
    d.line([(85, 125), (118, 158), (172, 98)], fill=W, width=16, joint="curve")
    save(img, "admin")


def settings():
    img, d = canvas()
    for i in range(8):
        a = math.radians(i * 45)
        d.line(
            [(128 + 78 * math.cos(a), 128 + 78 * math.sin(a)),
             (128 + 108 * math.cos(a), 128 + 108 * math.sin(a))],
            fill=W, width=30,
        )
    d.ellipse((50, 50, 206, 206), outline=W, width=24)
    d.ellipse((100, 100, 156, 156), outline=W, width=14)
    save(img, "settings")


def device():
    img, d = canvas()
    d.rounded_rectangle((30, 45, 226, 170), radius=14, outline=W, width=16)
    d.line([(128, 170), (128, 210)], fill=W, width=16)
    d.line([(80, 214), (176, 214)], fill=W, width=16)
    save(img, "device")


def play():
    img, d = canvas()
    d.polygon([(80, 45), (80, 211), (215, 128)], fill=W)
    save(img, "play")


def stop():
    img, d = canvas()
    d.rounded_rectangle((55, 55, 201, 201), radius=18, fill=W)
    save(img, "stop")


def plus():
    img, d = canvas()
    d.line([(128, 45), (128, 211)], fill=W, width=22)
    d.line([(45, 128), (211, 128)], fill=W, width=22)
    save(img, "plus")


def trash():
    img, d = canvas()
    d.line([(50, 80), (206, 80)], fill=W, width=16)
    d.line([(100, 80), (100, 52), (156, 52), (156, 80)], fill=W, width=14, joint="curve")
    d.line([(70, 90), (80, 226), (176, 226), (186, 90)], fill=W, width=16, joint="curve")
    d.line([(112, 120), (112, 190)], fill=W, width=12)
    d.line([(144, 120), (144, 190)], fill=W, width=12)
    save(img, "trash")


def user():
    img, d = canvas()
    d.ellipse((85, 28, 171, 114), fill=W)
    d.pieslice((36, 135, 220, 330), 180, 360, fill=W)
    save(img, "user")


def user_plus():
    img, d = canvas()
    d.ellipse((60, 28, 140, 108), fill=W)
    d.pieslice((15, 128, 185, 300), 180, 360, fill=W)
    d.line([(205, 90), (205, 170)], fill=W, width=18)
    d.line([(165, 130), (245, 130)], fill=W, width=18)
    save(img, "user_plus")


def alert():
    img, d = canvas()
    d.line([(128, 35), (225, 215), (31, 215), (128, 35)], fill=W, width=16, joint="curve")
    d.line([(128, 95), (128, 150)], fill=W, width=16)
    d.ellipse((118, 168, 138, 188), fill=W)
    save(img, "alert")


def app_ico():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((8, 8, 248, 248), radius=50, fill=(31, 106, 165, 255))
    d.line([(70, 100), (115, 128), (70, 156)], fill=W, width=22, joint="curve")
    d.line([(135, 165), (190, 165)], fill=W, width=22)
    img.save(os.path.join(OUT, "app.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])


for fn in (home, task, hacking, control, admin, settings, device,
           play, stop, plus, trash, user, user_plus, alert, app_ico):
    fn()

print("Icons created in", OUT)