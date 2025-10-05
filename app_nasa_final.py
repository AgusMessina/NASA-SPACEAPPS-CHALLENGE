import tkinter as tk
import requests 
import datetime
import sys
import numpy as np
from Meteorito3D import Meteorito3D 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCavasTkAgg
import matplotlib.pyplot as plt
import random
from PIL import Image, ImageTk # <-- ¡IMPORTACIÓN NECESARIA PARA LA IMAGEN!

# Importar lógica consolidada (Reemplaza a lista_Asteroides)
try:
    from logica_simulacion import diccionarioAsteroides as dic
    from logica_simulacion import obtener_datos_reales_para_ais, calcular_consecuencias, simular_desviacion
except ImportError:
    print("Error: No se encontró logica_simulacion.py. Asegúrese de haber creado este archivo.")
    dic = {}
    def obtener_datos_reales_para_ais(id): return {'nombre': 'Datos Fallidos', 'diametro_metros': 300, 'velocidad_impacto_kms': 15.0, 'latitud_impacto': 40.71, 'longitud_impacto': -74.00, 'a': 1.5, 'e': 0.3, 'i': 5.0}
    def calcular_consecuencias(d, v): return {'energia_mt': 0, 'crater_diametro_km': 0, 'sismico_magnitud': 0, 'radio_vientos_km': 0, 'radio_calor_km': 0}
    def simular_desviacion(d, i, a): return {'a_modificado': 1.5, 'impacto_evitado': False, 'latitud_final': 40.71, 'longitud_final': -74.00, 'impulso_efectivo': 0}

# Importar visualización 3D para AIS
try:
    import G3D_AIS as pg
except ImportError:
    print("Error: No se encontró G3D_AIS.py.")
    pg = None


# =========================================================
# CONFIGURACIÓN Y DATOS GLOBALES
# =========================================================

# Colores y estilos
COLOR_NASA_AZUL = "#0B3D91" 
COLOR_PANEL_OSCURO = "#2C3E50" 
COLOR_FONDO_TABLA = "#34495E"
COLOR_TEXTO_CLARO = "white"
COLOR_PELIGRO = '#FF4500' 
COLOR_SEGURO = '#32CD32' 

NASA_API_KEY = "m6W81jDrD2TMVWarINf6yCbvesjH82cCUeGBFb41" 

# Diccionario de datos estáticos de emergencia 
DATOS_ASTEROIDES_ESTATICOS = {
    "Vesta (Estatico)": "4_Vesta_ID_Fallback"
}

panel_abierto = None 

# Variables de la simulación AIS
diametro_var, impulso_var, angulo_var = None, None, None
datos_ais_global = {} 
ax_3d_ais, ax_mapa_ais = None, None
resultado_var_ais = None
energia_label, crater_label, sismo_label, estado_label = None, None, None, None 

# Variables para la imagen de fondo (GLOBALES)
imagen_fondo_tk = None
label_fondo = None

# =========================================================
# FUNCIONES DE LA SIMULACIÓN AIS (VENTANA NUEVA)
# =========================================================

# ... (Todas las funciones de la simulación AIS y 3D se mantienen iguales) ...
# Dado que ocupan mucho espacio, se omiten aquí, pero se asume que están
# definidas en tu código original, ya que la modificación es solo en el bloque de inicio.

def actualizar_visualizacion_mapa(ax_mapa, resultados_mitigacion, consecuencias, nombre_ast):
    """Actualiza el mapa 2D de AIS."""
    ax_mapa.clear()
    
    # Dibujar mapa de referencia (simplificado)
    ax_mapa.set_facecolor('darkblue') 
    ax_mapa.add_patch(plt.Rectangle((-180, -90), 360, 180, color='darkgreen', alpha=0.3)) 
    
    lat = resultados_mitigacion['latitud_final']
    lon = resultados_mitigacion['longitud_final']
    
    if not resultados_mitigacion['impacto_evitado']:
        # Simulación de Consecuencias (Mejoras 2D)
        
        # 1. Daño por Calor (círculo interior)
        radio_calor_grados = consecuencias['radio_calor_km'] / 111 
        circulo_calor = plt.Circle((lon, lat), radio_calor_grados, color='yellow', alpha=0.3, fill=True)
        ax_mapa.add_artist(circulo_calor)

        # 2. Vientos/Sismo (círculo intermedio)
        radio_vientos_grados = consecuencias['radio_vientos_km'] / 111
        circulo_vientos = plt.Circle((lon, lat), radio_vientos_grados, color=COLOR_PELIGRO, alpha=0.2, fill=True)
        ax_mapa.add_artist(circulo_vientos)

        # 3. Cráter (círculo central)
        crater_diametro = consecuencias['crater_diametro_km']
        radio_mapa_grados = crater_diametro / 111 
        circulo_crater = plt.Circle((lon, lat), radio_mapa_grados, color='darkred', alpha=0.9)
        ax_mapa.add_artist(circulo_crater)
    
    # Marcador de impacto final
    color_marcador = 'yellow' if not resultados_mitigacion['impacto_evitado'] else COLOR_SEGURO
    ax_mapa.plot(lon, lat, marker='X', color=color_marcador, markersize=10, linestyle='')
    
    ax_mapa.set_title(f"Mapa de Impacto 2D\nAsteroide: {nombre_ast}", color=COLOR_TEXTO_CLARO, fontsize=10)
    ax_mapa.set_xlim(-180, 180)
    ax_mapa.set_ylim(-90, 90)
    ax_mapa.tick_params(colors=COLOR_TEXTO_CLARO)
    
    ax_mapa.figure.canvas.draw()


def actualizar_simulacion_ais(event=None):
    """Llama a la lógica de AIS y actualiza la UI de la simulación."""
    global datos_ais_global, ax_3d_ais
    
    if not pg: return # Salir si la librería no cargó

    try:
        diametro = diametro_var.get()
        impulso = impulso_var.get()
        angulo = angulo_var.get()
    except Exception:
        return 

    velocidad = datos_ais_global['velocidad_impacto_kms']
    
    # 1. Simular Desviación (incluye ángulo)
    resultados_mitigacion = simular_desviacion(datos_ais_global, impulso, angulo)
    
    # 2. Calcular Consecuencias (usa el diámetro de la UI)
    consecuencias = calcular_consecuencias(diametro, velocidad)
    
    # 3. Actualizar UI de Métricas
    energia_label.config(text=f"{consecuencias['energia_mt']:.2f} Mt")
    crater_label.config(text=f"{consecuencias['crater_diametro_km']:.2f} km")
    sismo_label.config(text=f"M {consecuencias['sismico_magnitud']:.1f}")
    
    # 4. Actualizar Estado
    if resultados_mitigacion['impacto_evitado']:
        resultado_var_ais.set("ESTADO: ¡RIESGO MITIGADO! 🎉")
        estado_label.config(fg=COLOR_SEGURO, text=f"Impulso Efectivo: {resultados_mitigacion['impulso_efectivo']:.2f} km/s")
    else:
        resultado_var_ais.set("ESTADO: IMPACTO INEVITABLE ")
        estado_label.config(fg=COLOR_PELIGRO, text=f"Punto de Impacto: ({resultados_mitigacion['latitud_final']:.2f}, {resultados_mitigacion['longitud_final']:.2f})")
        
    # 5. Actualizar Visualizaciones
    pg.actualizar_visualizacion_3d(ax_3d_ais, datos_ais_global, resultados_mitigacion)
    actualizar_visualizacion_mapa(ax_mapa_ais, resultados_mitigacion, consecuencias, datos_ais_global['nombre'])


def iniciar_ventana_ais(datos_iniciales):
    """Crea y configura la ventana de la simulación AIS, inicializándola con datos reales."""
    global diametro_var, impulso_var, angulo_var, resultado_var_ais
    global ax_3d_ais, ax_mapa_ais
    global energia_label, crater_label, sismo_label, estado_label
    
    if not pg: 
        tk.messagebox.showerror("Error de Carga", "No se pudo cargar la librería G3D_AIS.py. Asegúrese de que el archivo existe.")
        return

    ventana_ais = tk.Toplevel(ventana)
    ventana_ais.title(f"AIS: Simulación de Mitigación - {datos_iniciales['nombre']}")
    ventana_ais.geometry("1200x750") 
    ventana_ais.configure(bg=COLOR_PANEL_OSCURO)
    ventana_ais.grab_set()

    # Inicialización de variables de control con datos REALES del asteroide
    diametro_var = tk.DoubleVar(value=datos_iniciales['diametro_metros'])
    impulso_var = tk.DoubleVar(value=0.0)
    angulo_var = tk.DoubleVar(value=0.0)
    resultado_var_ais = tk.StringVar(value="ESTADO: Inicializando...")

    # Layout
    main_frame = tk.Frame(ventana_ais, bg=COLOR_PANEL_OSCURO)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    main_frame.grid_columnconfigure(0, weight=2)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)

    # Panel de Gráficas (Izquierda)
    panel_graficas = tk.Frame(main_frame, bg=COLOR_PANEL_OSCURO)
    panel_graficas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    panel_graficas.rowconfigure(0, weight=1)
    panel_graficas.columnconfigure(0, weight=1)
    
    # 1. Gráfico 3D (AIS)
    fig_3d, ax_3d_ais = pg.inicializar_visualizacion_3d(panel_graficas, COLOR_PANEL_OSCURO, COLOR_TEXTO_CLARO, figsize=(7, 7))
    canvas_3d = FigureCavasTkAgg(fig_3d, master=panel_graficas)
    canvas_3d_widget = canvas_3d.get_tk_widget()
    canvas_3d_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    
    # Panel de Control y Resultados (Derecha)
    panel_control = tk.Frame(main_frame, bg=COLOR_FONDO_TABLA)
    panel_control.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

    tk.Label(panel_control, text=f"SISTEMA AIS\n{datos_iniciales['nombre']}", bg=COLOR_FONDO_TABLA, fg="yellow", font=("Arial", 14, "bold"), wraplength=250).pack(pady=10)
    
    # --- INFO ASTEROIDE ---
    info_ast = tk.Frame(panel_control, bg=COLOR_FONDO_TABLA)
    info_ast.pack(fill='x', padx=10, pady=5)
    tk.Label(info_ast, text=f"Velocidad Impacto (V): {datos_iniciales['velocidad_impacto_kms']:.2f} km/s", bg=COLOR_FONDO_TABLA, fg='cyan').pack(anchor='w')
    tk.Label(info_ast, text=f"Diámetro Inicial (D): {datos_iniciales['diametro_metros']:.0f} m", bg=COLOR_FONDO_TABLA, fg='cyan').pack(anchor='w')
    
    # --- CONTROLES DE ENTRADA ---
    tk.Label(panel_control, text="Diámetro Simulado (m)", bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO).pack(pady=(5,0))
    tk.Scale(panel_control, variable=diametro_var, from_=10, to=500, resolution=10, orient=tk.HORIZONTAL, length=250, bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO, command=actualizar_simulacion_ais).pack(pady=5)
    
    tk.Label(panel_control, text="Impulso Cinético (km/s)", bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO).pack(pady=(5,0))
    tk.Scale(panel_control, variable=impulso_var, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, length=250, bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO, command=actualizar_simulacion_ais).pack(pady=5)
    
    tk.Label(panel_control, text="Ángulo de Aplicación (°)", bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO).pack(pady=(5,0))
    tk.Scale(panel_control, variable=angulo_var, from_=0, to=45, resolution=1, orient=tk.HORIZONTAL, length=250, bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO, command=actualizar_simulacion_ais).pack(pady=5)
    
    tk.Button(panel_control, text="RUN SIMULACIÓN AIS", command=actualizar_simulacion_ais, bg=COLOR_SEGURO, fg=COLOR_PANEL_OSCURO, font=("Arial", 12, "bold")).pack(pady=10, fill='x', padx=10)

    # --- RESULTADOS DE SALIDA ---
    results_frame = tk.Frame(panel_control, bg=COLOR_FONDO_TABLA)
    results_frame.pack(pady=10, padx=10, fill='x')
    
    tk.Label(results_frame, text="Energía Impacto (Mt):", bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO, anchor="w").grid(row=0, column=0, sticky="w")
    energia_label = tk.Label(results_frame, text="---", bg=COLOR_FONDO_TABLA, fg=COLOR_PELIGRO, font=("Arial", 12, "bold"))
    energia_label.grid(row=0, column=1, sticky="w", padx=10)

    tk.Label(results_frame, text="Cráter Estimado (km):", bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO, anchor="w").grid(row=1, column=0, sticky="w")
    crater_label = tk.Label(results_frame, text="---", bg=COLOR_FONDO_TABLA, fg=COLOR_PELIGRO, font=("Arial", 12, "bold"))
    crater_label.grid(row=1, column=1, sticky="w", padx=10)

    tk.Label(results_frame, text="Sismo Estimado (M):", bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO, anchor="w").grid(row=2, column=0, sticky="w")
    sismo_label = tk.Label(results_frame, text="---", bg=COLOR_FONDO_TABLA, fg=COLOR_PELIGRO, font=("Arial", 12, "bold"))
    sismo_label.grid(row=2, column=1, sticky="w", padx=10)

    tk.Label(panel_control, textvariable=resultado_var_ais, bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO, font=("Arial", 16, "bold")).pack(pady=10)
    estado_label = tk.Label(panel_control, text="", bg=COLOR_FONDO_TABLA, fg=COLOR_TEXTO_CLARO)
    estado_label.pack()

    # --- GRÁFICO 2D (MAPA) ---
    fig_mapa = plt.Figure(figsize=(4, 4), facecolor=COLOR_FONDO_TABLA)
    ax_mapa_ais = fig_mapa.add_subplot(111, facecolor='darkblue')
    canvas_mapa = FigureCavasTkAgg(fig_mapa, master=panel_control)
    canvas_mapa_widget = canvas_mapa.get_tk_widget()
    canvas_mapa_widget.pack(pady=10)

    actualizar_simulacion_ais() # Ejecutar la simulación inicial


def lanzar_simulacion_ais_con_datos(nombre_asteroide, diccionario_asteroides):
    """
    Recupera los datos reales del asteroide y lanza la ventana de simulación AIS.
    """
    global datos_ais_global
    
    asteroid_id = diccionario_asteroides.get(nombre_asteroide)
    if not asteroid_id:
        asteroid_id = DATOS_ASTEROIDES_ESTATICOS.get(nombre_asteroide, "4_Vesta_ID_Fallback")
        if isinstance(asteroid_id, dict):
             asteroid_id = asteroid_id.get('id', '4_Vesta_ID_Fallback')
        print("Error: ID de asteroide no encontrado. Usando datos de respaldo.")

    # Obtener datos reales (diámetro, velocidad, orbitales)
    datos_iniciales = obtener_datos_reales_para_ais(asteroid_id)
    
    # Guardar datos iniciales para la simulación
    datos_ais_global = datos_iniciales
    
    # Iniciar la ventana y pasar los datos
    iniciar_ventana_ais(datos_iniciales)


# =========================================================
# FUNCIONES DE LA INTERFAZ PRINCIPAL (Modificadas)
# =========================================================

def terminarPrograma(event=None):
    ventana.destroy()
    sys.exit()

def scrollTabla(event):              
    global canvas_lista 
    canvas_lista.configure(scrollregion=canvas_lista.bbox("all"))


def click3D(event, nombre_asteroide, diccionario):                
    cargar_simulacion_3d(nombre_asteroide, diccionario)

# ... (otras funciones arriba)

def cargar_simulacion_3d(nombre_asteroide, diccionario):                       
    asteroid_id = diccionario.get(nombre_asteroide)
    if not asteroid_id:
        print(f"No se encontró el ID para el asteroide: {nombre_asteroide}")
        return
    
    if isinstance(asteroid_id, dict):
        asteroid_id = asteroid_id.get('id', 'ID Desconocido')

    ventana_3d = tk.Toplevel(ventana)
    ventana_3d.title(f"Visualización 3D Detallada: {nombre_asteroide}")
    ventana_3d.geometry("1100x700") 
    ventana_3d.configure(bg="#1E1E1E")
    ventana_3d.grab_set()

    main_frame = tk.Frame(ventana_3d, bg="#1E1E1E")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    main_frame.grid_columnconfigure(0, weight=3) 
    main_frame.grid_columnconfigure(1, weight=2) 
    main_frame.grid_rowconfigure(0, weight=1)

    graph_frame = tk.Frame(main_frame, bg="#1E1E1E")
    graph_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    data_frame = tk.Frame(main_frame, bg="#333333", padx=15, pady=15)
    data_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
    data_frame.grid_columnconfigure(0, weight=1) 

    tk.Label(data_frame, text="DATOS DETALLADOS DEL OBJETO (NEO)", font=("Arial", 14, "bold"), fg="yellow", bg="#333333").pack(pady=10)
    tk.Label(data_frame, text=f"ID: {asteroid_id}", font=("Courier New", 12), fg="cyan", bg="#333333").pack(pady=5)
    
    tk.Frame(data_frame, height=2, bg="#555555").pack(fill='x', pady=5)


    try:
        meteorito = Meteorito3D(NASA_API_KEY, asteroid_id)
        meteorito.obtener_datos() 
        
        def crear_etiqueta_dato(parent, clave, valor, unidad=""):
            tk.Label(parent, 
                     text=f"{clave}:", 
                     font=("Courier New", 12), 
                     fg="gray", 
                     bg="#333333", 
                     anchor="w").pack(fill='x')
            tk.Label(parent, 
                     text=f"{valor} {unidad}", 
                     font=("Courier New", 14, "bold"), 
                     fg="white", 
                     bg="#333333", 
                     anchor="w").pack(fill='x', padx=10, pady=(0, 5))

        diam_min = f"{meteorito.diameter_min_m:,.0f}" if meteorito.diameter_min_m is not None else "N/A"
        diam_max = f"{meteorito.diameter_max_m:,.0f}" if meteorito.diameter_max_m is not None else "N/A"
        crear_etiqueta_dato(data_frame, "Diámetro Min/Max", f"{diam_min} / {diam_max}", "m")
        
        mag_h = f"{meteorito.absolute_magnitude_h:.2f}" if meteorito.absolute_magnitude_h is not None else "N/A"
        crear_etiqueta_dato(data_frame, "Magnitud Absoluta (H)", mag_h)

        tk.Frame(data_frame, height=2, bg="#555555").pack(fill='x', pady=10)

        color_peligro = "red" if meteorito.is_hazardous else "lightgreen"
        texto_peligro = "SÍ" if meteorito.is_hazardous else "NO"
        tk.Label(data_frame, text="¿Potencialmente Peligroso?", font=("Arial", 12, "bold"), fg="yellow", bg="#333333").pack(fill='x', pady=5)
        tk.Label(data_frame, text=texto_peligro, font=("Arial", 18, "bold"), fg=color_peligro, bg="#333333", anchor="center").pack(fill='x', pady=5)

        tk.Frame(data_frame, height=2, bg="#555555").pack(fill='x', pady=10)
        
        tk.Label(data_frame, text="DATOS DE APROXIMACIÓN MÁS CERCANA", font=("Arial", 12, "bold"), fg="yellow", bg="#333333").pack(pady=5)
        
        crear_etiqueta_dato(data_frame, "Fecha", meteorito.closest_approach_date)

        vel_kmh = f"{meteorito.relative_velocity_kmh:,.0f}" if isinstance(meteorito.relative_velocity_kmh, float) else "N/A"
        crear_etiqueta_dato(data_frame, "Velocidad Relativa", vel_kmh, "km/h")
        
        dist_au = f"{meteorito.miss_distance_au:.4f}" if isinstance(meteorito.miss_distance_au, float) else "N/A"
        crear_etiqueta_dato(data_frame, "Distancia de Fallo", dist_au, "UA")


        meteorito.generar_puntos()
        fig = meteorito.graficar()

        canvas = FigureCavasTkAgg(fig, master=graph_frame)
        canvas.widget = canvas.get_tk_widget()
        canvas.widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()
        
    except Exception as e:
        print(f"Error al generar el gráfico 3D para {nombre_asteroide}: {e}")
        tk.Label(graph_frame, text=f"Error al generar el gráfico 3D o al obtener datos: {e}", fg="red", bg="#1E1E1E", font=("Arial", 14)).pack(pady=20)
    
    tk.Button(data_frame, text="Cerrar Visualización", command=ventana_3d.destroy,
             bg="#C0392B", fg="white", font=("Arial", 12, "bold")).pack(pady=20)


def crear_tabla_dinamica(parent_frame): 
    """Crea la tabla de asteroides dentro del frame_contenido."""
    
    datos_mostrar = dic if dic else DATOS_ASTEROIDES_ESTATICOS
    
    for widget in parent_frame.winfo_children():
        widget.destroy()

    row_start = 0 
    
    # Encabezados de Columna
    tk.Label(parent_frame, text="NOMBRE", font=("Courier New", 12, "bold"), bg=COLOR_FONDO_TABLA, fg="yellow").grid(row=row_start, column=0, padx=20, pady=5, sticky="w")
    tk.Label(parent_frame, text="ID", font=("Courier New", 12, "bold"), bg=COLOR_FONDO_TABLA, fg="yellow").grid(row=row_start, column=1, padx=20, pady=5, sticky="w")
    tk.Label(parent_frame, text="VISUALIZAR 3D", font=("Courier New", 12, "bold"), bg=COLOR_FONDO_TABLA, fg="yellow").grid(row=row_start, column=2, padx=20, pady=5, sticky="w")
    tk.Label(parent_frame, text="SIMULAR AIS", font=("Courier New", 12, "bold"), bg=COLOR_FONDO_TABLA, fg="yellow").grid(row=row_start, column=3, padx=20, pady=5, sticky="w")


    for i, (nombre, asteroid_id) in enumerate(datos_mostrar.items()):
        row_num = row_start + 1 + i
        
        # --- COLUMNA NOMBRE INTERACTIVA ---
        label_nombre = tk.Label(
            parent_frame, 
            text=nombre, 
            font=("Courier New", 12, "bold"), 
            bg=COLOR_FONDO_TABLA, 
            fg="white",
            cursor="hand2"
        )
        label_nombre.grid(row=row_num, column=0, padx=20, pady=2, sticky="w")
        label_nombre.bind(
            "<Button-1>", 
            lambda event, n=nombre: click3D(event, n, datos_mostrar)
        )
        
        # --- COLUMNA ID ---
        id_mostrar = asteroid_id
        if isinstance(asteroid_id, dict):
            id_mostrar = asteroid_id.get('id', 'ID Desconocido')
            
        tk.Label(parent_frame, text=id_mostrar, font=("Courier New", 12), bg=COLOR_FONDO_TABLA, fg="cyan").grid(row=row_num, column=1, padx=20, pady=2, sticky="w")
        
        # --- COLUMNA BOTÓN VISUALIZAR 3D ---
        tk.Button(
            parent_frame,
            text="Ver Objeto",
            command=lambda n=nombre: cargar_simulacion_3d(n, datos_mostrar),
            bg=COLOR_NASA_AZUL,
            fg="white",
            font=("Arial", 10)
        ).grid(row=row_num, column=2, padx=20, pady=2, sticky="w")
        
        # --- COLUMNA BOTÓN SIMULAR AIS (NUEVO) ---
        tk.Button(
            parent_frame,
            text="Simular Riesgo",
            command=lambda n=nombre: lanzar_simulacion_ais_con_datos(n, datos_mostrar),
            bg=COLOR_PELIGRO,
            fg="white",
            font=("Arial", 10, "bold")
        ).grid(row=row_num, column=3, padx=20, pady=2, sticky="w")


import os
from pathlib import Path

# ... (resto de las importaciones)

# =========================================================
# INTERFAZ GRÁFICA (TKINTER) - INICIO CON IMAGEN DE FONDO
# =========================================================

ventana = tk.Tk()
# ... (otras configuraciones)

# --- 1. CARGAR Y ESCALAR LA IMAGEN DE FONDO ---
try:
    # 1. Define la ruta absoluta al script actual
    directorio_actual = Path(__file__).parent 
    
    # 2. Combina la ruta del script con el nombre del archivo
    ruta_imagen_completa = directorio_actual / "descarga.jpg" 
    
    # 3. Abre la imagen usando la ruta completa
    imagen_fondo_pil = Image.open(ruta_imagen_completa)
    
    # ... (el resto del código de redimensionamiento se mantiene) ...
    
    ancho_ventana = ventana.winfo_screenwidth()
    alto_ventana = ventana.winfo_screenheight()
    
    imagen_fondo_pil = imagen_fondo_pil.resize((ancho_ventana, alto_ventana), Image.Resampling.LANCZOS)
    
    imagen_fondo_tk = ImageTk.PhotoImage(imagen_fondo_pil)
    
except NameError:
    # Este error ocurre si ejecutas el código en un entorno interactivo (como IDLE)
    # Volver a la ruta simple en ese caso
    try:
        imagen_fondo_pil = Image.open("descarga.jpg")
        ancho_ventana = ventana.winfo_screenwidth()
        alto_ventana = ventana.winfo_screenheight()
        imagen_fondo_pil = imagen_fondo_pil.resize((ancho_ventana, alto_ventana), Image.Resampling.LANCZOS)
        imagen_fondo_tk = ImageTk.PhotoImage(imagen_fondo_pil)
    except Exception as e:
        print(f"Error cargando la imagen de fondo: {e}. Se usará el color de fondo por defecto.")
        imagen_fondo_tk = None

except Exception as e:
    print(f"Error cargando la imagen de fondo: {e}. Se usará el color de fondo por defecto.")
    imagen_fondo_tk = None

# ... (El resto del código de la interfaz sigue igual) ...

# --- 2. CREAR EL LABEL DE FONDO Y COLOCARLO CON PLACE() ---
if imagen_fondo_tk:
    # Crear un Label para mostrar la imagen
    label_fondo = tk.Label(ventana, image=imagen_fondo_tk)
    
    # Usar PLACE para colocar la imagen en (0,0) y que ocupe todo el espacio.
    label_fondo.place(x=0, y=0, relwidth=1, relheight=1)

    # **CRUCIAL:** Mantener una referencia a la imagen para evitar que Python la elimine (Garbage Collection).
    ventana.imagen_fondo_referencia = imagen_fondo_tk

# --- 3. CREAR EL PANEL PRINCIPAL (Se colocará encima de la imagen de fondo) ---
panel_principal = tk.Frame(
    ventana,
    # Hacemos que el panel sea ligeramente transparente al fondo
    # En Tkinter, la única forma de "transparencia" es usar el mismo color de fondo,
    # pero aquí podemos usar un color oscuro y poner un nivel de opacidad si fuera una
    # librería externa. Como no lo es, dejamos el color sólido para un mejor contraste con la tabla.
    bg=COLOR_PANEL_OSCURO,
    bd=5,
    relief=tk.RIDGE
)
# Usamos pack() para este panel, que se coloca *encima* del Label de fondo.
panel_principal.pack(padx=50, pady=50, fill=tk.BOTH, expand=True)

panel_principal.columnconfigure(0, weight=1) 
panel_principal.rowconfigure(1, weight=1) 

# --- TÍTULO Y BOTONES DE ACCIÓN (Fila 0) ---
header_frame = tk.Frame(panel_principal, bg=COLOR_PANEL_OSCURO)
header_frame.grid(row=0, column=0, pady=10, sticky="ew")

tk.Label(
    header_frame,
    text="ASTEROIDES CERCANOS EN LOS ÚLTIMOS 7 DÍAS (DATOS API)",
    font=("Arial", 16, "bold"),
    bg=COLOR_PANEL_OSCURO,
    fg="yellow"
).pack(side=tk.LEFT, padx=20) 

primer_asteroide = next(iter(dic), next(iter(DATOS_ASTEROIDES_ESTATICOS)))
if isinstance(primer_asteroide, dict):
    nombre_btn = primer_asteroide 
else:
    nombre_btn = primer_asteroide




# --- ÁREA SCROLLABLE (Fila 1) ---

scroll_frame = tk.Frame(panel_principal, bg=COLOR_PANEL_OSCURO)
scroll_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))
scroll_frame.columnconfigure(0, weight=1)
scroll_frame.rowconfigure(0, weight=1)

canvas_lista = tk.Canvas(
    scroll_frame, 
    bg=COLOR_FONDO_TABLA,
    highlightthickness=0 
)
canvas_lista.grid(row=0, column=0, sticky="nsew")

scrollbar = tk.Scrollbar(
    scroll_frame, 
    orient="vertical", 
    command=canvas_lista.yview
)
scrollbar.grid(row=0, column=1, sticky="ns")

canvas_lista.configure(yscrollcommand=scrollbar.set)

# Usamos COLOR_FONDO_TABLA para el fondo del Frame que contiene los datos (para que la tabla sea uniforme)
frame_contenido = tk.Frame(canvas_lista, bg=COLOR_FONDO_TABLA)
canvas_lista.create_window((0, 0), window=frame_contenido, anchor="nw")

# Es esencial que el frame_contenido use el mismo fondo que las etiquetas de la tabla
frame_contenido.bind("<Configure>", lambda event: canvas_lista.configure(scrollregion=canvas_lista.bbox("all")))
canvas_lista.bind_all("<MouseWheel>", lambda event: canvas_lista.yview_scroll(int(-1*(event.delta/120)), "units"))


# Llenar el Frame Interno con los datos (La tabla)
crear_tabla_dinamica(frame_contenido)


if __name__ == "__main__":
    ventana.mainloop()