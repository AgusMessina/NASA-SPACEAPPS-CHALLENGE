import matplotlib.pyplot as plt
import numpy as np
import requests
import random

class Meteorito3D:
    def __init__(self, api_key, asteroid_id):                       #Inicializacion
        # Tenemos la API KEY de los objetos cercanos a la tierra
        self.api_key = api_key
        # De aqui recuperamos todo
        self.asteroid_id = asteroid_id
        self.nombre_asteroide = None
        self.diameter = None
        self.x = None
        self.y = None
        self.z = None

    def obtener_datos(self):
        # Recupera los datos de la api
        url = f'https://api.nasa.gov/neo/rest/v1/neo/{self.asteroid_id}?api_key={self.api_key}'
        response = requests.get(url)
        data = response.json()
        self.nombre_asteroide = data['name']
        # Extraer diámetro estimado
        self.diameter = data['estimated_diameter']['meters']['estimated_diameter_max']

    def generar_puntos(self):
        # 15 numeros el cual su distancia es uniforme, desde 0 hasta 2 * un numero aleatorio entre pi-1 y pi+1 
        u = np.linspace(0, 2 * random.uniform((np.pi - 1), np.pi + 1), 15)
        # 15 numeros el cual su distancia es uniforme, desde 0 hasta 2 * un numero aleatorio entre pi-1 y pi+1
        v = np.linspace(0, 2 * random.uniform((np.pi - 1), np.pi + 1), 15)
        # Crea una malla a partir de los vectores de coordenadas u y v       
        u, v = np.meshgrid(u, v)
        # Usar el diámetro de la NASA para el radio base
        r = (self.diameter / 2) * (1 + 0.5 * np.random.rand(*u.shape))
        self.x = r * np.cos(u) * np.sin(v)
        self.y = r * np.sin(u) * np.sin(v)
        self.z = r * np.cos(v)

    def graficar(self):
        # Crear la figura 3D
        fig = plt.figure(figsize=(7,6))
        ax = fig.add_subplot(111, projection='3d')

        # El meteorito es de color gris, con una transparencia del 75% y sombreado
        ax.plot_surface(self.x, self.y, self.z, color='grey', alpha=0.7, shade=True)

        # El fondo del 3D se pone en color negro
        ax.set_facecolor('black')
        # La grilla es de color blanco, algo transparente
        ax.grid(True, color='white', alpha=0.3)
        # El fondo de la ventana se pone en color negro
        fig.patch.set_facecolor('black')

        # Etiquetamos los respectivos ejes, representados en metros
        ax.set_xlabel('X (Meters)')
        ax.set_ylabel('Y (Meters)')
        ax.set_zlabel('Z (Meters)')

        # Color blanco la etiqueta de cada eje
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.zaxis.label.set_color('white')

        # Color blanco para la escala
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='z', colors='white')

        ax.set_title(f"Meteorito 3D \n (ID: {self.asteroid_id}, Nombre: {self.nombre_asteroide}")
        ax.title.set_color('white')

        if self.diameter:
            radio = max(self.diameter / 2, 100)
            ax.set_xlim(-radio, radio)
            ax.set_ylim(-radio, radio)
            ax.set_zlim(-radio, radio)

        plt.get_current_fig_manager().toolbar.pack_forget()  # Oculta la toolbar
        return fig