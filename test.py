import tkinter as tk
from tkinter import messagebox
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim

# Función para geocodificar dirección
def buscar_direccion():
    direccion = entry_direccion.get()
    if not direccion:
        messagebox.showerror("Error", "Ingrese una dirección válida.")
        return
    
    geolocator = Nominatim(user_agent="tp_integrador")
    try:
        location = geolocator.geocode(direccion)
        if location:
            lat, lon = location.latitude, location.longitude
            map_widget.set_position(lat, lon)  # centra el mapa
            map_widget.set_marker(lat, lon, text=direccion)  # pone un marcador
        else:
            messagebox.showwarning("No encontrado", "No se pudo encontrar la dirección.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {e}")

# Interfaz
root = tk.Tk()
root.title("TP Integrador - Mapa con Dirección")

root.geometry("800x600")

frame = tk.Frame(root)
frame.pack(pady=10)

entry_direccion = tk.Entry(frame, width=50)
entry_direccion.pack(side=tk.LEFT, padx=5)

btn_buscar = tk.Button(frame, text="Buscar Dirección", command=buscar_direccion)
btn_buscar.pack(side=tk.LEFT)

# Mapa
map_widget = TkinterMapView(root, width=780, height=500, corner_radius=0)
map_widget.pack(pady=10)
map_widget.set_position(-27.4698, -58.8344)  # Posición inicial (Corrientes)
map_widget.set_zoom(7)

root.mainloop()