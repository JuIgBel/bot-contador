# 🧮 Bot Contador Virtual para Telegram

Bot de Telegram que funciona como contador y asesor financiero personal, impulsado por IA (Google Gemini).

## ✨ Funciones

- 💰 **Gestión de gastos** con categorías
- 🧾 **Control de facturas** y vencimientos
- 🔔 **Recordatorios automáticos** 3 días antes del vencimiento
- 📊 **Exportar a Excel** con formato profesional
- 📈 **Asesor financiero IA** (bolsa, cripto, inversiones)
- 👥 **Multi-usuario** — cada persona tiene sus propios datos

---

## 🚀 Instalación y Deploy

### Paso 1 — Configurar variables de entorno

Copiá `.env.example` a `.env` y completá:

```
TELEGRAM_TOKEN=tu_token_de_botfather
GEMINI_API_KEY=tu_api_key_de_gemini
```

### Paso 2 — Instalar dependencias (local)

```bash
pip install -r requirements.txt
```

### Paso 3 — Correr localmente

```bash
python bot.py
```

---

## ☁️ Deploy en Railway (gratis)

1. Subí el código a un repositorio de GitHub
2. Entrá a [railway.app](https://railway.app) y creá un nuevo proyecto
3. Conectá tu repositorio de GitHub
4. En **Settings → Variables**, agregá:
   - `TELEGRAM_TOKEN` = tu token de Telegram
   - `GEMINI_API_KEY` = tu API key de Gemini
5. Railway va a hacer el deploy automáticamente ✅

---

## 📁 Estructura del proyecto

```
bot-contador/
├── bot.py                  # Archivo principal
├── requirements.txt        # Dependencias
├── Procfile               # Para Railway
├── .env.example           # Template de variables
├── database/
│   └── db.py              # Base de datos SQLite
└── handlers/
    ├── gastos.py          # Manejo de gastos + Excel
    ├── facturas.py        # Manejo de facturas
    ├── recordatorios.py   # Recordatorios automáticos
    └── ia.py              # Asesor financiero con Gemini
```

---

## 🤖 Comandos del bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Iniciar el bot |
| `/menu` | Ver menú principal |
| `/gastos` | Ver mis gastos |
| `/facturas` | Ver facturas pendientes |
| `/excel` | Exportar reporte Excel |
| `/resumen` | Resumen mensual |
| `/ia` | Consultar asesor financiero |
| `/ayuda` | Ver ayuda |

---

## 🔑 Obtener las API Keys

**Telegram Token:**
1. Abrí Telegram y buscá @BotFather
2. Ejecutá `/newbot`
3. Seguí las instrucciones y copiá el token

**Gemini API Key:**
1. Entrá a [aistudio.google.com](https://aistudio.google.com)
2. Hacé clic en "Get API Key"
3. Creá una nueva key (es gratis)
