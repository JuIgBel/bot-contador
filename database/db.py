import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.getenv("DB_PATH", "contador.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            categoria TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            servicio TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha_vencimiento TEXT NOT NULL,
            pagada INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada")

def agregar_gasto_db(user_id, descripcion, categoria, monto):
    conn = get_connection()
    cursor = conn.cursor()
    fecha = date.today().isoformat()
    cursor.execute(
        "INSERT INTO gastos (user_id, descripcion, categoria, monto, fecha) VALUES (?, ?, ?, ?, ?)",
        (user_id, descripcion, categoria, monto, fecha)
    )
    conn.commit()
    conn.close()

def obtener_gastos_db(user_id, mes=None):
    conn = get_connection()
    cursor = conn.cursor()
    if mes:
        cursor.execute(
            "SELECT * FROM gastos WHERE user_id = ? AND strftime('%Y-%m', fecha) = ? ORDER BY fecha DESC",
            (user_id, mes)
        )
    else:
        cursor.execute(
            "SELECT * FROM gastos WHERE user_id = ? ORDER BY fecha DESC LIMIT 20",
            (user_id,)
        )
    gastos = cursor.fetchall()
    conn.close()
    return gastos

def agregar_factura_db(user_id, servicio, monto, fecha_vencimiento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO facturas (user_id, servicio, monto, fecha_vencimiento) VALUES (?, ?, ?, ?)",
        (user_id, servicio, monto, fecha_vencimiento)
    )
    conn.commit()
    conn.close()

def obtener_facturas_db(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM facturas WHERE user_id = ? AND pagada = 0 ORDER BY fecha_vencimiento ASC",
        (user_id,)
    )
    facturas = cursor.fetchall()
    conn.close()
    return facturas

def marcar_factura_pagada(factura_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE facturas SET pagada = 1 WHERE id = ? AND user_id = ?",
        (factura_id, user_id)
    )
    conn.commit()
    conn.close()

def obtener_facturas_proximas():
    """Obtiene facturas que vencen en los próximos 3 días (para todos los usuarios)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM facturas 
           WHERE pagada = 0 
           AND date(fecha_vencimiento) BETWEEN date('now') AND date('now', '+3 days')
           ORDER BY fecha_vencimiento ASC"""
    )
    facturas = cursor.fetchall()
    conn.close()
    return facturas

def get_resumen_mensual(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    mes_actual = datetime.now().strftime('%Y-%m')
    
    cursor.execute(
        """SELECT categoria, SUM(monto) as total 
           FROM gastos 
           WHERE user_id = ? AND strftime('%Y-%m', fecha) = ?
           GROUP BY categoria""",
        (user_id, mes_actual)
    )
    gastos_por_categoria = {row['categoria']: row['total'] for row in cursor.fetchall()}
    total_gastos = sum(gastos_por_categoria.values())
    
    cursor.execute(
        "SELECT COUNT(*) as count FROM facturas WHERE user_id = ? AND pagada = 0",
        (user_id,)
    )
    facturas_pendientes = cursor.fetchone()['count']
    
    conn.close()
    return {
        'gastos': gastos_por_categoria,
        'total_gastos': total_gastos,
        'facturas_pendientes': facturas_pendientes
    }

def obtener_todos_gastos_db(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM gastos WHERE user_id = ? ORDER BY fecha DESC",
        (user_id,)
    )
    gastos = cursor.fetchall()
    conn.close()
    return gastos

def obtener_todas_facturas_db(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM facturas WHERE user_id = ? ORDER BY fecha_vencimiento DESC",
        (user_id,)
    )
    facturas = cursor.fetchall()
    conn.close()
    return facturas
