# -*- coding: utf-8 -*-
"""Auto-generates SVG product images for the Herbalife CRM catalog."""
import os

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'products')


def _svg(title, subtitle, emoji, c1, c2, c3=None):
    c3 = c3 or c2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 280" width="400" height="280">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c3}"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="42%" r="38%">
      <stop offset="0%"   stop-color="rgba(255,255,255,0.22)"/>
      <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
    </radialGradient>
  </defs>

  <!-- Background -->
  <rect width="400" height="280" fill="url(#bg)"/>
  <rect width="400" height="280" fill="url(#glow)"/>

  <!-- Decorative blobs -->
  <circle cx="370" cy="40"  r="120" fill="rgba(255,255,255,0.06)"/>
  <circle cx="30"  cy="260" r="100" fill="rgba(255,255,255,0.04)"/>
  <circle cx="200" cy="290" r="130" fill="rgba(0,0,0,0.08)"/>

  <!-- Top accent line -->
  <rect x="0" y="0" width="400" height="4" fill="rgba(255,255,255,0.35)"/>

  <!-- Herbalife leaf watermark (top-left) -->
  <text x="18" y="26" font-size="15" font-family="Arial" fill="rgba(255,255,255,0.25)" font-weight="bold">🌿 HERBALIFE</text>

  <!-- Product circle bg -->
  <circle cx="200" cy="118" r="72" fill="rgba(0,0,0,0.18)"/>
  <circle cx="200" cy="118" r="62" fill="rgba(255,255,255,0.10)"/>

  <!-- Main product emoji -->
  <text x="200" y="138"
        text-anchor="middle" dominant-baseline="middle"
        font-size="58" font-family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, sans-serif">{emoji}</text>

  <!-- Product name -->
  <text x="200" y="198"
        text-anchor="middle"
        font-size="18" font-weight="700" letter-spacing="0.3"
        font-family="Arial, Helvetica, sans-serif" fill="#FFFFFF">{title}</text>

  <!-- Subtitle / flavor -->
  <text x="200" y="220"
        text-anchor="middle"
        font-size="13" font-family="Arial, sans-serif"
        fill="rgba(255,255,255,0.72)">{subtitle}</text>

  <!-- Bottom label badge -->
  <rect x="138" y="240" width="124" height="24" rx="12" fill="rgba(255,255,255,0.13)"/>
  <text x="200" y="256"
        text-anchor="middle"
        font-size="8.5" letter-spacing="3.5" font-weight="600"
        font-family="Arial, sans-serif" fill="rgba(255,255,255,0.55)">NUTRITION</text>
</svg>'''


# (filename, product_name_in_db, display_title, subtitle, emoji, grad_start, grad_end)
CATALOG = [
    ('f1_chocolate',  'Formula 1 Шоколад',          'Formula 1',        'Шоколад',        '🍫', '#3E2723', '#6D4C41'),
    ('f1_vanilla',    'Formula 1 Ваниль',            'Formula 1',        'Ваниль',         '🍦', '#E65100', '#FFB300'),
    ('f1_strawberry', 'Formula 1 Клубника',          'Formula 1',        'Клубника',       '🍓', '#880E4F', '#D81B60'),
    ('f1_hazelnut',   'Formula 1 Лесной Орех',       'Formula 1',        'Лесной Орех',    '🌰', '#4E342E', '#795548'),
    ('f1_vega',       'Formula 1 Vega',              'Formula 1 Vega',   'Растительный',   '🌱', '#1B5E20', '#2E7D32'),
    ('protein',       'Протеиновый Коктейль',        'Протеин',          'Высокобелковый', '💪', '#0D47A1', '#1976D2'),
    ('cr7',           'CR7 Drive',                   'CR7 Drive',        'Изотоник',       '⚡', '#B71C1C', '#F57F17'),
    ('aloe',          'Алоэ Вера Концентрат',        'Алоэ Вера',        'Концентрат',     '🌿', '#1B5E20', '#388E3C'),
    ('nrg_lemon',     'Чай НРГ Лимон-Имбирь',       'NRG Чай',          'Лимон-Имбирь',  '🍋', '#F57F17', '#FFA000'),
    ('nrg_raspberry', 'Чай НРГ Малина',              'NRG Чай',          'Малина',         '🫐', '#6A1B9A', '#AD1457'),
    ('formula2',      'Formula 2 Мультивитамины',    'Formula 2',        'Мультивитамины', '💊', '#01579B', '#0288D1'),
    ('omega3',        'Омега-3',                     'Омега-3',          'EPA + DHA',      '🐟', '#004D40', '#00695C'),
    ('collagen',      'Skin Коллаген',               'Skin Коллаген',    'Морской коллаген','✨', '#880E4F', '#C2185B'),
    ('thermo',        'Термо Комплит',               'Термо Комплит',    'Снижение веса',  '🔥', '#BF360C', '#E64A19'),
    ('immune',        'Иммью Буст',                  'Иммью Буст',       'Иммунитет',      '🛡', '#1A237E', '#303F9F'),
    ('fiber',         'Активная Клетчатка',          'Клетчатка',        'Активная',       '🌾', '#33691E', '#558B2F'),
]

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
    print(f'[images] {created} SVG rasmlar yaratildi → static/images/products/')
    return created


if __name__ == '__main__':
    generate_all()
    print('Tayyor!')
