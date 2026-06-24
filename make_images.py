# -*- coding: utf-8 -*-
"""Generates SVG product images for the Herbalife CRM catalog (all 46 products)."""
import os

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'products')


def _svg(title, subtitle, emoji, c1, c2, c3=None):
    c3 = c3 or c2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c3}"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="38%" r="40%">
      <stop offset="0%"   stop-color="rgba(255,255,255,0.25)"/>
      <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
    </radialGradient>
    <filter id="shadow">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="rgba(0,0,0,0.3)"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="400" height="400" rx="0" fill="url(#bg)"/>
  <rect width="400" height="400" rx="0" fill="url(#glow)"/>

  <!-- Decorative circles -->
  <circle cx="380" cy="50"  r="140" fill="rgba(255,255,255,0.07)"/>
  <circle cx="20"  cy="370" r="120" fill="rgba(255,255,255,0.05)"/>
  <circle cx="200" cy="420" r="160" fill="rgba(0,0,0,0.10)"/>

  <!-- Top accent line -->
  <rect x="0" y="0" width="400" height="4" fill="rgba(255,255,255,0.4)"/>

  <!-- Brand watermark -->
  <text x="20" y="30" font-size="13" font-family="Arial, sans-serif"
        fill="rgba(255,255,255,0.3)" font-weight="700" letter-spacing="1">HERBALIFE NUTRITION</text>

  <!-- Product emoji circle bg -->
  <circle cx="200" cy="170" r="90" fill="rgba(0,0,0,0.20)" filter="url(#shadow)"/>
  <circle cx="200" cy="170" r="78" fill="rgba(255,255,255,0.12)"/>

  <!-- Main emoji -->
  <text x="200" y="196"
        text-anchor="middle" dominant-baseline="middle"
        font-size="72"
        font-family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, sans-serif">{emoji}</text>

  <!-- Product name -->
  <text x="200" y="286"
        text-anchor="middle"
        font-size="22" font-weight="800" letter-spacing="0.2"
        font-family="Arial Black, Arial, sans-serif" fill="#FFFFFF"
        filter="url(#shadow)">{title}</text>

  <!-- Subtitle / flavor -->
  <text x="200" y="314"
        text-anchor="middle"
        font-size="15" font-family="Arial, sans-serif"
        fill="rgba(255,255,255,0.75)" letter-spacing="0.5">{subtitle}</text>

  <!-- Bottom badge -->
  <rect x="130" y="345" width="140" height="30" rx="15" fill="rgba(255,255,255,0.15)"/>
  <text x="200" y="364"
        text-anchor="middle"
        font-size="9" letter-spacing="3" font-weight="700"
        font-family="Arial, sans-serif" fill="rgba(255,255,255,0.65)">NUTRITION</text>
</svg>'''


# (filename, product_name_in_db, display_title, subtitle, emoji, grad_start, grad_end)
CATALOG = [
    # ── Formula 1 Kokteylar ──────────────────────────────────────────
    ('f1_chocolate',   'Formula 1 Шоколад',            'Formula 1',       'Шоколад',          '🍫', '#3E2723', '#6D4C41'),
    ('f1_choc_soft',   'Formula 1 Нежный Шоколад',     'Formula 1',       'Нежный Шоколад',   '🍫', '#5D4037', '#8D6E63'),
    ('f1_vanilla',     'Formula 1 Ваниль',              'Formula 1',       'Ваниль',           '🍦', '#8D6E63', '#BCAAA4'),
    ('f1_strawberry',  'Formula 1 Клубника',            'Formula 1',       'Клубника',         '🍓', '#880E4F', '#D81B60'),
    ('f1_hazelnut',    'Formula 1 Лесной Орех',         'Formula 1',       'Лесной Орех',      '🌰', '#4E342E', '#795548'),
    ('f1_coconut',     'Formula 1 Кокос',               'Formula 1',       'Кокос',            '🥥', '#004D40', '#00897B'),
    ('f1_mango',       'Formula 1 Манго',               'Formula 1',       'Манго',            '🥭', '#E65100', '#FF8F00'),
    ('f1_melon',       'Formula 1 Дыня',                'Formula 1',       'Дыня',             '🍈', '#F57F17', '#FDD835'),
    ('f1_banana',      'Formula 1 Банан-Карамель',      'Formula 1',       'Банан-Карамель',   '🍌', '#FF8F00', '#F9A825'),
    ('f1_cookie',      'Formula 1 Хрустящее Печенье',  'Formula 1',       'Печенье',          '🍪', '#5D4037', '#8D6E63'),
    ('f1_soup',        'Formula 1 Курица-Крем-Суп',    'Formula 1',       'Крем-Суп',         '🍲', '#827717', '#9E9D24'),
    ('f1_night',       'Formula 1 Найт Мод',            'Formula 1',       'Night Mode',       '🌙', '#1A237E', '#283593'),
    ('f1_vega',        'Formula 1 Vega',                'Formula 1 Vega',  'Растительный',     '🌱', '#1B5E20', '#2E7D32'),
    ('protein',        'Протеиновый Коктейль',          'Протеин',         'Высокобелковый',   '💪', '#0D47A1', '#1565C0'),
    # ── Napitki ─────────────────────────────────────────────────────
    ('nrg_lemon',      'Чай НРГ Лимон-Имбирь',         'NRG Чай',         'Лимон-Имбирь',     '🍋', '#F57F17', '#FFA000'),
    ('nrg_raspberry',  'Чай НРГ Малина',                'NRG Чай',         'Малина',           '🫐', '#880E4F', '#AD1457'),
    ('nrg_peach',      'Чай НРГ Персик',                'NRG Чай',         'Персик',           '🍑', '#E64A19', '#FF8A65'),
    ('nrg_mango',      'Чай НРГ Манго-Питахайя',        'NRG Чай',         'Манго-Питахайя',   '🐉', '#6A1B9A', '#8E24AA'),
    ('nrg_black',      'Чай НРГ Чёрная Смородина',      'NRG Чай',         'Чёрная Смородина', '🫐', '#4527A0', '#512DA8'),
    ('cr7',            'CR7 Drive',                     'CR7 Drive',       'Изотоник',         '⚡', '#B71C1C', '#F57F17'),
    ('aloe',           'Алоэ Вера Концентрат',          'Алоэ Вера',       'Концентрат',       '🌿', '#1B5E20', '#2E7D32'),
    ('aloe_mango',     'Алоэ Вера Манго',               'Алоэ Вера',       'Манго',            '🥭', '#00695C', '#00897B'),
    ('mangostin',      'Мангостин-Малина Напиток',       'Мангостин',       'Малина',           '🍇', '#880E4F', '#6A1B9A'),
    # ── Sport H24 ────────────────────────────────────────────────────
    ('h24_achieve',    'H24 Achieve',                   'H24 Achieve',     'Pre-Workout',      '🏋️', '#B71C1C', '#C62828'),
    ('h24_prolong',    'H24 Prolong',                   'H24 Prolong',     'During Workout',   '🚴', '#1565C0', '#1976D2'),
    ('h24_strength',   'H24 Rebuild Strength',          'H24 Rebuild',     'Strength',         '💪', '#1B5E20', '#2E7D32'),
    ('h24_endurance',  'H24 Rebuild Endurance',         'H24 Rebuild',     'Endurance',        '🏃', '#BF360C', '#D84315'),
    # ── Vitaminlar ───────────────────────────────────────────────────
    ('formula2',       'Formula 2 Мультивитамины',      'Formula 2',       'Мультивитамины',   '💊', '#01579B', '#0288D1'),
    ('omega3',         'Омега-3',                       'Омега-3',         'EPA + DHA',        '🐟', '#004D40', '#00695C'),
    ('immune',         'Иммью Буст',                    'Иммью Буст',      'Иммунитет',        '🛡️', '#1A237E', '#303F9F'),
    ('thermo',         'Термо Комплит',                 'Термо Комплит',   'Снижение веса',    '🔥', '#BF360C', '#E64A19'),
    ('vitamin_c',      'Витамин C 250мг',               'Витамин C',       '250 мг',           '🍊', '#E64A19', '#FF7043'),
    ('calcium',        'Кальций Плюс',                  'Кальций Плюс',    'D3 + K2',          '🦴', '#546E7A', '#78909C'),
    ('formula3',       'Формула 3 Протеин',             'Formula 3',       'Протеин',          '💚', '#1B5E20', '#388E3C'),
    ('multimineral',   'Мультиминерал',                 'Мультиминерал',   'Комплекс',         '⚗️', '#37474F', '#546E7A'),
    # ── Krasota ──────────────────────────────────────────────────────
    ('collagen',       'Skin Коллаген',                 'Skin Коллаген',   'Морской коллаген', '✨', '#880E4F', '#C2185B'),
    ('collagen_beef',  'Коллаген Говяжий',              'Коллаген',        'Говяжий',          '🌸', '#AD1457', '#E91E63'),
    ('aloe_face',      'Алоэ Гель для лица',            'Алоэ Гель',       'Для лица',         '🧴', '#00838F', '#00ACC1'),
    ('shower_gel',     'Гель для душа Алоэ',            'Гель для душа',   'Алоэ Вера',        '🚿', '#006064', '#00838F'),
    ('hand_cream',     'Крем для рук',                  'Крем для рук',    'Питательный',      '🤲', '#C2185B', '#E91E63'),
    # ── Dobavki ──────────────────────────────────────────────────────
    ('fiber',          'Активная Клетчатка',            'Клетчатка',       'Активная',         '🌾', '#33691E', '#558B2F'),
    ('probiotic',      'Пробиотик Комплекс',            'Пробиотик',       '10 штаммов',       '🦠', '#6A1B9A', '#7B1FA2'),
    ('lcarnitine',     'Л-Карнитин',                    'L-Карнитин',      '1000 мг',          '🔥', '#283593', '#303F9F'),
    ('bcaa',           'BCAA Комплекс',                 'BCAA',            '2:1:1',            '💪', '#0277BD', '#0288D1'),
    ('glucosamine',    'Глюкозамин Плюс',               'Глюкозамин',      'Суставы',          '🦴', '#558B2F', '#689F38'),
    ('detox_tea',      'Детокс Чай 7 дней',             'Детокс Чай',      '7 дней',           '🍵', '#00695C', '#00796B'),
]

# Mapping: product DB name → local SVG filename (without extension)
NAME_TO_FILE = {row[1]: row[0] for row in CATALOG}


def generate_all():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    created = 0
    for row in CATALOG:
        fname, _, title, subtitle, emoji, c1, c2 = row
        path = os.path.join(IMAGES_DIR, fname + '.svg')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(_svg(title, subtitle, emoji, c1, c2))
        created += 1
        print(f'  OK {fname}.svg')
    print(f'\n[images] {created} SVG rasmlar yaratildi -> static/images/products/')
    return created


if __name__ == '__main__':
    generate_all()
    print('Tayyor!')
