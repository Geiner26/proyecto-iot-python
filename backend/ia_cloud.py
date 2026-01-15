import requests
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. CONEXIÓN CON LA NUBE
# ==========================================
# PON TU URL DE RENDER AQUÍ (Sin la barra al final)
URL_SERVIDOR = "https://proyecto-iot-python.onrender.com"

print(f"📡 Conectando a {URL_SERVIDOR} para descargar memoria...")

try:
    # Pedimos TODOS los datos a la nueva ruta que creamos
    response = requests.get(f"{URL_SERVIDOR}/api/all")
    
    if response.status_code == 200:
        datos_json = response.json()
        print(f"✅ Datos descargados: {len(datos_json)} registros.")
    else:
        print("❌ Error en el servidor:", response.text)
        exit()
except Exception as e:
    print(f"❌ No se pudo conectar a internet: {e}")
    exit()

# Si hay muy pocos datos, no podemos entrenar
if len(datos_json) < 5:
    print("⚠️ Muy pocos datos en la nube. Espera a que el ESP32 envíe más.")
    exit()

# ==========================================
# 2. PREPARACIÓN DE DATOS
# ==========================================
df = pd.DataFrame(datos_json)

# Convertir fecha de texto a objeto fecha real
df['fecha'] = pd.to_datetime(df['fecha'])

# Calcular minutos desde el primer dato (para que la IA entienda el tiempo)
start_time = df['fecha'].iloc[0]
df['minutos'] = (df['fecha'] - start_time).dt.total_seconds() / 60.0

X = df[['minutos']]
y = df['temp']

# ==========================================
# 3. ENTRENAMIENTO
# ==========================================
modelo = LinearRegression()
modelo.fit(X, y)

print("🧠 IA Re-Entrenada con datos frescos de la nube.")

# ==========================================
# 4. PREDICCIÓN Y GRÁFICA
# ==========================================
ultimo_minuto = df['minutos'].iloc[-1]
futuro = ultimo_minuto + 15 # Predecir 15 mins adelante
prediccion = modelo.predict([[futuro]])

print(f"🔮 Predicción a 15 min: {prediccion[0]:.2f}°C")

# Graficar
plt.figure(figsize=(10, 6))
plt.scatter(X, y, color='blue', alpha=0.5, label='Datos Reales (Nube)')
plt.plot(X, modelo.predict(X), color='red', linewidth=2, label='Tendencia IA')

# Punto futuro
plt.scatter([futuro], prediccion, color='green', marker='*', s=300, label='Futuro')

plt.title(f'Análisis Remoto: {len(df)} muestras desde la Nube')
plt.xlabel('Tiempo (Minutos)')
plt.ylabel('Temperatura (°C)')
plt.legend()
plt.grid(True)
plt.show()