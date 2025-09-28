import tkinter as tk
from tkinter import ttk, messagebox
import heapq

# ============================
# Grafo para rutas TransMilenio
# ============================
class Grafo:
    def __init__(self):
        self.nodos = {}

    def agregar_nodo(self, nombre):
        if nombre not in self.nodos:
            self.nodos[nombre] = []

    def agregar_arista(self, origen, destino, peso, bus):
        self.agregar_nodo(origen)
        self.agregar_nodo(destino)
        self.nodos[origen].append((destino, peso, bus))
        self.nodos[destino].append((origen, peso, bus))  # bidireccional

    def dijkstra(self, inicio, fin):
        distancias = {nodo: float("inf") for nodo in self.nodos}
        distancias[inicio] = 0
        anteriores = {nodo: None for nodo in self.nodos}
        buses = {nodo: None for nodo in self.nodos}
        cola = [(0, inicio, None)]

        while cola:
            distancia_actual, nodo_actual, bus_actual = heapq.heappop(cola)

            if distancia_actual > distancias[nodo_actual]:
                continue

            for vecino, peso, bus in self.nodos[nodo_actual]:
                nueva_distancia = distancia_actual + peso
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    anteriores[vecino] = nodo_actual
                    buses[vecino] = bus
                    heapq.heappush(cola, (nueva_distancia, vecino, bus))

        ruta, ruta_buses = [], []
        actual = fin
        while actual is not None:
            ruta.insert(0, actual)
            ruta_buses.insert(0, buses[actual])
            actual = anteriores[actual]

        return ruta, ruta_buses, distancias[fin]


# ============================
# Crear grafo con estaciones
# ============================
grafo = Grafo()
grafo.agregar_arista("Portal Norte", "Calle 170", 5, "B23")
grafo.agregar_arista("Calle 170", "Toberín", 4, "B23")
grafo.agregar_arista("Toberín", "Calle 142", 6, "B23")
grafo.agregar_arista("Calle 142", "Calle 127", 4, "B23")
grafo.agregar_arista("Calle 127", "Calle 100", 6, "B23")
grafo.agregar_arista("Calle 100", "Héroes", 5, "B23")
grafo.agregar_arista("Héroes", "Calle 72", 5, "B23")
grafo.agregar_arista("Calle 72", "Museo Nacional", 6, "B23")
grafo.agregar_arista("Museo Nacional", "Museo del Oro", 4, "B23")
grafo.agregar_arista("Museo del Oro", "Av Jiménez", 2, "B23")

grafo.agregar_arista("Portal Sur", "Restrepo", 6, "H74")
grafo.agregar_arista("Restrepo", "Calle 1ra", 6, "H74")
grafo.agregar_arista("Calle 1ra", "Av Jiménez", 10, "H74")

grafo.agregar_arista("Portal 80", "Av 68", 8, "C15")
grafo.agregar_arista("Av 68", "Calle 100", 9, "C15")
grafo.agregar_arista("Calle 100", "Museo del Oro", 12, "C15")

# ============================
# Interfaz gráfica Tkinter mejorada
# ============================
def calcular_ruta():
    origen = combo_origen.get()
    destino = combo_destino.get()

    if origen == destino:
        messagebox.showwarning("Error", "El origen y destino no pueden ser iguales")
        return

    ruta, buses, tiempo = grafo.dijkstra(origen, destino)

    if tiempo == float("inf"):
        messagebox.showerror("Sin ruta", "No existe ruta posible entre esas estaciones")
        return

    resultado_text.config(state="normal")
    resultado_text.delete(1.0, tk.END)
    resultado_text.insert(tk.END, f"🟢 Origen: {origen}\n")
    resultado_text.insert(tk.END, f"🔴 Destino: {destino}\n")
    resultado_text.insert(tk.END, f"⏱️ Tiempo estimado: {tiempo} minutos\n\n")

    bus_actual = buses[1]
    resultado_text.insert(tk.END, f"🚍 En {ruta[0]} tomar bus {bus_actual}\n")

    for i in range(1, len(ruta)):
        estacion = ruta[i]
        bus = buses[i]

        if bus != bus_actual and bus is not None:
            resultado_text.insert(tk.END, f"➡️ Bájese en {ruta[i-1]} y cambie al bus {bus}\n")
            bus_actual = bus

        resultado_text.insert(tk.END, f"📍 Llegar a {estacion} (bus {bus_actual})\n")

    resultado_text.config(state="disabled")

def reiniciar():
    combo_origen.set("")
    combo_destino.set("")
    resultado_text.config(state="normal")
    resultado_text.delete(1.0, tk.END)
    resultado_text.config(state="disabled")


# Ventana principal
ventana = tk.Tk()
ventana.title("🚏 Sistema de Rutas TransMilenio")
ventana.geometry("650x500")
ventana.configure(bg="#e8f0fe")

estaciones = sorted(list(grafo.nodos.keys()))

# Estilo
style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=6)
style.configure("TLabel", font=("Arial", 12), background="#e8f0fe")

# Widgets
ttk.Label(ventana, text="Seleccione estación de origen 🟢:").pack(pady=5)
combo_origen = ttk.Combobox(ventana, values=estaciones, width=40)
combo_origen.pack(pady=5)

ttk.Label(ventana, text="Seleccione estación de destino 🔴:").pack(pady=5)
combo_destino = ttk.Combobox(ventana, values=estaciones, width=40)
combo_destino.pack(pady=5)

frame_botones = tk.Frame(ventana, bg="#e8f0fe")
frame_botones.pack(pady=10)
ttk.Button(frame_botones, text="Calcular Ruta", command=calcular_ruta).grid(row=0, column=0, padx=10)
ttk.Button(frame_botones, text="Reiniciar", command=reiniciar).grid(row=0, column=1, padx=10)

resultado_text = tk.Text(ventana, wrap="word", height=15, state="disabled", font=("Arial", 11))
resultado_text.pack(fill="both", expand=True, padx=10, pady=10)

ventana.mainloop()
