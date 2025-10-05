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


def obtener_datos_asteroides_desde_api():
    """
    Devuelve un diccionario {nombre: datos_detallados} y una lista de datos simples para la tabla principal,
    usando el diccionario importado de lista_Asteroides.py.
    """
    datos_menu = {}
    datos_tabla = []

    for nombre, asteroid_id in dic.items():
        # Puedes agregar más detalles si los tienes en el diccionario original
        datos_menu[nombre] = {
            "id": asteroid_id,
            "tipo": "Asteroide Cercano a la Tierra",
            "descripcion": f"ID: {asteroid_id}",
            "peligrosidad": "Desconocida",  # Si tienes este dato, cámbialo aquí
            "fecha_aprox": "N/A",           # Si tienes este dato, cámbialo aquí
            "diameter_meters": None         # Si tienes este dato, cámbialo aquí
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


# --- Función CLAVE: Integración de la Visualización 3D ---

def cargar_simulacion_3d(nombre_asteroide, diccionario):
    """
    Crea una ventana Toplevel y muestra un gráfico 3D interactivo del asteroide usando la clase Meteorito3D.
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
    panel_abierto.place(relx=1.0, rely=0, x=-50, y=0, anchor=tk.NE)

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
    for widget in parent_frame.winfo_children():
        if int(widget.grid_info().get("row", 0)) > 0:
            widget.destroy()

    row_start = 1

    tk.Label(parent_frame, text="NOMBRE", font=("Courier New", 12, "bold"), bg=COLOR_PANEL_OSCURO, fg="yellow").grid(row=row_start, column=0, padx=20, pady=5, sticky="w")
    tk.Label(parent_frame, text="ID", font=("Courier New", 12, "bold"), bg=COLOR_PANEL_OSCURO, fg="yellow").grid(row=row_start, column=0, padx=200, pady=5, sticky="w")

    for i, (nombre, asteroid_id) in enumerate(dic.items()):
        row_num = row_start + 1 + i
        tk.Label(parent_frame, text=nombre, font=("Courier New", 12), bg=COLOR_PANEL_OSCURO, fg="white").grid(row=row_num, column=0, padx=20, pady=2, sticky="w")
        tk.Label(parent_frame, text=asteroid_id, font=("Courier New", 12), bg=COLOR_PANEL_OSCURO, fg="cyan").grid(row=row_num, column=0, padx=200, pady=2, sticky="w")

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