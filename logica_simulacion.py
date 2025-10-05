import requests
import datetime
import numpy as np

# --- CONFIGURACIÓN DE LA API DE NASA ---
API_KEY = 'm6W81jDrD2TMVWarINf6yCbvesjH82cCUeGBFb41'
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=7)
urlBusqueda = f'https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={API_KEY}'

# --- LÓGICA DE API (Para la lista principal) ---
diccionarioAsteroides = {}
try:
    response = requests.get(urlBusqueda, timeout=5)
    response.raise_for_status() # Lanza error para códigos 4xx/5xx
    data = response.json()
    for fecha in data.get('near_earth_objects', {}):
        for asteroide in data['near_earth_objects'][fecha]:
            asteroideId = asteroide['id']
            nombre_asteroide = asteroide['name']
            diccionarioAsteroides[nombre_asteroide] = asteroideId
except requests.exceptions.RequestException as e:
    # Si la API falla, el diccionario queda vacío
    print(f"Error al conectar con la API de NASA: {e}. El diccionario de asteroides está vacío.")


# --- CONSTANTES Y LÓGICA PARA LA SIMULACIÓN AIS ---
DENSIDAD_ROCA = 3000 # kg/m^3
JOULES_POR_MEGATON = 4.184e15 # Conversión de energía (TNT)

def obtener_datos_reales_para_ais(asteroid_id):
    """
    Recupera el diámetro, velocidad y datos orbitales de un asteroide específico 
    de la API de la NASA para usar en la simulación AIS.
    """
    url = f'https://api.nasa.gov/neo/rest/v1/neo/{asteroid_id}?api_key={API_KEY}'
    
    # Datos de respaldo en caso de fallo de API
    fallback_data = {
        'nombre': "Asteroide Desconocido",
        'diametro_metros': 300.0,        
        'velocidad_impacto_kms': 15.0, 
        'latitud_impacto': 40.71,      
        'longitud_impacto': -74.00,    
        'a': 1.5, # Semi-eje mayor (UA)
        'e': 0.3, # Excentricidad
        'i': 5.0, # Inclinación (grados)
    }

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Extracción de velocidad (del primer close_approach)
        velocidades = data.get('close_approach_data', [])
        velocidad_impacto_kms = fallback_data['velocidad_impacto_kms']
        if velocidades:
            v_rel = velocidades[0]['relative_velocity']['kilometers_per_second']
            velocidad_impacto_kms = float(v_rel)
        
        # Extracción de diámetro
        diametro_metros = data['estimated_diameter']['meters']['estimated_diameter_max']
        
        # Extracción de datos orbitales para 3D
        datos_orbitales = data.get('orbital_data', {})
        a = float(datos_orbitales.get('semi_major_axis', fallback_data['a']))
        e = float(datos_orbitales.get('eccentricity', fallback_data['e']))
        i = float(datos_orbitales.get('inclination', fallback_data['i']))

        return {
            'nombre': data['name'],
            'diametro_metros': diametro_metros,        
            'velocidad_impacto_kms': velocidad_impacto_kms, 
            'latitud_impacto': fallback_data['latitud_impacto'], # Punto de impacto simulado (NYC)
            'longitud_impacto': fallback_data['longitud_impacto'], # Punto de impacto simulado (NYC)
            'a': a, 
            'e': e, 
            'i': i, 
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de NEO {asteroid_id}: {e}. Usando valores por defecto.")
        return fallback_data

def calcular_consecuencias(diametro_m, velocidad_kms):
    """Calcula las consecuencias físicas del impacto (energía, cráter, sismo)."""
    
    radio = diametro_m / 2
    volumen = (4/3) * np.pi * (radio ** 3)
    masa_kg = volumen * DENSIDAD_ROCA
    
    velocidad_ms = velocidad_kms * 1000 
    energia_joules = 0.5 * masa_kg * (velocidad_ms ** 2)
    energia_mt = energia_joules / JOULES_POR_MEGATON

    if energia_mt > 0:
        crater_diametro_km = 0.05 * (energia_mt ** (1/3.4)) 
        sismico_magnitud = 0.67 * np.log10(energia_joules) - 5.8
        
        # Mejoras de simulación: Radio de Vientos y Calor
        radio_vientos_km = 1.0 * (energia_mt ** (1/3)) 
        radio_calor_km = 0.5 * (energia_mt ** (1/3)) 
    else:
        crater_diametro_km = 0.0
        sismico_magnitud = 0.0
        radio_vientos_km = 0.0
        radio_calor_km = 0.0
    
    return {
        'masa_kg': masa_kg,
        'energia_mt': energia_mt,
        'crater_diametro_km': crater_diametro_km,
        'sismico_magnitud': sismico_magnitud,
        'radio_vientos_km': radio_vientos_km,
        'radio_calor_km': radio_calor_km
    }

def simular_desviacion(datos_orbitales, impulso_kms, angulo_aplicacion_deg=0):
    """Modela el cambio de órbita debido a un impulso cinético con ángulo."""
    
    impulso_efectivo = impulso_kms * np.cos(np.deg2rad(angulo_aplicacion_deg))
    
    v_original = datos_orbitales['velocidad_impacto_kms']
    v_nueva = v_original - impulso_efectivo
    
    a_modificado = datos_orbitales['a'] * (1 + (v_nueva / v_original - 1) * 0.5)
    
    # Lógica de mitigación: Impulso mínimo para desvío
    if impulso_efectivo >= 0.15: 
        impacto_evitado = True
        # Nuevo punto de impacto simulado (Océano)
        nuevo_punto_lat = datos_orbitales['latitud_impacto'] - 20 
        nuevo_punto_lon = datos_orbitales['longitud_impacto'] - 40
    else:
        impacto_evitado = False
        # Mantiene el punto de impacto original simulado (NYC)
        nuevo_punto_lat = datos_orbitales['latitud_impacto']
        nuevo_punto_lon = datos_orbitales['longitud_impacto']

    return {
        'a_modificado': a_modificado,
        'impacto_evitado': impacto_evitado,
        'latitud_final': nuevo_punto_lat,
        'longitud_final': nuevo_punto_lon,
        'impulso_efectivo': impulso_efectivo
    }