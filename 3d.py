import matplotlib.pyplot as plt
import numpy as np
import requests
import random

# Paso 1: Obtener datos de la NASA NeoWs API

API_KEY = 'm6W81jDrD2TMVWarINf6yCbvesjH82cCUeGBFb41'
asteroid_id = '3727639'

url = f'https://api.nasa.gov/neo/rest/v1/neo/{asteroid_id}?api_key={API_KEY}'
response = requests.get(url)
data = response.json()
nombre_asteroide = data['name']

# Paso 2: Extraer diámetro estimado
diameter = data['estimated_diameter']['meters']['estimated_diameter_max']
x = random.randint(1,100)
# Paso 3: Generar puntos para simular la forma del meteorito
u = np.linspace(0, np.pi, 15)
v = np.linspace(0, np.pi, 15)
u, v = np.meshgrid(u, v)

# Usar el diámetro de la NASA para el radio base
r = (diameter / 2) * (1 + 0.5 * np.random.rand(*u.shape))
x = r * np.cos(u) * np.sin(v)
y = r * np.sin(u) * np.sin(v)
z = r * np.cos(v)

# Crear la figura 3D
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(x, y, z, color='grey', alpha=0.75, shade=True)

ax.set_xlabel('X (Meters)')
ax.set_ylabel('Y (Meters)')
ax.set_zlabel('Z (Meters)')
ax.set_title(f"Meteorito 3D (ID: {asteroid_id}, Nombre: {nombre_asteroide}")

plt.show()