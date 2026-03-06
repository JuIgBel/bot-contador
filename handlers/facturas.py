from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import agregar_factura_db, obtener_facturas_db, marcar_factura_pagada
from datetime import datetime, timedelta

ESPERANDO_FACTURA = "esperando_factura"
ESPERANDO_VENCIMIENTO = "esperando_vencimiento"
ESPERANDO_MONTO_FACTURA = "esperando_monto_factura"

async def agregar_factura(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estado = context.user_data.get('estado')
    user_id = update.effective_user.id
    texto = update.message.text

    if estado == ESPERANDO_FACTURA:
        context.user_data['factura_servicio'] = texto
        context.user_data['estado'] = ESPERANDO_MONTO_FACTURA
        await update.message.reply_text(
            f"🧾 Servicio: *{texto}*\n\n💵 ¿Cuánto es el monto? (ej: `5000`):",
            parse_mode='Markdown'
        )
    elif estado == ESPERANDO_MONTO_FACTURA:
        try:
            monto = float(texto.replace(',', '.').replace('$', '').strip())
            context.user_data['factura_monto'] = monto
            context.user_data['estado'] = ESPERANDO_VENCIMIENTO
            
            # Sugerir fechas comunes
            hoy = datetime.now()
            sugerencias = [
                (hoy + timedelta(days=7)).strftime('%d/%m/%Y'),
                (hoy + timedelta(days=15)).strftime('%d/%m/%Y'),
                (hoy + timedelta(days=30)).strftime('%d/%m/%Y'),
            ]
            keyboard = [[InlineKeyboardButton(f"📅 {f}", callback_data=f"venc_{f}")] for f in sugerencias]
            keyboard.append([InlineKeyboardButton("📝 Ingresar otra fecha", callback_data="venc_manual")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📅 *¿Cuándo vence?*\n\nSeleccioná o escribí la fecha (formato: DD/MM/AAAA):",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text("❌ Ingresá un número válido (ej: `5000`):", parse_mode='Markdown')
    
    elif estado == ESPERANDO_VENCIMIENTO:
        try:
            fecha = datetime.strptime(texto.strip(), '%d/%m/%Y')
            servicio = context.user_data.get('factura_servicio')
            monto = context.user_data.get('factura_monto')
            agregar_factura_db(user_id, servicio, monto, fecha.strftime('%Y-%m-%d'))
            context.user_data['estado'] = None
            await update.message.reply_text(
                f"✅ *Factura registrada!*\n\n"
                f"🏢 {servicio}\n"
                f"💵 ${monto:,.2f}\n"
                f"📅 Vence: {fecha.strftime('%d/%m/%Y')}\n\n"
                f"Te voy a avisar 3 días antes del vencimiento 🔔\n\n"
                f"Usá /menu para continuar.",
                parse_mode='Markdown'
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Formato incorrecto. Ingresá la fecha así: `25/12/2025`",
                parse_mode='Markdown'
            )

async def handle_vencimiento_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if query.data == "venc_manual":
        context.user_data['estado'] = ESPERANDO_VENCIMIENTO
        await query.message.reply_text(
            "📅 Escribí la fecha de vencimiento (formato: `DD/MM/AAAA`):",
            parse_mode='Markdown'
        )
    else:
        fecha_str = query.data.replace("venc_", "")
        try:
            fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
            servicio = context.user_data.get('factura_servicio')
            monto = context.user_data.get('factura_monto')
            agregar_factura_db(user_id, servicio, monto, fecha.strftime('%Y-%m-%d'))
            context.user_data['estado'] = None
            await query.message.reply_text(
                f"✅ *Factura registrada!*\n\n"
                f"🏢 {servicio}\n"
                f"💵 ${monto:,.2f}\n"
                f"📅 Vence: {fecha_str}\n\n"
                f"Te voy a avisar 3 días antes del vencimiento 🔔\n\n"
                f"Usá /menu para continuar.",
                parse_mode='Markdown'
            )
        except ValueError:
            await query.message.reply_text("❌ Error con la fecha. Intentá de nuevo.")

async def listar_facturas(update: Update, context: ContextTypes.DEFAULT_TYPE, via_callback=False):
    user_id = update.effective_user.id
    facturas = obtener_facturas_db(user_id)
    
    if not facturas:
        texto = "📅 No tenés facturas pendientes.\nUsá el menú para agregar una."
    else:
        texto = "📅 *Facturas Pendientes:*\n\n"
        keyboard = []
        for f in facturas:
            fecha_venc = datetime.strptime(f['fecha_vencimiento'], '%Y-%m-%d')
            dias_restantes = (fecha_venc - datetime.now()).days
            if dias_restantes < 0:
                emoji = "🔴"
                dias_text = f"VENCIDA hace {abs(dias_restantes)} días"
            elif dias_restantes <= 3:
                emoji = "🟡"
                dias_text = f"vence en {dias_restantes} días"
            else:
                emoji = "🟢"
                dias_text = f"vence en {dias_restantes} días"
            
            texto += f"{emoji} *{f['servicio']}* | ${f['monto']:,.2f} | {fecha_venc.strftime('%d/%m/%Y')} ({dias_text})\n"
            keyboard.append([InlineKeyboardButton(f"✅ Pagar {f['servicio']}", callback_data=f"pagar_{f['id']}")])
    
    if via_callback:
        msg = update.callback_query.message
    else:
        msg = update.message
    
    if facturas:
        await msg.reply_text(texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await msg.reply_text(texto, parse_mode='Markdown')

async def handle_pagar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    factura_id = int(query.data.replace("pagar_", ""))
    marcar_factura_pagada(factura_id, user_id)
    await query.message.reply_text("✅ *Factura marcada como pagada!*", parse_mode='Markdown')
