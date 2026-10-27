# Sistema de Minimarket (Python)

Programa académico de la UNICEN (Bolivia) para administrar un minimarket:
productos, clientes, ventas con factura y reportes.

Hay **dos versiones** que comparten la misma lógica y la misma base SQLite:

| Versión | Archivo | ¿Cumple la consigna? |
|---|---|---|
| Terminal (menús con `input`/`print`) | `minimarket.py` | **Sí. Esta es la entrega principal.** |
| Flet (escritorio y web) | `app_flet.py` | Extra |

La lógica (validaciones, CRUD y ventas) está en `minimarket.py` y **no usa
`input()` ni `print()`**. La interfaz Flet hace `import minimarket as mm`
y llama a esas funciones. Los datos viven en `minimarket.db` (un solo
archivo SQLite). Si se registra un dato en la terminal, aparece en Flet
(y al revés).

## Requisitos

- Python 3 (el que viene con Windows o el de la universidad).
- Biblioteca estándar: `sqlite3`, `os` y `datetime`.
- **Solo Flet** es un paquete extra (para la interfaz gráfica/web).

En Windows se usa el comando `python` (no `python3`).

## Cómo instalar y ejecutar

Abrir una terminal (cmd o PowerShell) en la carpeta del proyecto.

Instalar Flet una sola vez:

```
pip install -r requirements.txt
```

### 1) Terminal (la que pide el profesor)

```
python minimarket.py
```

Aparece un menú: Productos, Clientes, Ventas, Reportes y Salir.

### 2) Flet en escritorio (extra)

```
python app_flet.py
```

o también:

```
flet run app_flet.py
```

Se abre una ventana con un menú a la izquierda (Inicio, Productos,
Clientes, Ventas, Reportes).

### 3) Flet en el navegador (extra)

```
flet run --web app_flet.py
```

El mismo programa se abre en el navegador (por ejemplo
http://127.0.0.1:un-puerto). Para detenerlo: `Ctrl + C` en la terminal.

La primera vez que se ejecuta **cualquier** versión, Python crea
`minimarket.db` y carga datos de ejemplo de un minimarket boliviano
(precios en Bs). Ese archivo no se sube a Git: se genera solo.

## Estructura del proyecto

```
minimarket-python/
├── minimarket.py         # Lógica + menús de terminal
├── base_datos.py         # SQLite: tablas, semilla y consultas
├── app_flet.py           # Extra: interfaz Flet (escritorio y web)
├── requirements.txt      # Solo Flet 1.0.5
├── docs/                 # Guía, informes y video (ver nota abajo)
└── README.md
```

Todo el programa está en archivos `.py`. No hay CSV, ni HTML, ni `.kv`.

## La base de datos SQLite

Un solo archivo: `minimarket.db` (junto a los `.py`).
Lo crea `base_datos.py` con `CREATE TABLE IF NOT EXISTS` y, si las
tablas están vacías, inserta ~10 productos, ~5 clientes y ~8 ventas.

### Tablas

```sql
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL CHECK (precio > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    stock_minimo INTEGER NOT NULL CHECK (stock_minimo >= 0)
);

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ci_nit TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    telefono TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    id_cliente INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario REAL NOT NULL,
    total REAL NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);
```

- **PRIMARY KEY AUTOINCREMENT:** el `id` lo asigna SQLite (1, 2, 3…).
- **UNIQUE:** no se puede repetir el código de un producto ni el CI/NIT.
- **CHECK:** el motor rechaza precio ≤ 0 o stock negativo.
- **FOREIGN KEY:** cada venta apunta a un cliente y a un producto
  que existen. Se activan con `PRAGMA foreign_keys = ON` en cada
  conexión (SQLite las apaga por defecto).
- **Fecha de venta:** texto `AAAA-MM-DD HH:MM` (ejemplo:
  `2026-10-26 09:15`).

### CRUD mapeado a SQL

| Acción | SQL | Función de lógica |
|---|---|---|
| Crear producto/cliente | `INSERT` | `agregar_producto` / `agregar_cliente` |
| Listar / buscar | `SELECT` | `obtener_productos` / `obtener_clientes` |
| Actualizar | `UPDATE` | `modificar_producto` / `modificar_cliente` |
| Eliminar | `DELETE` | `borrar_producto` / `borrar_cliente` |
| Registrar venta | `INSERT` + `UPDATE` stock | `realizar_venta` |

Todas las consultas usan `?` (consultas parametrizadas) para que el
valor no se mezcle con el comando SQL. Así se evita la **inyección SQL**.

## Resumen de las reglas de negocio

**Productos y clientes**

- Código de producto y CI/NIT no se repiten.
- Precio > 0; stock y stock mínimo ≥ 0.
- No se puede eliminar un producto o cliente que ya tenga ventas.

**Ventas**

- Se elige cliente, producto y cantidad.
- No se puede vender más de lo que hay en stock.
- Al vender se descuenta el stock (en la misma transacción) y se
  muestra una factura.
- Si el stock queda en el mínimo o por debajo, aparece un aviso.

**Reportes**

- Ventas del día (con total recaudado en Bs).
- Productos más vendidos (unidades).
- Productos con stock bajo.

## Nota para la exposición

La versión de **terminal** (`python minimarket.py`) es la que cumple la
consigna: menús en consola, base de datos, CRUD y sin inteligencia
artificial. Flet es un **extra** para mostrar la misma lógica en
escritorio y en el navegador.

La guía oral actualizada está en `docs/Guia_Exposicion.md`.

Los archivos `docs/*.docx` y `docs/demo_minimarket.mp4` se hicieron
con una versión anterior que usaba CSV, tkinter y Flask. **Esa parte
está desactualizada.** Hoy la base es SQLite y la interfaz extra es
Flet; no hay CSV ni tkinter ni Flask en el código.
