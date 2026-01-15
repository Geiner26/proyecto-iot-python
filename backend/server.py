import sqlite3
from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os

app = Flask(__name__)
DB_NAME = 'estacion_clima.db'

# --- GESTIÓN DE BASE DE DATOS ---
def init_db():
    """Crea la tabla si no existe"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mediciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                temperatura REAL,
                humedad REAL,
                modo TEXT
            )
        ''')
        conn.commit()

# Inicializamos la DB al arrancar
init_db()

# --- RUTAS WEB ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# --- API: RECIBIR DATOS (ESP32) ---
@app.route('/api/data', methods=['POST'])
def recibir_datos():
    try:
        payload = request.json
        if not payload: return jsonify({'error': 'Sin datos'}), 400

        temp = payload.get('temp')
        hum = payload.get('hum')
        modo = payload.get('modo')
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # INSERTAR EN SQLITE
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO mediciones (fecha, temperatura, humedad, modo) VALUES (?, ?, ?, ?)',
                (fecha, temp, hum, modo)
            )
            conn.commit()

        print(f"💾 SQL GUARDADO: T:{temp} H:{hum}")
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

# --- API: ENVIAR DATOS AL DASHBOARD ---
@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    try:
        # CONSULTAR SQLITE (Los últimos 20 registros)
        with sqlite3.connect(DB_NAME) as conn:
            # Esto permite acceder a las columnas por nombre
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM mediciones ORDER BY id DESC LIMIT 20')
            filas = cursor.fetchall()

        # Convertir a formato JSON para JavaScript
        datos = []
        # Invertimos la lista para que la gráfica vaya de izquierda a derecha (pasado -> presente)
        for fila in reversed(filas):
            datos.append({
                'hora': fila['fecha'].split(' ')[1], # Solo la hora
                'temp': fila['temperatura'],
                'hum': fila['humedad']
            })
            
        return jsonify(datos), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- API: EXPORTAR TODO PARA LA IA ---
@app.route('/api/all', methods=['GET'])
def descargar_todo():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Sin limite, traemos toda la historia
            cursor.execute('SELECT * FROM mediciones ORDER BY id ASC') 
            filas = cursor.fetchall()

        datos = []
        for fila in filas:
            datos.append({
                'fecha': fila['fecha'], # Formato completo YYYY-MM-DD HH:MM:SS
                'temp': fila['temperatura'],
                'hum': fila['humedad']
            })
        return jsonify(datos), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)