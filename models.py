# -*- coding: utf-8 -*-
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name     = db.Column(db.String(120), default='')
    phone         = db.Column(db.String(30), default='')
    plan          = db.Column(db.String(20), default='starter')  # starter / pro / team
    is_admin      = db.Column(db.Boolean, default=False)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def plan_label(self):
        return {'starter': '🌱 Starter', 'pro': '⭐ Pro', 'team': '🚀 Team'}.get(self.plan, self.plan)


class Client(db.Model):
    __tablename__ = 'clients'
    id            = db.Column(db.Integer, primary_key=True)
    owner_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    full_name     = db.Column(db.String(120), nullable=False)
    phone         = db.Column(db.String(30))
    email         = db.Column(db.String(120))
    address       = db.Column(db.String(200))
    goal          = db.Column(db.String(200))
    birthday      = db.Column(db.Date, nullable=True)
    weight_start  = db.Column(db.Float)
    weight_now    = db.Column(db.Float)
    notes         = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    orders        = db.relationship('Order', backref='client', lazy=True, cascade='all, delete-orphan')
    weight_logs   = db.relationship('WeightLog', backref='client', lazy=True, cascade='all, delete-orphan')

    def total_spent(self):
        return sum(o.total_price for o in self.orders)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'goal': self.goal,
            'weight_start': self.weight_start,
            'weight_now': self.weight_now,
            'orders_count': len(self.orders),
            'total_spent': self.total_spent(),
            'created_at': self.created_at.strftime('%d.%m.%Y'),
        }


class Product(db.Model):
    __tablename__ = 'products'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    category    = db.Column(db.String(80))
    vid         = db.Column(db.String(80))       # Шоколадные / Фруктово-ягодные / Нейтральные / Напитки / Вега
    direction   = db.Column(db.Text)             # comma-separated: Снижение веса,Энергия,...
    price       = db.Column(db.Float, default=0)
    cost_price  = db.Column(db.Float, default=0)
    stock       = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    sostav      = db.Column(db.Text)
    recipe      = db.Column(db.Text)
    image_url   = db.Column(db.String(500))
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def profit_margin(self):
        if self.price > 0:
            return round((self.price - self.cost_price) / self.price * 100, 1)
        return 0

    def directions_list(self):
        if self.direction:
            return [d.strip() for d in self.direction.split(',') if d.strip()]
        return []


class Order(db.Model):
    __tablename__ = 'orders'
    id          = db.Column(db.Integer, primary_key=True)
    client_id   = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    status      = db.Column(db.String(30), default='Yangi')   # Yangi, To\'langan, Yetkazildi
    notes       = db.Column(db.Text)
    total_price = db.Column(db.Float, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    items       = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def recalc(self):
        self.total_price = sum(i.qty * i.unit_price for i in self.items)

    def commission(self, pct=25):
        return round(self.total_price * pct / 100, 2)


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    qty        = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0)


class WeightLog(db.Model):
    __tablename__ = 'weight_logs'
    id         = db.Column(db.Integer, primary_key=True)
    client_id  = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    date       = db.Column(db.Date, default=datetime.utcnow)
    weight     = db.Column(db.Float, nullable=False)
    note       = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Challenge(db.Model):
    __tablename__ = 'challenges'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text)
    start_date    = db.Column(db.Date, nullable=False)
    duration_days = db.Column(db.Integer, default=21)
    prize         = db.Column(db.String(200))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    participants  = db.relationship('ChallengeParticipant', backref='challenge', lazy=True,
                                    cascade='all, delete-orphan')

    def days_left(self):
        from datetime import date
        end = self.start_date + __import__('datetime').timedelta(days=self.duration_days)
        delta = (end - date.today()).days
        return max(0, delta)

    def is_active(self):
        from datetime import date
        import datetime as _dt
        end = self.start_date + _dt.timedelta(days=self.duration_days)
        return self.start_date <= date.today() <= end


class ChallengeParticipant(db.Model):
    __tablename__ = 'challenge_participants'
    id            = db.Column(db.Integer, primary_key=True)
    challenge_id  = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    client_id     = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    start_weight  = db.Column(db.Float)
    current_weight= db.Column(db.Float)
    joined_at     = db.Column(db.DateTime, default=datetime.utcnow)
    client        = db.relationship('Client', backref='challenges', lazy=True)

    def lost_kg(self):
        if self.start_weight and self.current_weight:
            return round(self.start_weight - self.current_weight, 1)
        return 0.0
