from flask import Flask, request, jsonify
from datetime import datetime
import csv
import os

app = Flask(__name__)

# Nombre del archivo donde guardaremos la historia
ARCHIVO_CSV = 'historial_clima.csv'

# Función para preparar el archivo (crear encabezados si no existe)
def inicializar_csv():
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Fecha', 'Temperatura', 'Humedad', 'Modo'])

inicializar_csv()

@app.route('/api/data', methods=['POST'])
def recibir_datos():
    try:
        payload = request.json
        if not payload:
            return jsonify({'error': 'Sin datos'}), 400

        # Obtener datos
        temp = payload.get('temp')
        hum = payload.get('hum')
        modo = payload.get('modo')
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Guardar en CSV (Append mode 'a')
        with open(ARCHIVO_CSV, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([fecha, temp, hum, modo])

        # 2. Mostrar en consola
        print(f"💾 GUARDADO: {fecha} | T:{temp}°C | H:{hum}%")
        
        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Servidor con Base de Datos CSV iniciado...")
    app.run(host='0.0.0.0', port=5000)