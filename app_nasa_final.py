import tkinter as tk
import requests 
from datetime import date, timedelta
import sys
import matplotlib.pyplot as plt
# <<<<< SOLUCIÓN AL ERROR: Forzar el backend TkAgg >>>>>
plt.switch_backend('TkAgg') 
# <<<<< SOLUCIÓN AL ERROR: Forzar el backend TkAgg >>>>>
import numpy as np
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 


# =========================================================
# CONFIGURACIÓN Y DATOS GLOBALES
# =========================================================

# Colores y estilos
COLOR_NASA_AZUL = "#0B3D91"      
COLOR_PANEL_OSCURO = "#2C3E50"  
COLOR_TEXTO_CLARO = "white"

# Clave de la API de la NASA (NeoWs)
NASA_API_KEY = "m6W81jDrD2TMVWarINf6yCbvesjH82cCUeGBFb41" 
NEOWS_FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed"

# Diccionario de datos estáticos de emergencia (fallback si la API falla)
DATOS_ASTEROIDES_ESTATICOS = {
    "Vesta (Estatico)": {
        "id": "4 Vesta",
        "tipo": "Asteroide tipo V",
        "descripcion": "Datos de respaldo (7 días). Falla en la conexion a la API de NASA.",
        "peligrosidad": "Baja",
        "fecha_aprox": "N/A" 
    }
}

panel_abierto = None


# =========================================================
# FUNCIÓN DE API CENTRAL
# =========================================================

def obtener_datos_asteroides_desde_api(dias_a_buscar=7):
    """
    Realiza una solicitud al endpoint Neo - Feed de la NASA buscando asteroides 
    cercanos en los últimos 'dias_a_buscar' días.
    
    Devuelve un diccionario {nombre: datos_detallados} y una lista de datos 
    simples para la tabla principal.
    """
    
    end_date = date.today()
    start_date = end_date - timedelta(days=dias_a_buscar)

    parametros = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "api_key": NASA_API_KEY
    }
    
    datos_menu = {}       
    datos_tabla = []      
    
    try:
        print(f"Buscando asteroides desde {start_date} hasta {end_date}...")
        
        respuesta = requests.get(NEOWS_FEED_URL, params=parametros, timeout=15)
        respuesta.raise_for_status() 
        datos_api = respuesta.json()
        
        for fecha in datos_api.get('near_earth_objects', {}):
            for asteroide in datos_api['near_earth_objects'][fecha]:
                
                nombre_completo = asteroide.get("name", "Desconocido")
                nombre = nombre_completo.split('(')[0].strip()
                
                if nombre in datos_menu: 
                    continue 

                es_peligroso = asteroide.get("is_potentially_hazardous_asteroid", False)
                spk_id = asteroide.get("neo_reference_id", "N/A")
                
                # Manejo seguro del diámetro
                try:
                    diameter_max = asteroide['estimated_diameter']['meters']['estimated_diameter_max']
                except KeyError:
                    diameter_max = 100.0 # Valor seguro
                
                
                datos_menu[nombre] = {
                    "id": spk_id,
                    "tipo": "Asteroide Cercano a la Tierra",
                    "descripcion": f"Fecha de avistamiento: {fecha}. Diámetro est. max: {diameter_max:.2f} m.",
                    "peligrosidad": "ALTA" if es_peligroso else "Baja",
                    "fecha_aprox": fecha,
                    "diameter_meters": diameter_max # ¡Guardamos el diámetro seguro!
                }
                
                datos_tabla.append({
                    "nombre": nombre,
                    "fecha_aprox": fecha,
                    "peligrosidad": "Sí" if es_peligroso else "No"
                })
        
        print(f"--- Datos de {len(datos_menu)} asteroides obtenidos de la NASA. ---")
        if not datos_menu:
             return DATOS_ASTEROIDES_ESTATICOS, []
        return datos_menu, datos_tabla
        
    except requests.exceptions.RequestException as e:
        print(f"🔴 ERROR DE CONEXIÓN A LA API: {e}")
        datos_tabla_estatica = [{"nombre": k, "fecha_aprox": v['fecha_aprox'], "peligrosidad": v['peligrosidad']} for k, v in DATOS_ASTEROIDES_ESTATICOS.items()]
        return DATOS_ASTEROIDES_ESTATICOS, datos_tabla_estatica


# =========================================================
# FUNCIONES DE LA INTERFAZ
# =========================================================

def salir_de_fullscreen(event=None):
    ventana.destroy()


# --- Función CLAVE: Integración de la Visualización 3D ---
def cargar_simulacion_3d(nombre_asteroide, datos):
    """
    Crea una ventana Toplevel y muestra un gráfico 3D interactivo del asteroide.
    """
    datos_asteroide = datos.get(nombre_asteroide, {})
    if not datos_asteroide:
        print(f"No se encontraron datos para el asteroide: {nombre_asteroide}")
        return 

    asteroid_id = datos_asteroide.get('id', 'N/A')
    diameter = datos_asteroide.get('diameter_meters', 100)
    
    ventana_3d = tk.Toplevel(ventana)
    ventana_3d.title(f"Visualización 3D: {nombre_asteroide} (ID: {asteroid_id})")
    ventana_3d.geometry("800x800")
    ventana_3d.configure(bg="#1E1E1E") 
    ventana_3d.grab_set() 

    info_frame = tk.Frame(ventana_3d, bg="#1E1E1E")
    info_frame.pack(pady=10)

    tk.Label(info_frame, 
             text=f"ASTEROIDE: {nombre_asteroide.upper()}", 
             font=("Arial", 20, "bold"), fg="#00E676", bg="#1E1E1E").pack()
    
    info_texto = (
        f"ID SPK-ID: {datos_asteroide.get('id', 'N/A')}\n"
        f"Tipo: {datos_asteroide.get('tipo', 'N/A')}\n"
        f"Peligrosidad: {datos_asteroide.get('peligrosidad', 'N/A')}\n"
        f"Descripción: {datos_asteroide.get('descripcion', 'N/A')}"
    )
    tk.Label(info_frame, text=info_texto, font=("Courier New", 12), 
             justify=tk.LEFT, fg="cyan", bg="#1E1E1E").pack(pady=10)

    # 3. Generar el gráfico 3D de Matplotlib
    try:
        fig = plt.figure(figsize=(7, 7), facecolor="#1E1E1E") 
        ax = fig.add_subplot(111, projection='3d')
        
        # --- Lógica para generar el asteroide 3D ---
        u = np.linspace(0, 2 * np.pi, 30) 
        v = np.linspace(0, np.pi, 30)
        u, v = np.meshgrid(u, v)

        r = (diameter / 2) * (1 + 0.3 * (np.random.rand(*u.shape) - 0.5)) 
        x = r * np.cos(u) * np.sin(v)
        y = r * np.sin(u) * np.sin(v)
        z = r * np.cos(v)

        ax.plot_surface(x, y, z, color='grey', alpha=0.9, shade=True)
        
        # Configuración visual para el tema oscuro
        ax.set_xlabel('X (Meters)', color='white')
        ax.set_ylabel('Y (Meters)', color='white')
        ax.set_zlabel('Z (Meters)', color='white')
        ax.set_title(f"Visualización de {nombre_asteroide}", color='white', fontsize=14)
        
        ax.tick_params(axis='both', colors='white')
        ax.set_frame_on(False)
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.set_facecolor("#1E1E1E") 
        fig.patch.set_facecolor("#1E1E1E")
        
        # 4. Integrar Matplotlib en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=ventana_3d)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        canvas.draw()
        
    except Exception as e:
        # Esto atrapará el error de "NoneType" object is not callable
        print(f"Error al generar el gráfico 3D para {nombre_asteroide}: {e}")
        tk.Label(ventana_3d, text="Error al generar el gráfico 3D. Intente reinstalar Matplotlib.", fg="red", bg="#1E1E1E", font=("Arial", 14)).pack(pady=20)
    
    # 5. Botón para cerrar
    tk.Button(ventana_3d, text="Cerrar Visualización", command=ventana_3d.destroy, 
              bg="#C0392B", fg="white", font=("Arial", 12, "bold")).pack(pady=10)


def abrir_menu():
    global panel_abierto
    
    if panel_abierto and panel_abierto.winfo_exists():
        panel_abierto.destroy()
        panel_abierto = None
        return

    datos_menu, _ = obtener_datos_asteroides_desde_api()
    
    panel_abierto = tk.Frame(ventana, bg="#111111", bd=5, relief=tk.RAISED)
    panel_abierto.place(relx=1.0, rely=0, x=-50, y=0, anchor=tk.NE) 

    tk.Label(panel_abierto, text="ASTEROIDES CERCANOS (7 DÍAS)", font=("Arial", 12, "bold"), bg="#111111", fg="orange").pack(pady=15, padx=10)

    for nombre in datos_menu.keys():
        tk.Button(
            panel_abierto,
            text=nombre,
            command=lambda n=nombre, d=datos_menu: cargar_simulacion_3d(n, d), 
            bg="#34495E",
            fg="white",
            width=30, 
            anchor="w" 
        ).pack(pady=4, padx=10)
        
    tk.Button(panel_abierto, text="☰ Cerrar Panel", command=abrir_menu, bg="#C0392B", fg="white", width=30).pack(pady=20, padx=10)

# ---------------------------------------------------------
# FUNCIÓN CLAVE: PARA RECARGAR LA TABLA PRINCIPAL
# ---------------------------------------------------------

def crear_tabla_dinamica(parent_frame):
    
    for widget in parent_frame.winfo_children():
        if int(widget.grid_info().get("row", 0)) > 0:
            widget.destroy()

    _, datos_tabla = obtener_datos_asteroides_desde_api()
    
    row_start = 1 

    # Encabezados
    tk.Label(parent_frame, text="NOMBRE", font=("Courier New", 12, "bold"), bg=COLOR_PANEL_OSCURO, fg="yellow").grid(row=row_start, column=0, padx=20, pady=5, sticky="w")
    tk.Label(parent_frame, text="FECHA APROXIMACIÓN", font=("Courier New", 12, "bold"), bg=COLOR_PANEL_OSCURO, fg="yellow").grid(row=row_start, column=0, padx=200, pady=5, sticky="w") 
    tk.Label(parent_frame, text="PELIGROSO (S/N)", font=("Courier New", 12, "bold"), bg=COLOR_PANEL_OSCURO, fg="yellow").grid(row=row_start, column=0, padx=450, pady=5, sticky="w") 

    # Filas de datos
    for i, item in enumerate(datos_tabla):
        row_num = row_start + 1 + i
        color_peligro = "red" if item['peligrosidad'] == "Sí" else "cyan"

        tk.Label(parent_frame, text=item['nombre'], font=("Courier New", 12), bg=COLOR_PANEL_OSCURO, fg="white").grid(row=row_num, column=0, padx=20, pady=2, sticky="w")
        tk.Label(parent_frame, text=item['fecha_aprox'], font=("Courier New", 12), bg=COLOR_PANEL_OSCURO, fg="white").grid(row=row_num, column=0, padx=200, pady=2, sticky="w")
        tk.Label(parent_frame, text=item['peligrosidad'], font=("Courier New", 12), bg=COLOR_PANEL_OSCURO, fg=color_peligro).grid(row=row_num, column=0, padx=450, pady=2, sticky="w")

# =========================================================
# INTERFAZ GRÁFICA (TKINTER) - INICIO
# =========================================================

ventana = tk.Tk()
ventana.title("Aplicación de Meteoritos Estilo NASA (Datos API)")
ventana.configure(bg=COLOR_NASA_AZUL)
ventana.attributes('-fullscreen', True) 
ventana.bind('<Escape>', salir_de_fullscreen)

panel_meteoritos = tk.Frame(
    ventana,
    bg=COLOR_PANEL_OSCURO,
    bd=5,
    relief=tk.RIDGE
)
panel_meteoritos.pack(padx=50, pady=50, fill=tk.BOTH, expand=True)

panel_meteoritos.columnconfigure(0, weight=9) 
panel_meteoritos.columnconfigure(1, weight=1) 

titulo_lista = tk.Label(
    panel_meteoritos,
    text="ASTEROIDES CERCANOS EN LOS ÚLTIMOS 7 DÍAS (DATOS API)",
    font=("Arial", 16, "bold"),
    bg=COLOR_PANEL_OSCURO,
    fg="yellow"
)
titulo_lista.grid(row=0, column=0, pady=10, sticky="w", padx=20) 

boton_menu = tk.Button(
    panel_meteoritos,
    text="☰", 
    font=("Arial", 20),
    bg=COLOR_PANEL_OSCURO,
    fg=COLOR_TEXTO_CLARO,
    command=abrir_menu, 
    bd=0, 
    activebackground=COLOR_PANEL_OSCURO
)
boton_menu.grid(row=0, column=1, pady=10, sticky="e", padx=20)

crear_tabla_dinamica(panel_meteoritos)

if __name__ == "__main__":
    ventana.mainloop()