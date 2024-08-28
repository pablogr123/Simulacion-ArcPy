import tkinter as tk
from tkinter import messagebox
from humedal_cienegas_lerma_sim import SimulacionCienegas
import subprocess  # Importamos subprocess para ejecutar otros scripts

class AplicacionSimulaciones:
    def __init__(self, master):
        self.master = master
        master.title("Simulaciones de las Ciénegas de Lerma")
        master.geometry("450x300")  # Aumentamos un poco el ancho de la ventana

        button_style = {'font': ('Arial', 12), 'width': 30, 'height': 2, 'bg': '#4CAF50', 'fg': 'white'}

        self.btn_reduccion = tk.Button(master, text="Simulación reducción", command=self.simulacion_reduccion, **button_style)
        self.btn_reduccion.pack(pady=10)

        self.btn_microplasticos = tk.Button(master, text="Microplásticos Actuales", command=self.simulacion_microplasticos, **button_style)
        self.btn_microplasticos.pack(pady=10)

        self.btn_pendiente = tk.Button(master, text="Microplásticos en el Tiempo", command=self.simulacion_pendiente, **button_style)
        self.btn_pendiente.pack(pady=10)

        self.btn_salir = tk.Button(master, text="Salir", command=self.salir, **button_style)
        self.btn_salir.pack(pady=10)

        self.simulacion = SimulacionCienegas()

    def simulacion_reduccion(self):
        self.simulacion.ejecutar_simulacion_reduccion()

    def simulacion_microplasticos(self):
        try:
            subprocess.run(["python", "microplasticos.py"], check=True)  # Ejecuta microplasticos.py
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error al ejecutar la simulación de microplásticos:\n{e}")

    def simulacion_pendiente(self):
        try:
            subprocess.run(["python", "MicroplasticosTiempo.py"], check=True)  # Ejecuta Microplasticos tiempo.py
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error al ejecutar la simulación de microplásticos en el tiempo:\n{e}")

    def salir(self):
        self.master.quit()
        self.master.destroy()

def main():
    root = tk.Tk()
    app = AplicacionSimulaciones(root)
    root.mainloop()

if __name__ == "__main__":
    main()
