import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 

# --- CONSTANTES ---
RADIO_ORBITA_TIERRA = 1.0 # 1.0 UA

# --- VARIABLES GLOBALES PARA REFERENCIAS DE OBJETOS ---
plano_tierra = None
plano_tierra_x = None  
plano_tierra_y = None  
lineas_ast = [] 
puntos_ast = [] 

# --- FUNCIÓN: CÁLCULO DE PUNTOS ORBITALES ---
def generar_puntos_orbita(a, e, i, num_puntos=360):
    """Genera puntos (x, y, z) de una órbita Kepleriana simplificada."""
    
    f = np.linspace(0, 2 * np.pi, num_puntos) 
    r = a * (1 - e**2) / (1 + e * np.cos(f))
    
    X_orb = r * np.cos(f)
    Y_orb = r * np.sin(f)
    
    i_rad = np.deg2rad(i)
    
    x = X_orb
    y = Y_orb * np.cos(i_rad)
    z = Y_orb * np.sin(i_rad)
    
    return x, y, z

def generar_orbita_tierra(num_puntos=100):
    """Genera una órbita circular simple para la Tierra."""
    theta = np.linspace(0, 2 * np.pi, num_puntos)
    x = RADIO_ORBITA_TIERRA * np.cos(theta)
    y = RADIO_ORBITA_TIERRA * np.sin(theta)
    z = np.zeros_like(x)
    return x, y, z

# --- FUNCIÓN: INICIALIZACIÓN DEL GRÁFICO 3D ---
def inicializar_visualizacion_3d(parent_frame, COLOR_FONDO_CLARO, COLOR_TEXTO_CLARO, figsize=(6, 6)):
    """Crea la figura de Matplotlib, los ejes 3D, y el plano deformable."""
    global plano_tierra, plano_tierra_x, plano_tierra_y
    
    fig = plt.Figure(figsize=figsize, facecolor=COLOR_FONDO_CLARO)
    ax = fig.add_subplot(111, projection='3d', facecolor='black') 
    
    ax.set_title("ANÁLISIS DE TRAYECTORIA ORBITAL (AIS)", color=COLOR_TEXTO_CLARO, fontsize=10)
    
    limite = 2.0 
    ax.set_xlim([-limite, limite])
    ax.set_ylim([-limite, limite])
    ax.set_zlim([-limite, limite])
    ax.set_axis_off() 
    
    # Objetos estáticos
    ax.scatter(0, 0, 0, color='#FFD700', s=300, label='Sol') 
    x_t, y_t, z_t = generar_orbita_tierra()
    ax.plot(x_t, y_t, z_t, color='#00BFFF', linestyle='--', alpha=0.3) 
    ax.scatter([RADIO_ORBITA_TIERRA], [0], [0], color='#00BFFF', s=50, label='Tierra')
    
    # Crear la malla base del plano (Tierra)
    lim_mesh = 2.0 
    u = np.linspace(-lim_mesh, lim_mesh, 30) 
    v = np.linspace(-lim_mesh, lim_mesh, 30)
    x, y = np.meshgrid(u, v)
    z = np.zeros_like(x) 
    
    plano_tierra_x = x
    plano_tierra_y = y
    
    plano_tierra = ax.plot_surface(x, y, z, color='#00BFFF', alpha=0.1, linewidth=0)
    
    return fig, ax

# --- FUNCIÓN: ACTUALIZACIÓN DINÁMICA DEL GRÁFICO 3D (con Deformación) ---
def actualizar_visualizacion_3d(ax, datos_ast, resultados_mitigacion):
    """Limpia los objetos dinámicos y dibuja las nuevas trayectorias, aplicando la deformación al plano."""
    global plano_tierra, lineas_ast, puntos_ast
    global plano_tierra_x, plano_tierra_y
    
    # 1. LIMPIEZA EXPLÍCITA
    for line in lineas_ast:
        line.remove()
    lineas_ast.clear()
    for coll in puntos_ast:
        coll.remove()
    puntos_ast.clear()
    
    # 2. Lógica de deformación del plano
    plano_tierra.remove() 
    
    x_data = plano_tierra_x
    y_data = plano_tierra_y
    
    if not resultados_mitigacion.get('impacto_evitado', False):
        # Deformación (simula perturbación gravitacional)
        factor_deformacion = 0.0005 * datos_ast.get('diametro_metros', 300) 
        distancia = np.sqrt(x_data**2 + y_data**2)
        z_deformado = -factor_deformacion * np.exp(-1 * (distancia)**2)
        
        plano_tierra = ax.plot_surface(x_data, y_data, z_deformado, 
                                       color='#FF4500', alpha=0.5, linewidth=0) 
    else:
        # Restauración (Plano Z=0)
        z_restaurado = np.zeros_like(x_data) 
        plano_tierra = ax.plot_surface(x_data, y_data, z_restaurado, 
                                       color='#00BFFF', alpha=0.1, linewidth=0) 
        
    # 3. DIBUJAR TRAYECTORIAS Y GUARDAR REFERENCIAS
    
    # Trayectoria Original
    a_orig = datos_ast.get('a', 1.5)
    e_orig = datos_ast.get('e', 0.3)
    i_orig = datos_ast.get('i', 5.0)

    x_orig, y_orig, z_orig = generar_puntos_orbita(a_orig, e_orig, i_orig)
    line_orig, = ax.plot(x_orig, y_orig, z_orig, color='red', linewidth=1.5, label='Original') 
    lineas_ast.append(line_orig)
    
    if resultados_mitigacion.get('impacto_evitado', False):
        # Trayectoria Desviada
        a_mod = resultados_mitigacion.get('a_modificado', a_orig)
        x_mod, y_mod, z_mod = generar_puntos_orbita(a_mod, e_orig, i_orig)
        
        line_mod, = ax.plot(x_mod, y_mod, z_mod, color='lime', linewidth=1.5, label='Desviada')
        lineas_ast.append(line_mod)
        
        # Punto Final Desviado
        scatter_mod = ax.scatter([x_mod[-1]], [y_mod[-1]], [z_mod[-1]], color='lime', s=70, marker='^', label='NEO Final')
        puntos_ast.append(scatter_mod)
    else:
        # Punto Final de Impacto
        scatter_orig = ax.scatter([x_orig[-1]], [y_orig[-1]], [z_orig[-1]], color='red', s=70, marker='o', label='NEO Final') 
        puntos_ast.append(scatter_orig)
        
    ax.figure.canvas.draw()