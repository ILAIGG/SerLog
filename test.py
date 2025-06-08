import tkinter as tk
from math import sqrt

# Coordenadas simuladas (x, y) - Escala simple (pueden ser km o "píxeles")
PUNTOS = {
    "Central": (100, 300),
    "Ciudad A": (200, 200),
    "Ciudad B": (300, 250),
    "Rosario": (400, 150)
}

def calcular_distancia(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return round(sqrt((x2 - x1)**2 + (y2 - y1)**2), 2)

def mostrar_ruta(canvas, puntos):
    total = 0
    canvas.delete("all")
    
    keys = list(puntos.keys())
    for i in range(len(keys) - 1):
        p1 = puntos[keys[i]]
        p2 = puntos[keys[i + 1]]
        canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="blue", width=2)
        canvas.create_oval(p1[0]-5, p1[1]-5, p1[0]+5, p1[1]+5, fill="red")
        canvas.create_text(p1[0]+10, p1[1]-10, text=keys[i], anchor="w")
        total += calcular_distancia(p1, p2)
    
    # Último punto
    px, py = puntos[keys[-1]]
    canvas.create_oval(px-5, py-5, px+5, py+5, fill="green")
    canvas.create_text(px+10, py-10, text=keys[-1], anchor="w")
    
    label_resultado.config(text=f"Distancia total: {total} unidades")

# Interfaz
root = tk.Tk()
root.title("Ruta de Transporte")

canvas = tk.Canvas(root, width=500, height=400, bg="white")
canvas.pack()

label_resultado = tk.Label(root, text="", font=("Arial", 12))
label_resultado.pack()

btn_trazar = tk.Button(root, text="Trazar Ruta", command=lambda: mostrar_ruta(canvas, PUNTOS))
btn_trazar.pack(pady=10)

root.mainloop()