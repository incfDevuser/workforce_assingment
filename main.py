import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

INSTANCE = 'A'

BASE_DIR = os.path.dirname(__file__)
POINTS_PATH = os.path.join(BASE_DIR, "POINTS", f"POINTS_{INSTANCE}.dat")
GUARDS_PATH = os.path.join(BASE_DIR, "GUARDS", f"GUARDS_{INSTANCE}.dat")
ODMATRIX_PATH = os.path.join(BASE_DIR, "ODMATRIX", f"ODMATRIX_{INSTANCE}.dat")
LOCATION_PATH = os.path.join(BASE_DIR, "LOCATIONS", f"LOCATION_{INSTANCE}.dat")
SOLUTION_PATH = os.path.join(BASE_DIR, "SOLUTIONS", f"SOLUTION_{INSTANCE}.out")
VISUAL_PATH = os.path.join(BASE_DIR, "SOLUTIONS", f"VISUAL_{INSTANCE}.png")

SUELDO_MINIMO = 460000
VALOR_OCASIONAL = 47000
VALOR_PLANTA = 1.6 * SUELDO_MINIMO

points_cols = ["PuntoID", "LocID", "Demanda", "Lat", "Lon"]
guards_cols = ["ID", "Tipo", "HorasUsadas", "MaxHoras", "Lat", "Lon"]
odmatrix_cols = ["GuardID", "PuntoID", "Tiempo"]
location_cols = ["LocID", "Nombre", "Comuna", "Prioridad"]

points = pd.read_csv(POINTS_PATH, sep='\\s+', comment='#', engine='python', names=points_cols)
guards = pd.read_csv(GUARDS_PATH, sep='\\s+', comment='#', engine='python', names=guards_cols)
od_matrix = pd.read_csv(ODMATRIX_PATH, sep='\\s+', comment='#', engine='python', names=odmatrix_cols)

locations = pd.read_fwf(LOCATION_PATH, comment='#', 
                        colspecs=[(0, 9), (9, 35), (35, 55), (55, 65)],
                        names=location_cols)

locations['LocID'] = locations['LocID'].astype(int)

densidad = points.groupby("LocID").size().reset_index(name="Cantidad_Puntos")
densidad = densidad.sort_values(by="Cantidad_Puntos", ascending=False)
assignments = []
costo_total = 0
turnos_no_cubiertos = 0
guard_hours = {g['ID']: g['HorasUsadas'] for _, g in guards.iterrows()}

for _, row in densidad.iterrows():
    loc_id = row['LocID']
    puntos_loc = points[points['LocID'] == loc_id]
    for _, punto in puntos_loc.iterrows():
        punto_id = punto['PuntoID']
        asignado = False
        candidatos = guards[
            (guards['Tipo'] == 'Planta') &
            (guards['ID'].isin(od_matrix[od_matrix['PuntoID'] == punto_id]['GuardID']))
        ]
        for _, guard in candidatos.iterrows():
            tiempo = od_matrix[
                (od_matrix['GuardID'] == guard['ID']) &
                (od_matrix['PuntoID'] == punto_id)
            ]['Tiempo'].values[0]
            if tiempo <= 2.5 and guard_hours[guard['ID']] + 7 <= 42:
                assignments.append([guard['ID'], punto_id, loc_id, 1, "Planta", 0])
                guard_hours[guard['ID']] += 7
                asignado = True
                break
        if not asignado:
            candidatos = guards[
                (guards['Tipo'] == 'Ocasional') &
                (guards['ID'].isin(od_matrix[od_matrix['PuntoID'] == punto_id]['GuardID']))
            ]
            for _, guard in candidatos.iterrows():
                assignments.append([guard['ID'], punto_id, loc_id, 1, "Ocasional", VALOR_OCASIONAL])
                costo_total += VALOR_OCASIONAL
                asignado = True
                break
        if not asignado:
            turnos_no_cubiertos += 1

guardias_usados_planta = {a[0] for a in assignments if a[4] == "Planta"}
costo_total += len(guardias_usados_planta) * VALOR_PLANTA

with open(SOLUTION_PATH, 'w') as f:
    f.write("NAME : GUARD_ASSIGNMENT_PROBLEM\n")
    f.write("TYPE : SOLUTION\n")
    f.write(f"COSTO_TOTAL : {int(costo_total)}\n")
    f.write(f"TURNOS_NO_CUBIERTOS : {turnos_no_cubiertos}\n\n")
    f.write("ASSIGNMENTS :\n")
    f.write("# Guardia   PuntoID   LocID   Turno   Tipo       Costo\n")
    for a in assignments:
        f.write(f"{a[0]}\t{a[1]}\t{a[2]}\t{a[3]}\t{a[4]}\t{int(a[5])}\n")
    f.write("EOF\n")

print(f"Asignación completada. Archivo generado en: {SOLUTION_PATH}")

asignaciones_df = pd.DataFrame(assignments, columns=["Guardia", "PuntoID", "LocID", "Turno", "Tipo", "Costo"])
asignaciones_df = asignaciones_df.merge(points, on="PuntoID", suffixes=('', '_points'))
asignaciones_df = asignaciones_df.merge(locations, on="LocID")

fig, ax = plt.subplots(figsize=(12, 8))
colores_loc = plt.cm.tab10(range(len(locations)))
loc_color_map = {loc_id: colores_loc[i] for i, loc_id in enumerate(locations['LocID'])}

for loc_id, group in asignaciones_df.groupby("LocID"):
    cx, cy = group["Lon"].mean(), group["Lat"].mean()
    nombre_loc = group["Nombre"].iloc[0]
    color = loc_color_map[loc_id]
    from math import sqrt
    distancias = ((group["Lon"] - cx)**2 + (group["Lat"] - cy)**2).apply(sqrt)
    radio = distancias.max() + 0.002  # margen de seguridad
    ax.add_patch(plt.Circle((cx, cy), radio, color=color, alpha=0.3))

    ax.text(cx, cy - 0.003, nombre_loc, ha='center', va='top', fontsize=10, 
            fontweight='bold', color=color, bbox=dict(facecolor='white', alpha=0.7, pad=2))
for tipo, group in asignaciones_df.groupby("Tipo"):
    ax.scatter(group["Lon"], group["Lat"], label=tipo, s=100, alpha=0.8)
for _, row in asignaciones_df.iterrows():
    label = f"G{int(row['Guardia'])}-P{int(row['PuntoID'])}"
    ax.annotate(label, (row["Lon"], row["Lat"]), textcoords="offset points", 
                xytext=(0, 8), ha='center', fontsize=8)
import matplotlib.patches as mpatches
loc_patches = [mpatches.Patch(color=loc_color_map[loc_id], 
                            alpha=0.3, 
                            label=f"{loc_id} - {nombre}") 
              for loc_id, nombre in zip(locations['LocID'], locations['Nombre'])]

ax.legend(handles=loc_patches + ax.get_legend_handles_labels()[0], 
         loc='upper left', bbox_to_anchor=(1.05, 1), title="Locaciones y Tipos")
ax.set_xlabel("Longitud")
ax.set_ylabel("Latitud")
ax.set_title("Asignaciones con Locaciones y Tipos de Guardia")
ax.grid(True)
plt.tight_layout()
plt.savefig(VISUAL_PATH, bbox_inches='tight')
print(f"Visualización generada: {VISUAL_PATH}")
