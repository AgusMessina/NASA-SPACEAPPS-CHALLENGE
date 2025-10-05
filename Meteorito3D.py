import matplotlib.pyplot as plt
import numpy as np
import requests
import random
import matplotlib.figure

class Meteorito3D:
    def __init__(self, api_key, asteroid_id):
        # Tenemos la API KEY de los objetos cercanos a la tierra
        self.api_key = api_key
        # De aqui recuperamos todo
        self.asteroid_id = asteroid_id
        
        # --- Variables de Datos de la API (Nuevas) ---
        self.nombre_asteroide = None
        self.diameter = None # Será el max_diameter (usado para la escala)
        self.diameter_min_m = None
        self.diameter_max_m = None
        self.is_hazardous = None
        self.absolute_magnitude_h = None
        self.closest_approach_date = "N/A"
        self.relative_velocity_kmh = "N/A"
        self.miss_distance_au = "N/A"
        
        self.x = None
        self.y = None
        self.z = None

    def obtener_datos(self):
        # Recupera todos los datos necesarios de la API
        url = f'https://api.nasa.gov/neo/rest/v1/neo/{self.asteroid_id}?api_key={self.api_key}'
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            self.nombre_asteroide = data['name']
            
            # Extraer diámetros estimados (min y max)
            diameter_data = data['estimated_diameter']['meters']
            self.diameter_min_m = diameter_data['estimated_diameter_min']
            self.diameter_max_m = diameter_data['estimated_diameter_max']
            # Asignar a la variable 'diameter' usada por la lógica antigua
            self.diameter = self.diameter_max_m 
            
            self.is_hazardous = data['is_potentially_hazardous_asteroid']
            self.absolute_magnitude_h = data['absolute_magnitude_h']
            
            # Extraer datos del Close Approach más cercano
            approach_data = data.get('close_approach_data', [])
            if approach_data:
                first_approach = approach_data[0]
                self.closest_approach_date = first_approach['close_approach_date_full']
                
                # Velocidad
                vel_data = first_approach['relative_velocity']
                # Se usa float() para asegurar el tipo de dato
                self.relative_velocity_kmh = float(vel_data['kilometers_per_hour']) 
                
                # Distancia de paso
                dist_data = first_approach['miss_distance']
                # Se usa float() para asegurar el tipo de dato
                self.miss_distance_au = float(dist_data['astronomical'])

        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos detallados del NEO {self.asteroid_id}: {e}")
            self.nombre_asteroide = "Error de Conexión"
            self.diameter_max_m = 0
            self.diameter = 0

    def generar_puntos(self):
        # Lógica de la versión "vieja" para la forma irregular y la malla completa
        
        # 15 numeros el cual su distancia es uniforme, desde 0 hasta 2 * un numero aleatorio entre pi-1 y pi+1 
        u = np.linspace(0, 2 * random.uniform((np.pi - 1), np.pi + 1), 15)
        # 15 numeros el cual su distancia es uniforme, desde 0 hasta 2 * un numero aleatorio entre pi-1 y pi+1
        v = np.linspace(0, 2 * random.uniform((np.pi - 1), np.pi + 1), 15)
        
        # Crea una malla a partir de los vectores de coordenadas u y v       
        u, v = np.meshgrid(u, v)
        
        # Usar el diámetro de la NASA para el radio base y añadir una perturbación aleatoria
        r = (self.diameter / 2) * (1 + 0.5 * np.random.rand(*u.shape))
        self.x = r * np.cos(u) * np.sin(v)
        self.y = r * np.sin(u) * np.sin(v)
        self.z = r * np.cos(v)

    def graficar(self):
        # Usamos matplotlib.figure.Figure para compatibilidad con Tkinter
        fig = matplotlib.figure.Figure(figsize=(7, 7)) 
        ax = fig.add_subplot(111, projection='3d')

        # El meteorito es de color gris, con una transparencia del 75% y sombreado
        ax.plot_surface(self.x, self.y, self.z, color='grey', alpha=0.7, shade=True)

        # Estilo de gráfico (manteniendo los colores y etiquetas)
        ax.set_facecolor('black')
        ax.grid(True, color='white', alpha=0.3)
        fig.patch.set_facecolor('black')

        ax.set_xlabel('X (Meters)')
        ax.set_ylabel('Y (Meters)')
        ax.set_zlabel('Z (Meters)')

        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.zaxis.label.set_color('white')

        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='z', colors='white')

        # Título original
        ax.set_title(f"Meteorito 3D \n (ID: {self.asteroid_id}, Nombre: {self.nombre_asteroide})", color='white')

        # Límite de Ejes Dinámico (Lógica antigua)
        if self.diameter:
            radio = max(self.diameter / 2, 100) # Asegura un límite mínimo de 100m
            ax.set_xlim(-radio, radio)
            ax.set_ylim(-radio, radio)
            ax.set_zlim(-radio, radio)
            
        return fig