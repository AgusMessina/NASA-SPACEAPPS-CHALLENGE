import tkinter as tk
import requests 
import datetime
import sys
from Meteorito3D import Meteorito3D 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCavasTkAgg
from datetime import date, timedelta
import matplotlib.pyplot as plt
import random

from lista_Asteroides import diccionarioAsteroides as dic
from lista_Asteroides import start_date, end_date


# =========================================================
# CONFIGURACIÓN Y DATOS GLOBALES
# =========================================================

# Colores y estilos
COLOR_NASA_AZUL = "#0B3D91" 
COLOR_PANEL_OSCURO = "#2C3E50" 
COLOR_TEXTO_CLARO = "white"

# Clave de la API de la NASA (solo como marcador de posición)
NASA_API_KEY = "m6W81jDrD2TMVWarINf6yCbvesjH82cCUeGBFb41" 
NEOWS_FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed"

# Diccionario de datos estáticos de emergencia 
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

def obtener_datos_asteroides_desde_api():
    """Devuelve datos estructurados a partir del diccionario importado."""
    datos_menu = {}
    datos_tabla = []

    for nombre, asteroid_id in dic.items():
        datos_menu[nombre] = {
            "id": asteroid_id,
            "tipo": "Asteroide Cercano a la Tierra",
            "descripcion": f"ID: {asteroid_id}",
            "peligrosidad": "Desconocida",  
            "fecha_aprox": "N/A",          
            "diameter_meters": None         
        }
        datos_tabla.append({
            "nombre": nombre,
            "fecha_aprox": "N/A",
            "peligrosidad": "Desconocida"
        })

    if not datos_menu:
        return DATOS_ASTEROIDES_ESTATICOS, []
    return datos_menu, datos_tabla


# =========================================================
# FUNCIONES DE LA INTERFAZ
# =========================================================

def salir_de_fullscreen(event=None):
    ventana.destroy()
    sys.exit()

def configurar_scroll_region(event):
    """Ajusta la región de desplazamiento del Canvas al tamaño del frame interno."""
    global canvas_lista 
    canvas_lista.configure(scrollregion=canvas_lista.bbox("all"))


def manejar_click_en_tabla(event, nombre_asteroide, diccionario):
    """Función intermediaria para llamar a la visualización 3D al hacer click."""
    cargar_simulacion_3d(nombre_asteroide, diccionario)


def cargar_simulacion_3d(nombre_asteroide, diccionario):
    """
    Crea una ventana Toplevel y muestra un gráfico 3D interactivo del asteroide.
    """
    asteroid_id = diccionario.get(nombre_asteroide)
    if not asteroid_id:
        print(f"No se encontró el ID para el asteroide: {nombre_asteroide}")
        return

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

    tk.Label(info_frame, text=f"ID: {asteroid_id}", font=("Courier New", 12),
             justify=tk.LEFT, fg="cyan", bg="#1E1E1E").pack(pady=10)

    try:
        meteorito = Meteorito3D(NASA_API_KEY, asteroid_id)
        meteorito.obtener_datos()
        meteorito.generar_puntos()
        fig = meteorito.graficar()

        canvas = FigureCavasTkAgg(fig, master=ventana_3d)
        canvas.widget = canvas.get_tk_widget()
        canvas.widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()
    except Exception as e:
        print(f"Error al generar el gráfico 3D para {nombre_asteroide}: {e}")
        tk.Label(ventana_3d, text="Error al generar el gráfico 3D. Intente reinstalar Matplotlib.", fg="red", bg="#1E1E1E", font=("Arial", 14)).pack(pady=20)

    tk.Button(ventana_3d, text="Cerrar Visualización", command=ventana_3d.destroy,
             bg="#C0392B", fg="white", font=("Arial", 12, "bold")).pack(pady=10)


def abrir_menu():
    global panel_abierto

    if panel_abierto and panel_abierto.winfo_exists():
        panel_abierto.destroy()
        panel_abierto = None
        return

    panel_abierto = tk.Frame(ventana, bg="#111111", bd=5, relief=tk.RAISED)
    
    # Usa pack() para colocar el panel lateral
    panel_abierto.pack(side=tk.RIGHT, anchor=tk.NE, padx=50, pady=50, fill=tk.Y) 

    tk.Label(panel_abierto, text="ASTEROIDES CERCANOS (7 DÍAS)", font=("Arial", 12, "bold"), bg="#111111", fg="orange").pack(pady=15, padx=10)

    for nombre in dic.keys():
        tk.Button(
            panel_abierto,
            text=nombre,
            command=lambda n=nombre: cargar_simulacion_3d(n, dic),
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
    """Crea la tabla de asteroides dentro del frame_contenido."""
    
    for widget in parent_frame.winfo_children():
        widget.destroy()

    row_start = 0 
    
    # Encabezados de Columna
    tk.Label(parent_frame, text="NOMBRE", font=("Courier New", 12, "bold"), bg=COLOR_PANEL_OSCURO, fg="yellow").grid(row=row_start, column=0, padx=20, pady=5, sticky="w")
    tk.Label(parent_frame, text="ID", font=("Courier New", 12, "bold"), bg=COLOR_PANEL_OSCURO, fg="yellow").grid(row=row_start, column=1, padx=20, pady=5, sticky="w")

    for i, (nombre, asteroid_id) in enumerate(dic.items()):
        row_num = row_start + 1 + i
        
        # --- CREAR LA ETIQUETA INTERACTIVA (NOMBRE) ---
        
        label_nombre = tk.Label(
            parent_frame, 
            text=nombre, 
            font=("Courier New", 12, "bold"), 
            bg=COLOR_PANEL_OSCURO, 
            fg="white",
            cursor="hand2"
        )
        label_nombre.grid(row=row_num, column=0, padx=20, pady=2, sticky="w")

        # Vincular el click a la función de visualización
        label_nombre.bind(
            "<Button-1>", 
            lambda event, n=nombre: manejar_click_en_tabla(event, n, dic)
        )
        
        # --- ETIQUETA NO INTERACTIVA (ID) ---
        
        tk.Label(parent_frame, text=asteroid_id, font=("Courier New", 12), bg=COLOR_PANEL_OSCURO, fg="cyan").grid(row=row_num, column=1, padx=20, pady=2, sticky="w")


# =========================================================
# INTERFAZ GRÁFICA (TKINTER) - INICIO
# =========================================================

ventana = tk.Tk()
ventana.title("Aplicación de Meteoritos Estilo NASA (Scroll e Interacción)")
ventana.configure(bg=COLOR_NASA_AZUL)
ventana.attributes('-fullscreen', True) 
ventana.bind('<Escape>', salir_de_fullscreen)

# El contenedor principal usa PACK
panel_principal = tk.Frame(
    ventana,
    bg=COLOR_PANEL_OSCURO,
    bd=5,
    relief=tk.RIDGE
)
panel_principal.pack(padx=50, pady=50, fill=tk.BOTH, expand=True)

# Configuración del Grid para el contenido (Título, Menú y Canvas)
panel_principal.columnconfigure(0, weight=9) 
panel_principal.columnconfigure(1, weight=1)
panel_principal.rowconfigure(1, weight=1) 


# --- TÍTULO Y BOTÓN DE MENÚ (Fila 0 de panel_principal - usa GRID) ---
titulo_lista = tk.Label(
    panel_principal,
    text="ASTEROIDES CERCANOS EN LOS ÚLTIMOS 7 DÍAS (DATOS API)",
    font=("Arial", 16, "bold"),
    bg=COLOR_PANEL_OSCURO,
    fg="yellow"
)
titulo_lista.grid(row=0, column=0, pady=10, sticky="w", padx=20) 




# --- ÁREA SCROLLABLE (Fila 1 de panel_principal - usa GRID y PACK) ---

# 1. Crear el Canvas (La ventana de visualización)
canvas_lista = tk.Canvas(
    panel_principal, 
    bg=COLOR_PANEL_OSCURO, 
    highlightthickness=0 
)
canvas_lista.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))


# 2. Crear la Scrollbar
scrollbar = tk.Scrollbar(
    panel_principal, 
    orient="vertical", 
    command=canvas_lista.yview
)
scrollbar.grid(row=1, column=1, sticky="nse", padx=(0, 20), pady=(0, 20))


# 3. Vincular el Canvas y la Scrollbar
canvas_lista.configure(yscrollcommand=scrollbar.set)

# 4. Crear el Frame Interno (El contenedor real de la tabla)
frame_contenido = tk.Frame(canvas_lista, bg=COLOR_PANEL_OSCURO)

# 5. Insertar el Frame Interno en el Canvas
canvas_lista.create_window((0, 0), window=frame_contenido, anchor="nw")

# 6. Configurar el desplazamiento cuando el contenido cambie
frame_contenido.bind("<Configure>", configurar_scroll_region)

# 7. VINCULAR LA RUEDA DEL RATÓN AL CANVAS
canvas_lista.bind_all("<MouseWheel>", lambda event: canvas_lista.yview_scroll(int(-1*(event.delta/120)), "units"))


# 8. Llenar el Frame Interno con los datos (La tabla)
crear_tabla_dinamica(frame_contenido)


if __name__ == "__main__":
    ventana.mainloop()