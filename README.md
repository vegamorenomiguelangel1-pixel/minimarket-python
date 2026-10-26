# Sistema de Minimarket (Python)

Programa académico de la UNICEN (Bolivia) para administrar un minimarket:
productos, clientes, ventas con factura y reportes.

Hay **tres versiones** que comparten la misma lógica y los mismos archivos CSV:

| Versión | Archivo | ¿Cumple la consigna? |
|---|---|---|
| Terminal (menús con `input`/`print`) | `minimarket.py` | **Sí. Esta es la entrega principal.** |
| Ventana gráfica (tkinter) | `minimarket_gui.py` | Extra |
| Página web (Flask) | `app_web.py` | Extra |

La lógica (validaciones, CRUD y ventas) está en `minimarket.py` y **no usa
`input()` ni `print()`**. Por eso la GUI y la web hacen
`import minimarket as mm` y reutilizan esas funciones. Si se registra un
dato en la terminal, aparece en la ventana y en el navegador (y al revés).

## Requisitos

- Python 3 (el que viene con Windows o el de la universidad).
- Biblioteca estándar: `csv`, `os`, `datetime` y `tkinter` (viene con Python).
- **Solo la versión web** necesita un paquete extra: Flask.

En Windows se usa el comando `python` (no `python3`).

## Cómo ejecutar cada versión

Abrir una terminal (cmd o PowerShell) en la carpeta del proyecto.

### 1) Terminal (la que pide el profesor)

```
python minimarket.py
```

Aparece un menú: Productos, Clientes, Ventas, Reportes y Salir.

### 2) Ventana gráfica (extra)

```
python minimarket_gui.py
```

Se abre una ventana con cuatro pestañas. Usa los mismos CSV.

### 3) Versión web (extra)

Instalar Flask una sola vez:

```
pip install -r requirements.txt
```

Arrancar el servidor:

```
python app_web.py
```

Abrir el navegador en: [http://127.0.0.1:5000](http://127.0.0.1:5000)

Para detener el servidor: `Ctrl + C` en la terminal.

## Estructura del proyecto

```
minimarket-python/
├── minimarket.py              # Lógica + menús de terminal
├── minimarket_gui.py          # Extra: ventana tkinter
├── app_web.py                 # Extra: servidor Flask
├── productos.csv              # Base de datos de productos
├── clientes.csv               # Base de datos de clientes
├── ventas.csv                 # Base de datos de ventas
├── requirements.txt           # Solo Flask (para la web)
├── templates/                 # Páginas HTML de la web
├── static/estilo.css          # Estilos de la web
├── docs/                      # Guía, informes y video de demo
└── README.md
```

## Los archivos CSV (la “base de datos”)

Están **en la misma carpeta** que los `.py`, para que las tres versiones
lean y escriban los mismos datos. **No se ignoran en Git**: el repositorio
incluye datos de ejemplo de un minimarket boliviano (precios en Bs).

| Archivo | Columnas | Ejemplo |
|---|---|---|
| `productos.csv` | id, codigo, nombre, categoria, precio, stock, stock_minimo | `P002`, Leche PIL 1L, 8.50 |
| `clientes.csv` | id, ci_nit, nombre, telefono | CI `8452167`, María Quispe |
| `ventas.csv` | id, fecha, id_cliente, id_producto, cantidad, precio_unitario, total | fecha `2026-10-26 09:15` |

La fecha de cada venta se guarda como `AAAA-MM-DD HH:MM`.
Cada venta guarda el `id` del cliente y del producto (como una llave
foránea): así se sabe quién compró qué.

Si se borran los CSV, el programa los vuelve a crear vacíos la primera vez
que se ejecuta (`inicializar_base_de_datos()`).

## Resumen del CRUD

**Productos y clientes**

- **Crear:** registrar un producto o un cliente.
- **Leer:** listar todos o buscar por texto (nombre/código o nombre/CI-NIT).
- **Actualizar:** cambiar los datos (en terminal, Enter deja el valor actual).
- **Eliminar:** solo si **no** tiene ventas registradas (pide confirmación).

**Ventas**

- Se elige cliente, producto y cantidad.
- No se puede vender más de lo que hay en stock.
- Al vender se descuenta el stock y se muestra una factura.
- Si el stock queda en el mínimo o por debajo, aparece un aviso.

**Reportes**

- Ventas del día (con total recaudado en Bs).
- Productos más vendidos (unidades).
- Productos con stock bajo.

Otras reglas: el código de producto no se repite, el CI/NIT no se repite,
el precio debe ser mayor a 0.

## Nota para la exposición

La versión de **terminal** (`python minimarket.py`) es la que cumple la
consigna del profesor: menús en consola, CSV como base de datos, CRUD y
sin inteligencia artificial.

La GUI y la web son **extras** para mostrar que la lógica se puede
reutilizar. En la guía de exposición (`docs/Guia_Exposicion.md`) está el
recorrido del código y las preguntas frecuentes.
