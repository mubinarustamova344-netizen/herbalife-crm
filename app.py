# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from models import db, Client, Product, Order, OrderItem, Challenge, ChallengeParticipant, User, WeightLog
from make_images import generate_all as _gen_images, NAME_TO_FILE as _IMG_MAP
from download_images import download_all as _download_real_images, NAME_TO_URL as _REAL_URL

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'herbalife-secret-2024'),
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(os.path.dirname(__file__), 'herbalife.db')}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Iltimos tizimga kiring.'
login_manager.login_message_category = 'warning'

COMMISSION_PCT = 25

# CDN URLs — to'g'ridan-to'g'ri tashqi manzillar (Railway uchun)
PRODUCT_CDN_IMAGES = {
    'Formula 1 Шоколад':        'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/112/1092/herbalife-formula1-smooth-chocolate-550g-tub__69257.1760112844.jpg?c=2',
    'Formula 1 Ваниль':         'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/160/992/herbalife-formula1-vanilla-cream-780g-tub__40073.1756481225.jpg?c=2',
    'Formula 1 Клубника':       'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/115/989/herbalife-formula1-healthy-meal-nutritional-shake-strawberry-delight-550g-container__22723.1756456788.jpg?c=2',
    'Formula 1 Лесной Орех':    'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/126/1001/herbalife-formula1-healthy-meal-nutritional-shake-mint-and-chocolate-550g-container__97767.1760368011.jpg?c=2',
    'Formula 1 Vega':           'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/154/895/pc-2600-gb-ie-ic.png-pdp-w875h783__05483__68310.1760537301.jpg?c=2',
    'Протеиновый Коктейль':     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/154/888/pp-pdm-emea.jpg-pdp-w875h783__55053.1760537301.jpg?c=2',
    'CR7 Drive':                'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/183/984/herbalife24-cr7-drive-cannister-acai-berry-flavour-tub__52720.1751969190.jpg?c=2',
    'Алоэ Вера Концентрат':     'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/166/631/1065-aloe-concentrate-aloe-mango-473ml_-_Bottle__83104.1705400368.png?c=2',
    'Чай НРГ Лимон-Имбирь':    'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/149/1076/herbalife-instant-herbal-beverage-with-tea-extracts-lemon-flavour-51g-container__51157.1758441060.jpg?c=2',
    'Чай НРГ Малина':           'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/148/1073/herbalife-instant-herbal-beverage-rasperry-flavour-bottle__17428.1758294813.jpg?c=2',
    'Formula 2 Мультивитамины': 'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/532x532/products/113/401/Formula_2_-_Vitamin_and_Mineral_Complex_Womens_60_Tablets_-_Container__55652.1758111798.png?c=2',
    'Омега-3':                  'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/122/970/herbalife-herbalifeline-max-BOX__38280.1751640428.jpg?c=2',
    'Skin Коллаген':            'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/199/861/Collagen_SKIN_Booster_strawberry_and_lemon_171g__28360.1704382807.png?c=2',
    'Термо Комплит':            'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/218/1166/herbalife-phyto-complete-sachet__86770.1767713545.1280.1280__18875.1767719966.jpg?c=2',
    'Иммью Буст':               'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/728x728/products/188/1140/herbalife-immune-booster-berry-flavour-box__72386.1761751718.jpg?c=2',
    'Активная Клетчатка':       'https://cdn11.bigcommerce.com/s-yyr3tzu8q0/images/stencil/532x532/products/135/1047/herbalife-oat-apple-fibre-tub__82549.1757692511.jpg?c=2',
}


@login_manager.user_loader
def load_user(uid):
    try:
        return User.query.get(int(uid))
    except (ValueError, TypeError):
        return None


def _cq():
    """Client query filtered by current user (admin sees all)."""
    q = Client.query
    if not current_user.is_admin:
        q = q.filter_by(owner_id=current_user.id)
    return q


def _oq():
    """Order query filtered by current user (admin sees all)."""
    if current_user.is_admin:
        return Order.query
    return Order.query.join(Client).filter(Client.owner_id == current_user.id)


_db_initialized = False


def _init_db():
    global _db_initialized
    if _db_initialized:
        return
    db.create_all()

    # Schema migrations for new columns
    from sqlalchemy import text, inspect as sa_inspect
    insp = sa_inspect(db.engine)
    with db.engine.connect() as conn:
        # clients.owner_id
        client_cols = [c['name'] for c in insp.get_columns('clients')]
        if 'owner_id' not in client_cols:
            conn.execute(text('ALTER TABLE clients ADD COLUMN owner_id INTEGER REFERENCES users(id)'))
            conn.commit()
        # products columns (vid, direction, etc.)
        prod_cols = [c['name'] for c in insp.get_columns('products')]
        for col, typ in [('vid','VARCHAR(80)'),('direction','TEXT'),('sostav','TEXT'),
                         ('recipe','TEXT'),('image_url','VARCHAR(500)')]:
            if col not in prod_cols:
                conn.execute(text(f'ALTER TABLE products ADD COLUMN {col} {typ}'))
        conn.commit()
        # clients.birthday
        client_cols2 = [c['name'] for c in insp.get_columns('clients')]
        if 'birthday' not in client_cols2:
            conn.execute(text('ALTER TABLE clients ADD COLUMN birthday DATE'))
            conn.commit()

    if not User.query.first():
        admin = User(username='admin', full_name='Admin', is_admin=True, is_active=True)
        admin.set_password('herbalife123')
        db.session.add(admin)
        db.session.commit()

    _db_initialized = True


@app.before_request
def ensure_db():
    _init_db()


# ── Landing page ──────────────────────────────────────────────────────────────
@app.route('/landing')
def landing():
    return render_template('landing.html')


@app.route('/order-request', methods=['POST'])
def order_request():
    data = request.get_json() or {}
    full_name = data.get('full_name', '')
    phone     = data.get('phone', '')
    telegram  = data.get('telegram', '')
    plan      = data.get('plan', '')
    city      = data.get('city', '')

    # Telegram orqali bildirishnoma yuborish
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id_file = os.path.join(os.path.dirname(__file__), '.chat_id')
    if token and os.path.exists(chat_id_file):
        try:
            import urllib.request, urllib.parse
            chat_id = open(chat_id_file).read().strip()
            msg = (
                f"🔥 YANGI ARIZA!\n\n"
                f"👤 Ism: {full_name}\n"
                f"📱 Tel: {phone}\n"
                f"💬 Telegram: {telegram}\n"
                f"🌍 Shahar: {city}\n"
                f"💎 Tarif: {plan}\n\n"
                f"Tez bog'laning! 🚀"
            )
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            params = urllib.parse.urlencode({'chat_id': chat_id, 'text': msg})
            urllib.request.urlopen(f"{url}?{params}", timeout=5)
        except Exception:
            pass
    return jsonify({'ok': True})


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '')
        user = User.query.filter_by(username=u, is_active=True).first()
        if user and user.check_password(p):
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        flash("Login yoki parol noto'g'ri!", 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ── User Management ───────────────────────────────────────────────────────────
@app.route('/users')
@login_required
def users_list():
    if not current_user.is_admin:
        flash("Bu sahifaga kirish huquqingiz yo'q.", 'danger')
        return redirect(url_for('dashboard'))
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=all_users)


@app.route('/users/add', methods=['POST'])
@login_required
def user_add():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    username  = request.form.get('username', '').strip()
    password  = request.form.get('password', '').strip()
    full_name = request.form.get('full_name', '').strip()
    phone     = request.form.get('phone', '').strip()
    plan      = request.form.get('plan', 'starter')
    if not username or not password:
        flash('Login va parol kiritilishi shart!', 'danger')
        return redirect(url_for('users_list'))
    if User.query.filter_by(username=username).first():
        flash('Bu login allaqachon mavjud!', 'warning')
        return redirect(url_for('users_list'))
    u = User(username=username, full_name=full_name, phone=phone, plan=plan)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    flash(f"Foydalanuvchi '{username}' yaratildi!", 'success')
    return redirect(url_for('users_list'))


@app.route('/users/<int:uid>/toggle', methods=['POST'])
@login_required
def user_toggle(uid):
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    u = db.get_or_404(User, uid)
    if u.is_admin:
        flash("Admin hisobini o'chirish mumkin emas!", 'warning')
    else:
        u.is_active = not u.is_active
        db.session.commit()
        action = 'faollashtirildi' if u.is_active else "o'chirildi"
        flash(f"'{u.username}' {action}.", 'info')
    return redirect(url_for('users_list'))


@app.route('/users/<int:uid>/reset', methods=['POST'])
@login_required
def user_reset(uid):
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    u = db.get_or_404(User, uid)
    new_pass = request.form.get('new_password', '').strip()
    if new_pass:
        u.set_password(new_pass)
        db.session.commit()
        flash(f"'{u.username}' paroli yangilandi.", 'success')
    return redirect(url_for('users_list'))


@app.route('/users/<int:uid>/delete', methods=['POST'])
@login_required
def user_delete(uid):
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    u = db.get_or_404(User, uid)
    if u.is_admin:
        flash("Admin hisobini o'chirib bo'lmaydi!", 'danger')
        return redirect(url_for('users_list'))
    db.session.delete(u)
    db.session.commit()
    flash(f"'{u.username}' o'chirildi.", 'info')
    return redirect(url_for('users_list'))


# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def dashboard():
    total_clients = _cq().count()
    total_orders  = _oq().count()
    total_revenue = _oq().with_entities(func.sum(Order.total_price)).scalar() or 0
    total_commission = round(total_revenue * COMMISSION_PCT / 100, 2)

    since = datetime.utcnow() - timedelta(days=30)
    monthly_revenue = _oq().filter(Order.created_at >= since).with_entities(
        func.sum(Order.total_price)).scalar() or 0
    monthly_commission = round(monthly_revenue * COMMISSION_PCT / 100, 2)

    recent_orders = _oq().order_by(Order.created_at.desc()).limit(8).all()

    monthly_data = []
    for i in range(5, -1, -1):
        d = datetime.utcnow() - timedelta(days=30 * i)
        label = d.strftime('%b %Y')
        start = d.replace(day=1, hour=0, minute=0, second=0)
        end = (start + timedelta(days=32)).replace(day=1)
        total = _oq().filter(Order.created_at >= start, Order.created_at < end).with_entities(
            func.sum(Order.total_price)).scalar() or 0
        monthly_data.append({'label': label, 'total': round(total, 2)})

    statuses = _oq().with_entities(Order.status, func.count(Order.id)).group_by(Order.status).all()
    status_data = {s: c for s, c in statuses}

    top_clients = _cq().join(Order).with_entities(
        Client, func.sum(Order.total_price).label('spent')
    ).group_by(Client.id).order_by(func.sum(Order.total_price).desc()).limit(5).all()

    # Oylik maqsad (default $3000 komissiya)
    MONTHLY_GOAL = 3000
    goal_pct = min(100, round(monthly_commission / MONTHLY_GOAL * 100))

    return render_template('dashboard.html',
        total_clients=total_clients,
        total_orders=total_orders,
        total_revenue=round(total_revenue, 2),
        total_commission=total_commission,
        monthly_revenue=round(monthly_revenue, 2),
        monthly_commission=monthly_commission,
        recent_orders=recent_orders,
        monthly_data=monthly_data,
        status_data=status_data,
        top_clients=top_clients,
        commission_pct=COMMISSION_PCT,
        monthly_goal=MONTHLY_GOAL,
        goal_pct=goal_pct,
    )


# ── Clients ───────────────────────────────────────────────────────────────────
@app.route('/clients')
@login_required
def clients():
    q = request.args.get('q', '').strip()
    query = _cq().order_by(Client.created_at.desc())
    if q:
        query = query.filter(
            Client.full_name.ilike(f'%{q}%') | Client.phone.ilike(f'%{q}%')
        )
    all_clients = query.all()
    return render_template('clients.html', clients=all_clients, q=q)


@app.route('/clients/add', methods=['GET', 'POST'])
@login_required
def client_add():
    if request.method == 'POST':
        from datetime import date as _date
        bday_str = request.form.get('birthday', '').strip()
        c = Client(
            owner_id=current_user.id,
            full_name=request.form['full_name'].strip(),
            phone=request.form.get('phone', '').strip(),
            email=request.form.get('email', '').strip(),
            address=request.form.get('address', '').strip(),
            goal=request.form.get('goal', '').strip(),
            birthday=_date.fromisoformat(bday_str) if bday_str else None,
            weight_start=float(request.form['weight_start']) if request.form.get('weight_start') else None,
            weight_now=float(request.form['weight_now']) if request.form.get('weight_now') else None,
            notes=request.form.get('notes', '').strip(),
        )
        db.session.add(c)
        db.session.commit()
        flash(f'{c.full_name} qo\'shildi!', 'success')
        return redirect(url_for('clients'))
    return render_template('client_form.html', client=None)


@app.route('/clients/<int:cid>/edit', methods=['GET', 'POST'])
@login_required
def client_edit(cid):
    c = _cq().filter_by(id=cid).first_or_404()
    if request.method == 'POST':
        from datetime import date as _date
        bday_str = request.form.get('birthday', '').strip()
        c.full_name    = request.form['full_name'].strip()
        c.phone        = request.form.get('phone', '').strip()
        c.email        = request.form.get('email', '').strip()
        c.address      = request.form.get('address', '').strip()
        c.goal         = request.form.get('goal', '').strip()
        c.birthday     = _date.fromisoformat(bday_str) if bday_str else None
        c.weight_start = float(request.form['weight_start']) if request.form.get('weight_start') else None
        c.weight_now   = float(request.form['weight_now']) if request.form.get('weight_now') else None
        c.notes        = request.form.get('notes', '').strip()
        db.session.commit()
        flash('Ma\'lumotlar yangilandi!', 'success')
        return redirect(url_for('client_detail', cid=cid))
    return render_template('client_form.html', client=c)


@app.route('/clients/<int:cid>')
@login_required
def client_detail(cid):
    c = _cq().filter_by(id=cid).first_or_404()
    orders = Order.query.filter_by(client_id=cid).order_by(Order.created_at.desc()).all()
    weight_logs = WeightLog.query.filter_by(client_id=cid).order_by(WeightLog.date).all()
    return render_template('client_detail.html', client=c, orders=orders,
                           weight_logs=weight_logs, commission_pct=COMMISSION_PCT)


@app.route('/clients/<int:cid>/weight', methods=['POST'])
@login_required
def client_weight_log(cid):
    _cq().filter_by(id=cid).first_or_404()
    w = request.form.get('weight', '').strip()
    note = request.form.get('note', '').strip()
    date_str = request.form.get('date', '').strip()
    if not w:
        flash('Vazn kiritilishi shart!', 'warning')
        return redirect(url_for('client_detail', cid=cid))
    from datetime import date as _date
    log_date = _date.fromisoformat(date_str) if date_str else _date.today()
    log = WeightLog(client_id=cid, weight=float(w), note=note, date=log_date)
    db.session.add(log)
    # Update client's current weight
    c = Client.query.get(cid)
    c.weight_now = float(w)
    db.session.commit()
    flash('Vazn saqlandi!', 'success')
    return redirect(url_for('client_detail', cid=cid))


@app.route('/clients/<int:cid>/telegram', methods=['POST'])
@login_required
def client_telegram(cid):
    c = _cq().filter_by(id=cid).first_or_404()
    msg = request.form.get('message', '').strip()
    if not msg:
        flash('Xabar bo\'sh!', 'warning')
        return redirect(url_for('client_detail', cid=cid))
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id_file = os.path.join(os.path.dirname(__file__), '.chat_id')
    if token and os.path.exists(chat_id_file):
        try:
            import urllib.request, urllib.parse
            chat_id = open(chat_id_file).read().strip()
            full_msg = f"📩 {c.full_name} ga xabar:\n\n{msg}"
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            params = urllib.parse.urlencode({'chat_id': chat_id, 'text': full_msg})
            urllib.request.urlopen(f"{url}?{params}", timeout=5)
            flash('Telegram xabar yuborildi!', 'success')
        except Exception:
            flash('Telegram xabar yuborishda xato!', 'danger')
    else:
        flash('Telegram bot sozlanmagan.', 'warning')
    return redirect(url_for('client_detail', cid=cid))


@app.route('/orders/<int:oid>/invoice')
@login_required
def order_invoice(oid):
    order = Order.query.get_or_404(oid)
    return render_template('invoice.html', order=order, commission_pct=COMMISSION_PCT)


@app.route('/clients/<int:cid>/delete', methods=['POST'])
@login_required
def client_delete(cid):
    c = _cq().filter_by(id=cid).first_or_404()
    name = c.full_name
    db.session.delete(c)
    db.session.commit()
    flash(f'{name} o\'chirildi.', 'info')
    return redirect(url_for('clients'))


# ── Products ──────────────────────────────────────────────────────────────────
DIRECTIONS = [
    ('Снижение веса',        '⚖️'),
    ('Правильное питание',   '🥗'),
    ('Здоровый образ жизни', '💚'),
    ('Красота',              '💄'),
    ('Анти-стресс',          '🧘'),
    ('Долголетие',           '⏳'),
    ('Детокс',               '🌿'),
    ('Иммунитет',            '🛡️'),
    ('Пищеварение',          '🌱'),
    ('Энергия',              '⚡'),
]
VIDI = ['Шоколадные', 'Фруктово-ягодные', 'Нейтральные', 'Напитки', 'Вега']


@app.route('/products')
@login_required
def products():
    cat   = request.args.get('cat', '').strip()
    vid   = request.args.get('vid', '').strip()
    direc = request.args.get('dir', '').strip()
    query = Product.query.order_by(Product.category, Product.name)
    if cat:
        query = query.filter_by(category=cat)
    if vid:
        query = query.filter_by(vid=vid)
    all_products = query.all()
    if direc:
        all_products = [p for p in all_products if direc in (p.direction or '')]
    categories = sorted(set(p.category for p in Product.query.all() if p.category))
    return render_template('products.html',
        products=all_products, categories=categories,
        cat=cat, vid=vid, direc=direc,
        directions=DIRECTIONS, vidi=VIDI,
    )


def _product_from_form(p):
    p.name        = request.form['name'].strip()
    p.category    = request.form.get('category', '').strip()
    p.vid         = request.form.get('vid', '').strip()
    p.direction   = ','.join(request.form.getlist('direction'))
    p.price       = float(request.form.get('price') or 0)
    p.cost_price  = float(request.form.get('cost_price') or 0)
    p.stock       = int(request.form.get('stock') or 0)
    p.description = request.form.get('description', '').strip()
    p.sostav      = request.form.get('sostav', '').strip()
    p.recipe      = request.form.get('recipe', '').strip()
    p.image_url   = request.form.get('image_url', '').strip()
    return p


@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def product_add():
    if request.method == 'POST':
        p = _product_from_form(Product())
        db.session.add(p)
        db.session.commit()
        flash(f'{p.name} mahsulot qo\'shildi!', 'success')
        return redirect(url_for('products'))
    return render_template('product_form.html', product=None,
                           directions=DIRECTIONS, vidi=VIDI)


@app.route('/products/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
def product_edit(pid):
    p = db.get_or_404(Product, pid)
    if request.method == 'POST':
        _product_from_form(p)
        db.session.commit()
        flash('Mahsulot yangilandi!', 'success')
        return redirect(url_for('products'))
    return render_template('product_form.html', product=p,
                           directions=DIRECTIONS, vidi=VIDI)


@app.route('/products/<int:pid>/delete', methods=['POST'])
@login_required
def product_delete(pid):
    p = db.get_or_404(Product, pid)
    db.session.delete(p)
    db.session.commit()
    flash('Mahsulot o\'chirildi.', 'info')
    return redirect(url_for('products'))


# ── Orders ────────────────────────────────────────────────────────────────────
@app.route('/orders')
@login_required
def orders():
    status_f = request.args.get('status', '').strip()
    query = _oq().order_by(Order.created_at.desc())
    if status_f:
        query = query.filter(Order.status == status_f)
    all_orders = query.all()
    return render_template('orders.html', orders=all_orders, status_f=status_f,
                           commission_pct=COMMISSION_PCT)


@app.route('/orders/add', methods=['GET', 'POST'])
@login_required
def order_add():
    clients_list  = _cq().order_by(Client.full_name).all()
    products_list = Product.query.order_by(Product.name).all()
    preset_pid    = request.args.get('pid', type=int)
    if request.method == 'POST':
        cid = int(request.form['client_id'])
        o = Order(
            client_id=cid,
            status=request.form.get('status', 'Yangi'),
            notes=request.form.get('notes', '').strip(),
        )
        db.session.add(o)
        db.session.flush()

        product_ids = request.form.getlist('product_id[]')
        qtys        = request.form.getlist('qty[]')
        prices      = request.form.getlist('unit_price[]')

        for pid, qty, price in zip(product_ids, qtys, prices):
            if not pid or not qty:
                continue
            item = OrderItem(
                order_id=o.id,
                product_id=int(pid),
                qty=int(qty),
                unit_price=float(price),
            )
            db.session.add(item)
            prod = Product.query.get(int(pid))
            if prod:
                prod.stock = max(0, prod.stock - int(qty))

        db.session.flush()
        o.recalc()
        db.session.commit()
        flash('Buyurtma yaratildi!', 'success')
        return redirect(url_for('orders'))
    return render_template('order_form.html', order=None,
                           clients=clients_list, products=products_list,
                           preset_pid=preset_pid)


@app.route('/orders/<int:oid>')
@login_required
def order_detail(oid):
    o = db.get_or_404(Order, oid)
    return render_template('order_detail.html', order=o, commission_pct=COMMISSION_PCT)


@app.route('/orders/<int:oid>/status', methods=['POST'])
@login_required
def order_status(oid):
    o = db.get_or_404(Order, oid)
    new_status = request.form.get('status', o.status)
    if new_status in ('Yangi', "To'langan", 'Yetkazildi', 'Bekor'):
        o.status = new_status
        db.session.commit()
        flash('Status yangilandi!', 'success')
    return redirect(url_for('order_detail', oid=oid))


@app.route('/orders/<int:oid>/delete', methods=['POST'])
@login_required
def order_delete(oid):
    o = db.get_or_404(Order, oid)
    db.session.delete(o)
    db.session.commit()
    flash('Buyurtma o\'chirildi.', 'info')
    return redirect(url_for('orders'))


# ── Napitki & Calculator ──────────────────────────────────────────────────────
@app.route('/napitki')
@login_required
def napitki():
    shakes = Product.query.filter_by(category='Коктейль').order_by(Product.name).all()
    drinks = Product.query.filter_by(category='Напиток').order_by(Product.name).all()

    special_recipes = [
        {
            'name': 'Tropik Yangilovchi',
            'emoji': '🏝',
            'goal': 'Energiya & Detoks',
            'color': '#00897b',
            'ingredients': [
                '2 o\'lchov Formula 1 (Ваниль)',
                '200ml kokos suvi',
                '1/2 mango (muzlatilgan)',
                '1 banan',
                '1 choy qoshiq Алоэ вера',
            ],
            'steps': [
                'Barcha ingredientlarni blenderga soling',
                '60 soniya aralashtiring',
                'Muzli stakanga quying',
                'Mango tilimi bilan bezating',
            ],
            'nutrition': {'Kaloriya': '280 kcal', 'Protein': '18g', 'Yog': '4g', 'Karbo': '38g'},
        },
        {
            'name': 'Protein Quvvat',
            'emoji': '💪',
            'goal': 'Mushak o\'sishi',
            'color': '#1565c0',
            'ingredients': [
                '2 o\'lchov Formula 1 (Шоколад)',
                '1 o\'lchov Протеин',
                '300ml sut (2.5%)',
                '1 osh qoshiq yeryong\'oq yog\'i',
                'Bir hovuch muzli sholi',
            ],
            'steps': [
                'Sut va muz blenderga',
                'Protein va Formula 1 qo\'shing',
                'Yeryong\'oq yog\'ini qo\'shing',
                '45 soniya aralashting',
            ],
            'nutrition': {'Kaloriya': '420 kcal', 'Protein': '42g', 'Yog': '14g', 'Karbo': '28g'},
        },
        {
            'name': 'Yashil Detoks',
            'emoji': '🌿',
            'goal': 'Detoks & Tozalash',
            'color': '#388e3c',
            'ingredients': [
                '2 o\'lchov Formula 1 Vega',
                '1 stakan spinach',
                '1/2 limon sharbati',
                '200ml suv',
                '1 choy qoshiq Алоэ вера konsent.',
            ],
            'steps': [
                'Spinachni blenderga soling',
                'Suv va limon sharbatini qo\'shing',
                'Formula 1 Vega qo\'shing',
                'Bir daqiqa aralashtiring',
            ],
            'nutrition': {'Kaloriya': '190 kcal', 'Protein': '18g', 'Yog': '2g', 'Karbo': '22g'},
        },
        {
            'name': 'Qulupnay Romantik',
            'emoji': '🍓',
            'goal': 'Vazn Kamaytirish',
            'color': '#c62828',
            'ingredients': [
                '2 o\'lchov Formula 1 (Клубника)',
                '200ml suv yoki bodom suvi',
                '100g muzlatilgan qulupnay',
                '1/2 limon sharbati',
                'Bir necha varaq yalpiz',
            ],
            'steps': [
                'Muzlatilgan qulupnayni blenderga',
                'Suv va limon qo\'shing',
                'Formula 1 qo\'shing',
                'Yalpiz bilan bezating',
            ],
            'nutrition': {'Kaloriya': '210 kcal', 'Protein': '17g', 'Yog': '2g', 'Karbo': '30g'},
        },
        {
            'name': 'Kecha & Tong Kokteyil',
            'emoji': '🌙',
            'goal': 'Uyqu & Tiklanish',
            'color': '#4527a0',
            'ingredients': [
                '2 o\'lchov Formula 1 (Ваниль)',
                '250ml iliq sut',
                '1/2 banan',
                '1 choy qoshiq asal',
                'Bir oz darçin',
            ],
            'steps': [
                'Sut va bananni aralashtiring',
                'Formula 1 qo\'shing',
                'Asal va darçin qo\'shing',
                'Yaxshilab ko\'pirtiring',
            ],
            'nutrition': {'Kaloriya': '290 kcal', 'Protein': '19g', 'Yog': '6g', 'Karbo': '36g'},
        },
        {
            'name': 'Enerji Boost',
            'emoji': '⚡',
            'goal': 'Energiya & Sport',
            'color': '#e65100',
            'ingredients': [
                '1 o\'lchov Formula 1 (Шоколад)',
                '1 piyola NRG Чай Лимон',
                '1/2 stakan CR7 Drive',
                '100ml sut',
                'Bir oz muz',
            ],
            'steps': [
                'NRG Чай tayyorlang va sovuting',
                'CR7 bilan aralashtiring',
                'Formula 1 va sut qo\'shing',
                'Muz bilan serve qiling',
            ],
            'nutrition': {'Kaloriya': '240 kcal', 'Protein': '14g', 'Yog': '3g', 'Karbo': '35g'},
        },
    ]

    return render_template('napitki.html',
                           shakes=shakes,
                           drinks=drinks,
                           special_recipes=special_recipes)


@app.route('/calculator')
@login_required
def calculator():
    return render_template('calculator.html')


# ── Reports ───────────────────────────────────────────────────────────────────
@app.route('/reports')
@login_required
def reports():
    # Oylik hisobot
    monthly = []
    for i in range(11, -1, -1):
        d = datetime.utcnow() - timedelta(days=30 * i)
        start = d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=32)).replace(day=1)
        revenue = _oq().filter(
            Order.created_at >= start, Order.created_at < end,
            Order.status != 'Bekor'
        ).with_entities(func.sum(Order.total_price)).scalar() or 0
        count = _oq().filter(
            Order.created_at >= start, Order.created_at < end,
            Order.status != 'Bekor'
        ).count()
        monthly.append({
            'label': start.strftime('%b %Y'),
            'revenue': round(revenue, 2),
            'commission': round(revenue * COMMISSION_PCT / 100, 2),
            'count': count,
        })

    # Top mahsulotlar (filtered by user's orders)
    top_products = _oq().join(OrderItem, Order.id == OrderItem.order_id).join(
        Product, OrderItem.product_id == Product.id
    ).with_entities(
        Product.name,
        func.sum(OrderItem.qty).label('total_qty'),
        func.sum(OrderItem.qty * OrderItem.unit_price).label('total_revenue')
    ).group_by(Product.id).order_by(
        func.sum(OrderItem.qty * OrderItem.unit_price).desc()
    ).limit(10).all()

    # Kategoriya bo'yicha daromad
    cat_revenue = _oq().join(OrderItem, Order.id == OrderItem.order_id).join(
        Product, OrderItem.product_id == Product.id
    ).with_entities(
        Product.category,
        func.sum(OrderItem.qty * OrderItem.unit_price).label('revenue')
    ).group_by(Product.category).all()

    total_revenue = _oq().filter(
        Order.status != 'Bekor'
    ).with_entities(func.sum(Order.total_price)).scalar() or 0

    return render_template('reports.html',
        monthly=monthly,
        top_products=top_products,
        cat_revenue=cat_revenue,
        total_revenue=round(total_revenue, 2),
        total_commission=round(total_revenue * COMMISSION_PCT / 100, 2),
        commission_pct=COMMISSION_PCT,
    )


# ── Reminders / WhatsApp ──────────────────────────────────────────────────────
@app.route('/reminders')
@login_required
def reminders():
    from models import Challenge, ChallengeParticipant
    cutoff_30 = datetime.utcnow() - timedelta(days=30)
    cutoff_60 = datetime.utcnow() - timedelta(days=60)

    all_clients = _cq().all()
    result = []
    for c in all_clients:
        last_order = Order.query.filter_by(client_id=c.id).order_by(Order.created_at.desc()).first()
        if last_order:
            days_ago = (datetime.utcnow() - last_order.created_at).days
        else:
            days_ago = (datetime.utcnow() - c.created_at).days
        if days_ago >= 14:
            result.append({'client': c, 'days_ago': days_ago, 'last_order': last_order})
    result.sort(key=lambda x: x['days_ago'], reverse=True)

    # WhatsApp message templates
    WA_TEMPLATES = [
        {'name': 'Eslatma',
         'text': 'Salom {name}! Herbalife dasturingizni davom ettirishni unutmang. Yangi buyurtma uchun aloqaga chiqing! 🌿'},
        {'name': 'Natijalar so\'rovi',
         'text': 'Salom {name}! Herbalife natijalari qanday? Vaznda o\'zgarish bormi? Yangi retseptlar bor, ulashsam bo\'ladimi? 😊'},
        {'name': 'Maxsus taklif',
         'text': 'Salom {name}! Bu hafta Formula 1 + NRG Чай birgalikda olganlarga maxsus chegirma bor! Qiziqasizmi? 🎁'},
        {'name': 'Challenge taklifi',
         'text': 'Salom {name}! 21 kunlik vazn kamaytirish marafonimiz boshlandi! Ishtirok etmoqchimisiz? Batafsil aytib beraman 🏃'},
    ]

    return render_template('reminders.html', clients=result, templates=WA_TEMPLATES,
                           commission_pct=COMMISSION_PCT)


# ── Challenge / Marafon ────────────────────────────────────────────────────────
@app.route('/challenge')
@login_required
def challenge_list():
    from models import Challenge
    challenges = Challenge.query.order_by(Challenge.start_date.desc()).all()
    all_clients = _cq().order_by(Client.full_name).all()
    import datetime as _dt
    return render_template('challenge.html', challenges=challenges,
                           all_clients=all_clients, now=_dt.datetime.utcnow())


@app.route('/challenge/add', methods=['POST'])
@login_required
def challenge_add():
    from models import Challenge
    import datetime as _dt
    name  = request.form.get('name', '').strip()
    start = request.form.get('start_date', '')
    days  = int(request.form.get('duration_days', 21))
    prize = request.form.get('prize', '').strip()
    desc  = request.form.get('description', '').strip()
    if name and start:
        ch = Challenge(name=name, description=desc,
                       start_date=_dt.date.fromisoformat(start),
                       duration_days=days, prize=prize)
        db.session.add(ch)
        db.session.commit()
        flash('Marafon yaratildi!', 'success')
    return redirect(url_for('challenge_list'))


@app.route('/challenge/<int:cid>/join', methods=['POST'])
@login_required
def challenge_join(cid):
    from models import Challenge, ChallengeParticipant
    ch = db.get_or_404(Challenge, cid)
    client_id    = int(request.form.get('client_id', 0))
    start_weight = float(request.form.get('start_weight', 0) or 0)
    if client_id:
        existing = ChallengeParticipant.query.filter_by(
            challenge_id=cid, client_id=client_id).first()
        if not existing:
            p = ChallengeParticipant(challenge_id=cid, client_id=client_id,
                                     start_weight=start_weight,
                                     current_weight=start_weight)
            db.session.add(p)
            db.session.commit()
            flash('Ishtirokchi qo\'shildi!', 'success')
        else:
            flash('Bu mijoz allaqachon ishtirokchi!', 'warning')
    return redirect(url_for('challenge_list'))


@app.route('/challenge/<int:cid>/update/<int:pid>', methods=['POST'])
@login_required
def challenge_update(cid, pid):
    from models import ChallengeParticipant
    p = db.get_or_404(ChallengeParticipant, pid)
    new_w = float(request.form.get('current_weight', p.current_weight) or p.current_weight)
    p.current_weight = new_w
    db.session.commit()
    flash('Vazn yangilandi!', 'success')
    return redirect(url_for('challenge_list'))


@app.route('/challenge/<int:cid>/delete', methods=['POST'])
@login_required
def challenge_delete(cid):
    from models import Challenge
    ch = db.get_or_404(Challenge, cid)
    db.session.delete(ch)
    db.session.commit()
    flash('Marafon o\'chirildi.', 'info')
    return redirect(url_for('challenge_list'))


# ── Print Catalog ──────────────────────────────────────────────────────────────
@app.route('/catalog')
@login_required
def catalog_print():
    products = Product.query.order_by(Product.category, Product.name).all()
    cats = {}
    for p in products:
        cats.setdefault(p.category or 'Boshqa', []).append(p)
    return render_template('catalog.html', cats=cats)


# ── API ───────────────────────────────────────────────────────────────────────
@app.route('/api/product/<int:pid>')
@login_required
def api_product(pid):
    p = Product.query.get_or_404(pid)
    return jsonify({'id': p.id, 'name': p.name, 'price': p.price, 'stock': p.stock})


@app.route('/api/clients')
@login_required
def api_clients():
    clients_list = _cq().order_by(Client.full_name).all()
    return jsonify([{'id': c.id, 'name': c.full_name} for c in clients_list])


@app.route('/api/search')
@login_required
def api_search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'results': []})
    results = []
    pattern = f'%{q}%'
    for c in _cq().filter(Client.full_name.ilike(pattern)).limit(5).all():
        results.append({'icon': '👤', 'label': c.full_name,
                        'type': 'Mijoz', 'url': f'/clients/{c.id}'})
    for o in Order.query.join(Client).filter(
        (Client.full_name.ilike(pattern)) | (Order.id == q if q.isdigit() else False)
    ).limit(4).all():
        results.append({'icon': '🛒', 'label': f'#{o.id} — {o.client.full_name}',
                        'type': 'Buyurtma', 'url': f'/orders/{o.id}'})
    for p in Product.query.filter(Product.name.ilike(pattern)).limit(4).all():
        results.append({'icon': '📦', 'label': p.name,
                        'type': 'Mahsulot', 'url': f'/products'})
    return jsonify({'results': results[:10]})


if __name__ == '__main__':
    import socket
    with app.app_context():
        db.create_all()

        # Init DB, migrations, and default admin
        _init_db()

        # Generate SVG product images (fallbacks)
        _gen_images()

        # Download real Herbalife product images from CDN
        _download_real_images()

        # Agar eski mahsulotlar bo'lsa — o'chir va yangi to'liq katalog bilan to'ldir
        if Product.query.count() == 0 or not Product.query.filter(Product.vid.isnot(None)).first():
            Product.query.delete()
            db.session.commit()
            IMG = {
                'f1_chok':  'https://i.imgur.com/8K3vZ2Q.png',
                'f1_van':   'https://i.imgur.com/w9Ry5Xk.png',
                'f1_klub':  'https://i.imgur.com/qL7mN1J.png',
                'f1_nut':   'https://i.imgur.com/Tp4KvXm.png',
                'f1_vega':  'https://i.imgur.com/RnGx8WP.png',
                'protein':  'https://i.imgur.com/YkDm6Lc.png',
                'cr7':      'https://i.imgur.com/Hs3xQ9P.png',
                'aloe':     'https://i.imgur.com/Jf2bN8V.png',
                'nrg_lim':  'https://i.imgur.com/Mc5KP7R.png',
                'nrg_mal':  'https://i.imgur.com/Bz9Wx3L.png',
                'multi':    'https://i.imgur.com/Aq7KN2E.png',
                'omega':    'https://i.imgur.com/Xr4Dm8W.png',
                'koll':     'https://i.imgur.com/Tv6Kn9S.png',
                'termo':    'https://i.imgur.com/Np2Kx7Q.png',
                'immun':    'https://i.imgur.com/Gq8Lm5T.png',
                'fiber':    'https://i.imgur.com/Wk3Rv6P.png',
            }
            demo = [
                Product(
                    name='Formula 1 Шоколад', category='Коктейль', vid='Шоколадные',
                    direction='Снижение веса,Правильное питание',
                    price=45, cost_price=33, stock=50,
                    description='Основной заменитель питания — богатый шоколадный вкус',
                    sostav='Соевый белок, какао-порошок, фруктоза, витамины A,C,D,E,B1,B2,B6,B12, кальций, железо, цинк',
                    recipe='2 мерные ложки (26г) на 250мл молока. Взбить блендером 30 сек. Употреблять вместо завтрака или обеда.',
                    image_url='https://placehold.co/400x300/5D4037/FFFFFF?text=Formula+1+%F0%9F%8D«',
                ),
                Product(
                    name='Formula 1 Ваниль', category='Коктейль', vid='Нейтральные',
                    direction='Снижение веса,Правильное питание,Здоровый образ жизни',
                    price=45, cost_price=33, stock=40,
                    description='Классический ванильный коктейль — нежный вкус',
                    sostav='Соевый белок, ваниль, фруктоза, 25 витаминов и минералов',
                    recipe='2 мерные ложки на 250мл молока или воды. Можно добавить банан или ягоды.',
                    image_url='',
                ),
                Product(
                    name='Formula 1 Клубника', category='Коктейль', vid='Фруктово-ягодные',
                    direction='Снижение веса,Правильное питание',
                    price=45, cost_price=33, stock=35,
                    description='Клубничный коктейль с ярким ягодным вкусом',
                    sostav='Соевый белок, натуральный клубничный ароматизатор, витаминный комплекс',
                    recipe='2 ложки + 250мл молока. Добавьте свежую клубнику для усиления вкуса.',
                    image_url='',
                ),
                Product(
                    name='Formula 1 Лесной Орех', category='Коктейль', vid='Нейтральные',
                    direction='Снижение веса,Правильное питание',
                    price=47, cost_price=34, stock=30,
                    description='Коктейль со вкусом дикого лесного ореха',
                    sostav='Соевый белок, ореховый ароматизатор, 21 витамин и минерал, клетчатка',
                    recipe='2 ложки на 250мл молока. Подавать охлаждённым.',
                    image_url='',
                ),
                Product(
                    name='Formula 1 Vega', category='Коктейль', vid='Вега',
                    direction='Снижение веса,Правильное питание,Здоровый образ жизни',
                    price=52, cost_price=38, stock=25,
                    description='Растительный коктейль — без молочных продуктов и глютена',
                    sostav='Растительный белок (горох+рис), куркума, инулин из цикория, B12, D3',
                    recipe='2 ложки на 250мл растительного молока (миндальное, овсяное). Взбить блендером.',
                    image_url='',
                ),
                Product(
                    name='Протеиновый Коктейль', category='Коктейль', vid='Нейтральные',
                    direction='Правильное питание,Энергия,Здоровый образ жизни',
                    price=38, cost_price=27, stock=60,
                    description='Высокобелковый коктейль для поддержания мышечной массы',
                    sostav='Сывороточный белок 24г, BCAA, L-глютамин, витамины группы B',
                    recipe='1-2 мерные ложки на 200мл воды или молока после тренировки.',
                    image_url='',
                ),
                Product(
                    name='CR7 Drive', category='Напиток', vid='Напитки',
                    direction='Энергия,Здоровый образ жизни',
                    price=32, cost_price=23, stock=45,
                    description='Изотоник Криштиану Роналду — апельсиновый вкус',
                    sostav='Электролиты (натрий, калий, магний), витамин C, B6, ниацин, углеводы',
                    recipe='Смешать 1 мерную ложку с 500мл воды. Пить во время тренировки.',
                    image_url='',
                ),
                Product(
                    name='Алоэ Вера Концентрат', category='Напиток', vid='Напитки',
                    direction='Детокс,Пищеварение,Здоровый образ жизни',
                    price=28, cost_price=19, stock=30,
                    description='Концентрат алоэ для здоровья пищеварения',
                    sostav='Сок алоэ вера 97%, мёд, лимонный сок, натуральные ароматизаторы',
                    recipe='30мл концентрата на 1 стакан воды. Принимать утром до еды.',
                    image_url='',
                ),
                Product(
                    name='Чай НРГ Лимон-Имбирь', category='Напиток', vid='Напитки',
                    direction='Энергия,Детокс,Снижение веса',
                    price=20, cost_price=13, stock=55,
                    description='Мгновенный чай с зелёным чаем и женьшенем',
                    sostav='Зелёный чай, женьшень, экстракт имбиря, лимонный аромат, кофеин 85мг',
                    recipe='½ ч.л. на 200мл горячей воды. Можно холодным — добавить лёд.',
                    image_url='',
                ),
                Product(
                    name='Чай НРГ Малина', category='Напиток', vid='Фруктово-ягодные',
                    direction='Энергия,Детокс,Снижение веса',
                    price=20, cost_price=13, stock=50,
                    description='Малиновый чай с бодрящим эффектом',
                    sostav='Зелёный чай, малиновый ароматизатор, женьшень, кофеин 85мг',
                    recipe='½ ч.л. на стакан горячей или холодной воды.',
                    image_url='',
                ),
                Product(
                    name='Formula 2 Мультивитамины', category='Витамины', vid='Нейтральные',
                    direction='Здоровый образ жизни,Иммунитет,Долголетие',
                    price=22, cost_price=15, stock=80,
                    description='Ежедневный витаминно-минеральный комплекс',
                    sostav='Витамины A,C,D,E,B-комплекс, кальций, железо, цинк, магний, хром',
                    recipe='1 таблетка в день во время еды. Курс 1-3 месяца.',
                    image_url='',
                ),
                Product(
                    name='Омега-3', category='Витамины', vid='Нейтральные',
                    direction='Здоровый образ жизни,Долголетие,Иммунитет,Красота',
                    price=30, cost_price=21, stock=45,
                    description='Рыбий жир высокой степени очистки — EPA+DHA',
                    sostav='Рыбий жир EPA 180мг, DHA 120мг, витамин E',
                    recipe='1 капсула 3 раза в день во время еды.',
                    image_url='',
                ),
                Product(
                    name='Skin Коллаген', category='Красота', vid='Нейтральные',
                    direction='Красота,Долголетие,Анти-стресс',
                    price=55, cost_price=38, stock=25,
                    description='Морской коллаген для кожи, волос и ногтей',
                    sostav='Морской коллаген 5000мг, гиалуроновая кислота, витамин C, биотин',
                    recipe='1 саше растворить в стакане воды. Принимать утром натощак.',
                    image_url='',
                ),
                Product(
                    name='Термо Комплит', category='Витамины', vid='Нейтральные',
                    direction='Снижение веса,Энергия',
                    price=35, cost_price=24, stock=35,
                    description='Термогенный комплекс для активного снижения веса',
                    sostav='Экстракт зелёного чая, кофеин, L-карнитин, хром, витамин B6',
                    recipe='1 таблетка 2 раза в день во время еды. Не принимать вечером.',
                    image_url='',
                ),
                Product(
                    name='Иммью Буст', category='Витамины', vid='Нейтральные',
                    direction='Иммунитет,Здоровый образ жизни,Анти-стресс',
                    price=28, cost_price=19, stock=40,
                    description='Комплекс для укрепления иммунитета',
                    sostav='Витамин C 1000мг, цинк, витамин D3, эхинацея, бузина',
                    recipe='1 таблетка в день. В период простуды 2 таблетки.',
                    image_url='',
                ),
                Product(
                    name='Активная Клетчатка', category='Добавки', vid='Нейтральные',
                    direction='Пищеварение,Детокс,Снижение веса',
                    price=25, cost_price=17, stock=60,
                    description='Растворимая клетчатка для здоровья кишечника',
                    sostav='Гуаровая камедь, пектин яблока, инулин, пробиотики 1 млрд КОЕ',
                    recipe='1 мерная ложка на стакан воды 2-3 раза в день до еды.',
                    image_url='',
                ),
            ]
            for p in demo:
                db.session.add(p)
            db.session.commit()
            print(f'Katalog: {len(demo)} ta mahsulot qo\'shildi!')

        # CDN URL larini to'g'ridan-to'g'ri bazaga yozamiz
        updated = 0
        for prod in Product.query.all():
            cdn_url = PRODUCT_CDN_IMAGES.get(prod.name)
            if cdn_url and prod.image_url != cdn_url:
                prod.image_url = cdn_url
                updated += 1
        if updated:
            db.session.commit()
            print(f'[images] {updated} ta mahsulotga CDN rasm biriktirildi.')

    env_port = os.environ.get('PORT')
    if env_port:
        port = int(env_port)
    else:
        port = 5000
        for p in range(5000, 5010):
            s = socket.socket()
            s.settimeout(0.2)
            in_use = s.connect_ex(('127.0.0.1', p)) == 0
            s.close()
            if not in_use:
                port = p
                break

    print(f'\n  Herbalife CRM: http://127.0.0.1:{port}')
    print(f'  Login: admin  |  Parol: herbalife123\n')
    host = '0.0.0.0' if env_port else '127.0.0.1'
    app.run(debug=not env_port, port=port, host=host)
