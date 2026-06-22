# -*- coding: utf-8 -*-
"""5 ta Instagram post rasm yaratish (1080x1080)"""
from PIL import Image, ImageDraw, ImageFont
import os, random

SIZE = 1080
OUT  = os.path.join(os.path.dirname(__file__), 'static', 'posts')
os.makedirs(OUT, exist_ok=True)

GREEN   = (0, 114, 63)
DARK    = (0, 55, 30)
DARKER  = (3, 22, 12)
WHITE   = (255, 255, 255)
GOLD    = (245, 166, 35)
RED_S   = (255, 100, 100)
GREEN_S = (120, 255, 160)
LGRAY   = (245, 247, 245)
DGRAY   = (60, 60, 60)

FONT_PATHS_BOLD = [
    'C:/Windows/Fonts/calibrib.ttf',
    'C:/Windows/Fonts/arialbd.ttf',
    'C:/Windows/Fonts/verdanab.ttf',
]
FONT_PATHS = [
    'C:/Windows/Fonts/calibri.ttf',
    'C:/Windows/Fonts/arial.ttf',
    'C:/Windows/Fonts/verdana.ttf',
]

def fnt(size, bold=False):
    for p in (FONT_PATHS_BOLD if bold else FONT_PATHS):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def grad(img, c1, c2):
    d = ImageDraw.Draw(img)
    for y in range(SIZE):
        t = y / SIZE
        d.line([(0,y),(SIZE,y)], fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))

def cx(d, text, y, f, color=WHITE):
    bb = d.textbbox((0,0), text, font=f)
    d.text(((SIZE - bb[2] + bb[0]) // 2, y), text, font=f, fill=color)

def rx(d, x, y, w, h, r, fill, outline=None, ow=2):
    d.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill,
                         outline=outline, width=ow)

# ─── POST 1 : Muammo vs Yechim ────────────────────────────────────────────────
def post1():
    img = Image.new('RGB', (SIZE, SIZE))
    grad(img, DARKER, (0, 35, 18))
    d = ImageDraw.Draw(img)

    # Background circles
    d.ellipse([-150,-150, 350,350], fill=(0,90,45))
    d.ellipse([750, 730,1250,1250], fill=(0,60,30))

    # Top badge
    rx(d, 280, 50, 520, 70, 25, GREEN)
    cx(d, "HERBALIFE DISTRIBYUTOR", 63, fnt(30,True))

    # Titles
    cx(d, "MUAMMO",      148, fnt(80,True), GOLD)
    cx(d, "YECHIM BOR!", 238, fnt(80,True), GREEN_S)

    d.line([(50,335),(SIZE-50,335)], fill=(0,114,63), width=2)

    # Columns
    col_titles = [("ESKI USUL", 60, RED_S), ("HERBALIFE CRM", 560, GREEN_S)]
    for title, tx, col in col_titles:
        d.text((tx, 350), title, font=fnt(34,True), fill=col)

    probs = ["Daftarga yozish","Eslab qolish qiyin",
             "Hisob-kitob yo'q","Eslatma yo'q","Vaqt yo'qotish"]
    sols  = ["Barcha mijozlar bazada","Avtomatik eslatma",
             "Komissiya hisobi","Telegram bot","Vaqtni tejash"]

    for i, (p, s) in enumerate(zip(probs, sols)):
        y = 415 + i * 68
        d.text((60,  y), "x  " + p, font=fnt(33), fill=(255,110,110))
        d.text((560, y), "v  " + s, font=fnt(33), fill=(130,255,170))

    d.line([(SIZE//2, 340),(SIZE//2, 770)], fill=(0,114,63), width=2)

    # CTA box
    rx(d, 50, 810, SIZE-100, 155, 28, GREEN)
    cx(d, "BEPUL SINAB KORING!", 835, fnt(50,True))
    cx(d, "@herbalife_crm_bot",   910, fnt(38))

    img.save(f'{OUT}/post1_muammo.png')
    print("post1 OK")

# ─── POST 2 : Features grid ───────────────────────────────────────────────────
def post2():
    img = Image.new('RGB', (SIZE, SIZE), (240, 248, 242))
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([0,0,SIZE,190], fill=GREEN)
    cx(d, "HERBALIFE CRM",                   28, fnt(66,True))
    cx(d, "Distribyutorlar uchun maxsus tizim", 115, fnt(34), (200,240,215))

    features = [
        ("MIJOZLAR",    "Barchasi bir joyda\ntarix bilan"),
        ("BUYURTMALAR", "Tez yaratish\nva kuzatish"),
        ("TELEGRAM BOT","Har kuni hisobot\nva eslatmalar"),
        ("$3000 MAQSAD","Oylik daromad\nkuzatuvi"),
        ("21-KUN MARAFON","Challange\nva liderlar"),
        ("PDF KATALOG",  "Mahsulot katalogi\nnashr qilish"),
    ]

    cw, ch, pad = 320, 260, 30
    for i, (title, desc) in enumerate(features):
        col, row = i % 3, i // 3
        x = pad + col * (cw + pad)
        y = 210 + row * (ch + pad)

        # Shadow
        rx(d, x+4, y+4, cw, ch, 18, (200,220,208))
        # Card
        rx(d, x, y, cw, ch, 18, WHITE)
        # Green top bar
        d.rounded_rectangle([x, y, x+cw, y+10], radius=5, fill=GREEN)

        d.text((x+18, y+22), title, font=fnt(28,True), fill=GREEN)
        d.line([(x+18, y+60),(x+cw-18, y+60)], fill=(220,235,225), width=1)

        for j, line in enumerate(desc.split('\n')):
            d.text((x+18, y+72+j*34), line, font=fnt(26), fill=DGRAY)

    # Bottom strip
    d.rectangle([0, SIZE-72, SIZE, SIZE], fill=GREEN)
    cx(d, "@herbalife_crm_bot   |   1 OY BEPUL SINOV", SIZE-58, fnt(30))

    img.save(f'{OUT}/post2_features.png')
    print("post2 OK")

# ─── POST 3 : Telegram Bot ────────────────────────────────────────────────────
def post3():
    img = Image.new('RGB', (SIZE, SIZE))
    grad(img, (12,18,40), (5,12,28))
    d = ImageDraw.Draw(img)

    random.seed(7)
    for _ in range(60):
        sx,sy = random.randint(0,SIZE), random.randint(0,280)
        r = random.randint(1,2)
        d.ellipse([sx-r,sy-r,sx+r,sy+r], fill=(255,255,255,80))

    cx(d, "TELEGRAM BOT", 38, fnt(58,True), GOLD)
    cx(d, "Har kuni ertalab shuni olasiz:", 112, fnt(34), (170,195,220))

    # Phone body
    px,py,pw,ph = 165, 168, 750, 740
    d.rounded_rectangle([px,py,px+pw,py+ph], radius=42, fill=(28,32,48))
    d.rounded_rectangle([px+2,py+2,px+pw-2,py+ph-2], radius=40,
                         outline=(55,65,88), width=2)

    # Screen
    sx,sy,sw,sh = px+18, py+18, pw-36, ph-36
    d.rounded_rectangle([sx,sy,sx+sw,sy+sh], radius=28, fill=(18,18,20))

    # Telegram top bar
    d.rounded_rectangle([sx,sy,sx+sw,sy+56], radius=14, fill=(33,150,243))
    d.ellipse([sx+10,sy+8,sx+46,sy+44], fill=WHITE)
    d.text((sx+10,sy+8), "H", font=fnt(24,True), fill=GREEN)
    d.text((sx+56,sy+14), "Herbalife CRM Bot", font=fnt(26,True), fill=WHITE)
    d.text((sx+sw-80,sy+14), "online", font=fnt(20), fill=(160,220,160))

    def bubble(text_lines, by, highlight=False):
        lh = 32
        h  = len(text_lines)*lh + 18
        bx2 = sx+sw-14
        bx1 = sx+14
        fill = (0,90,50) if highlight else (40,42,54)
        d.rounded_rectangle([bx1,by,bx2,by+h], radius=12, fill=fill)
        for j,line in enumerate(text_lines):
            d.text((bx1+14, by+10+j*lh), line, font=fnt(22), fill=WHITE)
        return by + h + 8

    y = sy + 65
    y = bubble(["Xayrli tong!  Bugungi holat:"], y)
    y = bubble(["Oylik maqsad: 67%",
                "[========--]  $2,010 / $3,000"], y, highlight=True)
    y = bubble(["3 ta mijozga eslatma:"], y)
    y = bubble(["  1. Aziza T. (45 kun) - WhatsApp"], y)
    y = bubble(["  2. Bobur K. (38 kun) - WhatsApp"], y)
    y = bubble(["  3. Malika R. (32 kun) - WhatsApp"], y)
    y = bubble(["/stats  /maqsad  /mijozlar"], y)

    cx(d, "Avtomatik — siz uxlayotganingizda!", SIZE-108, fnt(34,True), GOLD)
    cx(d, "@herbalife_crm_bot",                  SIZE-56,  fnt(30),     (140,220,160))

    img.save(f'{OUT}/post3_bot.png')
    print("post3 OK")

# ─── POST 4 : Pricing ─────────────────────────────────────────────────────────
def post4():
    img = Image.new('RGB', (SIZE, SIZE))
    grad(img, GREEN, DARKER)
    d = ImageDraw.Draw(img)

    cx(d, "NARXLAR",                       38, fnt(78,True))
    cx(d, "O'zingizga mos tarifni tanlang",128, fnt(34),(200,240,215))

    plans = [
        {"name":"STARTER","price":"$10","sub":"/oy","col":(40,120,55),
         "feats":["50 ta mijoz","Telegram bot","Eslatmalar","Statistika"]},
        {"name":"PRO","price":"$30","sub":"/oy","col":GREEN,"popular":True,
         "feats":["Cheksiz mijoz","21-kun Marafon","BMI Kalkulyator","PDF Katalog","Ustuvor yordam"]},
        {"name":"TEAM","price":"$100","sub":"/oy","col":(180,110,0),
         "feats":["5 distribyutor","Admin panel","Umumiy statistika","VIP yordam"]},
    ]

    cw = 308
    gap = (SIZE - 3*cw - 40) // 2
    base_y = 195

    for i, p in enumerate(plans):
        pop = p.get('popular', False)
        x   = 20 + i*(cw+gap)
        y   = base_y - (24 if pop else 0)
        ch  = 630 + (24 if pop else 0)

        # Shadow
        rx(d, x+5, y+5, cw, ch, 22, (0,25,12))
        # Card
        rx(d, x, y, cw, ch, 22, WHITE)

        if pop:
            rx(d, x+60, y-22, cw-120, 28, 12, GOLD)
            label = "ENG MASHHUR"
            lb = d.textbbox((0,0), label, font=fnt(18,True))
            d.text((x+(cw-(lb[2]-lb[0]))//2, y-19), label, font=fnt(18,True), fill=WHITE)

        # Header strip
        d.rounded_rectangle([x, y, x+cw, y+115], radius=22, fill=p['col'])
        d.rounded_rectangle([x, y+95, x+cw, y+115], radius=4, fill=p['col'])

        nb = d.textbbox((0,0), p['name'], font=fnt(32,True))
        d.text((x+(cw-(nb[2]-nb[0]))//2, y+10), p['name'], font=fnt(32,True), fill=WHITE)

        pb = d.textbbox((0,0), p['price'], font=fnt(60,True))
        d.text((x+(cw-(pb[2]-pb[0]))//2, y+48), p['price'], font=fnt(60,True), fill=WHITE)

        fy = y + 128
        for feat in p['feats']:
            d.text((x+18, fy), "v  " + feat, font=fnt(27), fill=DGRAY)
            fy += 52

        # Button
        by = y + ch - 72
        rx(d, x+18, by, cw-36, 54, 14, p['col'])
        bt = "Boshlash"
        bb = d.textbbox((0,0), bt, font=fnt(28,True))
        d.text((x+(cw-(bb[2]-bb[0]))//2, by+12), bt, font=fnt(28,True), fill=WHITE)

    cx(d, "1 OY BEPUL SINOV   |   @herbalife_crm_bot",
       SIZE-38, fnt(28), (200,240,215))

    img.save(f'{OUT}/post4_pricing.png')
    print("post4 OK")

# ─── POST 5 : CTA ─────────────────────────────────────────────────────────────
def post5():
    img = Image.new('RGB', (SIZE, SIZE))
    grad(img, DARKER, GREEN)
    d = ImageDraw.Draw(img)

    # Circles
    d.ellipse([-200,-200, 650,650], outline=(0,140,70), width=4)
    d.ellipse([430, 430,1280,1280], outline=(0,90,45), width=3)
    d.ellipse([300, 200,780, 680],  outline=(0,114,63), width=1)

    # Badge
    rx(d, 310, 72, 460, 64, 28, (255,255,255,30))
    cx(d, "HERBALIFE CRM", 84, fnt(32,True), (200,255,220))

    # Big text
    cx(d, "OYIGA",       180, fnt(88,True), (190,255,215))
    cx(d, "$3,000",      278, fnt(155,True), GOLD)
    cx(d, "ISHLASHNI",  448, fnt(88,True), (190,255,215))
    cx(d, "HOHLAYSIZMI?", 548, fnt(78,True), (190,255,215))

    d.line([(90,658),(SIZE-90,658)], fill=(0,150,75), width=2)

    items = ["Mijozlar boshqaruvi", "Telegram bot", "Avtomatik hisob"]
    for j, item in enumerate(items):
        xp = 55 + j*345
        d.text((xp, 674), "v " + item, font=fnt(28,True), fill=(140,255,175))

    d.line([(90,730),(SIZE-90,730)], fill=(0,150,75), width=2)

    # CTA button
    rx(d, 100, 762, SIZE-200, 115, 32, GOLD)
    cx(d, "HOZIROQ BOSHLANG",  782, fnt(50,True), (25,15,0))
    cx(d, "1 OY BEPUL SINOV",  843, fnt(32,True), (60,35,0))

    cx(d, "@herbalife_crm_bot", 920, fnt(44,True), (175,255,200))
    cx(d, "#herbalife  #distribyutor  #crm  #biznes",
       998, fnt(26), (90,170,115))

    img.save(f'{OUT}/post5_cta.png')
    print("post5 OK")


if __name__ == '__main__':
    print("Instagram postlar yaratilmoqda...\n")
    post1(); post2(); post3(); post4(); post5()
    print(f"\nBarchasi saqlandi: {OUT}")
