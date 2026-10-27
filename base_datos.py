"""
Módulo de base de datos SQLite del Minimarket.

Un solo archivo minimarket.db (junto a los .py) guarda tres tablas:
productos, clientes y ventas.

Las consultas usan el signo de interrogación (?) como marcador.
Así el valor viaja SEPARADO del comando SQL y no se mezcla con el
código. Eso evita la inyección SQL (por ejemplo, si alguien escribiera
un código de producto como  ' OR 1=1 --  no se ejecutaría como SQL).

Este módulo NO muestra menús ni ventanas: solo abre la base, crea
tablas, carga datos de ejemplo y ejecuta INSERT/SELECT/UPDATE/DELETE.
"""

import os
import sqlite3
from datetime import datetime, timedelta

# El .db se crea en la misma carpeta que este archivo .py
CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(CARPETA, "minimarket.db")


def usar_archivo(ruta):
    """Cambia la ruta del .db (lo usan las pruebas con un archivo temporal)."""
    global RUTA_DB
    RUTA_DB = ruta


def conectar():
    """Abre la base y activa las llaves foráneas en ESTA conexión.

    SQLite apaga las FOREIGN KEY por defecto. Hay que encenderlas
    cada vez que se abre el archivo.
    """
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row   # para leer fila["nombre"]
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def fila_a_dict(fila):
    """Convierte un sqlite3.Row en un diccionario de textos.

    Así el resto del programa (terminal y Flet) trabaja igual que
    cuando los datos venían de un CSV: todo se lee como str.
    """
    if fila is None:
        return None
    resultado = {}
    for clave in fila.keys():
        valor = fila[clave]
        resultado[clave] = "" if valor is None else str(valor)
    return resultado


def crear_tablas(conexion):
    """Crea las tres tablas si todavía no existen."""
    # PRIMARY KEY AUTOINCREMENT: el id lo asigna SQLite (1, 2, 3...)
    # UNIQUE: no se puede repetir el código de un producto
    # CHECK: el motor rechaza precio <= 0 o stock negativo
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL CHECK (precio > 0),
            stock INTEGER NOT NULL CHECK (stock >= 0),
            stock_minimo INTEGER NOT NULL CHECK (stock_minimo >= 0)
        )
        """
    )
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ci_nit TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
        """
    )
    # FOREIGN KEY: id_cliente debe existir en clientes,
    #              id_producto debe existir en productos
    conexion.execute(
        """
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
        )
        """
    )


def _contar(conexion, tabla):
    """Devuelve cuántas filas hay en una tabla."""
    # El nombre de la tabla lo elige el programa, no el usuario
    return conexion.execute(
        f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]


def cargar_datos_de_ejemplo(conexion):
    """Inserta productos, clientes y ventas de un minimarket boliviano.

    Solo corre si las tres tablas están vacías (primera ejecución).
    Las fechas de venta se arman con la fecha de hoy, para que el
    reporte "ventas del día" siempre tenga datos.
    """
    if (_contar(conexion, "productos") > 0
            or _contar(conexion, "clientes") > 0
            or _contar(conexion, "ventas") > 0):
        return

    productos = [
        ("P001", "Pan francés", "Panadería", 0.50, 45, 20),
        ("P002", "Leche PIL 1L", "Lácteos", 8.50, 3, 5),
        ("P003", "Arroz TAQUIÑA 1kg", "Abarrotes", 9.00, 25, 8),
        ("P004", "Azúcar Guabirá 1kg", "Abarrotes", 7.50, 18, 6),
        ("P005", "Aceite Fino 900ml", "Abarrotes", 15.00, 12, 4),
        ("P006", "Coca Cola 2L", "Bebidas", 12.00, 8, 6),
        ("P007", "Galletas Ducales", "Snacks", 6.50, 2, 8),
        ("P008", "Huevos criollos x12", "Frescos", 18.00, 10, 4),
        ("P009", "Fideo Molitalia 400g", "Abarrotes", 4.50, 30, 10),
        ("P010", "Papel higiénico Elite", "Limpieza", 8.00, 1, 5),
    ]
    conexion.executemany(
        """
        INSERT INTO productos
            (codigo, nombre, categoria, precio, stock, stock_minimo)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        productos,
    )

    clientes = [
        ("8452167", "María Quispe", "71234567"),
        ("3921845", "Juan Mamani", "77654321"),
        ("6719034", "Ana Flores", "70011223"),
        ("5588210", "Carlos Rojas", "76445566"),
        ("2234678", "Lucía Vargas", "72119988"),
    ]
    conexion.executemany(
        """
        INSERT INTO clientes (ci_nit, nombre, telefono)
        VALUES (?, ?, ?)
        """,
        clientes,
    )

    hoy = datetime.now()
    f = []
    for dias, hora in [
        (0, "09:15"), (0, "11:40"), (0, "15:20"), (0, "17:05"),
        (1, "10:30"), (1, "16:45"), (2, "08:50"), (3, "19:10"),
    ]:
        dia = hoy - timedelta(days=dias)
        f.append(dia.strftime("%Y-%m-%d") + " " + hora)

    # id_cliente, id_producto, cantidad, precio, total  (ids 1..n)
    ventas = [
        (f[0], 1, 1, 10, 0.50, 5.00),
        (f[1], 2, 6, 2, 12.00, 24.00),
        (f[2], 3, 2, 3, 8.50, 25.50),
        (f[3], 1, 7, 2, 6.50, 13.00),
        (f[4], 4, 3, 2, 9.00, 18.00),
        (f[5], 5, 8, 1, 18.00, 18.00),
        (f[6], 2, 5, 1, 15.00, 15.00),
        (f[7], 3, 10, 3, 8.00, 24.00),
    ]
    conexion.executemany(
        """
        INSERT INTO ventas
            (fecha, id_cliente, id_producto, cantidad,
             precio_unitario, total)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ventas,
    )


def inicializar():
    """Crea el archivo, las tablas y (si está vacío) los datos de ejemplo."""
    conexion = conectar()
    try:
        crear_tablas(conexion)
        cargar_datos_de_ejemplo(conexion)
        conexion.commit()
    finally:
        conexion.close()


# ============================================================
# CONSULTAS (SELECT)
# ============================================================

def listar(tabla):
    """Devuelve todas las filas de una tabla como lista de dicts."""
    conexion = conectar()
    try:
        filas = conexion.execute(f"SELECT * FROM {tabla}").fetchall()
        return [fila_a_dict(f) for f in filas]
    finally:
        conexion.close()


def listar_productos():
    """Lista los productos ordenados por id."""
    return listar("productos")


def listar_clientes():
    """Lista los clientes ordenados por id."""
    return listar("clientes")


def listar_ventas():
    """Lista las ventas ordenadas por id."""
    return listar("ventas")


def obtener(tabla, id_fila):
    """Busca una fila por id. Devuelve el dict o None."""
    conexion = conectar()
    try:
        fila = conexion.execute(
            f"SELECT * FROM {tabla} WHERE id = ?",
            (id_fila,),
        ).fetchone()
        return fila_a_dict(fila)
    finally:
        conexion.close()


def obtener_producto(id_producto):
    """Devuelve un producto o None."""
    return obtener("productos", id_producto)


def obtener_cliente(id_cliente):
    """Devuelve un cliente o None."""
    return obtener("clientes", id_cliente)


def obtener_venta(id_venta):
    """Devuelve una venta o None."""
    return obtener("ventas", id_venta)


def existe_codigo(codigo, id_excluido=""):
    """True si otro producto ya usa ese código."""
    conexion = conectar()
    try:
        if id_excluido == "":
            fila = conexion.execute(
                "SELECT id FROM productos WHERE codigo = ?",
                (codigo,),
            ).fetchone()
        else:
            fila = conexion.execute(
                "SELECT id FROM productos WHERE codigo = ? AND id != ?",
                (codigo, id_excluido),
            ).fetchone()
        return fila is not None
    finally:
        conexion.close()


def existe_ci(ci_nit, id_excluido=""):
    """True si otro cliente ya usa ese CI/NIT."""
    conexion = conectar()
    try:
        if id_excluido == "":
            fila = conexion.execute(
                "SELECT id FROM clientes WHERE ci_nit = ?",
                (ci_nit,),
            ).fetchone()
        else:
            fila = conexion.execute(
                "SELECT id FROM clientes WHERE ci_nit = ? AND id != ?",
                (ci_nit, id_excluido),
            ).fetchone()
        return fila is not None
    finally:
        conexion.close()


def tiene_ventas(campo, id_buscado):
    """True si existe alguna venta con ese id_cliente o id_producto."""
    # campo solo puede ser id_cliente o id_producto (lo elige el programa)
    conexion = conectar()
    try:
        fila = conexion.execute(
            f"SELECT id FROM ventas WHERE {campo} = ?",
            (id_buscado,),
        ).fetchone()
        return fila is not None
    finally:
        conexion.close()


# ============================================================
# ALTAS, BAJAS Y CAMBIOS (INSERT / UPDATE / DELETE)
# ============================================================

def insertar_producto(datos):
    """INSERT de un producto. Devuelve el id nuevo."""
    conexion = conectar()
    try:
        cursor = conexion.execute(
            """
            INSERT INTO productos
                (codigo, nombre, categoria, precio, stock, stock_minimo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (datos["codigo"], datos["nombre"], datos["categoria"],
             datos["precio"], datos["stock"], datos["stock_minimo"]),
        )
        conexion.commit()
        return cursor.lastrowid
    finally:
        conexion.close()


def actualizar_producto(id_producto, datos):
    """UPDATE de un producto existente."""
    conexion = conectar()
    try:
        conexion.execute(
            """
            UPDATE productos
            SET codigo = ?, nombre = ?, categoria = ?,
                precio = ?, stock = ?, stock_minimo = ?
            WHERE id = ?
            """,
            (datos["codigo"], datos["nombre"], datos["categoria"],
             datos["precio"], datos["stock"], datos["stock_minimo"],
             id_producto),
        )
        conexion.commit()
    finally:
        conexion.close()


def eliminar_fila(tabla, id_fila):
    """DELETE de una fila por id."""
    conexion = conectar()
    try:
        conexion.execute(
            f"DELETE FROM {tabla} WHERE id = ?",
            (id_fila,),
        )
        conexion.commit()
    finally:
        conexion.close()


def insertar_cliente(datos):
    """INSERT de un cliente. Devuelve el id nuevo."""
    conexion = conectar()
    try:
        cursor = conexion.execute(
            """
            INSERT INTO clientes (ci_nit, nombre, telefono)
            VALUES (?, ?, ?)
            """,
            (datos["ci_nit"], datos["nombre"], datos["telefono"]),
        )
        conexion.commit()
        return cursor.lastrowid
    finally:
        conexion.close()


def actualizar_cliente(id_cliente, datos):
    """UPDATE de un cliente existente."""
    conexion = conectar()
    try:
        conexion.execute(
            """
            UPDATE clientes
            SET ci_nit = ?, nombre = ?, telefono = ?
            WHERE id = ?
            """,
            (datos["ci_nit"], datos["nombre"], datos["telefono"],
             id_cliente),
        )
        conexion.commit()
    finally:
        conexion.close()


def guardar_venta_y_descontar_stock(venta, id_producto, stock_nuevo):
    """INSERT de la venta y UPDATE del stock en la MISMA transacción.

    Si falla el segundo comando, no se guarda la venta a medias.
    """
    conexion = conectar()
    try:
        cursor = conexion.execute(
            """
            INSERT INTO ventas
                (fecha, id_cliente, id_producto, cantidad,
                 precio_unitario, total)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (venta["fecha"], venta["id_cliente"], venta["id_producto"],
             venta["cantidad"], venta["precio_unitario"], venta["total"]),
        )
        conexion.execute(
            "UPDATE productos SET stock = ? WHERE id = ?",
            (stock_nuevo, id_producto),
        )
        conexion.commit()
        return cursor.lastrowid
    finally:
        conexion.close()
