import tkinter as tk
from tkinter import messagebox
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
import openrouteservice
from openrouteservice import convert
from datetime import datetime
import uuid
import os
import platform

# VARIABLES GLOBALES
marcadores = []
direccion_deposito = "-27.464833, -58.767972"
geolocator = Nominatim(user_agent="tp_integrador")
ors_client = openrouteservice.Client(key="5b3ce3597851110001cf6248b291fdb25ae44917855d2eeb7288848d")
ruta_actual = None
seccion_actual = 0
datos_logistica = {}
id_registro = str(uuid.uuid4()).replace("-", "")
distancia_ruta = 0

# FUNCIONES DE LOGIN
def verificar_login():
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()
    if usuario == "admin" and contrasena == "1234":
        mostrar_seccion(1)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

# FUNCIONES DE MAPA Y RUTA
def geocodificar(direccion):
    try:
        location = geolocator.geocode(direccion)
        if location:
            print(f"Geocodificación exitosa para {direccion}: ({location.latitude}, {location.longitude})")
            return location.latitude, location.longitude
        else:
            print(f"Geocodificación fallida para {direccion}: No se encontró la ubicación")
            messagebox.showerror("Error", f"No se pudo geocodificar: {direccion}")
            return None
    except Exception as e:
        print(f"Error en geocodificación para {direccion}: {str(e)}")
        messagebox.showerror("Error", f"Error al geocodificar {direccion}: {str(e)}")
        return None

def agregar_marcador(direccion, fijo=False):
    coords = geocodificar(direccion)
    if not coords:
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
    global ruta_actual, distancia_ruta
    if ruta_actual:
        ruta_actual.delete()
        ruta_actual = None

    coords = []
    deposito_coords = geocodificar(direccion_deposito)
    if not deposito_coords:
        messagebox.showerror("Error", "No se pudo geocodificar el depósito. Verifique la dirección.")
        return

    # Convertimos a formato (lon, lat)
    coords_set = set()
    deposito_lonlat = (deposito_coords[1], deposito_coords[0])
    coords.append(deposito_lonlat)
    coords_set.add(deposito_lonlat)

    if len(marcadores) == 0:
        messagebox.showerror("Error", "Debe agregar al menos una dirección para calcular la ruta.")
        return

    for direccion, marcador in marcadores:
        coord = (marcador.position[1], marcador.position[0])
        if coord not in coords_set:
            coords.append(coord)
            coords_set.add(coord)

    if len(coords) < 2:
        messagebox.showerror("Error", "Los puntos de la ruta son idénticos. Agregue una dirección diferente al depósito.")
        return

    try:
        print(f"Calculando ruta con coordenadas: {coords}")
        ruta = ors_client.directions(coords, profile='driving-car', format='geojson')
        if 'features' in ruta and ruta['features'][0]['properties']['segments']:
            puntos = [(coord[1], coord[0]) for coord in ruta['features'][0]['geometry']['coordinates']]
            ruta_actual = map_widget.set_path(puntos)
            distancia_ruta = ruta['features'][0]['properties']['segments'][0]['distance'] / 1000
            print(f"Distancia calculada: {distancia_ruta:.2f} km")
            messagebox.showinfo("Éxito", f"Ruta calculada correctamente. Distancia: {distancia_ruta:.2f} km")
        else:
            raise Exception("La respuesta de la ruta no contiene datos válidos para calcular la distancia.")
    except Exception as e:
        print(f"Error al calcular la ruta: {str(e)}")
        messagebox.showerror("Error", f"No se pudo calcular la ruta: {str(e)}")
        distancia_ruta = 0


def confirmar_ruta():
    if ruta_actual and distancia_ruta > 0:
        mostrar_seccion(2)
    else:
        messagebox.showerror("Error", "Por favor, calcule la ruta primero.")

# FUNCIONES DE INGRESAR DATOS
def confirmar_datos():
    try:
        costo_combustible = costo_combustible_var.get()
        tipo_camion = tipo_camion_var.get()
        peso_carga = peso_carga_var.get()
        pago_chofer = pago_chofer_var.get()
        dinero_comida = dinero_comida_var.get()
        dinero_hotel = dinero_hotel_var.get()
        horario = horario_var.get()

        if costo_combustible <= 0 or peso_carga <= 0 or pago_chofer <= 0 or dinero_comida < 0 or dinero_hotel < 0:
            messagebox.showerror("Error", "Los valores numéricos deben ser mayores a cero (o no negativos para comida y hotel).")
            return

        if not tipo_camion or not horario:
            messagebox.showerror("Error", "El tipo de camión y el horario no pueden estar vacíos.")
            return

        global datos_logistica
        datos_logistica = {
            "costo_combustible": costo_combustible,
            "tipo_camion": tipo_camion,
            "peso_carga": peso_carga,
            "pago_chofer": pago_chofer,
            "dinero_comida": dinero_comida,
            "dinero_hotel": dinero_hotel,
            "horario": horario,
            "fecha": datetime.now().strftime("%d-%m-%Y"),
            "hora": datetime.now().strftime("%H.%M.%S")
        }

        messagebox.showinfo("Éxito", "Datos guardados correctamente.")
        mostrar_seccion(3)

    except tk.TclError:
        messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos en los campos correspondientes.")

def actualizar_resultados():
    if 'datos_logistica' not in globals() or not datos_logistica:
        messagebox.showerror("Error", "No se han ingresado datos de logística.")
        return
    if distancia_ruta == 0:
        messagebox.showerror("Error", "No se ha calculado una ruta válida.")
        return

    peso_carga = datos_logistica["peso_carga"]
    precio_combustible = datos_logistica["costo_combustible"]
    costo_comida = datos_logistica["dinero_comida"]
    costo_hotel = datos_logistica["dinero_hotel"]
    costo_peaje = 100.0

    combustible_consumido = 0.3 * distancia_ruta + 0.02 * distancia_ruta * peso_carga
    costo_combustible = combustible_consumido * precio_combustible
    costo_total = costo_combustible + costo_comida + costo_hotel + costo_peaje

    lbl_combustible.config(text=f"Combustible: ${costo_combustible:.2f}")
    lbl_comida.config(text=f"Comida: ${costo_comida:.2f}")
    lbl_hotel.config(text=f"Hotel: ${costo_hotel:.2f}")
    lbl_peaje.config(text=f"Peaje: ${costo_peaje:.2f}")
    lbl_total.config(text=f"Total: ${costo_total:.2f}")
    lbl_fecha.config(text=f"Fecha: {datos_logistica['fecha']}")
    lbl_hora.config(text=f"Hora: {datos_logistica['hora']}")

def guardar_datos():
    if not datos_logistica:
        messagebox.showerror("Error", "No hay datos para guardar.")
        return

    fecha_hora = f"{datos_logistica['fecha'].replace('-', '')}_{datos_logistica['hora'].replace(':', '')}"
    nombre_archivo = f"{id_registro}_{fecha_hora}.txt"

    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write("Registro de Logística\n")
            archivo.write(f"ID Registro: {id_registro}\n")
            archivo.write(f"Fecha: {datos_logistica['fecha']}\n")
            archivo.write(f"Hora: {datos_logistica['hora']}\n")
            archivo.write(f"Distancia de la ruta: {distancia_ruta:.2f} km\n")
            archivo.write("\nDatos Ingresados:\n")
            for clave, valor in datos_logistica.items():
                archivo.write(f"{clave.replace('_', ' ').title()}: {valor}\n")
            combustible_consumido = 0.3 * distancia_ruta + 0.02 * distancia_ruta * datos_logistica["peso_carga"]
            costo_combustible = combustible_consumido * datos_logistica["costo_combustible"]
            archivo.write(f"Costo Combustible: ${costo_combustible:.2f}\n")

        sistema = platform.system()
        if sistema == "Windows":
            os.startfile(nombre_archivo)
        else:
            messagebox.showwarning("Advertencia", f"Sistema operativo {sistema} no soportado para abrir el archivo automáticamente.")

        messagebox.showinfo("Éxito", f"Datos guardados en {nombre_archivo}")
        mostrar_seccion(1)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

def mostrar_seccion(seccion):
    global seccion_actual
    if seccion == 3 and distancia_ruta == 0:
        messagebox.showerror("Error", "Debe calcular una ruta válida en la sección de mapa antes de ver los resultados.")
        return
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
        actualizar_resultados()

# INTERFAZ
root = tk.Tk()
root.title("SerLog - Aplicación de Logística")
root.geometry("1050x600")

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

frame_datos = tk.Frame(root, bg="#1c2526")
panel_datos = tk.Frame(frame_datos, width=330, bg="#1c2526")
panel_datos.pack(side=tk.LEFT, fill=tk.Y)
panel_datos.pack_propagate(False)

tk.Label(panel_datos, text="Ingresar Datos", fg="white", bg="#444444", font=("Arial", 14)).pack(pady=10)

costo_combustible_var = tk.DoubleVar()
tipo_camion_var = tk.StringVar()
peso_carga_var = tk.DoubleVar()
pago_chofer_var = tk.DoubleVar()
dinero_comida_var = tk.DoubleVar()
dinero_hotel_var = tk.DoubleVar()
horario_var = tk.StringVar()

tk.Label(panel_datos, text="Costo del combustible ($/L):", fg="white", bg="#1c2526").pack(padx=10, pady=5)
entry_costo_combustible = tk.Entry(panel_datos, textvariable=costo_combustible_var)
entry_costo_combustible.pack(padx=10, pady=5)

tk.Label(panel_datos, text="Tipo de camión:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
entry_tipo_camion = tk.Entry(panel_datos, textvariable=tipo_camion_var)
entry_tipo_camion.pack(padx=10, pady=5)

tk.Label(panel_datos, text="Peso de la carga (toneladas):", fg="white", bg="#1c2526").pack(padx=10, pady=5)
entry_peso_carga = tk.Entry(panel_datos, textvariable=peso_carga_var)
entry_peso_carga.pack(padx=10, pady=5)

tk.Label(panel_datos, text="Pago del chófer:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
entry_pago_chofer = tk.Entry(panel_datos, textvariable=pago_chofer_var)
entry_pago_chofer.pack(padx=10, pady=5)

tk.Label(panel_datos, text="Dinero destinado a comida:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
entry_dinero_comida = tk.Entry(panel_datos, textvariable=dinero_comida_var)
entry_dinero_comida.pack(padx=10, pady=5)

tk.Label(panel_datos, text="Dinero destinado a hotel:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
entry_dinero_hotel = tk.Entry(panel_datos, textvariable=dinero_hotel_var)
entry_dinero_hotel.pack(padx=10, pady=5)

tk.Label(panel_datos, text="Horario:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
entry_horario = tk.Entry(panel_datos, textvariable=horario_var)
entry_horario.pack(padx=10, pady=5)

tk.Button(panel_datos, text="Confirmar", bg="magenta", fg="white", command=confirmar_datos).pack(padx=10, pady=10)

imagen_datos = tk.Label(frame_datos)
imagen_datos.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
imagen_datos.image = tk.PhotoImage(file="preparativo_envio.png")
imagen_datos.config(image=imagen_datos.image)

frame_resultados = tk.Frame(root, bg="#1c2526")
panel_resultados = tk.Frame(frame_resultados, width=330, bg="#1c2526")
panel_resultados.pack(side=tk.LEFT, fill=tk.Y)
panel_resultados.pack_propagate(False)

tk.Label(panel_resultados, text="Resultados", fg="white", bg="#444444", font=("Arial", 14)).pack(pady=10)

tk.Label(panel_resultados, text="Gastos:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
lbl_combustible = tk.Label(panel_resultados, text="Combustible: $0.00", fg="white", bg="#1c2526")
lbl_combustible.pack(padx=10, pady=5)
tk.Label(panel_resultados, text="Viaticos:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
lbl_comida = tk.Label(panel_resultados, text="Comida: $0.00", fg="white", bg="#1c2526")
lbl_comida.pack(padx=10, pady=5)
lbl_hotel = tk.Label(panel_resultados, text="Hotel: $0.00", fg="white", bg="#1c2526")
lbl_hotel.pack(padx=10, pady=5)
lbl_peaje = tk.Label(panel_resultados, text="Peaje: $0.00", fg="white", bg="#1c2526")
lbl_peaje.pack(padx=10, pady=5)
lbl_total = tk.Label(panel_resultados, text="Total: $0.00", fg="white", bg="#1c2526")
lbl_total.pack(padx=10, pady=5)

tk.Label(panel_resultados, text="Fecha y Hora:", fg="white", bg="#1c2526").pack(padx=10, pady=5)
lbl_fecha = tk.Label(panel_resultados, text="Fecha: --/--/----", fg="white", bg="#1c2526")
lbl_fecha.pack(padx=10, pady=5)
lbl_hora = tk.Label(panel_resultados, text="Hora: --:--", fg="white", bg="#1c2526")
lbl_hora.pack(padx=10, pady=5)

tk.Button(panel_resultados, text="Envio", bg="green", fg="white", command=guardar_datos).pack(padx=10, pady=10)

imagen_resultados = tk.Label(frame_resultados)
imagen_resultados.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
imagen_resultados.image = tk.PhotoImage(file="truck.png")
imagen_resultados.config(image=imagen_resultados.image)

mostrar_seccion(1)
root.mainloop()