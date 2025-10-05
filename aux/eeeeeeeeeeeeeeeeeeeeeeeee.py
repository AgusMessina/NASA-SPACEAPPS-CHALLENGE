import datetime
import tkinter as tk

fecha_hoy = datetime.date.today() #fecha actual que sirve lesgo
resta_fecha = datetime.timedelta(days=7)

fechalol = fecha_hoy - resta_fecha
print("Hoy:", fecha_hoy)
print("Hace 7 dias:", fechalol)

#ahora para cambiar el texto segun el momento del dia xdnt
def saludemos():
    horaYA = datetime.datetime.now().hour

    if 6 <= horaYA < 12:
        return "Buenos días!"
    if 12 <= horaYA < 19:
        return "Buenas tardes!"
    elif 19 <= horaYA:
        return "Buenas noches!"

def actualiza(label):
    saludo_ahora = saludemos()
    label.config(text=saludo_ahora)
    label.after(60000, actualiza, label) #eeeeeee actualiza dsp de 1 min

#mostrar en una ventana (la concha de tu madre ia)

ventana = tk.Tk()
ventana.title("Eh???") #titulo lol
ventana.geometry("300x100") #tam

#config ventana
saludo = tk.Label(ventana, text="joputa", font=("Lucida Console", 20))
saludo.pack(pady=20)

actualiza(saludo)
ventana.mainloop()