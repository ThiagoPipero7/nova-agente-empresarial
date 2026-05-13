import sqlite3

# Creamos la base de datos y la tabla
conn = sqlite3.connect("empresa.db")
cursor = conn.cursor()

# Solo crea las tablas si no existen — nunca borra datos
cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        email TEXT,
        telefono TEXT,
        consulta TEXT,
        estado TEXT DEFAULT 'pendiente',
        fecha_alta TEXT DEFAULT (datetime('now'))
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        mensaje TEXT,
        respuesta TEXT,
        fecha TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )
""")

conn.commit()
conn.close()

print("Base de datos lista!")