from database.db import obtener_facturas_proximas
from datetime import datetime

async def verificar_vencimientos(bot):
    """Se ejecuta todos los días a las 9am para enviar recordatorios"""
    facturas = obtener_facturas_proximas()
    
    for factura in facturas:
        fecha_venc = datetime.strptime(factura['fecha_vencimiento'], '%Y-%m-%d')
        dias_restantes = (fecha_venc - datetime.now()).days
        
        if dias_restantes == 0:
            emoji = "🔴"
            mensaje = f"¡VENCE HOY!"
        elif dias_restantes == 1:
            emoji = "🟡"
            mensaje = f"vence MAÑANA"
        else:
            emoji = "🟡"
            mensaje = f"vence en {dias_restantes} días"
        
        texto = (
            f"{emoji} *Recordatorio de Vencimiento*\n\n"
            f"🏢 Servicio: *{factura['servicio']}*\n"
            f"💵 Monto: *${factura['monto']:,.2f}*\n"
            f"📅 Fecha: *{fecha_venc.strftime('%d/%m/%Y')}* ({mensaje})\n\n"
            f"Usá /facturas para marcarlo como pagado."
        )
        
        try:
            await bot.send_message(
                chat_id=factura['user_id'],
                text=texto,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Error enviando recordatorio a {factura['user_id']}: {e}")
