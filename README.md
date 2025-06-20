# SerLog - Sistema de Optimización Logística

## Descripción General
SerLog es un Producto Mínimo Viable (MVP) desarrollado como parte del Trabajo Práctico Integrador (TPI) de la *Universidad de la Cuenca del Plata* por el **Equipo 5**. El sistema aborda los desafíos logísticos de *SERPROVE* (Servicios Veterinarios Profesionales), una distribuidora de productos veterinarios. SerLog automatiza la planificación de rutas, optimiza el consumo de combustible y reduce costos operativos para entregas desde Corrientes a diversos destinos, incluyendo Rosario. El proyecto integra conocimientos de *Análisis Matemático II*, *Física I*, *Ingeniería de Software I* y *Paradigmas y Lenguajes de Programación I*.

---

## Contexto del Proyecto
El sistema fue diseñado para resolver ineficiencias en las operaciones logísticas de SERPROVE, como:
- Falta de automatización en la planificación de rutas.
- Alto consumo de combustible por rutas no óptimas.
- Demoras en entregas debido a locales cerrados.
- Gestión ineficiente de recursos y altos costos operativos.

Mediante la combinación de modelado físico, optimización matemática y desarrollo de software, SerLog ofrece una solución práctica para optimizar la logística, mejorar la eficiencia y reducir costos.

---

## Características
- **Optimización de Rutas**: Calcula rutas de entrega óptimas utilizando la API de OpenRouteService, considerando distancia y consumo de combustible.
- **Geocodificación**: Convierte direcciones en coordenadas usando la librería `geopy` para un mapeo preciso.
- **Estimación de Costos**: Calcula costos de combustible, gastos de conductores y otros costos logísticos basados en modelos físicos y matemáticos.
- **Interfaz Interactiva**: Desarrollada con `tkinter` y `tkintermapview` para una entrada de datos y visualización de rutas amigable.
- **Gestión de Datos**: Almacena datos logísticos (e.g., costos de combustible, peso de carga, gastos de conductores) y genera reportes detallados.
- **Gestión Dinámica de Rutas**: Permite agregar, reordenar o eliminar puntos de entrega dinámicamente.

---

## Tecnologías Utilizadas
- **Python**: Lenguaje principal para la aplicación.
- **Librerías**:
  - `tkinter`: Para la interfaz gráfica.
  - `tkintermapview`: Para visualización de mapas y rutas.
  - `geopy`: Para geocodificación de direcciones.
  - `openrouteservice`: Para cálculo y optimización de rutas.
- **Control de Versiones**: Git y GitHub para desarrollo colaborativo.
- **APIs**:
  - API de OpenRouteService (requiere una clave activa).
- **Dependencias**: Ver `requirements.txt` para la lista completa de paquetes requeridos.

---

## Instalación
1. **Clonar el Repositorio**:
   ```bash
   git clone https://github.com/ILAIGG/SerLog.git
   cd SerLog
   ```

2. **Instalar Dependencias**:
   Asegúrese de tener Python 3.8+ instalado, luego ejecute:
   ```bash
   pip install -r requirements.txt
   ```
   Paquetes requeridos:
   - `tkintermapview`
   - `geopy`
   - `openrouteservice`

3. **Configuración de la Clave API**:
   - Obtenga una clave API de [OpenRouteService](https://openrouteservice.org/).
   - Reemplace la clave de ejemplo en `Logistica.py` (línea 37) con su propia clave:
     ```python
     ors_client = openrouteservice.Client(key="SU_CLAVE_API_AQUÍ")
     ```

4. **Archivos de Imagen**:
   - Asegúrese de que los siguientes archivos de imagen estén en el directorio del proyecto:
     - `preparativo_envio.png`
     - `truck.png`
   - Estos pueden descargarse desde el [repositorio de GitHub de SerLog](https://github.com/ILAIGG/SerLog).

5. **Ejecutar la Aplicación**:
   ```bash
   python Logistica.py
   ```

---

## Uso
1. **Inicio de Sesión**:
   - Use las credenciales predeterminadas: Usuario: `admin`, Contraseña: `1234`.
2. **Agregar Puntos de Entrega**:
   - Ingrese direcciones en el campo de entrada para añadir marcadores en el mapa.
   - La ubicación predeterminada del depósito es `-27.464833, -58.767972` (Corrientes).
3. **Gestión de Rutas**:
   - Reordene o elimine puntos de entrega usando los botones de flechas y eliminación.
   - Haga clic en "Calcular Ruta Óptima" para generar la ruta óptima.
4. **Ingresar Datos Logísticos**:
   - Introduzca detalles como costo de combustible, tipo de camión, peso de carga, gastos de conductores y fecha/hora de entrega.
5. **Ver Resultados**:
   - Revise los costos calculados (combustible, comida, hotel, peajes) y detalles de la ruta.
   - Guarde el reporte logístico como un archivo `.txt`.
6. **Guardar y Reiniciar**:
   - Tras guardar el reporte, el sistema se reinicia para permitir la planificación de nuevas rutas.

---

## Estructura del Proyecto
```
SerLog/
├── Logistica.py          # Script principal de la aplicación
├── preparativo_envio.png # Imagen para la sección de entrada de datos
├── truck.png             # Imagen para la sección de resultados
├── README.md             # Este archivo
└── requirements.txt      # Lista de dependencias de Python
```

---

## Modelos Matemáticos y Físicos
El sistema incorpora modelos para optimizar el consumo de combustible y la logística:
- **Modelo de Consumo de Combustible**:
  \[
  f(x, y) = 0.4x + 0.05xy
  \]
  Donde:
  - \(x\): Distancia recorrida (km)
  - \(y\): Peso de la carga (toneladas)
  - \(f(x, y)\): Consumo de combustible (litros)

- **Análisis Físico**:
  - Analiza fuerzas (fricción, resistencia aerodinámica, pendiente) usando ecuaciones como:
    \[
    F_r = C_{rr} \cdot m \cdot g
    \]
    \[
    F_d = \frac{1}{2} \cdot \rho \cdot C_d \cdot A \cdot v^2
    \]
    \[
    P(v, \theta) = v \cdot (F_r + F_p + F_d)
    \]
  - Estas ecuaciones modelan los requerimientos energéticos para un camión Mercedes-Benz Atego.

- **Optimización**:
  - Minimiza el consumo de combustible seleccionando rutas más cortas, validado mediante optimización con restricciones:
    \[
    g(x, y) = x \cdot y - K = 0
    \]
    Donde \(K\) es el total de toneladas-kilómetro.

---

## Equipo de Desarrollo
- **Lucas Ayen Mordka**
- **Aylen Meza Chiesa**
- **Santiago Meza**
- **Rosario Gauto**
- **Lautaro Romero Stach**
- **Julian Karatanasopuloz**
- **Lucas Cremaschi**

**Docentes**:
- Ing. Gilda Romero
- Maria Mendoza
- Fernando Figueredo
- Walter Vazquez

---

## Resultados de Aprendizaje
Este proyecto integra múltiples disciplinas:
- **Análisis Matemático II**: Desarrollo de modelos multivariables para consumo de combustible y optimización.
- **Física I**: Modelado de fenómenos físicos (e.g., fricción, tracción) para estimar requerimientos energéticos.
- **Ingeniería de Software I**: Aplicación de metodologías ágiles, control de versiones (Git) y herramientas colaborativas (Trello, GitHub).
- **Paradigmas y Lenguajes de Programación I**: Implementación de código modular en Python con tipos de datos abstractos (e.g., listas, diccionarios) y APIs.

---

## Mejoras Futuras
- Agregar seguimiento en tiempo real con integración de GPS.
- Incorporar confirmación de disponibilidad de clientes para evitar entregas fallidas.
- Mejorar la interfaz con visualizaciones adicionales (e.g., gráficos de desglose de costos).
- Soportar múltiples tipos de vehículos con modelos dinámicos de consumo de combustible.
- Integrar con los sistemas existentes de SERPROVE para una adopción fluida.

---

## Referencias
- Larson, R., & Edwards, B. H. (2010). *Cálculo 1: De una variable* (9.ª ed.). McGraw-Hill.
- Sommerville, I. (2011). *Ingeniería de software* (9.ª ed.). Pearson Educación.
- Young, H. D., & Freedman, R. A. (2009). *Física universitaria* (12.ª ed.). Pearson Educación.
- Documentación de la API de OpenRouteService: [openrouteservice.org](https://openrouteservice.org/)
- Repositorio de GitHub: [ILAIGG/SerLog](https://github.com/ILAIGG/SerLog)

---

## Licencia
Este proyecto está libre de licencia OpenSource para más su uso.

---

*Desarrollado como parte del Trabajo Práctico Integrador en la Universidad de la Cuenca del Plata, 19 de junio de 2025.*