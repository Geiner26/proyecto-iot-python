import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt # <--- NUEVA LIBRERÍA
import numpy as np

# 1. CARGAR DATOS
archivo = 'historial_clima.csv'

try:
    df = pd.read_csv(archivo)
except FileNotFoundError:
    print("❌ Error: Falta el archivo historial_clima.csv")
    exit()

if len(df) < 5:
    print("⚠️ Muy pocos datos. Espera a que el servidor recolecte al menos 5 registros.")
    exit()

# 2. PROCESAR TIEMPO (Minutos desde el inicio)
df['Fecha'] = pd.to_datetime(df['Fecha'])
start_time = df['Fecha'].iloc[0]
df['Minutos'] = (df['Fecha'] - start_time).dt.total_seconds() / 60.0

X = df[['Minutos']]
y = df['Temperatura']

# 3. ENTRENAR MODELO
modelo = LinearRegression()
modelo.fit(X, y)

# 4. PREDECIR FUTURO (10 min más adelante)
ultimo_minuto = df['Minutos'].iloc[-1]
minuto_futuro = ultimo_minuto + 10
prediccion_futura = modelo.predict([[minuto_futuro]])

print(f"🌡️ Temp Actual: {y.iloc[-1]}°C")
print(f"🔮 Predicción (10min): {prediccion_futura[0]:.2f}°C")

# ==========================================
#        NUEVA SECCIÓN: GRAFICAR
# ==========================================
print("📊 Generando gráfico...")

# A. Dibujar los puntos reales (Scatter plot)
plt.scatter(X, y, color='blue', label='Datos Reales (Sensor)')

# B. Dibujar la línea de la IA (Regresión)
# Creamos una línea que vaya desde el minuto 0 hasta el futuro
linea_tiempo = np.linspace(0, minuto_futuro, 100).reshape(-1, 1)
linea_prediccion = modelo.predict(linea_tiempo)

plt.plot(linea_tiempo, linea_prediccion, color='red', linewidth=2, label='Tendencia (IA)')

# C. Marcar el punto futuro con una estrella verde
plt.scatter([minuto_futuro], prediccion_futura, color='green', marker='*', s=200, label='Predicción Futura')

# D. Decorar el gráfico
plt.title('Monitor de Clima IoT + IA Predictiva')
plt.xlabel('Tiempo (Minutos desde inicio)')
plt.ylabel('Temperatura (°C)')
plt.legend()
plt.grid(True)

# E. Mostrar ventana
plt.show()
