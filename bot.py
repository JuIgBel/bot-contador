import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)
from database.db import init_db
from handlers.gastos import (
    agregar_gasto, listar_gastos, exportar_excel,
    ESPERANDO_GASTO, ESPERANDO_CATEGORIA, ESPERANDO_MONTO
)
from handlers.facturas import (
    agregar_factura, listar_facturas,
    ESPERANDO_FACTURA, ESPERANDO_VENCIMIENTO, ESPERANDO_MONTO_FACTURA
)
from handlers.recordatorios import verificar_vencimientos
from handlers.ia import consulta_ia
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "TU_TOKEN_AQUI")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("💰 Agregar Gasto", callback_data="agregar_gasto"),
         InlineKeyboardButton("📋 Ver Gastos", callback_data="ver_gastos")],
        [InlineKeyboardButton("🧾 Agregar Factura", callback_data="agregar_factura"),
         InlineKeyboardButton("📅 Ver Facturas", callback_data="ver_facturas")],
        [InlineKeyboardButton("📊 Exportar Excel", callback_data="exportar_excel"),
         InlineKeyboardButton("📈 Resumen Mensual", callback_data="resumen")],
        [InlineKeyboardButton("🤖 Asesor IA", callback_data="asesor_ia")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 ¡Hola {user.first_name}!\n\n"
        f"Soy tu *Contador Virtual* 🧮\n\n"
        f"Puedo ayudarte a:\n"
        f"• 💰 Registrar y controlar tus gastos\n"
        f"• 🧾 Gestionar facturas y vencimientos\n"
        f"• 📊 Exportar reportes en Excel\n"
        f"• 📈 Asesorarte en inversiones con IA\n\n"
        f"¿Qué querés hacer hoy?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Agregar Gasto", callback_data="agregar_gasto"),
         InlineKeyboardButton("📋 Ver Gastos", callback_data="ver_gastos")],
        [InlineKeyboardButton("🧾 Agregar Factura", callback_data="agregar_factura"),
         InlineKeyboardButton("📅 Ver Facturas", callback_data="ver_facturas")],
        [InlineKeyboardButton("📊 Exportar Excel", callback_data="exportar_excel"),
         InlineKeyboardButton("📈 Resumen Mensual", callback_data="resumen")],
        [InlineKeyboardButton("🤖 Asesor IA", callback_data="asesor_ia")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📌 *Menú Principal*", parse_mode='Markdown', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "agregar_gasto":
        await query.message.reply_text(
            "💰 *Nuevo Gasto*\n\nEscribí el nombre del gasto (ej: `Supermercado`):",
            parse_mode='Markdown'
        )
        context.user_data['estado'] = ESPERANDO_GASTO
    elif data == "ver_gastos":
        await listar_gastos(update, context, via_callback=True)
    elif data == "agregar_factura":
        await query.message.reply_text(
            "🧾 *Nueva Factura*\n\nEscribí el nombre del servicio (ej: `Luz`, `Internet`):",
            parse_mode='Markdown'
        )
        context.user_data['estado'] = ESPERANDO_FACTURA
    elif data == "ver_facturas":
        await listar_facturas(update, context, via_callback=True)
    elif data == "exportar_excel":
        await exportar_excel(update, context, via_callback=True)
    elif data == "resumen":
        await resumen_mensual(update, context, via_callback=True)
    elif data == "asesor_ia":
        await query.message.reply_text(
            "🤖 *Asesor Financiero IA*\n\n"
            "Haceme cualquier consulta sobre:\n"
            "• 📈 Bolsa de valores\n"
            "• 💎 Criptomonedas\n"
            "• 💵 Inversiones\n"
            "• 💡 Consejos financieros\n\n"
            "Escribí tu pregunta:",
            parse_mode='Markdown'
        )
        context.user_data['estado'] = 'esperando_consulta_ia'

async def resumen_mensual(update: Update, context: ContextTypes.DEFAULT_TYPE, via_callback=False):
    from database.db import get_resumen_mensual
    user_id = update.effective_user.id
    resumen = get_resumen_mensual(user_id)
    
    texto = "📈 *Resumen del Mes*\n\n"
    if resumen['gastos']:
        texto += "💰 *Gastos por categoría:*\n"
        for cat, total in resumen['gastos'].items():
            texto += f"  • {cat}: ${total:,.2f}\n"
        texto += f"\n💵 *Total Gastos: ${resumen['total_gastos']:,.2f}*\n"
    else:
        texto += "No hay gastos registrados este mes.\n"
    
    if resumen['facturas_pendientes'] > 0:
        texto += f"\n⚠️ *Facturas pendientes: {resumen['facturas_pendientes']}*"
    
    if via_callback:
        await update.callback_query.message.reply_text(texto, parse_mode='Markdown')
    else:
        await update.message.reply_text(texto, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estado = context.user_data.get('estado')
    
    if estado == ESPERANDO_GASTO:
        await agregar_gasto(update, context)
    elif estado == ESPERANDO_CATEGORIA:
        await agregar_gasto(update, context)
    elif estado == ESPERANDO_MONTO:
        await agregar_gasto(update, context)
    elif estado == ESPERANDO_FACTURA:
        await agregar_factura(update, context)
    elif estado == ESPERANDO_VENCIMIENTO:
        await agregar_factura(update, context)
    elif estado == ESPERANDO_MONTO_FACTURA:
        await agregar_factura(update, context)
    elif estado == 'esperando_consulta_ia':
        await consulta_ia(update, context)
    else:
        await update.message.reply_text(
            "No entendí ese mensaje 😅\nUsá /menu para ver las opciones disponibles."
        )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Comandos disponibles:*\n\n"
        "/start - Iniciar el bot\n"
        "/menu - Ver menú principal\n"
        "/gastos - Ver mis gastos\n"
        "/facturas - Ver mis facturas\n"
        "/excel - Exportar a Excel\n"
        "/resumen - Resumen mensual\n"
        "/ia - Consultar al asesor IA\n"
        "/ayuda - Ver esta ayuda",
        parse_mode='Markdown'
    )

def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Scheduler para recordatorios diarios
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        verificar_vencimientos,
        'cron',
        hour=9,
        minute=0,
        args=[app.bot]
    )
    scheduler.start()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("gastos", listar_gastos))
    app.add_handler(CommandHandler("facturas", listar_facturas))
    app.add_handler(CommandHandler("excel", exportar_excel))
    app.add_handler(CommandHandler("resumen", resumen_mensual))
    app.add_handler(CommandHandler("ia", consulta_ia))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Bot iniciado correctamente!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
