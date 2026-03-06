import os
from google import genai
from telegram import Update
from telegram.ext import ContextTypes

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "TU_GEMINI_KEY_AQUI")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """Eres ContadorBot, un asesor financiero virtual experto y amigable. 
Tu especialidad incluye:
- Contabilidad personal y empresarial
- Inversiones en bolsa de valores (acciones, ETFs, bonos)
- Criptomonedas y DeFi
- Finanzas personales y ahorro
- Economía argentina e internacional

Respondes siempre en español, de forma clara, concisa y didáctica.
Usas emojis para hacer el texto más amigable.
Siempre aclarás que tus consejos son educativos y no reemplazan a un asesor financiero certificado.
Cuando das consejos de inversión, siempre mencionás el riesgo involucrado.
Sos especialmente útil para usuarios argentinos: conocés el contexto del dólar, inflación, plazos fijos, CEDEARs, criptomonedas, etc."""

async def consulta_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '/ia':
        context.user_data['estado'] = 'esperando_consulta_ia'
        await update.message.reply_text(
            "🤖 *Asesor Financiero IA*\n\n"
            "Escribí tu pregunta sobre finanzas, inversiones, bolsa o cripto:",
            parse_mode='Markdown'
        )
        return
    
    pregunta = update.message.text
    user_name = update.effective_user.first_name
    
    await update.message.reply_text("🤔 Analizando tu consulta...")
    
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nEl usuario se llama {user_name}.\nPregunta: {pregunta}"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        respuesta = response.text
        
        if len(respuesta) > 4000:
            partes = [respuesta[i:i+4000] for i in range(0, len(respuesta), 4000)]
            for parte in partes:
                await update.message.reply_text(parte, parse_mode='Markdown')
        else:
            await update.message.reply_text(respuesta, parse_mode='Markdown')
        
        context.user_data['estado'] = 'esperando_consulta_ia'
        await update.message.reply_text(
            "💬 ¿Tenés otra consulta? Escribila directamente o usá /menu para volver al menú.",
        )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Hubo un error al consultar la IA: {str(e)}\n\n"
            f"Verificá que la API Key de Gemini sea correcta."
        )
        context.user_data['estado'] = None
