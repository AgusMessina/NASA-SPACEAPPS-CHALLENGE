import requests
import datetime


diccionarioAsteroides = {}

API_KEY = 'm6W81jDrD2TMVWarINf6yCbvesjH82cCUeGBFb41'       #API KEY de la NASA


fechaAux = datetime.timedelta(days=7)       #fecha de hace 7 dias
end_date = datetime.date.today()            #fecha actual que sirve lesgo

start_date = end_date - fechaAux


urlBusqueda = f'https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={API_KEY}'
response = requests.get(urlBusqueda)
data = response.json()

for fecha in data['near_earth_objects']:
    for asteroide in data['near_earth_objects'][fecha]:
        asteroideId = asteroide['id']
        nombre_asteroide = asteroide['name']
        diccionarioAsteroides[nombre_asteroide] = asteroideId

stringAux = input("Nombre del asteroide: ")
print(diccionarioAsteroides.get(stringAux, "Asteroide no encontrado"))
