"""
Sistema de Minimarket - versión web (extra).

Usa Flask y REUTILIZA las funciones de minimarket.py:
los mismos archivos CSV y las mismas reglas de negocio.
Ejecutar con:  python app_web.py
Luego abrir:   http://127.0.0.1:5000
"""

from flask import (Flask, flash, redirect, render_template, request,
                   session, url_for)

import minimarket as mm   # importa la lógica; NO arranca el menú de terminal

# Clave simple para los mensajes flash (proyecto académico)
app = Flask(__name__)
app.secret_key = "minimarket-unicen"


# ============================================================
# 1) FUNCIONES DE AYUDA
# ============================================================

def datos_producto_desde_formulario(formulario):
    """Lee el formulario web y arma el diccionario del producto."""
    precio = mm.convertir_precio(formulario.get("precio", ""))
    stock = mm.convertir_entero(formulario.get("stock", ""))
    minimo = mm.convertir_entero(formulario.get("stock_minimo", ""))
    if precio is None or stock is None or minimo is None:
        return None, "Precio, stock y stock mínimo deben ser números."
    datos = {
        "codigo": formulario.get("codigo", "").strip(),
        "nombre": formulario.get("nombre", "").strip(),
        "categoria": formulario.get("categoria", "").strip(),
        "precio": precio,
        "stock": stock,
        "stock_minimo": minimo,
    }
    return datos, ""


def datos_cliente_desde_formulario(formulario):
    """Lee el formulario web y arma el diccionario del cliente."""
    return {
        "ci_nit": formulario.get("ci_nit", "").strip(),
        "nombre": formulario.get("nombre", "").strip(),
        "telefono": formulario.get("telefono", "").strip(),
    }


def filtrar_productos(texto):
    """Devuelve los productos cuyo nombre o código contiene el texto."""
    texto = texto.strip().lower()
    resultado = []
    for p in mm.leer_datos(mm.ARCHIVO_PRODUCTOS):
        if texto in p["nombre"].lower() or texto in p["codigo"].lower():
            resultado.append(p)
    return resultado


def filtrar_clientes(texto):
    """Devuelve los clientes cuyo nombre o CI/NIT contiene el texto."""
    texto = texto.strip().lower()
    resultado = []
    for c in mm.leer_datos(mm.ARCHIVO_CLIENTES):
        if texto in c["nombre"].lower() or texto in c["ci_nit"]:
            resultado.append(c)
    return resultado


def ventas_con_nombres():
    """Agrega el nombre del cliente y del producto a cada venta."""
    clientes = mm.leer_datos(mm.ARCHIVO_CLIENTES)
    productos = mm.leer_datos(mm.ARCHIVO_PRODUCTOS)
    resultado = []
    for v in mm.leer_datos(mm.ARCHIVO_VENTAS):
        fila = dict(v)
        cliente = mm.buscar_por_id(clientes, v["id_cliente"])
        producto = mm.buscar_por_id(productos, v["id_producto"])
        fila["nombre_cliente"] = mm.nombre_o_eliminado(cliente)
        fila["nombre_producto"] = mm.nombre_o_eliminado(producto)
        resultado.append(fila)
    return resultado


def guardar_flash(exito, mensaje):
    """Muestra el mensaje en verde si salió bien o en rojo si hubo error."""
    flash(mensaje, "exito" if exito else "error")


# ============================================================
# 2) INICIO
# ============================================================

@app.route("/")
def inicio():
    """Página de resumen: cantidades y alertas de stock bajo."""
    mm.inicializar_base_de_datos()
    ventas_hoy = mm.ventas_de_hoy()
    return render_template(
        "inicio.html",
        n_productos=len(mm.leer_datos(mm.ARCHIVO_PRODUCTOS)),
        n_clientes=len(mm.leer_datos(mm.ARCHIVO_CLIENTES)),
        n_ventas_hoy=len(ventas_hoy),
        total_hoy=mm.calcular_total(ventas_hoy),
        alertas=mm.productos_con_stock_bajo(),
    )


# ============================================================
# 3) PRODUCTOS
# ============================================================

@app.route("/productos", methods=["GET", "POST"])
def productos():
    """Lista, busca, crea y edita productos."""
    if request.method == "POST":
        datos, error = datos_producto_desde_formulario(request.form)
        if error != "":
            flash(error, "error")
            return redirect(url_for("productos"))
        id_producto = request.form.get("id", "").strip()
        if id_producto != "":
            exito, mensaje = mm.modificar_producto(id_producto, datos)
        else:
            exito, mensaje = mm.agregar_producto(datos)
        guardar_flash(exito, mensaje)
        return redirect(url_for("productos"))

    texto = request.args.get("q", "")
    editar_id = request.args.get("editar", "")
    producto_editar = None
    if editar_id != "":
        producto_editar = mm.buscar_por_id(
            mm.leer_datos(mm.ARCHIVO_PRODUCTOS), editar_id)
        if producto_editar is None:
            flash("Producto no encontrado.", "error")
    return render_template(
        "productos.html",
        productos=filtrar_productos(texto),
        texto=texto,
        producto_editar=producto_editar,
    )


@app.route("/productos/<id_producto>/eliminar", methods=["GET", "POST"])
def eliminar_producto(id_producto):
    """Pide confirmación y luego elimina el producto."""
    producto = mm.buscar_por_id(mm.leer_datos(mm.ARCHIVO_PRODUCTOS),
                                id_producto)
    if producto is None:
        flash("Producto no encontrado.", "error")
        return redirect(url_for("productos"))
    if request.method == "POST":
        exito, mensaje = mm.borrar_producto(id_producto)
        guardar_flash(exito, mensaje)
        return redirect(url_for("productos"))
    return render_template("confirmar_eliminar.html",
                           tipo="producto",
                           nombre=producto["nombre"],
                           cancelar=url_for("productos"))


# ============================================================
# 4) CLIENTES
# ============================================================

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    """Lista, busca, crea y edita clientes."""
    if request.method == "POST":
        datos = datos_cliente_desde_formulario(request.form)
        id_cliente = request.form.get("id", "").strip()
        if id_cliente != "":
            exito, mensaje = mm.modificar_cliente(id_cliente, datos)
        else:
            exito, mensaje = mm.agregar_cliente(datos)
        guardar_flash(exito, mensaje)
        return redirect(url_for("clientes"))

    texto = request.args.get("q", "")
    editar_id = request.args.get("editar", "")
    cliente_editar = None
    if editar_id != "":
        cliente_editar = mm.buscar_por_id(
            mm.leer_datos(mm.ARCHIVO_CLIENTES), editar_id)
        if cliente_editar is None:
            flash("Cliente no encontrado.", "error")
    return render_template(
        "clientes.html",
        clientes=filtrar_clientes(texto),
        texto=texto,
        cliente_editar=cliente_editar,
    )


@app.route("/clientes/<id_cliente>/eliminar", methods=["GET", "POST"])
def eliminar_cliente(id_cliente):
    """Pide confirmación y luego elimina el cliente."""
    cliente = mm.buscar_por_id(mm.leer_datos(mm.ARCHIVO_CLIENTES),
                               id_cliente)
    if cliente is None:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for("clientes"))
    if request.method == "POST":
        exito, mensaje = mm.borrar_cliente(id_cliente)
        guardar_flash(exito, mensaje)
        return redirect(url_for("clientes"))
    return render_template("confirmar_eliminar.html",
                           tipo="cliente",
                           nombre=cliente["nombre"],
                           cancelar=url_for("clientes"))


# ============================================================
# 5) VENTAS
# ============================================================

@app.route("/ventas", methods=["GET", "POST"])
def ventas():
    """Registra una venta y muestra la lista más la factura."""
    if request.method == "POST":
        id_cliente = request.form.get("id_cliente", "").strip()
        id_producto = request.form.get("id_producto", "").strip()
        cantidad = mm.convertir_entero(request.form.get("cantidad", ""))
        if id_cliente == "" or id_producto == "":
            flash("Elija un cliente y un producto.", "error")
            return redirect(url_for("ventas"))
        if cantidad is None:
            flash("La cantidad debe ser un número entero.", "error")
            return redirect(url_for("ventas"))
        exito, mensaje, venta = mm.realizar_venta(id_cliente, id_producto,
                                                  cantidad)
        if not exito:
            flash(mensaje, "error")
            return redirect(url_for("ventas"))
        flash(mensaje, "exito")
        # Guardamos la factura en la sesión para mostrarla después
        session["factura"] = mm.lineas_factura(venta)
        producto = mm.buscar_por_id(mm.leer_datos(mm.ARCHIVO_PRODUCTOS),
                                    id_producto)
        if producto is not None and mm.stock_bajo(producto):
            flash(f"¡AVISO! Stock bajo de '{producto['nombre']}': "
                  f"quedan {producto['stock']} unidades.", "aviso")
        return redirect(url_for("ventas"))

    factura = session.pop("factura", None)
    return render_template(
        "ventas.html",
        clientes=mm.leer_datos(mm.ARCHIVO_CLIENTES),
        productos=mm.leer_datos(mm.ARCHIVO_PRODUCTOS),
        ventas=ventas_con_nombres(),
        factura=factura,
    )


# ============================================================
# 6) REPORTES
# ============================================================

@app.route("/reportes")
def reportes():
    """Muestra ventas del día, más vendidos y stock bajo."""
    ventas_hoy = mm.ventas_de_hoy()
    return render_template(
        "reportes.html",
        ventas_hoy=ventas_hoy,
        n_ventas_hoy=len(ventas_hoy),
        total_hoy=mm.calcular_total(ventas_hoy),
        mas_vendidos=mm.calcular_mas_vendidos(),
        stock_bajo=mm.productos_con_stock_bajo(),
    )


# ============================================================
# 7) ARRANQUE
# ============================================================

if __name__ == "__main__":
    mm.inicializar_base_de_datos()
    # host 127.0.0.1 = solo esta computadora; debug=True recarga al guardar
    app.run(host="127.0.0.1", port=5000, debug=True)
