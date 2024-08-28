import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
from matplotlib_scalebar.scalebar import ScaleBar
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox

class SimulacionCienegas:
    def __init__(self):
        self.ruta_shapefile = r"C:\Users\Pablo\Downloads\Shapesxd\ShapeCienegas.shp"
        self.ventana_grafico = None
        self.ani = None
        self.fig = None
        self.ax = None

    def cargar_shapefile(self):
        try:
            return gpd.read_file(self.ruta_shapefile)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el shapefile: {e}")
            return None

    def calcular_factor_reduccion(self, año):
        tasa_anual = 0.01  # 1% de reducción anual
        return 1 - (1 - tasa_anual) ** (año - 2023)

    def reducir_geometria(self, geom, factor, area_total, area_original):
        if isinstance(geom, Polygon):
            # Factor de reducción ajustado para áreas pequeñas
            factor_ajustado = factor * (area_original / geom.area)
            factor_ajustado = min(factor_ajustado, 0.2)  # Limitar la reducción a un 20% máximo por iteración
            nueva_geom = geom.buffer(-factor_ajustado * geom.length)
            if nueva_geom.is_empty or nueva_geom.area <= 0:
                return None
            return nueva_geom
        elif isinstance(geom, MultiPolygon):
            reduced_polys = [self.reducir_geometria(poly, factor, area_total, area_original) for poly in geom.geoms]
            return MultiPolygon([poly for poly in reduced_polys if poly is not None])
        elif isinstance(geom, GeometryCollection):
            reduced_geoms = [self.reducir_geometria(g, factor, area_total, area_original) for g in geom.geoms]
            return GeometryCollection([g for g in reduced_geoms if g is not None])
        else:
            return geom

    def simular_reduccion(self, gdf, anos=10):
        area_total = gdf.area.sum()
        area_original = gdf.area.max()  # Máximo área inicial para el ajuste
        simulaciones = []
        for i in range(anos):
            año_actual = 2023 + i
            factor = self.calcular_factor_reduccion(año_actual)
            gdf_reducido = gdf.copy()
            gdf_reducido['geometry'] = gdf_reducido['geometry'].apply(
                lambda geom: self.reducir_geometria(geom, factor, area_total, area_original)
            )
            # Filtramos geometrías vacías
            gdf_reducido = gdf_reducido[~gdf_reducido.is_empty]
            gdf_reducido['año'] = año_actual
            simulaciones.append(gdf_reducido)
        return simulaciones

    def visualizar_reduccion(self, gdf_original, simulaciones):
        self.ventana_grafico = tk.Toplevel()
        self.ventana_grafico.title("Simulación de Reducción de las Ciénegas de Lerma")
        self.ventana_grafico.geometry("800x700")

        frame_grafico = tk.Frame(self.ventana_grafico)
        frame_grafico.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        gdf_original = gdf_original.to_crs(epsg=3857)
        simulaciones = [gdf.to_crs(epsg=3857) for gdf in simulaciones]

        minx, miny, maxx, maxy = gdf_original.total_bounds
        w, h = maxx - minx, maxy - miny
        self.ax.set_xlim(minx - 0.1*w, maxx + 0.1*w)
        self.ax.set_ylim(miny - 0.1*h, maxy + 0.1*h)

        scalebar = ScaleBar(dx=1, units="m", location="lower right")
        self.ax.add_artist(scalebar)

        def update(frame):
            self.ax.clear()
            self.ax.set_axis_off()
            
            cx.add_basemap(self.ax, source=cx.providers.OpenStreetMap.Mapnik, zoom=13)
            self.ax.add_artist(scalebar)
            
            año_actual = 2023 + frame  # Aseguramos que año_actual siempre esté definido
            gdf_actual = simulaciones[frame]
            
            if not gdf_actual.empty:
                gdf_original.plot(ax=self.ax, facecolor='none', edgecolor='red', linewidth=2)
                gdf_actual.plot(ax=self.ax, facecolor='blue', alpha=0.5)
            
                area_original = gdf_original.area.sum()
                area_actual = gdf_actual.area.sum()
                porcentaje_reduccion = (1 - area_actual / area_original) * 100

                self.ax.set_title(f"Año: {año_actual}\nReducción: {porcentaje_reduccion:.2f}%", fontsize=10)
            else:
                self.ax.set_title(f"Año: {año_actual}\nTodas las geometrías se han reducido a cero.", fontsize=10)
            
            self.ax.set_xlim(minx - 0.1*w, maxx + 0.1*w)
            self.ax.set_ylim(miny - 0.1*h, maxy + 0.1*h)
            
            return self.ax.collections

        self.ani = FuncAnimation(self.fig, update, frames=len(simulaciones),
                                 interval=1000, repeat=True, blit=False)

        plt.tight_layout()

        frame_botones = tk.Frame(self.ventana_grafico)
        frame_botones.pack(fill=tk.X, padx=10, pady=10)

        btn_volver = tk.Button(frame_botones, text="Volver al menú", command=self.volver_al_menu)
        btn_volver.pack(side=tk.LEFT, padx=5)

        btn_salir = tk.Button(frame_botones, text="Salir", command=self.salir)
        btn_salir.pack(side=tk.RIGHT, padx=5)

        self.ventana_grafico.protocol("WM_DELETE_WINDOW", self.salir)

    def volver_al_menu(self):
        if self.ani:
            self.ani.event_source.stop()
        if self.ventana_grafico:
            self.ventana_grafico.destroy()

    def salir(self):
        if self.ani:
            self.ani.event_source.stop()
        if self.ventana_grafico:
            self.ventana_grafico.quit()
            self.ventana_grafico.destroy()
        if self.fig:
            plt.close(self.fig)

    def ejecutar_simulacion_reduccion(self):
        gdf_original = self.cargar_shapefile()
        if gdf_original is not None:
            simulaciones = self.simular_reduccion(gdf_original)
            self.visualizar_reduccion(gdf_original, simulaciones)

if __name__ == "__main__":
    simulacion = SimulacionCienegas()
    simulacion.ejecutar_simulacion_reduccion()
