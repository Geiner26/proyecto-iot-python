import requests
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # <--- NECESARIO PARA LAS FECHAS
from datetime import timedelta
import numpy as np

# ==========================================
# 1. CONEXIÓN CON LA NUBE
# ==========================================
URL_SERVIDOR = "https://proyecto-iot-python.onrender.com" # <--- TU URL

print(f"📡 Conectando a {URL_SERVIDOR}...")

try:
    response = requests.get(f"{URL_SERVIDOR}/api/all")
    if response.status_code == 200:
        datos_json = response.json()
    else:
        print("❌ Error del servidor:", response.text)
        exit()
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit()

if len(datos_json) < 5:
    print("⚠️ Muy pocos datos para graficar.")
    exit()

# ==========================================
# 2. LIMPIEZA Y FILTRADO (ZOOM)
# ==========================================
df = pd.DataFrame(datos_json)
df['fecha'] = pd.to_datetime(df['fecha'])

# --- TRUCO DE PROFESIONAL ---
# Si tienes 400 datos, la gráfica se ve apretada. 
# Nos quedamos solo con los últimos 60 registros (Zoom a lo reciente)
df = df.tail(60) 

# Reiniciamos el "cronómetro" interno para la IA basándonos en este recorte
start_time = df['fecha'].iloc[0]
df['minutos'] = (df['fecha'] - start_time).dt.total_seconds() / 60.0

X = df[['minutos']]
y_temp = df['temp']
y_hum = df['hum']

# ==========================================
# 3. ENTRENAMIENTO
# ==========================================
modelo_temp = LinearRegression()
modelo_temp.fit(X, y_temp)

modelo_hum = LinearRegression()
modelo_hum.fit(X, y_hum)

# ==========================================
# 4. PREDICCIÓN FUTURA (EN FECHA REAL)
# ==========================================
# Predecimos 15 minutos en el futuro
minuto_futuro_ia = df['minutos'].iloc[-1] + 15
pred_temp = modelo_temp.predict([[minuto_futuro_ia]])
pred_hum = modelo_hum.predict([[minuto_futuro_ia]])

# Calculamos qué HORA será en 15 minutos
hora_actual = df['fecha'].iloc[-1]
hora_futura = hora_actual + timedelta(minutes=15)

print(f"⏱️ Último dato: {hora_actual.strftime('%H:%M:%S')}")
print(f"🔮 Predicción para las {hora_futura.strftime('%H:%M:%S')}:")
print(f"   🌡️ Temp: {pred_temp[0]:.2f}°C")
print(f"   💧 Hum:  {pred_hum[0]:.2f}%")

# ==========================================
# 5. GRAFICAR CON FECHAS (FORMATO HH:MM)
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig.suptitle(f'Monitor IoT en Tiempo Real (Últimos {len(df)} registros)', fontsize=16)

# --- GRÁFICA TEMPERATURA ---
# Nota: Ahora en el eje X ponemos df['fecha'] (tiempos reales)
ax1.plot(df['fecha'], y_temp, 'o-', color='blue', alpha=0.5, label='Real')
ax1.plot(df['fecha'], modelo_temp.predict(X), color='red', linestyle='--', label='Tendencia IA')
ax1.scatter([hora_futura], pred_temp, color='green', marker='*', s=300, label='Futuro (+15min)', zorder=5)
ax1.set_ylabel('Temp (°C)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# --- GRÁFICA HUMEDAD ---
ax2.plot(df['fecha'], y_hum, 'o-', color='cyan', alpha=0.6, label='Real')
ax2.plot(df['fecha'], modelo_hum.predict(X), color='orange', linestyle='--', label='Tendencia IA')
ax2.scatter([hora_futura], pred_hum, color='purple', marker='*', s=300, label='Futuro (+15min)', zorder=5)
ax2.set_ylabel('Humedad (%)')
ax2.legend()
ax2.grid(True, alpha=0.3)

# --- FORMATEAR EL EJE X (TRUCO DE MATPLOTLIB) ---
# Esto hace que las fechas se vean bonitas (HH:MM) y no se amontonen
formato_hora = mdates.DateFormatter('%H:%M')
ax2.xaxis.set_major_formatter(formato_hora)
plt.gcf().autofmt_xdate() # Rota las fechas para que se lean bien

plt.show()