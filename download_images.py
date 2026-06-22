# -*- coding: utf-8 -*-
"""Downloads real Herbalife product images from the web and saves them locally."""
import os
import urllib.request
import urllib.error

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'products')

# (local_filename_no_ext, product_name_in_db, remote_url, ext)
REAL_IMAGES = [
    ('f1_chocolate', 'Formula 1 Шоколад',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/112/1092/herbalife-formula1-smooth-chocolate-550g-tub__69257.1760112844.jpg?c=2',
     'jpg'),
    ('f1_vanilla', 'Formula 1 Ваниль',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/160/992/herbalife-formula1-vanilla-cream-780g-tub__40073.1756481225.jpg?c=2',
     'jpg'),
    ('f1_strawberry', 'Formula 1 Клубника',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/115/989/herbalife-formula1-healthy-meal-nutritional-shake-strawberry-delight-550g-container__22723.1756456788.jpg?c=2',
     'jpg'),
    ('f1_hazelnut', 'Formula 1 Дикий Лесной Орех',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/126/1001/herbalife-formula1-healthy-meal-nutritional-shake-mint-and-chocolate-550g-container__97767.1760368011.jpg?c=2',
     'jpg'),
    ('f1_vega', 'Formula 1 Вега (Vega)',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/154/895/pc-2600-gb-ie-ic.png-pdp-w875h783__05483__68310.1760537301.jpg?c=2',
     'jpg'),
    ('protein', 'Протеиновый коктейль',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/154/888/pp-pdm-emea.jpg-pdp-w875h783__55053.1760537301.jpg?c=2',
     'jpg'),
    ('cr7', 'CR7 Drive',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/183/984/herbalife24-cr7-drive-cannister-acai-berry-flavour-tub__52720.1751969190.jpg?c=2',
     'jpg'),
    ('aloe', 'Алоэ вера концентрат',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/166/631/1065-aloe-concentrate-aloe-mango-473ml_-_Bottle__83104.1705400368.png?c=2',
     'png'),
    ('nrg_lemon', 'Чай НРГ Лимон-Имбирь',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/149/1076/herbalife-instant-herbal-beverage-with-tea-extracts-lemon-flavour-51g-container__51157.1758441060.jpg?c=2',
     'jpg'),
    ('nrg_raspberry', 'Чай НРГ Малина',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/148/1073/herbalife-instant-herbal-beverage-rasperry-flavour-bottle__17428.1758294813.jpg?c=2',
     'jpg'),
    ('formula2', 'Мультивитамины Formula 2',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/532x532/products/113/401/Formula_2_-_Vitamin_and_Mineral_Complex_Womens_60_Tablets_-_Container__55652.1758111798.png?c=2',
     'png'),
    ('omega3', 'Омега-3',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/122/970/herbalife-herbalifeline-max-BOX__38280.1751640428.jpg?c=2',
     'jpg'),
    ('collagen', 'Коллаген Skin',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/199/861/Collagen_SKIN_Booster_strawberry_and_lemon_171g__28360.1704382807.png?c=2',
     'png'),
    ('thermo', 'Термо Комплит',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/218/1166/herbalife-phyto-complete-sachet__86770.1767713545.1280.1280__18875.1767719966.jpg?c=2',
     'jpg'),
    ('immune', 'Иммью Буст',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/188/1140/herbalife-immune-booster-berry-flavour-box__72386.1761751718.jpg?c=2',
     'jpg'),
    ('fiber', 'Активный Волокно',
     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/532x532/products/135/1047/herbalife-oat-apple-fibre-tub__82549.1757692511.jpg?c=2',
     'jpg'),
]

# Maps product DB name → local static URL (after download)
NAME_TO_URL = {}

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://herbalnutritionforlife.com/',
}


def _download_one(fname, url, ext):
    local_path = os.path.join(IMAGES_DIR, f'{fname}.{ext}')
    if os.path.exists(local_path) and os.path.getsize(local_path) > 5000:
        return local_path  # already downloaded
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if len(data) < 1000:
            return None
        with open(local_path, 'wb') as f:
            f.write(data)
        return local_path
    except Exception as e:
        print(f'[images] Download failed for {fname}: {e}')
        return None


def download_all():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    ok = 0
    for fname, db_name, url, ext in REAL_IMAGES:
        result = _download_one(fname, url, ext)
        static_url = f'/static/images/products/{fname}.{ext}'
        if result:
            NAME_TO_URL[db_name] = static_url
            ok += 1
            print(f'[images] OK {db_name}')
        else:
            # fallback to SVG if download failed
            svg_path = os.path.join(IMAGES_DIR, f'{fname}.svg')
            if os.path.exists(svg_path):
                NAME_TO_URL[db_name] = f'/static/images/products/{fname}.svg'
                print(f'[images] SVG {db_name}')
            else:
                NAME_TO_URL[db_name] = static_url  # try anyway
    print(f'[images] {ok}/{len(REAL_IMAGES)} haqiqiy rasm yuklandi')
    return ok


if __name__ == '__main__':
    download_all()
    print('Yuklash tugadi!')
