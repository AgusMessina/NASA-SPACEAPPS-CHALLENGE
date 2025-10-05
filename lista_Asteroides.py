import requests
import datetime


diccionarioAsteroides = {}

API_KEY = 'm6W81jDrD2TMVWarINf6yCbvesjH82cCUeGBFb41'       #API KEY de la NASA


end_date = datetime.date.today()            #fecha actual que sirve lesgo
start_date = end_date - datetime.timedelta(days=7)  # Fecha de hace 7 días


urlBusqueda = f'https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={API_KEY}'        #Busqueda de meteoritos desde "start_date" hasta "end_date"
response = requests.get(urlBusqueda)
data = response.json()


for fecha in data['near_earth_objects']:                    #Recuperamos las fechas
    for asteroide in data['near_earth_objects'][fecha]:     #Recuperamos los datos de los asteroides
        asteroideId = asteroide['id']                       #Recuperamos el ID del asteroide
        nombre_asteroide = asteroide['name']                #Recuperamos el nombre de cada asteroide
        diccionarioAsteroides[nombre_asteroide] = asteroideId       #Guardamos en el diccionario, los asteroides como ID, teniendo su llave los nombres
        
#print(diccionarioAsteroides.keys(),'\n')
#stringAux = input("Nombre del asteroide: ")
#print(diccionarioAsteroides.get(stringAux, "Asteroide no encontrado"))