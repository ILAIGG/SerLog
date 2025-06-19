import tkinter as tk
from tkinter import messagebox
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
import openrouteservice
from openrouteservice import convert

# VARIABLES GLOBALES
marcadores = []
direccion_deposito = "27°27'53.4S 58°46'04.7W"
geolocator = Nominatim(user_agent="tp_integrador")
ors_client = openrouteservice.Client(key="5b3ce3597851110001cf6248b291fdb25ae44917855d2eeb7288848d")
ruta_actual = None
seccion_actual = 0  # 0: Login, 1: Mapa y Añadir Dirección, 2: Ingresar Datos, 3: Resultados

# FUNCIONES DE LOGIN
def verificar_login():
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()
    if usuario == "admin" and contrasena == "1234":
        mostrar_seccion(1)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

# FUNCIONES DE MAPA Y RUTA (REUTILIZADAS DE test.py)
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
    coords.append((deposito_coords[1], deposito_coords[0]))
    for direccion, marcador in marcadores:
        coords.append((marcador.position[1], marcador.position[0]))
    try:
        ruta = ors_client.directions(coords, profile='driving-car', format='geojson')
        puntos = [(coord[1], coord[0]) for coord in ruta['features'][0]['geometry']['coordinates']]
        ruta_actual = map_widget.set_path(puntos)
    except Exception as e:
        messagebox.showerror("Error al calcular ruta", str(e))

def confirmar_ruta():
    if ruta_actual:
        mostrar_seccion(2)
    else:
        messagebox.showerror("Error", "Por favor, calcule la ruta primero.")

# FUNCIONES DE INGRESAR DATOS
def confirmar_datos():
    mostrar_seccion(3)

# FUNCIONES DE CAMBIO DE SECCIÓN
def mostrar_seccion(seccion):
    global seccion_actual
    seccion_actual = seccion
    for frame in [frame_login, frame_mapa, frame_datos, frame_resultados]:
        frame.pack_forget()
    if seccion == 0:
        frame_login.pack(fill=tk.BOTH, expand=True)
    elif seccion == 1:
        frame_mapa.pack(fill=tk.BOTH, expand=True)
    elif seccion == 2:
        frame_datos.pack(fill=tk.BOTH, expand=True)
    elif seccion == 3:
        frame_resultados.pack(fill=tk.BOTH, expand=True)

# INTERFAZ
root = tk.Tk()
root.title("SerLog - Aplicación de Logística")
root.geometry("1050x600")

# Frame de Login
frame_login = tk.Frame(root, bg="#1c2526")
label_titulo = tk.Label(frame_login, text="SerLog", fg="magenta", bg="#1c2526", font=("Arial", 20))
label_titulo.pack(pady=20)
label_inicio = tk.Label(frame_login, text="Inicio de Sesión", fg="white", bg="#444444", font=("Arial", 14))
label_inicio.pack(pady=10)
tk.Label(frame_login, text="Usuario", bg="#444444", fg="white").pack()
entry_usuario = tk.Entry(frame_login)
entry_usuario.pack(pady=5)
tk.Label(frame_login, text="Contraseña", bg="#444444", fg="white").pack()
entry_contrasena = tk.Entry(frame_login, show="*")
entry_contrasena.pack(pady=5)
tk.Button(frame_login, text="Iniciar Sesión", bg="magenta", fg="white", command=verificar_login).pack(pady=20)

# Frame de Mapa y Añadir Dirección
frame_mapa = tk.Frame(root)
panel_izquierdo = tk.Frame(frame_mapa, width=330, bg="#1c2526")
panel_izquierdo.pack(side=tk.LEFT, fill=tk.Y)
panel_izquierdo.pack_propagate(False)
tk.Label(panel_izquierdo, text="Dirección:", fg="white", bg="#1c2526").pack(padx=10, pady=(10, 0), anchor="w")
entry_direccion = tk.Entry(panel_izquierdo)
entry_direccion.pack(padx=10, pady=5)
tk.Button(panel_izquierdo, text="Agregar marcador", command=buscar_direccion).pack(padx=10, pady=5)
tk.Button(panel_izquierdo, text="Calcular Ruta Óptima", bg="lightblue", command=calcular_ruta_optima).pack(padx=10, pady=5)
tk.Label(panel_izquierdo, text="Direcciones agregadas:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
frame_lista = tk.Frame(panel_izquierdo)
frame_lista.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
canvas = tk.Canvas(frame_lista)
scrollbar = tk.Scrollbar(frame_lista, orient="vertical", command=canvas.yview)
frame_lista_scrollable = tk.Frame(canvas)
frame_lista_scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=frame_lista_scrollable, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tk.Button(panel_izquierdo, text="Confirmar", bg="magenta", fg="white", command=confirmar_ruta).pack(padx=10, pady=10)
map_widget = TkinterMapView(frame_mapa, width=720, height=600, corner_radius=0)
map_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
map_widget.set_position(-27.4698, -58.8344)
map_widget.set_zoom(13)
agregar_marcador(direccion_deposito, fijo=False)

# Frame de Ingresar Datos
frame_datos = tk.Frame(root, bg="#1c2526")
panel_datos = tk.Frame(frame_datos, width=330, bg="#1c2526")
panel_datos.pack(side=tk.LEFT, fill=tk.Y)
panel_datos.pack_propagate(False)
tk.Label(panel_datos, text="Ingresar Datos", fg="white", bg="#444444", font=("Arial", 14)).pack(pady=10)
tk.Label(panel_datos, text="Costo del combustible ($/L):", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Entry(panel_datos).pack(padx=10, pady=5)
tk.Label(panel_datos, text="Tipo de camión:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Entry(panel_datos).pack(padx=10, pady=5)
tk.Label(panel_datos, text="Peso de la carga (toneladas):", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Entry(panel_datos).pack(padx=10, pady=5)
tk.Label(panel_datos, text="Pago del chófer:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Entry(panel_datos).pack(padx=10, pady=5)
tk.Label(panel_datos, text="Dinero destinado a comida:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Entry(panel_datos).pack(padx=10, pady=5)
tk.Label(panel_datos, text="Dinero destinado a hotel:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Entry(panel_datos).pack(padx=10, pady=5)
tk.Label(panel_datos, text="Horario:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Entry(panel_datos).pack(padx=10, pady=5)
tk.Button(panel_datos, text="Confirmar", bg="magenta", fg="white", command=confirmar_datos).pack(padx=10, pady=10)
map_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # Mapa con ruta visible

# Frame de Resultados
frame_resultados = tk.Frame(root, bg="#1c2526")
panel_resultados = tk.Frame(frame_resultados, width=330, bg="#1c2526")
panel_resultados.pack(side=tk.LEFT, fill=tk.Y)
panel_resultados.pack_propagate(False)
tk.Label(panel_resultados, text="Resultados", fg="white", bg="#444444", font=("Arial", 14)).pack(pady=10)
tk.Label(panel_resultados, text="Gastos:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Combustible: # Aquí calcularás el costo", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Viativos:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Comida: # Aquí calcularás el costo", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Hotel: # Aquí calcularás el costo", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Peaje: # Aquí calcularás el costo", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Total: # Aquí calcularás el total", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Fecha y Hora:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Fecha: # Aquí asignarás la fecha", fg="white", bg="#1c2526").pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Hora: # Aquí asignarás la hora", fg="white", bg="#1c2526").pack(padx=10, pady=5)
map_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # Mapa con ruta visible

# Iniciar en la sección de Login
mostrar_seccion(0)

root.mainloop()