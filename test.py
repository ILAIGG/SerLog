import tkinter as tk
from tkinter import messagebox, ttk
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim

# Lista para guardar marcadores y direcciones
marcadores = []

# Función para buscar y agregar marcador
def buscar_direccion():
    direccion = entry_direccion.get().strip()
    if not direccion:
        messagebox.showerror("Error", "Ingrese una dirección válida.")
        return

    geolocator = Nominatim(user_agent="tp_integrador")
    try:
        location = geolocator.geocode(direccion)
        if location:
            lat, lon = location.latitude, location.longitude
            marcador = map_widget.set_marker(lat, lon, text=direccion)
            marcadores.append((direccion, marcador))

            # Agregar a la lista visual
            lista_direcciones.insert(tk.END, direccion)

            # Centrar el mapa en la nueva posición
            map_widget.set_position(lat, lon)
        else:
            messagebox.showwarning("No encontrado", "No se pudo encontrar la dirección.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {e}")

# Crear ventana
root = tk.Tk()
root.title("TP Integrador - Múltiples Marcadores")
root.geometry("1000x600")

# Contenedor principal con dos columnas
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Panel Izquierdo
panel_izquierdo = tk.Frame(main_frame, width=300, bg="#f0f0f0")
panel_izquierdo.pack(side=tk.LEFT, fill=tk.Y)
panel_izquierdo.pack_propagate(False)

label = tk.Label(panel_izquierdo, text="Dirección:", bg="#f0f0f0", anchor="w")
label.pack(padx=10, pady=(10, 0), anchor="w")

entry_direccion = tk.Entry(panel_izquierdo, width=35)
entry_direccion.pack(padx=10, pady=5)

btn_buscar = tk.Button(panel_izquierdo, text="Agregar marcador", command=buscar_direccion)
btn_buscar.pack(padx=10, pady=5)

label_lista = tk.Label(panel_izquierdo, text="Direcciones agregadas:", bg="#f0f0f0", anchor="w")
label_lista.pack(padx=10, pady=(15, 0), anchor="w")

# Panel de lista de direcciones con scroll
frame_lista = tk.Frame(panel_izquierdo)
frame_lista.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_lista)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

lista_direcciones = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, height=20)
lista_direcciones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=lista_direcciones.yview)

# Panel Derecho (Mapa)
map_widget = TkinterMapView(main_frame, width=700, height=600, corner_radius=0)
map_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
map_widget.set_position(-27.4698, -58.8344)  # Corrientes
map_widget.set_zoom(7)

root.mainloop()
