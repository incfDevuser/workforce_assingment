# Workforce Assignment Problem

Este proyecto implementa un sistema de asignación de guardias a puntos de trabajo, optimizando costos y respetando restricciones de tiempo y distancia.

## Estructura del Proyecto

```
workforce_assignment/
├── GUARDS/             # Archivos con información de guardias disponibles
│   ├── GUARDS_A.dat
│   └── GUARDS_B.dat
├── INSTANCES/          # Archivos con definición de instancias del problema
│   ├── INSTANCE_A.dat
│   └── INSTANCE_B.dat
├── LOCATIONS/          # Archivos con información de locaciones
│   ├── LOCATION_A.dat
│   └── LOCATION_B.dat
├── ODMATRIX/           # Matrices de origen-destino con tiempos de viaje
│   ├── ODMATRIX_A.dat
│   └── ODMATRIX_B.dat
├── POINTS/             # Archivos con puntos a cubrir
│   ├── POINTS_A.dat
│   └── POINTS_B.dat
├── SOLUTIONS/          # Carpeta donde se guardan las soluciones generadas
├── main.py             # Script principal
└── README.md           # Este archivo
```
## Cómo ejecutar

1. Instalar las dependencias:

```bash
pip install pandas matplotlib
```

2. Ejecuta el script principal para la instancia A (configuración predeterminada):

```bash
python main.py
```

3. Esto generará dos archivos en la carpeta `SOLUTIONS/`:
   - `SOLUTION_A.out`: Archivo de texto con la solución (asignaciones y costo)
   - `VISUAL_A.png`: Visualización gráfica de las asignaciones

## Uso con diferentes instancias

Para usar el sistema con una instancia diferente (por ejemplo, la instancia B), necesitas modificar el script `main.py` para cambiar las rutas de los archivos de entrada y salida. Edita las siguientes líneas al principio del archivo:

```python
# Cambiar de 'A' a 'B' para usar la instancia B
INSTANCE = 'A'  # Cambia esto a 'B' para la instancia B

BASE_DIR = os.path.dirname(__file__)
POINTS_PATH = os.path.join(BASE_DIR, "POINTS", f"POINTS_{INSTANCE}.dat")
GUARDS_PATH = os.path.join(BASE_DIR, "GUARDS", f"GUARDS_{INSTANCE}.dat")
ODMATRIX_PATH = os.path.join(BASE_DIR, "ODMATRIX", f"ODMATRIX_{INSTANCE}.dat")
LOCATION_PATH = os.path.join(BASE_DIR, "LOCATIONS", f"LOCATION_{INSTANCE}.dat")
SOLUTION_PATH = os.path.join(BASE_DIR, "SOLUTIONS", f"SOLUTION_{INSTANCE}.out")
VISUAL_PATH = os.path.join(BASE_DIR, "SOLUTIONS", f"VISUAL_{INSTANCE}.png")
```

## Creación de nuevas instancias

Para crear una nueva instancia, necesitas proporcionar los siguientes archivos:

1. **GUARDS_{X}.dat**: Información sobre guardias disponibles
   ```
   # ID   Tipo       HorasUsadas  MaxHoras   Lat     Lon
   1      Planta     7            42         -33.45  -70.65
   2      Ocasional  0            8          -33.47  -70.68
   ...
   ```

2. **POINTS_{X}.dat**: Puntos a cubrir
   ```
   # PuntoID   LocID   Demanda   Lat       Lon
   1           1       1         -33.450   -70.650
   2           1       1         -33.451   -70.648
   ...
   ```

3. **ODMATRIX_{X}.dat**: Matriz de tiempos de viaje
   ```
   # GuardID   PuntoID   Tiempo
   1           1         1.2
   1           2         1.4
   ...
   ```

4. **LOCATION_{X}.dat**: Información de locaciones
   ```
   # LocID   Nombre                    Comuna             Prioridad
   1        Plaza Egaña               Ñuñoa              Alta
   2        Metro Universidad de Chile Santiago           Media
   ...
   ```

5. **INSTANCE_{X}.dat**: Metadatos de la instancia
   ```
   NAME : GUARD_ASSIGNMENT_PROBLEM
   TYPE : WORKFORCE_ASSIGNMENT
   LOCATIONS : 5
   POINTS : 9
   GUARDIAS : 4
   HORIZON : 30
   COMMENT : Descripción de la instancia
   ```

Luego, modifica el script `main.py` para usar tus nuevos archivos cambiando la variable `INSTANCE` como se explicó anteriormente.

## Interpretación de resultados

- **SOLUTION_{X}.out**: Contiene la asignación de guardias a puntos, el costo total y el número de turnos no cubiertos.
- **VISUAL_{X}.png**: Muestra una visualización geográfica de las asignaciones, donde:
  - Cada locación se representa con un círculo de color distinto
  - Los puntos representan las asignaciones de guardias
  - Las etiquetas G#-P# indican qué guardia está asignado a qué punto
  - La leyenda muestra las locaciones y tipos de guardias

## Lógica de asignación

El algoritmo actual asigna guardias en el siguiente orden de prioridad:
1. Primero intenta asignar guardias de planta a puntos cercanos (tiempo de viaje <= 2.5 horas)
2. Si no hay guardias de planta disponibles, asigna guardias ocasionales
3. Si no hay guardias disponibles, el turno queda sin cubrir

Los costos se calculan de la siguiente manera:
- Guardias de planta: 1.6 veces el sueldo mínimo por mes
- Guardias ocasionales: un valor fijo por turno