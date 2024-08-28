import geopandas as gpd
import pandas as pd  # Importar pandas para la concatenación de GeoDataFrames
import matplotlib.pyplot as plt
import contextily as cx
from matplotlib_scalebar.scalebar import ScaleBar
import numpy as np
import random
from shapely.geometry import Point
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox

class SimulacionMicroplasticos:
    def __init__(self, master):
        self.master = master
        self.ruta_industrias = {
            'Lerma_Apoyo': r"C:\Users\Pablo\Downloads\ShapeIndustrias\Lerma\Apoyo\ApoyoLerma.shp",
            'Lerma_Constructoras': r"C:\Users\Pablo\Downloads\ShapeIndustrias\Lerma\Constructoras\ConstructorasLerma.shp",
            'Lerma_Manufactureras': r"C:\Users\Pablo\Downloads\ShapeIndustrias\Lerma\Manufactureras\ManufaLerma.shp",
            'Lerma_Transporte': r"C:\Users\Pablo\Downloads\ShapeIndustrias\Lerma\Transporte\TransporteLerma.shp",
            'Ocoyoacac_Apoyo': r"C:\Users\Pablo\Downloads\ShapeIndustrias\Ocoyoacac\Apoyo\ApoyoOco.shp",
            'Ocoyoacac_Constructoras': r"C:\Users\Pablo\Downloads\ShapeIndustrias\Ocoyoacac\Constructoras\ConstructorasOco.shp",
            'Ocoyoacac_Manufactureras': r"C:\Users\Pablo\Downloads\ShapeIndustrias\Ocoyoacac\Manufactureras\ManuOco.shp",
            'Ocoyoacac_Transporte': r"C:\Users\Pablo\Downloads\ShapeIndustrias\Ocoyoacac\Transporte\TransporteOco.shp",
            'SanMateo_Apoyo': r"C:\Users\Pablo\Downloads\ShapeIndustrias\SanMateo\Apoyo\ApoyoSanMateo.shp",
            'SanMateo_Constructoras': r"C:\Users\Pablo\Downloads\ShapeIndustrias\SanMateo\Constructoras\ConstructorasSanMateo.shp",
            'SanMateo_Manufactureras': r"C:\Users\Pablo\Downloads\ShapeIndustrias\SanMateo\Manufactureras\ManuSanMateo.shp",
            'SanMateo_Transporte': r"C:\Users\Pablo\Downloads\ShapeIndustrias\SanMateo\Transporte\TransporteSanMateo.shp",
        }
        self.ruta_carreteras = r"C:\Users\Pablo\Downloads\ShapeIndustrias\CallesCienegas\CallesCienegas.shp"
        self.ruta_cienegas = r"C:\Users\Pablo\Downloads\Shapesxd\ShapeCienegas.shp"

        self.ventana_grafico = tk.Toplevel(self.master)  # Creamos una nueva ventana secundaria
        self.ventana_grafico.title("Simulación de Microplásticos en las Ciénegas de Lerma")
        self.ventana_grafico.geometry("800x700")
        self.fig = None
        self.ax = None

        self.ventana_grafico.protocol("WM_DELETE_WINDOW", self.salir)

    def cargar_shapefiles(self):
        # Cargar las industrias
        try:
            industrias = [gpd.read_file(shp).to_crs(epsg=3857) for shp in self.ruta_industrias.values()]
            gdf_industrias = gpd.GeoDataFrame(pd.concat(industrias, ignore_index=True))
            print("Shapefiles de industrias cargados correctamente.")
        except Exception as e:
            print(f"Error al cargar industrias: {e}")
            messagebox.showerror("Error", f"Error al cargar industrias: {e}")
            return None, None, None

        # Cargar las carreteras
        try:
            gdf_carreteras = gpd.read_file(self.ruta_carreteras).to_crs(epsg=3857)
            print("Shapefiles de carreteras cargados correctamente.")
        except Exception as e:
            print(f"Error al cargar carreteras: {e}")
            messagebox.showerror("Error", f"Error al cargar carreteras: {e}")
            return None, None, None

        # Cargar las ciénegas
        try:
            gdf_cienegas = gpd.read_file(self.ruta_cienegas).to_crs(epsg=3857)
            print("Shapefiles de ciénegas cargados correctamente.")
        except Exception as e:
            print(f"Error al cargar ciénegas: {e}")
            messagebox.showerror("Error", f"Error al cargar ciénegas: {e}")
            return None, None, None

        return gdf_industrias, gdf_carreteras, gdf_cienegas

    def dispersar_microplasticos(self, gdf_cienegas, gdf_industrias, gdf_carreteras):
        if gdf_cienegas is None or gdf_industrias is None or gdf_carreteras is None:
            return []

        # Crear una lista para almacenar los puntos de microplásticos
        puntos_microplasticos = []

        # Parámetros de simulación
        num_puntos_inicial = 1000  # Número inicial de puntos de microplásticos
        años = 10  # Número de años de simulación
        tasa_incremento = 1.1  # Tasa de incremento anual de microplásticos

        # Iterar a lo largo de los años
        for año in range(años):
            # Para cada polígono de las ciénegas, añadir puntos de microplásticos
            for idx, row in gdf_cienegas.iterrows():
                poligono = row['geometry']

                # Añadir puntos iniciales de microplásticos
                for _ in range(int(num_puntos_inicial * tasa_incremento ** año)):
                    # Generar un punto dentro del polígono
                    minx, miny, maxx, maxy = poligono.bounds
                    while True:
                        punto = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
                        if poligono.contains(punto):
                            break

                    # Evaluar la influencia de las industrias y carreteras
                    dist_industrias = gdf_industrias.distance(punto).min()
                    dist_carreteras = gdf_carreteras.distance(punto).min()

                    # Incrementar la cantidad de microplásticos según la proximidad
                    if dist_industrias < 5000:  # 5 km de influencia industrial
                        puntos_microplasticos.append(punto)
                    if dist_carreteras < 2000:  # 2 km de influencia de carreteras
                        puntos_microplasticos.append(punto)

        print(f"Simulación completada: {len(puntos_microplasticos)} puntos generados.")
        return puntos_microplasticos

    def mostrar_mapa(self, gdf_cienegas, puntos_microplasticos):
        if len(puntos_microplasticos) == 0:
            print("No se generaron puntos de microplásticos.")
            return

        frame_grafico = tk.Frame(self.ventana_grafico)
        frame_grafico.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Mostrar las ciénegas
        gdf_cienegas.plot(ax=self.ax, facecolor='none', edgecolor='blue', linewidth=2)

        # Añadir los puntos de microplásticos
        x_vals = [punto.x for punto in puntos_microplasticos]
        y_vals = [punto.y for punto in puntos_microplasticos]
        self.ax.scatter(x_vals, y_vals, color='red', s=1, label='Microplásticos')

        # Añadir mapa base
        cx.add_basemap(self.ax, source=cx.providers.OpenStreetMap.Mapnik, zoom=12)

        # Añadir barra de escala
        scalebar = ScaleBar(1, units="m", location="lower right")
        self.ax.add_artist(scalebar)

        plt.tight_layout()

        frame_botones = tk.Frame(self.ventana_grafico)
        frame_botones.pack(fill=tk.X, padx=10, pady=10)

        btn_volver = tk.Button(frame_botones, text="Volver al menú", command=self.salir)
        btn_volver.pack(side=tk.LEFT, padx=5)

        btn_salir = tk.Button(frame_botones, text="Salir", command=self.salir)
        btn_salir.pack(side=tk.RIGHT, padx=5)

    def ejecutar_simulacion(self):
        gdf_industrias, gdf_carreteras, gdf_cienegas = self.cargar_shapefiles()
        puntos_microplasticos = self.dispersar_microplasticos(gdf_cienegas, gdf_industrias, gdf_carreteras)
        self.mostrar_mapa(gdf_cienegas, puntos_microplasticos)

    def salir(self):
        self.master.quit()  # Cierra toda la aplicación, incluyendo la ventana principal (index.py)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal para que no aparezca
    simulacion = SimulacionMicroplasticos(root)
    simulacion.ejecutar_simulacion()
    root.mainloop()