"""
Sistema de Minimarket (programa de terminal).

Permite administrar productos, clientes y ventas de un minimarket.
Los datos se guardan en archivos CSV que funcionan como base de datos.
Solo usa la biblioteca estándar de Python: csv, os y datetime.

Las funciones de "lógica" (secciones 4 y 5) no usan input() ni print(),
por eso también las reutiliza la versión gráfica (minimarket_gui.py).
"""

import csv
import os
from datetime import datetime

# ============================================================
# 1) BASE DE DATOS CSV
# ============================================================

# Los CSV se guardan en la misma carpeta que este archivo .py
CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_PRODUCTOS = os.path.join(CARPETA, "productos.csv")
ARCHIVO_CLIENTES = os.path.join(CARPETA, "clientes.csv")
ARCHIVO_VENTAS = os.path.join(CARPETA, "ventas.csv")

CAMPOS_PRODUCTOS = ["id", "codigo", "nombre", "categoria",
                    "precio", "stock", "stock_minimo"]
CAMPOS_CLIENTES = ["id", "ci_nit", "nombre", "telefono"]
CAMPOS_VENTAS = ["id", "fecha", "id_cliente", "id_producto",
                 "cantidad", "precio_unitario", "total"]


def crear_archivo_si_no_existe(nombre_archivo, campos):
    """Crea el archivo CSV con su encabezado si todavía no existe."""
    if not os.path.exists(nombre_archivo):
        with open(nombre_archivo, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=campos)
            escritor.writeheader()


def inicializar_base_de_datos():
    """Crea los tres archivos CSV del sistema."""
    crear_archivo_si_no_existe(ARCHIVO_PRODUCTOS, CAMPOS_PRODUCTOS)
    crear_archivo_si_no_existe(ARCHIVO_CLIENTES, CAMPOS_CLIENTES)
    crear_archivo_si_no_existe(ARCHIVO_VENTAS, CAMPOS_VENTAS)


def leer_datos(nombre_archivo):
    """Lee el CSV y devuelve una lista de diccionarios (una fila = un dict)."""
    filas = []
    with open(nombre_archivo, "r", newline="", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            filas.append(fila)
    return filas


def guardar_datos(nombre_archivo, campos, filas):
    """Sobrescribe el CSV completo con la lista de filas recibida."""
    with open(nombre_archivo, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def generar_id(filas):
    """Devuelve el siguiente id: el mayor id existente + 1."""
    mayor = 0
    for fila in filas:
        if int(fila["id"]) > mayor:
            mayor = int(fila["id"])
    return mayor + 1


def buscar_por_id(filas, id_buscado):
    """Devuelve la fila con ese id o None si no existe."""
    for fila in filas:
        if fila["id"] == str(id_buscado):
            return fila
    return None


# ============================================================
# 2) ESTILO VISUAL (colores, pantalla y tablas)
# ============================================================

# Códigos ANSI: cambian el color del texto en la terminal
RESET = "\033[0m"
NEGRITA = "\033[1m"
ROJO = "\033[91m"
VERDE = "\033[92m"
AMARILLO = "\033[93m"
CIAN = "\033[96m"


def activar_colores():
    """En Windows, os.system('') activa los colores ANSI en la consola."""
    os.system("")


def limpiar_pantalla():
    """Borra la pantalla (cls en Windows, clear en Linux/Mac)."""
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_encabezado(titulo):
    """Limpia la pantalla y muestra el banner con el nombre del sistema."""
    limpiar_pantalla()
    print(CIAN + NEGRITA + "+" + "-" * 38 + "+")
    print("|" + "MINIMARKET".center(38) + "|")
    print("|" + titulo.center(38) + "|")
    print("+" + "-" * 38 + "+" + RESET)


def mensaje_exito(texto):
    """Muestra un mensaje en verde."""
    print(VERDE + texto + RESET)


def mensaje_error(texto):
    """Muestra un mensaje en rojo."""
    print(ROJO + texto + RESET)


def mensaje_aviso(texto):
    """Muestra un mensaje en amarillo."""
    print(AMARILLO + texto + RESET)


def mostrar_resultado(exito, mensaje):
    """Muestra el mensaje en verde si salió bien o en rojo si hubo error."""
    if exito:
        mensaje_exito(mensaje)
    else:
        mensaje_error(mensaje)


def formatear_fila(valores, anchos):
    """Arma una fila de tabla del tipo | valor | valor |."""
    linea = "|"
    for i in range(len(valores)):
        linea += " " + str(valores[i]).ljust(anchos[i]) + " |"
    return linea


def imprimir_tabla(encabezados, filas):
    """Imprime una tabla con bordes +---+ ajustando el ancho de columnas."""
    anchos = []
    for i in range(len(encabezados)):
        ancho = len(encabezados[i])
        for fila in filas:
            if len(str(fila[i])) > ancho:
                ancho = len(str(fila[i]))
        anchos.append(ancho)
    separador = "+"
    for ancho in anchos:
        separador += "-" * (ancho + 2) + "+"
    print(separador)
    print(NEGRITA + formatear_fila(encabezados, anchos) + RESET)
    print(separador)
    for fila in filas:
        print(formatear_fila(fila, anchos))
    print(separador)


def imprimir_caja(lineas):
    """Imprime una lista de líneas dentro de un recuadro (para la factura)."""
    ancho = 0
    for linea in lineas:
        if len(linea) > ancho:
            ancho = len(linea)
    borde = "+" + "-" * (ancho + 2) + "+"
    print(borde)
    print("| " + NEGRITA + lineas[0].center(ancho) + RESET + " |")
    print(borde)
    for linea in lineas[1:]:
        print("| " + linea.ljust(ancho) + " |")
    print(borde)


# ============================================================
# 3) UTILIDADES DE ENTRADA (terminal)
# ============================================================

def pedir_texto(mensaje):
    """Pide un texto y no acepta que quede vacío."""
    while True:
        texto = input(mensaje).strip()
        if texto != "":
            return texto
        mensaje_error("  Error: el dato no puede estar vacío.")


def pedir_entero(mensaje, minimo=0):
    """Pide un número entero mayor o igual al mínimo indicado."""
    while True:
        numero = convertir_entero(input(mensaje))
        if numero is not None and numero >= minimo:
            return numero
        mensaje_error(f"  Error: ingrese un entero mayor o igual a {minimo}.")


def pedir_precio(mensaje):
    """Pide un precio decimal que debe ser mayor a 0."""
    while True:
        precio = convertir_precio(input(mensaje))
        if precio is not None and precio > 0:
            return precio
        mensaje_error("  Error: ingrese un precio mayor a 0 (ej: 7.50).")


def pedir_opcional(etiqueta, valor_actual):
    """Pide un dato; si el usuario presiona Enter, se queda el valor actual."""
    texto = input(f"{etiqueta} [{valor_actual}]: ").strip()
    if texto == "":
        return valor_actual
    return texto


def confirmar(mensaje):
    """Pregunta s/n y devuelve True si el usuario responde 's'."""
    while True:
        respuesta = input(mensaje + " (s/n): ").strip().lower()
        if respuesta == "s":
            return True
        if respuesta == "n":
            return False
        mensaje_error("  Responda solo 's' o 'n'.")


def pausar():
    """Espera a que el usuario presione Enter."""
    input("\nPresiona Enter para continuar...")


# ============================================================
# 4) LÓGICA DE PRODUCTOS Y CLIENTES (sin input ni print)
#    Cada función devuelve (exito, mensaje).
# ============================================================

def convertir_entero(texto):
    """Convierte un texto a entero (>= 0). Devuelve None si no es válido."""
    texto = texto.strip()
    if texto.isdigit():
        return int(texto)
    return None


def convertir_precio(texto):
    """Convierte un texto a decimal (acepta coma). None si no es válido."""
    try:
        return float(texto.strip().replace(",", "."))
    except ValueError:
        return None


def codigo_repetido(productos, codigo, id_excluido=""):
    """Indica si el código ya lo usa otro producto."""
    for p in productos:
        if p["codigo"] == codigo and p["id"] != id_excluido:
            return True
    return False


def ci_repetido(clientes, ci_nit, id_excluido=""):
    """Indica si el CI/NIT ya lo usa otro cliente."""
    for c in clientes:
        if c["ci_nit"] == ci_nit and c["id"] != id_excluido:
            return True
    return False


def tiene_ventas(campo, id_buscado):
    """Indica si existe alguna venta con ese id en el campo indicado."""
    for v in leer_datos(ARCHIVO_VENTAS):
        if v[campo] == str(id_buscado):
            return True
    return False


def validar_producto(productos, datos, id_excluido=""):
    """Revisa las reglas del producto. Devuelve el error o "" si está bien."""
    if datos["codigo"] == "" or datos["nombre"] == "" \
            or datos["categoria"] == "":
        return "Código, nombre y categoría son obligatorios."
    if codigo_repetido(productos, datos["codigo"], id_excluido):
        return "Ya existe un producto con ese código."
    if datos["precio"] <= 0:
        return "El precio debe ser mayor a 0."
    if datos["stock"] < 0 or datos["stock_minimo"] < 0:
        return "El stock y el stock mínimo no pueden ser negativos."
    return ""


def agregar_producto(datos):
    """Guarda un producto nuevo. 'datos' es un dict con sus campos."""
    productos = leer_datos(ARCHIVO_PRODUCTOS)
    error = validar_producto(productos, datos)
    if error != "":
        return False, error
    datos["id"] = generar_id(productos)
    productos.append(datos)
    guardar_datos(ARCHIVO_PRODUCTOS, CAMPOS_PRODUCTOS, productos)
    return True, f"Producto registrado con id {datos['id']}."


def modificar_producto(id_producto, datos):
    """Reemplaza los datos de un producto existente."""
    productos = leer_datos(ARCHIVO_PRODUCTOS)
    p = buscar_por_id(productos, id_producto)
    if p is None:
        return False, "Producto no encontrado."
    error = validar_producto(productos, datos, p["id"])
    if error != "":
        return False, error
    p.update(datos)   # copia los nuevos valores dentro del producto
    guardar_datos(ARCHIVO_PRODUCTOS, CAMPOS_PRODUCTOS, productos)
    return True, "Producto actualizado."


def borrar_producto(id_producto):
    """Elimina un producto si no tiene ventas registradas."""
    productos = leer_datos(ARCHIVO_PRODUCTOS)
    p = buscar_por_id(productos, id_producto)
    if p is None:
        return False, "Producto no encontrado."
    if tiene_ventas("id_producto", p["id"]):
        return False, "No se puede eliminar: el producto tiene ventas."
    productos.remove(p)
    guardar_datos(ARCHIVO_PRODUCTOS, CAMPOS_PRODUCTOS, productos)
    return True, "Producto eliminado."


def validar_cliente(clientes, datos, id_excluido=""):
    """Revisa las reglas del cliente. Devuelve el error o "" si está bien."""
    if datos["ci_nit"] == "" or datos["nombre"] == "" \
            or datos["telefono"] == "":
        return "CI/NIT, nombre y teléfono son obligatorios."
    if ci_repetido(clientes, datos["ci_nit"], id_excluido):
        return "Ya existe un cliente con ese CI/NIT."
    return ""


def agregar_cliente(datos):
    """Guarda un cliente nuevo."""
    clientes = leer_datos(ARCHIVO_CLIENTES)
    error = validar_cliente(clientes, datos)
    if error != "":
        return False, error
    datos["id"] = generar_id(clientes)
    clientes.append(datos)
    guardar_datos(ARCHIVO_CLIENTES, CAMPOS_CLIENTES, clientes)
    return True, f"Cliente registrado con id {datos['id']}."


def modificar_cliente(id_cliente, datos):
    """Reemplaza los datos de un cliente existente."""
    clientes = leer_datos(ARCHIVO_CLIENTES)
    c = buscar_por_id(clientes, id_cliente)
    if c is None:
        return False, "Cliente no encontrado."
    error = validar_cliente(clientes, datos, c["id"])
    if error != "":
        return False, error
    c.update(datos)
    guardar_datos(ARCHIVO_CLIENTES, CAMPOS_CLIENTES, clientes)
    return True, "Cliente actualizado."


def borrar_cliente(id_cliente):
    """Elimina un cliente si no tiene ventas registradas."""
    clientes = leer_datos(ARCHIVO_CLIENTES)
    c = buscar_por_id(clientes, id_cliente)
    if c is None:
        return False, "Cliente no encontrado."
    if tiene_ventas("id_cliente", c["id"]):
        return False, "No se puede eliminar: el cliente tiene ventas."
    clientes.remove(c)
    guardar_datos(ARCHIVO_CLIENTES, CAMPOS_CLIENTES, clientes)
    return True, "Cliente eliminado."


# ============================================================
# 5) LÓGICA DE VENTAS Y REPORTES (sin input ni print)
# ============================================================

def realizar_venta(id_cliente, id_producto, cantidad):
    """Registra una venta y descuenta stock.

    Devuelve (exito, mensaje, venta). Si hay error, venta es None.
    """
    clientes = leer_datos(ARCHIVO_CLIENTES)
    productos = leer_datos(ARCHIVO_PRODUCTOS)
    if buscar_por_id(clientes, id_cliente) is None:
        return False, "Cliente no encontrado.", None
    producto = buscar_por_id(productos, id_producto)
    if producto is None:
        return False, "Producto no encontrado.", None
    stock = int(producto["stock"])
    if cantidad <= 0:
        return False, "La cantidad debe ser mayor a 0.", None
    # Regla: no se vende más de lo que hay en stock
    if cantidad > stock:
        return False, f"Stock insuficiente (solo hay {stock}).", None
    precio = float(producto["precio"])
    ventas = leer_datos(ARCHIVO_VENTAS)
    venta = {
        "id": generar_id(ventas),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "id_cliente": str(id_cliente),
        "id_producto": str(id_producto),
        "cantidad": cantidad,
        "precio_unitario": precio,
        "total": round(precio * cantidad, 2),
    }
    ventas.append(venta)
    guardar_datos(ARCHIVO_VENTAS, CAMPOS_VENTAS, ventas)
    # Regla: al vender se descuenta el stock
    producto["stock"] = stock - cantidad
    guardar_datos(ARCHIVO_PRODUCTOS, CAMPOS_PRODUCTOS, productos)
    return True, "Venta registrada.", venta


def stock_bajo(producto):
    """Indica si el stock está en o por debajo del stock mínimo."""
    return int(producto["stock"]) <= int(producto["stock_minimo"])


def lineas_factura(venta):
    """Devuelve la factura de una venta como lista de líneas de texto."""
    cliente = buscar_por_id(leer_datos(ARCHIVO_CLIENTES), venta["id_cliente"])
    producto = buscar_por_id(leer_datos(ARCHIVO_PRODUCTOS),
                             venta["id_producto"])
    precio = float(venta["precio_unitario"])
    return [
        "MINIMARKET - FACTURA",
        f"N° de venta: {venta['id']}",
        f"Fecha:       {venta['fecha']}",
        f"Cliente:     {nombre_o_eliminado(cliente)}",
        f"CI/NIT:      {cliente['ci_nit']}",
        f"Producto:    {nombre_o_eliminado(producto)}",
        f"Cantidad:    {venta['cantidad']} x Bs {precio:.2f}",
        f"TOTAL:       Bs {float(venta['total']):.2f}",
    ]


def nombre_o_eliminado(fila):
    """Devuelve el nombre de la fila o un texto si ya no existe."""
    if fila is None:
        return "(no encontrado)"
    return fila["nombre"]


def ventas_de_hoy():
    """Devuelve la lista de ventas cuya fecha es hoy."""
    hoy = datetime.now().strftime("%Y-%m-%d")
    resultado = []
    for v in leer_datos(ARCHIVO_VENTAS):
        if v["fecha"][:10] == hoy:   # los 10 primeros caracteres = fecha
            resultado.append(v)
    return resultado


def calcular_total(ventas):
    """Suma el total de una lista de ventas."""
    total = 0
    for v in ventas:
        total += float(v["total"])
    return total


def calcular_mas_vendidos():
    """Devuelve una lista [unidades, nombre] ordenada de mayor a menor."""
    unidades = {}   # clave: id_producto, valor: unidades vendidas
    for v in leer_datos(ARCHIVO_VENTAS):
        id_producto = v["id_producto"]
        if id_producto not in unidades:
            unidades[id_producto] = 0
        unidades[id_producto] += int(v["cantidad"])
    productos = leer_datos(ARCHIVO_PRODUCTOS)
    ranking = []
    for id_producto in unidades:
        nombre = nombre_o_eliminado(buscar_por_id(productos, id_producto))
        ranking.append([unidades[id_producto], nombre])
    ranking.sort(reverse=True)
    return ranking


def productos_con_stock_bajo():
    """Devuelve los productos cuyo stock es menor o igual al mínimo."""
    resultado = []
    for p in leer_datos(ARCHIVO_PRODUCTOS):
        if stock_bajo(p):
            resultado.append(p)
    return resultado


# ============================================================
# 6) PANTALLAS DE PRODUCTOS (terminal)
# ============================================================

def mostrar_tabla_productos(productos):
    """Muestra una lista de productos en forma de tabla."""
    filas = []
    for p in productos:
        filas.append([p["id"], p["codigo"], p["nombre"], p["categoria"],
                      f"{float(p['precio']):.2f}", p["stock"],
                      p["stock_minimo"]])
    imprimir_tabla(["Id", "Código", "Nombre", "Categoría", "Precio Bs",
                    "Stock", "Mínimo"], filas)


def crear_producto():
    """Pide los datos de un producto nuevo y lo registra."""
    productos = leer_datos(ARCHIVO_PRODUCTOS)
    codigo = pedir_texto("Código: ")
    if codigo_repetido(productos, codigo):
        mensaje_error("Error: ya existe un producto con ese código.")
        return
    datos = {
        "codigo": codigo,
        "nombre": pedir_texto("Nombre: "),
        "categoria": pedir_texto("Categoría: "),
        "precio": pedir_precio("Precio (Bs): "),
        "stock": pedir_entero("Stock inicial: ", 0),
        "stock_minimo": pedir_entero("Stock mínimo: ", 0),
    }
    exito, mensaje = agregar_producto(datos)
    mostrar_resultado(exito, mensaje)


def listar_productos():
    """Muestra todos los productos."""
    productos = leer_datos(ARCHIVO_PRODUCTOS)
    if len(productos) == 0:
        mensaje_aviso("No hay productos registrados.")
    else:
        mostrar_tabla_productos(productos)


def buscar_producto():
    """Busca productos cuyo nombre o código contenga el texto ingresado."""
    texto = pedir_texto("Texto a buscar (nombre o código): ").lower()
    encontrados = []
    for p in leer_datos(ARCHIVO_PRODUCTOS):
        if texto in p["nombre"].lower() or texto in p["codigo"].lower():
            encontrados.append(p)
    if len(encontrados) == 0:
        mensaje_aviso("No se encontraron productos.")
    else:
        mostrar_tabla_productos(encontrados)


def actualizar_producto():
    """Modifica un producto. Enter deja el valor actual."""
    p = buscar_por_id(leer_datos(ARCHIVO_PRODUCTOS),
                      pedir_entero("Id del producto: ", 1))
    if p is None:
        mensaje_error("Producto no encontrado.")
        return
    mostrar_tabla_productos([p])
    print("(Presione Enter para mantener el valor actual)")
    codigo = pedir_opcional("Código", p["codigo"])
    if codigo_repetido(leer_datos(ARCHIVO_PRODUCTOS), codigo, p["id"]):
        mensaje_error("Error: ese código ya pertenece a otro producto.")
        return
    datos = {
        "codigo": codigo,
        "nombre": pedir_opcional("Nombre", p["nombre"]),
        "categoria": pedir_opcional("Categoría", p["categoria"]),
        "precio": float(p["precio"]),
        "stock": int(p["stock"]),
        "stock_minimo": int(p["stock_minimo"]),
    }
    if confirmar("¿Cambiar precio, stock y stock mínimo?"):
        datos["precio"] = pedir_precio("Nuevo precio (Bs): ")
        datos["stock"] = pedir_entero("Nuevo stock: ", 0)
        datos["stock_minimo"] = pedir_entero("Nuevo stock mínimo: ", 0)
    exito, mensaje = modificar_producto(p["id"], datos)
    mostrar_resultado(exito, mensaje)


def eliminar_producto():
    """Elimina un producto (pide confirmación)."""
    p = buscar_por_id(leer_datos(ARCHIVO_PRODUCTOS),
                      pedir_entero("Id del producto: ", 1))
    if p is None:
        mensaje_error("Producto no encontrado.")
        return
    if tiene_ventas("id_producto", p["id"]):
        mensaje_error("No se puede eliminar: el producto tiene ventas.")
        return
    mostrar_tabla_productos([p])
    if confirmar("¿Seguro que desea eliminarlo?"):
        exito, mensaje = borrar_producto(p["id"])
        mostrar_resultado(exito, mensaje)
    else:
        mensaje_aviso("Operación cancelada.")


# ============================================================
# 7) PANTALLAS DE CLIENTES (terminal)
# ============================================================

def mostrar_tabla_clientes(clientes):
    """Muestra una lista de clientes en forma de tabla."""
    filas = []
    for c in clientes:
        filas.append([c["id"], c["ci_nit"], c["nombre"], c["telefono"]])
    imprimir_tabla(["Id", "CI/NIT", "Nombre", "Teléfono"], filas)


def crear_cliente():
    """Pide los datos de un cliente nuevo y lo registra."""
    ci_nit = pedir_texto("CI/NIT: ")
    if ci_repetido(leer_datos(ARCHIVO_CLIENTES), ci_nit):
        mensaje_error("Error: ya existe un cliente con ese CI/NIT.")
        return
    datos = {
        "ci_nit": ci_nit,
        "nombre": pedir_texto("Nombre: "),
        "telefono": pedir_texto("Teléfono: "),
    }
    exito, mensaje = agregar_cliente(datos)
    mostrar_resultado(exito, mensaje)


def listar_clientes():
    """Muestra todos los clientes."""
    clientes = leer_datos(ARCHIVO_CLIENTES)
    if len(clientes) == 0:
        mensaje_aviso("No hay clientes registrados.")
    else:
        mostrar_tabla_clientes(clientes)


def buscar_cliente():
    """Busca clientes por nombre o CI/NIT."""
    texto = pedir_texto("Texto a buscar (nombre o CI/NIT): ").lower()
    encontrados = []
    for c in leer_datos(ARCHIVO_CLIENTES):
        if texto in c["nombre"].lower() or texto in c["ci_nit"]:
            encontrados.append(c)
    if len(encontrados) == 0:
        mensaje_aviso("No se encontraron clientes.")
    else:
        mostrar_tabla_clientes(encontrados)


def actualizar_cliente():
    """Modifica un cliente. Enter deja el valor actual."""
    c = buscar_por_id(leer_datos(ARCHIVO_CLIENTES),
                      pedir_entero("Id del cliente: ", 1))
    if c is None:
        mensaje_error("Cliente no encontrado.")
        return
    mostrar_tabla_clientes([c])
    print("(Presione Enter para mantener el valor actual)")
    ci_nit = pedir_opcional("CI/NIT", c["ci_nit"])
    if ci_repetido(leer_datos(ARCHIVO_CLIENTES), ci_nit, c["id"]):
        mensaje_error("Error: ese CI/NIT ya pertenece a otro cliente.")
        return
    datos = {
        "ci_nit": ci_nit,
        "nombre": pedir_opcional("Nombre", c["nombre"]),
        "telefono": pedir_opcional("Teléfono", c["telefono"]),
    }
    exito, mensaje = modificar_cliente(c["id"], datos)
    mostrar_resultado(exito, mensaje)


def eliminar_cliente():
    """Elimina un cliente (pide confirmación)."""
    c = buscar_por_id(leer_datos(ARCHIVO_CLIENTES),
                      pedir_entero("Id del cliente: ", 1))
    if c is None:
        mensaje_error("Cliente no encontrado.")
        return
    if tiene_ventas("id_cliente", c["id"]):
        mensaje_error("No se puede eliminar: el cliente tiene ventas.")
        return
    mostrar_tabla_clientes([c])
    if confirmar("¿Seguro que desea eliminarlo?"):
        exito, mensaje = borrar_cliente(c["id"])
        mostrar_resultado(exito, mensaje)
    else:
        mensaje_aviso("Operación cancelada.")


# ============================================================
# 8) PANTALLAS DE VENTAS Y REPORTES (terminal)
# ============================================================

def registrar_venta():
    """Pide cliente, producto y cantidad; registra la venta y la factura."""
    id_cliente = pedir_entero("Id del cliente: ", 1)
    if buscar_por_id(leer_datos(ARCHIVO_CLIENTES), id_cliente) is None:
        mensaje_error("Cliente no encontrado.")
        return
    id_producto = pedir_entero("Id del producto: ", 1)
    producto = buscar_por_id(leer_datos(ARCHIVO_PRODUCTOS), id_producto)
    if producto is None:
        mensaje_error("Producto no encontrado.")
        return
    print(f"Producto: {producto['nombre']} | "
          f"Stock disponible: {producto['stock']}")
    cantidad = pedir_entero("Cantidad: ", 1)
    exito, mensaje, venta = realizar_venta(id_cliente, id_producto, cantidad)
    if not exito:
        mensaje_error("Error: " + mensaje)
        return
    imprimir_caja(lineas_factura(venta))
    mensaje_exito(mensaje)
    # Regla: aviso de stock bajo después de vender
    producto = buscar_por_id(leer_datos(ARCHIVO_PRODUCTOS), id_producto)
    if stock_bajo(producto):
        mensaje_aviso(f"¡AVISO! Stock bajo de '{producto['nombre']}': "
                      f"quedan {producto['stock']} unidades.")


def mostrar_tabla_ventas(ventas):
    """Muestra una lista de ventas con nombre de cliente y producto."""
    clientes = leer_datos(ARCHIVO_CLIENTES)
    productos = leer_datos(ARCHIVO_PRODUCTOS)
    filas = []
    for v in ventas:
        cliente = buscar_por_id(clientes, v["id_cliente"])
        producto = buscar_por_id(productos, v["id_producto"])
        filas.append([v["id"], v["fecha"], nombre_o_eliminado(cliente),
                      nombre_o_eliminado(producto), v["cantidad"],
                      f"{float(v['total']):.2f}"])
    imprimir_tabla(["Id", "Fecha", "Cliente", "Producto", "Cant.",
                    "Total Bs"], filas)


def listar_ventas():
    """Muestra todas las ventas."""
    ventas = leer_datos(ARCHIVO_VENTAS)
    if len(ventas) == 0:
        mensaje_aviso("No hay ventas registradas.")
    else:
        mostrar_tabla_ventas(ventas)


def ver_detalle_venta():
    """Vuelve a mostrar la factura de una venta según su id."""
    venta = buscar_por_id(leer_datos(ARCHIVO_VENTAS),
                          pedir_entero("Id de la venta: ", 1))
    if venta is None:
        mensaje_error("Venta no encontrada.")
    else:
        imprimir_caja(lineas_factura(venta))


def reporte_ventas_del_dia():
    """Muestra las ventas de hoy y el total recaudado."""
    ventas = ventas_de_hoy()
    if len(ventas) > 0:
        mostrar_tabla_ventas(ventas)
    print(f"Cantidad de ventas: {len(ventas)}")
    mensaje_exito(f"TOTAL RECAUDADO: Bs {calcular_total(ventas):.2f}")


def reporte_mas_vendidos():
    """Muestra el ranking de productos más vendidos."""
    ranking = calcular_mas_vendidos()
    if len(ranking) == 0:
        mensaje_aviso("Todavía no hay ventas.")
        return
    filas = []
    for posicion, par in enumerate(ranking, start=1):
        filas.append([posicion, par[1], par[0]])
    imprimir_tabla(["N°", "Producto", "Unidades"], filas)


def reporte_stock_bajo():
    """Muestra los productos con stock bajo."""
    productos = productos_con_stock_bajo()
    if len(productos) == 0:
        mensaje_exito("Todos los productos tienen stock suficiente.")
    else:
        mensaje_aviso("Productos con stock bajo:")
        mostrar_tabla_productos(productos)


# ============================================================
# 9) MENÚS
# ============================================================

def ejecutar_menu(titulo, opciones):
    """Muestra un submenú y ejecuta la función elegida hasta elegir 0.

    'opciones' es una lista de pares [texto, funcion].
    """
    while True:
        mostrar_encabezado(titulo)
        for numero, opcion in enumerate(opciones, start=1):
            print(f"  {numero}. {opcion[0]}")
        print("  0. Volver")
        eleccion = input("Opción: ").strip()
        if eleccion == "0":
            return
        if eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones):
            mostrar_encabezado(opciones[int(eleccion) - 1][0].upper())
            funcion = opciones[int(eleccion) - 1][1]
            funcion()
        else:
            mensaje_error("Opción inválida.")
        pausar()


def menu_productos():
    """Submenú de productos."""
    ejecutar_menu("PRODUCTOS", [
        ["Registrar producto", crear_producto],
        ["Listar productos", listar_productos],
        ["Buscar producto", buscar_producto],
        ["Actualizar producto", actualizar_producto],
        ["Eliminar producto", eliminar_producto],
    ])


def menu_clientes():
    """Submenú de clientes."""
    ejecutar_menu("CLIENTES", [
        ["Registrar cliente", crear_cliente],
        ["Listar clientes", listar_clientes],
        ["Buscar cliente", buscar_cliente],
        ["Actualizar cliente", actualizar_cliente],
        ["Eliminar cliente", eliminar_cliente],
    ])


def menu_ventas():
    """Submenú de ventas."""
    ejecutar_menu("VENTAS", [
        ["Registrar venta", registrar_venta],
        ["Listar ventas", listar_ventas],
        ["Ver detalle de una venta", ver_detalle_venta],
    ])


def menu_reportes():
    """Submenú de reportes."""
    ejecutar_menu("REPORTES", [
        ["Ventas del día", reporte_ventas_del_dia],
        ["Productos más vendidos", reporte_mas_vendidos],
        ["Productos con stock bajo", reporte_stock_bajo],
    ])


def menu_principal():
    """Menú principal del sistema."""
    activar_colores()
    inicializar_base_de_datos()
    while True:
        mostrar_encabezado("MENÚ PRINCIPAL")
        print("  1. Productos")
        print("  2. Clientes")
        print("  3. Ventas")
        print("  4. Reportes")
        print("  0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            menu_productos()
        elif opcion == "2":
            menu_clientes()
        elif opcion == "3":
            menu_ventas()
        elif opcion == "4":
            menu_reportes()
        elif opcion == "0":
            mensaje_exito("¡Hasta luego!")
            break
        else:
            mensaje_error("Opción inválida.")
            pausar()


if __name__ == "__main__":
    menu_principal()
