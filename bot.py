# -*- coding: utf-8 -*-
"""
Herbalife CRM — Telegram Bot
Ishga tushirish: python bot.py
Token: @BotFather dan oling va TOKEN o'zgaruvchisiga yozing
"""
import os
import asyncio
import logging
from datetime import datetime, timedelta, time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

from flask import Flask
from models import db, Client, Order, Product, OrderItem
from sqlalchemy import func

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# ── Config ────────────────────────────────────────────────────────────────────
TOKEN          = os.environ.get('TELEGRAM_BOT_TOKEN', '')
COMMISSION_PCT = 25
MONTHLY_GOAL   = 3000

# ── Flask app faqat DB uchun ─────────────────────────────────────────────────
_flask = Flask(__name__)
_flask.config.update(
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(os.path.dirname(__file__), 'herbalife.db')}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='bot-only',
)
db.init_app(_flask)


def ctx():
    return _flask.app_context()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _goal_bar(pct: float) -> str:
    filled = int(min(pct, 100) / 10)
    return '🟩' * filled + '⬜' * (10 - filled)


def _status_emoji(status: str) -> str:
    return {'Yangi': '🆕', "To'langan": '✅', 'Yetkazildi': '📦', 'Bekor': '❌'}.get(status, '❓')


def _wa_link(phone: str, text: str) -> str:
    import urllib.parse
    clean = ''.join(c for c in phone if c.isdigit() or c == '+')
    return f"https://wa.me/{clean}?text={urllib.parse.quote(text)}"


# ── /start ────────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save chat_id so we can send files
    chat_id = update.effective_chat.id
    id_file = os.path.join(os.path.dirname(__file__), '.chat_id')
    with open(id_file, 'w') as f:
        f.write(str(chat_id))

    text = (
        "🌿 *Herbalife CRM Bot*\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        "Salom! Men sizning distribyutor assistentingizman 💚\n\n"
        "*📌 Buyruqlar:*\n"
        "📊 /stats — Bugungi statistika\n"
        "🎯 /maqsad — $3000 oylik maqsad\n"
        "🔔 /eslatmalar — Eslatma kerak mijozlar\n"
        "👥 /mijozlar — Barcha mijozlar\n"
        "🛒 /buyurtmalar — So'nggi buyurtmalar\n"
        "🏆 /top — Top 5 mijoz\n"
        "💊 /mahsulotlar — Mahsulotlar soni\n\n"
        "🌿 _Herbalife CRM — Doim yoningizda!_"
    )
    kb = [[
        InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        InlineKeyboardButton("🎯 Maqsad", callback_data="maqsad"),
    ], [
        InlineKeyboardButton("🔔 Eslatmalar", callback_data="eslatmalar"),
        InlineKeyboardButton("👥 Mijozlar", callback_data="mijozlar"),
    ]]
    await update.message.reply_text(text, parse_mode='Markdown',
                                    reply_markup=InlineKeyboardMarkup(kb))


# ── /stats ────────────────────────────────────────────────────────────────────
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with ctx():
        total_clients  = Client.query.count()
        total_orders   = Order.query.count()
        total_revenue  = db.session.query(func.sum(Order.total_price)).scalar() or 0

        since = datetime.utcnow() - timedelta(days=30)
        m_rev = db.session.query(func.sum(Order.total_price)).filter(
            Order.created_at >= since).scalar() or 0
        m_com = round(m_rev * COMMISSION_PCT / 100, 2)

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        today_orders = Order.query.filter(Order.created_at >= today_start).count()
        today_rev = db.session.query(func.sum(Order.total_price)).filter(
            Order.created_at >= today_start).scalar() or 0

        goal_pct = min(100, round(m_com / MONTHLY_GOAL * 100, 1))
        bar = _goal_bar(goal_pct)

    text = (
        f"📊 *Statistika*\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"👥 Jami mijozlar: *{total_clients}*\n"
        f"🛒 Jami buyurtmalar: *{total_orders}*\n"
        f"💰 Jami daromad: *${total_revenue:,.2f}*\n\n"
        f"📅 *Bugun:*\n"
        f"🆕 Yangi buyurtmalar: *{today_orders}*\n"
        f"💵 Bugungi savdo: *${today_rev:,.2f}*\n\n"
        f"📆 *So'nggi 30 kun:*\n"
        f"💵 Savdo: *${m_rev:,.2f}*\n"
        f"💚 Komissiya (25%): *${m_com:,.2f}*\n\n"
        f"🎯 *Oylik maqsad: ${MONTHLY_GOAL}*\n"
        f"{bar}\n"
        f"*{goal_pct}%* bajarildi"
    )
    kb = [[InlineKeyboardButton("🔄 Yangilash", callback_data="stats")]]
    msg = update.message or update.callback_query.message
    await msg.reply_text(text, parse_mode='Markdown',
                         reply_markup=InlineKeyboardMarkup(kb))


# ── /maqsad ───────────────────────────────────────────────────────────────────
async def cmd_maqsad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with ctx():
        since = datetime.utcnow() - timedelta(days=30)
        m_rev = db.session.query(func.sum(Order.total_price)).filter(
            Order.created_at >= since).scalar() or 0
        m_com = round(m_rev * COMMISSION_PCT / 100, 2)
        remaining = max(0, MONTHLY_GOAL - m_com)
        goal_pct  = min(100, round(m_com / MONTHLY_GOAL * 100, 1))
        bar = _goal_bar(goal_pct)

        # Oyning qancha kuni qolgan
        now = datetime.utcnow()
        next_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1)
        days_left = (next_month - now).days

    if goal_pct >= 100:
        status_line = "🏆 *MAQSADGA ETDINGIZ! BARAKALLA!*"
    elif goal_pct >= 60:
        status_line = f"💪 Yaxshi ketayapti! Yana *${remaining:,.2f}* kerak"
    else:
        status_line = f"⚡ Harakatlaning! Yana *${remaining:,.2f}* kerak"

    text = (
        f"🎯 *Oylik Maqsad Kuzatuvi*\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Maqsad: *${MONTHLY_GOAL:,}* / oy\n"
        f"✅ Hozir: *${m_com:,.2f}*\n"
        f"📅 Oyda *{days_left}* kun qoldi\n\n"
        f"{bar}\n"
        f"*{goal_pct}%* bajarildi\n\n"
        f"{status_line}\n\n"
        f"💡 _Komissiya: 25% har buyurtmadan_"
    )
    msg = update.message or update.callback_query.message
    await msg.reply_text(text, parse_mode='Markdown')


# ── /eslatmalar ───────────────────────────────────────────────────────────────
async def cmd_eslatmalar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with ctx():
        all_clients = Client.query.all()
        result = []
        for c in all_clients:
            last = Order.query.filter_by(client_id=c.id).order_by(
                Order.created_at.desc()).first()
            ref_date = last.created_at if last else c.created_at
            days = (datetime.utcnow() - ref_date).days
            if days >= 14:
                result.append((c, days, last))
        result.sort(key=lambda x: x[1], reverse=True)

    if not result:
        msg = update.message or update.callback_query.message
        await msg.reply_text("✅ Hamma mijozlar faol! Eslatma kerak emas.")
        return

    lines = [
        f"🔔 *Eslatma kerak mijozlar* ({len(result)} ta)\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    ]
    wa_template = "Salom {name}! Herbalife dasturingizni davom ettirishni unutmang. Yangi buyurtma uchun aloqaga chiqing! 🌿"

    for c, days, last in result[:15]:
        if days >= 60:
            icon = '🔴'
        elif days >= 30:
            icon = '🟡'
        else:
            icon = '🟢'

        line = f"{icon} *{c.full_name}* — {days} kun\n"
        if c.phone:
            import urllib.parse
            txt = wa_template.replace('{name}', c.full_name)
            wa = f"https://wa.me/{c.phone.replace('+','').replace(' ','')}?text={urllib.parse.quote(txt)}"
            line += f"   📱 {c.phone} | [WhatsApp]({wa})\n"
        lines.append(line)

    if len(result) > 15:
        lines.append(f"\n_...va yana {len(result)-15} ta mijoz_")

    lines.append("\n🔴 60+ kun  🟡 30-60 kun  🟢 14-30 kun")

    msg = update.message or update.callback_query.message
    await msg.reply_text('\n'.join(lines), parse_mode='Markdown',
                         disable_web_page_preview=True)


# ── /mijozlar ─────────────────────────────────────────────────────────────────
async def cmd_mijozlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with ctx():
        clients = Client.query.order_by(Client.created_at.desc()).limit(20).all()
        total   = Client.query.count()

    if not clients:
        await (update.message or update.callback_query.message).reply_text(
            "👥 Hali mijoz yo'q.")
        return

    lines = [f"👥 *Mijozlar* (jami {total} ta, so'nggi 20)\n━━━━━━━━━━━━━\n"]
    for i, c in enumerate(clients, 1):
        spent = c.total_spent()
        goal_icon = f" | 🎯 {c.goal[:20]}..." if c.goal and len(c.goal) > 20 else (f" | 🎯 {c.goal}" if c.goal else "")
        phone_str = f"\n   📱 {c.phone}" if c.phone else ""
        lines.append(
            f"{i}. *{c.full_name}*{goal_icon}\n"
            f"   💰 ${spent:.2f} | 🛒 {len(c.orders)} ta buyurtma{phone_str}\n"
        )

    msg = update.message or update.callback_query.message
    await msg.reply_text('\n'.join(lines), parse_mode='Markdown')


# ── /buyurtmalar ──────────────────────────────────────────────────────────────
async def cmd_buyurtmalar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with ctx():
        orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        total  = Order.query.count()

    if not orders:
        await (update.message or update.callback_query.message).reply_text(
            "🛒 Hali buyurtma yo'q.")
        return

    lines = [f"🛒 *So'nggi Buyurtmalar* (jami {total})\n━━━━━━━━━━━━━━━\n"]
    for o in orders:
        st = _status_emoji(o.status)
        date_str = o.created_at.strftime('%d.%m.%Y %H:%M')
        commission = round(o.total_price * COMMISSION_PCT / 100, 2)
        lines.append(
            f"{st} *#{o.id}* — {o.client.full_name}\n"
            f"   💵 ${o.total_price:.2f} | 💚 ${commission:.2f} | 📅 {date_str}\n"
        )

    msg = update.message or update.callback_query.message
    await msg.reply_text('\n'.join(lines), parse_mode='Markdown')


# ── /top ──────────────────────────────────────────────────────────────────────
async def cmd_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with ctx():
        top = db.session.query(
            Client, func.sum(Order.total_price).label('spent')
        ).join(Order).group_by(Client.id).order_by(
            func.sum(Order.total_price).desc()
        ).limit(5).all()

    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
    lines = ["🏆 *Top 5 Mijoz*\n━━━━━━━━━━━━\n"]
    for i, (c, spent) in enumerate(top):
        commission = round(spent * COMMISSION_PCT / 100, 2)
        lines.append(
            f"{medals[i]} *{c.full_name}*\n"
            f"   💰 ${spent:.2f} | 💚 ${commission:.2f} | 🛒 {len(c.orders)} ta\n"
        )

    if not top:
        lines = ["🏆 Hali buyurtma yo'q."]

    await (update.message or update.callback_query.message).reply_text(
        '\n'.join(lines), parse_mode='Markdown')


# ── /mahsulotlar ──────────────────────────────────────────────────────────────
async def cmd_mahsulotlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with ctx():
        total = Product.query.count()
        by_cat = db.session.query(
            Product.category, func.count(Product.id)
        ).group_by(Product.category).all()

        top_sold = db.session.query(
            Product.name,
            func.sum(OrderItem.qty).label('qty')
        ).join(OrderItem).group_by(Product.id).order_by(
            func.sum(OrderItem.qty).desc()
        ).limit(5).all()

    lines = [f"💊 *Mahsulotlar* (jami {total} ta)\n━━━━━━━━━━━━━━\n"]
    cat_icons = {'Коктейль': '🥤', 'Напиток': '🍃', 'Витамины': '💊', 'Красота': '✨', 'Добавки': '🌿'}
    for cat, cnt in by_cat:
        icon = cat_icons.get(cat, '📦')
        lines.append(f"{icon} {cat}: *{cnt}* ta")

    if top_sold:
        lines.append("\n🔥 *Eng ko'p sotilganlar:*")
        medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
        for i, (name, qty) in enumerate(top_sold):
            lines.append(f"{medals[i]} {name} — *{qty}* ta")

    await (update.message or update.callback_query.message).reply_text(
        '\n'.join(lines), parse_mode='Markdown')


# ── Callback handler (inline buttons) ────────────────────────────────────────
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == 'stats':
        await cmd_stats(update, context)
    elif data == 'maqsad':
        await cmd_maqsad(update, context)
    elif data == 'eslatmalar':
        await cmd_eslatmalar(update, context)
    elif data == 'mijozlar':
        await cmd_mijozlar(update, context)


# ── Kunlik eslatma (har kuni 09:00) ──────────────────────────────────────────
async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    with ctx():
        all_clients = Client.query.all()
        urgent = []
        for c in all_clients:
            last = Order.query.filter_by(client_id=c.id).order_by(
                Order.created_at.desc()).first()
            ref = last.created_at if last else c.created_at
            days = (datetime.utcnow() - ref).days
            if days >= 30:
                urgent.append((c, days))
        urgent.sort(key=lambda x: x[1], reverse=True)

        since = datetime.utcnow() - timedelta(days=30)
        m_rev = db.session.query(func.sum(Order.total_price)).filter(
            Order.created_at >= since).scalar() or 0
        m_com = round(m_rev * COMMISSION_PCT / 100, 2)
        goal_pct = min(100, round(m_com / MONTHLY_GOAL * 100, 1))

    lines = [
        f"☀️ *Xayrli tong! Bugungi holat:*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🎯 Oylik maqsad: *{goal_pct}%* ({_goal_bar(goal_pct)})\n"
        f"💚 Komissiya: *${m_com:,.2f}* / ${MONTHLY_GOAL}\n"
    ]

    if urgent:
        lines.append(f"\n🔔 *{len(urgent)} ta mijozga eslatma kerak:*")
        import urllib.parse
        wa_txt = "Salom {name}! Herbalife dasturingizni davom ettirishni unutmang 🌿"
        for c, days in urgent[:5]:
            icon = '🔴' if days >= 60 else '🟡'
            line = f"{icon} {c.full_name} ({days} kun)"
            if c.phone:
                txt = wa_txt.replace('{name}', c.full_name)
                wa = f"https://wa.me/{c.phone.replace('+','').replace(' ','')}?text={urllib.parse.quote(txt)}"
                line += f" — [WhatsApp]({wa})"
            lines.append(line)
        if len(urgent) > 5:
            lines.append(f"_...va yana {len(urgent)-5} ta_")
    else:
        lines.append("\n✅ Barcha mijozlar faol!")

    lines.append("\n_/stats batafsil statistika uchun_")
    await context.bot.send_message(chat_id=chat_id, text='\n'.join(lines),
                                   parse_mode='Markdown',
                                   disable_web_page_preview=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not TOKEN:
        print("\n" + "="*50)
        print("  TELEGRAM_BOT_TOKEN topilmadi!")
        print("  1. @BotFather da /newbot buyrug'ini yuboring")
        print("  2. Tokenni nusxalang")
        print("  3. Quyidagicha ishga tushiring:")
        print("     set TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE")
        print("     python bot.py")
        print("="*50 + "\n")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start',       cmd_start))
    app.add_handler(CommandHandler('stats',       cmd_stats))
    app.add_handler(CommandHandler('maqsad',      cmd_maqsad))
    app.add_handler(CommandHandler('eslatmalar',  cmd_eslatmalar))
    app.add_handler(CommandHandler('mijozlar',    cmd_mijozlar))
    app.add_handler(CommandHandler('buyurtmalar', cmd_buyurtmalar))
    app.add_handler(CommandHandler('top',         cmd_top))
    app.add_handler(CommandHandler('mahsulotlar', cmd_mahsulotlar))
    app.add_handler(CallbackQueryHandler(on_callback))

    # Kunlik eslatma — foydalanuvchi chat_id sini birinchi /start dan olganida
    # Har kuni soat 09:00 da yuborish uchun quyidagi qatorni aktiv qiling:
    # app.job_queue.run_daily(daily_reminder, time=time(9, 0), data=YOUR_CHAT_ID)

    print("\n" + "="*50)
    print("  🌿 Herbalife CRM Bot ishga tushdi!")
    print("  Telegram-da botingizni toping va /start yuboring")
    print("="*50 + "\n")

    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
