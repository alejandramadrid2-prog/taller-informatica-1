# Sistema de gestión de signos vitales

Taller evaluativo de **Informática 1 – Unidades 3 y 4** (Universidad de Antioquia, Facultad de Ingeniería).
Aplicación en Python por consola para generar, validar, ordenar, almacenar y consultar registros biomédicos,
con persistencia en archivos (TXT, CSV, JSON) y en una base de datos NoSQL (MongoDB Atlas).

## Estructura del proyecto

```
taller_biomedico/
├── main.py          # Menú principal (integración)
├── datos.py         # Generación aleatoria y ordenamiento (merge sort) por FC
├── validacion.py    # Validación con expresiones regulares
├── archivos.py      # Lectura/escritura TXT, CSV, JSON con manejo de excepciones
├── sistema.py       # Carpetas (os/pathlib), movimiento de archivos y log.txt
├── mongo_db.py      # Conexión y consultas a MongoDB Atlas
├── requirements.txt
├── .env.example     # Plantilla para la cadena de conexión
└── data/            # Se crea automáticamente
    ├── txt/
    ├── csv/
    └── json/
```

## Formato de los registros

| Campo | Descripción                    | Formato     | Regex               |
|-------|--------------------------------|-------------|---------------------|
| `id`  | Identificación                 | `ID-001`    | `^ID-\d{3}$`        |
| `fr`  | Edad                           | `18 Años`   | `^\d{1,3} Años$`    |
| `fc`  | Frecuencia cardiaca            | `090ppm`    | `^\d{3}ppm$`        |
| `spo2`| Saturación periférica de O₂    | `95%`       | `^(?:100\|\d{2})%$` |

## Instalación

```bash
git clone <URL-DEL-REPOSITORIO>
cd taller_biomedico
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configurar MongoDB Atlas

1. Crea un clúster gratuito en [MongoDB Atlas](https://www.mongodb.com/atlas).
2. Crea un usuario de base de datos y, en *Network Access*, permite tu IP.
3. Copia `.env.example` como `.env` y reemplaza `REEMPLAZA_CON_TU_PASSWORD` por la contraseña real del usuario de base de datos `alejandramadrid2_db_user`.
   La cadena ya incluye tu host de Atlas y usa la base de datos `taller_biomedico`.
4. En Atlas, verifica que tu IP esté permitida en *Network Access* y que el usuario tenga permisos de lectura/escritura.
   No compartas el archivo `.env` ni lo subas a GitHub.

> El archivo `.env` está en `.gitignore`: **nunca subas tus credenciales al repositorio.**

## Uso

```bash
python main.py
```

| Opción | Acción |
|--------|--------|
| 1 | Ingresar datos: generar ≥50 registros aleatorios o ingresar uno manualmente (validado con regex) |
| 2 | Ver los datos ordenados por frecuencia cardiaca |
| 3 | Validar los datos con expresiones regulares |
| 4 | Exportar a TXT, CSV y JSON (se mueven a `data/txt`, `data/csv`, `data/json`) |
| 5 | Importar desde JSON o CSV (los registros inválidos se descartan) |
| 6 | Insertar los registros validados en la colección `signos vitales` |
| 7 | Consultas: promedio de FC, SpO₂ < 94, búsqueda por ID, o exportar todo a `resultados_mongo.json` |

Todas las acciones y errores quedan registrados en `log.txt`.

## Detalles de implementación

- **Ordenamiento:** merge sort implementado manualmente (estable, O(n log n)), con clave numérica de la FC.
- **Excepciones y rutas:** `verificar_ruta` comprueba extensión, que no sea una carpeta y crea directorios faltantes; todas las operaciones de E/S capturan `OSError`, `JSONDecodeError`, etc.
- **MongoDB:** cada documento conserva el formato original (`"090ppm"`) y agrega `fr_num`, `fc_num` y `spo2_num`
  para poder calcular promedios y comparar. La inserción es un *upsert* por `id`, así que repetirla no duplica documentos.
- **Consultas:** promedio con `$group`/`$avg`; SpO₂ con `find({"spo2_num": {"$lt": 94}})`.

## Autor

Alejandra Madrid – Informática 1, Universidad de Antioquia.
## Tecnologías utilizadas

- Python 3
- MongoDB Atlas
- PyMongo
- Expresiones regulares (Regex)
- Archivos TXT, CSV y JSON

  ## Instalación y ejecución

1. Instalar Python 3.
2. Instalar las dependencias:

   pip install -r requirements.txt

3. Configurar las credenciales de MongoDB Atlas en el archivo .env.
4. Ejecutar el programa:

   python main.py
   
## Funcionalidades del sistema

- Generación aleatoria de registros de signos vitales.
- Ingreso manual de registros.
- Validación de datos mediante expresiones regulares.
- Ordenamiento por frecuencia cardíaca.
- Visualización y consulta de registros.
- Exportación e importación de archivos TXT, CSV y JSON.
- Conexión con MongoDB Atlas.
- Inserción y consulta de documentos en MongoDB.
- Registro de operaciones y errores en log.txt.

## Estructura del proyecto

- main.py: menú principal y ejecución del sistema.
- datos.py: generación y ordenamiento de registros.
- archivos.py: importación y exportación de archivos.
- validacion.py: validación de datos mediante Regex.
- mongo_db.py: conexión y operaciones con MongoDB.
- sistema.py: registro de actividades y estructura de carpetas.
- data/: archivos TXT, CSV y JSON.
- log.txt: historial de operaciones.
