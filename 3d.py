import matplotlib.pyplot as plt
import numpy as np
import requests
import random

API_KEY = 'm6W81jDrD2TMVWarINf6yCbvesjH82cCUeGBFb41'        #Tenemos la API KEY de los objetos cercanos a la tierra
asteroid_id = '3727639'                                     #De aqui recuperamos todo 

url = f'https://api.nasa.gov/neo/rest/v1/neo/{asteroid_id}?api_key={API_KEY}'
response = requests.get(url)
data = response.json()                                      #"Data" recupera los datos de la api
nombre_asteroide = data['name']

# Paso 2: Extraer diámetro estimado
diameter = data['estimated_diameter']['meters']['estimated_diameter_max']   #El diametro es el estimado, representado en metros

# Paso 3: Generar puntos para simular la forma del meteorito
u = np.linspace(0, 2 * random.uniform((np.pi - 1), np.pi + 1), 15)          #15 numeros el cual su distancia es uniforme, desde 0 hasta 2 * un numero aleatorio entre pi-1 y pi+1 
v = np.linspace(0, 2 * random.uniform((np.pi - 1), np.pi + 1), 15)          #15 numeros el cual su distancia es uniforme, desde 0 hasta 2 * un numero aleatorio entre pi-1 y pi+1
u, v = np.meshgrid(u, v)                                                    #Crea una malla a partir de los vectores de coordenadas u y v       

# Usar el diámetro de la NASA para el radio base
r = (diameter / 2) * (1 + 0.5 * np.random.rand(*u.shape))
x = r * np.cos(u) * np.sin(v)
y = r * np.sin(u) * np.sin(v)
z = r * np.cos(v)

# Crear la figura 3D
fig = plt.figure(figsize=(7,6))
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(x, y, z, color='grey', alpha=0.75, shade=True)              #El meteorito es de color gris, con una transparencia del 75% y sombreado

ax.set_facecolor('black')                                                   #El fondo del 3D se pone en color negro
ax.grid(True, color='white', alpha=0.3)                                     #La grilla es de color blanco, algo transparente
fig.patch.set_facecolor('black')                                            #El fondo de la ventana se pone en color negro


#Etiquetamos los respectivos ejes, representados en metros
ax.set_xlabel('X (Meters)')
ax.set_ylabel('Y (Meters)')
ax.set_zlabel('Z (Meters)')

#Color blanco la etiqueta de cada eje
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.zaxis.label.set_color('white')

#Color blanco para la escala
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.tick_params(axis='z', colors='white')

ax.set_title(f"Meteorito 3D \n (ID: {asteroid_id}, Nombre: {nombre_asteroide}")
ax.title.set_color('white')

plt.get_current_fig_manager().toolbar.pack_forget()                         # Oculta la toolbar

plt.show()