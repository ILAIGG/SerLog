import tkinter as tk
from tkinter import messagebox
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
import openrouteservice
from openrouteservice import convert

#VARIABLES
marcadores = []
direccion_deposito = "27°27'53.4S 58°46'04.7W"
geolocator = Nominatim(user_agent="tp_integrador")
ors_client = openrouteservice.Client(key="5b3ce3597851110001cf6248b291fdb25ae44917855d2eeb7288848d")
ruta_actual = None

#FUNCIONES
def geocodificar(direccion):
    try:
        location = geolocator.geocode(direccion)
        if location:
            return location.latitude, location.longitude
    except:
        return None

def agregar_marcador(direccion, fijo=False):
    coords = geocodificar(direccion)
    if not coords:
        messagebox.showerror("Error", f"No se pudo geocodificar: {direccion}")
        return
    lat, lon = coords
    marcador = map_widget.set_marker(lat, lon, text=direccion)
    if fijo:
        marcador.fijo = True
    else:
        marcador.fijo = False
        marcadores.append((direccion, marcador))
    actualizar_lista()

def buscar_direccion():
    direccion = entry_direccion.get().strip()
    if not direccion:
        messagebox.showerror("Error", "Ingrese una dirección válida.")
        return
    agregar_marcador(direccion)

def mover_elemento(indice, sentido):
    nuevo_indice = indice + sentido
    if 0 <= nuevo_indice < len(marcadores):
        marcadores[indice], marcadores[nuevo_indice] = marcadores[nuevo_indice], marcadores[indice]
        actualizar_lista()

def eliminar_marcador(indice):
    direccion, marcador = marcadores.pop(indice)
    marcador.delete()
    actualizar_lista()

def actualizar_lista():
    for widget in frame_lista_scrollable.winfo_children():
        widget.destroy()
    
    for i, (direccion, marcador) in enumerate(marcadores):
        fila = tk.Frame(frame_lista_scrollable)
        fila.pack(fill=tk.X, pady=2)

        lbl = tk.Label(fila, text=direccion, anchor="w", width=22)
        lbl.pack(side=tk.LEFT, padx=3)

        btn_up = tk.Button(fila, text="⬆", width=2, command=lambda i=i: mover_elemento(i, -1))
        btn_up.pack(side=tk.LEFT, padx=1)
        btn_down = tk.Button(fila, text="⬇", width=2, command=lambda i=i: mover_elemento(i, 1))
        btn_down.pack(side=tk.LEFT, padx=1)
        btn_delete = tk.Button(fila, text="❌", width=2, command=lambda i=i: eliminar_marcador(i))
        btn_delete.pack(side=tk.LEFT, padx=1)

def calcular_ruta_optima():
    global ruta_actual

    if ruta_actual:
        ruta_actual.delete()
        ruta_actual = None

    coords = []
    deposito_coords = geocodificar(direccion_deposito)
    if not deposito_coords:
        messagebox.showerror("Error", "No se pudo geocodificar el depósito.")
        return
    coords.append((deposito_coords[1], deposito_coords[0]))  # longitud, latitud

    for direccion, marcador in marcadores:
        coords.append((marcador.position[1], marcador.position[0]))  # longitud, latitud

    try:
        ruta = ors_client.directions(coords, profile='driving-car', format='geojson')
        puntos = [(coord[1], coord[0]) for coord in ruta['features'][0]['geometry']['coordinates']]
        ruta_actual = map_widget.set_path(puntos)
    except Exception as e:
        messagebox.showerror("Error al calcular ruta", str(e))

#INTERFAZ
root = tk.Tk()
root.title("TP Integrador - Múltiples Marcadores")
root.geometry("1050x600")  # Aumentado ancho

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

#Panel izquierdo
panel_izquierdo = tk.Frame(main_frame, width=330, bg="#f0f0f0")
panel_izquierdo.pack(side=tk.LEFT, fill=tk.Y)
panel_izquierdo.pack_propagate(False)

label = tk.Label(panel_izquierdo, text="Dirección:", bg="#f0f0f0", anchor="w")
label.pack(padx=10, pady=(10, 0), anchor="w")

entry_direccion = tk.Entry(panel_izquierdo, width=35)
entry_direccion.pack(padx=10, pady=5)

btn_buscar = tk.Button(panel_izquierdo, text="Agregar marcador", command=buscar_direccion)
btn_buscar.pack(padx=10, pady=5)

btn_ruta = tk.Button(panel_izquierdo, text="Calcular Ruta Óptima", bg="lightblue", command=calcular_ruta_optima)
btn_ruta.pack(padx=10, pady=(0, 15))

label_lista = tk.Label(panel_izquierdo, text="Direcciones agregadas:", bg="#f0f0f0", anchor="w")
label_lista.pack(padx=10, pady=(5, 0), anchor="w")

#Lista con scroll
frame_lista = tk.Frame(panel_izquierdo)
frame_lista.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

canvas = tk.Canvas(frame_lista)
scrollbar = tk.Scrollbar(frame_lista, orient="vertical", command=canvas.yview)
frame_lista_scrollable = tk.Frame(canvas)

frame_lista_scrollable.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=frame_lista_scrollable, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

#Panel derecho (mapa)
map_widget = TkinterMapView(main_frame, width=720, height=600, corner_radius=0)
map_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

#Posición inicial
map_widget.set_position(-27.4698, -58.8344)
map_widget.set_zoom(13)

#Agregar el marcador del depósito (Acá dejamos en False, pero si el cliente lo solicita, se puede cambiar a True)
agregar_marcador(direccion_deposito, fijo=False)

root.mainloop()
