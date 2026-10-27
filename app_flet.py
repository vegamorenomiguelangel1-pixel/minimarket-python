"""
Sistema de Minimarket - versión Flet (escritorio y web).

Reutiliza las funciones de lógica de minimarket.py y la misma
base SQLite (minimarket.db). No abre el menú de terminal gracias
a if __name__ == "__main__" en minimarket.py.

Ejecutar en escritorio:
    python app_flet.py
    flet run app_flet.py

Ejecutar en el navegador:
    flet run --web app_flet.py
"""

import flet as ft

import minimarket as mm

# Controles que usan varias funciones (igual idea que un diccionario)
componentes = {}


# ============================================================
# 1) AYUDAS DE INTERFAZ
# ============================================================

def snack(page, texto, color):
    """Muestra un mensaje corto abajo (éxito, error o aviso)."""
    page.show_dialog(ft.SnackBar(content=ft.Text(texto), bgcolor=color))


def snack_resultado(page, exito, mensaje):
    """Verde si salió bien, rojo si hubo error."""
    snack(page, mensaje, ft.Colors.GREEN if exito else ft.Colors.RED)


def cerrar_dialogo(page):
    """Cierra el diálogo que está abierto."""
    page.pop_dialog()


def confirmar(page, titulo, mensaje, al_aceptar):
    """Diálogo Sí/Cancelar. Si el usuario acepta, llama a al_aceptar()."""
    def aceptar(e):
        cerrar_dialogo(page)
        al_aceptar()

    page.show_dialog(ft.AlertDialog(
        title=ft.Text(titulo),
        content=ft.Text(mensaje),
        actions=[
            ft.TextButton(content="Cancelar",
                          on_click=lambda e: cerrar_dialogo(page)),
            ft.TextButton(content="Sí, eliminar", on_click=aceptar),
        ],
    ))


def tabla(columnas, filas):
    """Arma un DataTable a partir de encabezados y celdas."""
    cols = [ft.DataColumn(label=ft.Text(c)) for c in columnas]
    rows = []
    for fila in filas:
        celdas = []
        for valor in fila:
            if isinstance(valor, ft.Control):
                celdas.append(ft.DataCell(content=valor))
            else:
                celdas.append(ft.DataCell(content=ft.Text(str(valor))))
        rows.append(ft.DataRow(cells=celdas))
    return ft.DataTable(
        columns=cols,
        rows=rows,
        heading_row_color=ft.Colors.GREEN_50,
        border=ft.Border.all(1, ft.Colors.GREEN_100),
    )


def tarjeta(numero, etiqueta):
    """Tarjeta del resumen (cantidad + texto)."""
    return ft.Container(
        bgcolor=ft.Colors.WHITE,
        padding=16,
        border_radius=8,
        border=ft.Border.all(1, ft.Colors.GREEN_100),
        content=ft.Column(controls=[
            ft.Text(str(numero), size=26, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREEN_800),
            ft.Text(etiqueta),
        ]),
    )


def mostrar(controles):
    """Reemplaza el contenido de la zona principal."""
    componentes["cuerpo"].controls = controles


# ============================================================
# 2) INICIO
# ============================================================

def vista_inicio():
    """Resumen: cantidades y alertas de stock bajo."""
    ventas_hoy = mm.ventas_de_hoy()
    alertas = mm.productos_con_stock_bajo()
    controles = [
        ft.Text("Resumen del minimarket", size=22,
                weight=ft.FontWeight.BOLD),
        ft.Row(controls=[
            tarjeta(len(mm.obtener_productos()), "Productos"),
            tarjeta(len(mm.obtener_clientes()), "Clientes"),
            tarjeta(len(ventas_hoy), "Ventas del día"),
            tarjeta(f"Bs {mm.calcular_total(ventas_hoy):.2f}",
                    "Total recaudado hoy"),
        ]),
        ft.Text("Alertas de stock bajo", size=18,
                weight=ft.FontWeight.BOLD),
    ]
    if alertas:
        filas = [[p["codigo"], p["nombre"], p["stock"], p["stock_minimo"]]
                 for p in alertas]
        controles.append(tabla(["Código", "Nombre", "Stock", "Mínimo"],
                               filas))
    else:
        controles.append(ft.Text("Todos los productos tienen stock "
                                 "suficiente."))
    mostrar(controles)


# ============================================================
# 3) PRODUCTOS
# ============================================================

def leer_formulario_producto():
    """Lee las cajas del producto y devuelve (datos, error)."""
    c = componentes
    precio = mm.convertir_precio(c["p_precio"].value or "")
    stock = mm.convertir_entero(c["p_stock"].value or "")
    minimo = mm.convertir_entero(c["p_minimo"].value or "")
    if precio is None or stock is None or minimo is None:
        return None, "Precio, stock y stock mínimo deben ser números."
    datos = {
        "codigo": (c["p_codigo"].value or "").strip(),
        "nombre": (c["p_nombre"].value or "").strip(),
        "categoria": (c["p_categoria"].value or "").strip(),
        "precio": precio,
        "stock": stock,
        "stock_minimo": minimo,
    }
    return datos, ""


def limpiar_producto():
    """Vacía el formulario de productos."""
    for clave in ("p_codigo", "p_nombre", "p_categoria",
                  "p_precio", "p_stock", "p_minimo"):
        componentes[clave].value = ""
    componentes["p_id"] = ""


def cargar_producto(id_producto):
    """Copia un producto de la base al formulario (para editar)."""
    p = next((x for x in mm.obtener_productos()
              if x["id"] == str(id_producto)), None)
    if p is None:
        return
    componentes["p_id"] = p["id"]
    componentes["p_codigo"].value = p["codigo"]
    componentes["p_nombre"].value = p["nombre"]
    componentes["p_categoria"].value = p["categoria"]
    componentes["p_precio"].value = p["precio"]
    componentes["p_stock"].value = p["stock"]
    componentes["p_minimo"].value = p["stock_minimo"]


def vista_productos(page):
    """Formulario, búsqueda y tabla de productos."""
    texto = (componentes.get("p_buscar") or ft.TextField()).value or ""
    texto = texto.strip().lower()

    def registrar(e):
        datos, error = leer_formulario_producto()
        if error != "":
            snack(page, error, ft.Colors.RED)
            return
        if componentes.get("p_id"):
            exito, mensaje = mm.modificar_producto(
                componentes["p_id"], datos)
        else:
            exito, mensaje = mm.agregar_producto(datos)
        snack_resultado(page, exito, mensaje)
        if exito:
            limpiar_producto()
            vista_productos(page)

    def pedir_borrar(id_producto, nombre):
        def borrar():
            exito, mensaje = mm.borrar_producto(id_producto)
            snack_resultado(page, exito, mensaje)
            limpiar_producto()
            vista_productos(page)
        confirmar(page, "Eliminar producto",
                  f"¿Seguro que desea eliminar {nombre}?", borrar)

    componentes["p_codigo"] = ft.TextField(label="Código", width=220)
    componentes["p_nombre"] = ft.TextField(label="Nombre", width=220)
    componentes["p_categoria"] = ft.TextField(label="Categoría", width=220)
    componentes["p_precio"] = ft.TextField(label="Precio (Bs)", width=220)
    componentes["p_stock"] = ft.TextField(label="Stock", width=220)
    componentes["p_minimo"] = ft.TextField(label="Stock mínimo", width=220)
    componentes["p_buscar"] = ft.TextField(label="Buscar (nombre o código)",
                                           width=260, value=texto)
    if "p_id" not in componentes:
        componentes["p_id"] = ""

    filas = []
    for p in mm.obtener_productos():
        if texto and texto not in p["nombre"].lower() \
                and texto not in p["codigo"].lower():
            continue
        pid, nombre = p["id"], p["nombre"]
        acciones = ft.Row(controls=[
            ft.TextButton(content="Editar",
                          on_click=lambda e, i=pid: cargar_producto(i)),
            ft.TextButton(
                content="Eliminar",
                on_click=lambda e, i=pid, n=nombre: pedir_borrar(i, n)),
        ])
        filas.append([
            p["id"], p["codigo"], p["nombre"], p["categoria"],
            f"{float(p['precio']):.2f}", p["stock"], p["stock_minimo"],
            acciones,
        ])

    mostrar([
        ft.Text("Productos", size=22, weight=ft.FontWeight.BOLD),
        ft.Text("Registrar o editar"),
        ft.Row(wrap=True, controls=[
            componentes["p_codigo"], componentes["p_nombre"],
            componentes["p_categoria"], componentes["p_precio"],
            componentes["p_stock"], componentes["p_minimo"],
        ]),
        ft.Row(controls=[
            ft.Button(content="Guardar", on_click=registrar),
            ft.Button(content="Limpiar", on_click=lambda e: (
                limpiar_producto(), vista_productos(page))),
        ]),
        ft.Row(controls=[
            componentes["p_buscar"],
            ft.Button(content="Buscar",
                      on_click=lambda e: vista_productos(page)),
            ft.Button(content="Ver todos",
                      on_click=lambda e: (
                          componentes["p_buscar"].__setattr__("value", ""),
                          vista_productos(page))),
        ]),
        tabla(["Id", "Código", "Nombre", "Categoría", "Precio Bs",
               "Stock", "Mínimo", ""], filas),
    ])


# ============================================================
# 4) CLIENTES
# ============================================================

def limpiar_cliente():
    """Vacía el formulario de clientes."""
    for clave in ("c_ci", "c_nombre", "c_telefono"):
        componentes[clave].value = ""
    componentes["c_id"] = ""


def cargar_cliente(id_cliente):
    """Copia un cliente de la base al formulario."""
    c = next((x for x in mm.obtener_clientes()
              if x["id"] == str(id_cliente)), None)
    if c is None:
        return
    componentes["c_id"] = c["id"]
    componentes["c_ci"].value = c["ci_nit"]
    componentes["c_nombre"].value = c["nombre"]
    componentes["c_telefono"].value = c["telefono"]


def vista_clientes(page):
    """Formulario, búsqueda y tabla de clientes."""
    texto = (componentes.get("c_buscar") or ft.TextField()).value or ""
    texto = texto.strip().lower()

    def registrar(e):
        datos = {
            "ci_nit": (componentes["c_ci"].value or "").strip(),
            "nombre": (componentes["c_nombre"].value or "").strip(),
            "telefono": (componentes["c_telefono"].value or "").strip(),
        }
        if componentes.get("c_id"):
            exito, mensaje = mm.modificar_cliente(
                componentes["c_id"], datos)
        else:
            exito, mensaje = mm.agregar_cliente(datos)
        snack_resultado(page, exito, mensaje)
        if exito:
            limpiar_cliente()
            vista_clientes(page)

    def pedir_borrar(id_cliente, nombre):
        def borrar():
            exito, mensaje = mm.borrar_cliente(id_cliente)
            snack_resultado(page, exito, mensaje)
            limpiar_cliente()
            vista_clientes(page)
        confirmar(page, "Eliminar cliente",
                  f"¿Seguro que desea eliminar {nombre}?", borrar)

    componentes["c_ci"] = ft.TextField(label="CI/NIT", width=220)
    componentes["c_nombre"] = ft.TextField(label="Nombre", width=220)
    componentes["c_telefono"] = ft.TextField(label="Teléfono", width=220)
    componentes["c_buscar"] = ft.TextField(label="Buscar (nombre o CI/NIT)",
                                           width=260, value=texto)
    if "c_id" not in componentes:
        componentes["c_id"] = ""

    filas = []
    for c in mm.obtener_clientes():
        if texto and texto not in c["nombre"].lower() \
                and texto not in c["ci_nit"]:
            continue
        cid, nombre = c["id"], c["nombre"]
        acciones = ft.Row(controls=[
            ft.TextButton(content="Editar",
                          on_click=lambda e, i=cid: cargar_cliente(i)),
            ft.TextButton(
                content="Eliminar",
                on_click=lambda e, i=cid, n=nombre: pedir_borrar(i, n)),
        ])
        filas.append([c["id"], c["ci_nit"], c["nombre"], c["telefono"],
                      acciones])

    mostrar([
        ft.Text("Clientes", size=22, weight=ft.FontWeight.BOLD),
        ft.Row(wrap=True, controls=[
            componentes["c_ci"], componentes["c_nombre"],
            componentes["c_telefono"],
        ]),
        ft.Row(controls=[
            ft.Button(content="Guardar", on_click=registrar),
            ft.Button(content="Limpiar", on_click=lambda e: (
                limpiar_cliente(), vista_clientes(page))),
        ]),
        ft.Row(controls=[
            componentes["c_buscar"],
            ft.Button(content="Buscar",
                      on_click=lambda e: vista_clientes(page)),
            ft.Button(content="Ver todos",
                      on_click=lambda e: (
                          componentes["c_buscar"].__setattr__("value", ""),
                          vista_clientes(page))),
        ]),
        tabla(["Id", "CI/NIT", "Nombre", "Teléfono", ""], filas),
    ])


# ============================================================
# 5) VENTAS
# ============================================================

def vista_ventas(page):
    """Formulario de venta, factura y lista."""
    opciones_cli = [
        ft.DropdownOption(key=c["id"],
                          text=f"{c['id']} - {c['nombre']}")
        for c in mm.obtener_clientes()
    ]
    opciones_pro = [
        ft.DropdownOption(
            key=p["id"],
            text=f"{p['id']} - {p['nombre']} (stock {p['stock']})")
        for p in mm.obtener_productos()
    ]
    combo_cli = ft.Dropdown(label="Cliente", width=340,
                            options=opciones_cli)
    combo_pro = ft.Dropdown(label="Producto", width=340,
                            options=opciones_pro)
    caja_cant = ft.TextField(label="Cantidad", width=160)

    def vender(e):
        if not combo_cli.value or not combo_pro.value:
            snack(page, "Elija un cliente y un producto.", ft.Colors.RED)
            return
        cantidad = mm.convertir_entero(caja_cant.value or "")
        if cantidad is None:
            snack(page, "La cantidad debe ser un número entero.",
                  ft.Colors.RED)
            return
        exito, mensaje, venta = mm.realizar_venta(
            combo_cli.value, combo_pro.value, cantidad)
        if not exito:
            snack(page, mensaje, ft.Colors.RED)
            return
        factura = "\n".join(mm.lineas_factura(venta))
        producto = next((p for p in mm.obtener_productos()
                         if p["id"] == str(combo_pro.value)), None)
        if producto is not None and mm.stock_bajo(producto):
            factura += (f"\n\n¡AVISO! Stock bajo de '{producto['nombre']}': "
                        f"quedan {producto['stock']} unidades.")
        vista_ventas(page)
        snack(page, mensaje, ft.Colors.GREEN)
        page.show_dialog(ft.AlertDialog(
            title=ft.Text("Factura"),
            content=ft.Text(factura),
            actions=[ft.TextButton(content="Cerrar",
                                   on_click=lambda e: cerrar_dialogo(page))],
        ))

    clientes = mm.obtener_clientes()
    productos = mm.obtener_productos()
    filas = []
    for v in mm.obtener_ventas():
        cli = mm.buscar_por_id(clientes, v["id_cliente"])
        pro = mm.buscar_por_id(productos, v["id_producto"])
        filas.append([
            v["id"], v["fecha"], mm.nombre_o_eliminado(cli),
            mm.nombre_o_eliminado(pro), v["cantidad"],
            f"{float(v['total']):.2f}",
        ])

    mostrar([
        ft.Text("Ventas", size=22, weight=ft.FontWeight.BOLD),
        ft.Row(wrap=True, controls=[combo_cli, combo_pro, caja_cant,
                                    ft.Button(content="Vender",
                                              on_click=vender)]),
        ft.Text("Lista de ventas", size=18, weight=ft.FontWeight.BOLD),
        tabla(["Id", "Fecha", "Cliente", "Producto", "Cant.", "Total Bs"],
              filas),
    ])


# ============================================================
# 6) REPORTES
# ============================================================

def vista_reportes():
    """Ventas del día, más vendidos y stock bajo."""
    ventas = mm.ventas_de_hoy()
    filas_hoy = [[v["id"], v["fecha"], v["cantidad"],
                  f"{float(v['total']):.2f}"] for v in ventas]
    ranking = mm.calcular_mas_vendidos()
    filas_top = [[i, par[1], par[0]]
                 for i, par in enumerate(ranking, start=1)]
    bajos = mm.productos_con_stock_bajo()
    filas_bajo = [[p["codigo"], p["nombre"], p["stock"], p["stock_minimo"]]
                  for p in bajos]

    controles = [
        ft.Text("Reportes", size=22, weight=ft.FontWeight.BOLD),
        ft.Text("Ventas del día", size=18, weight=ft.FontWeight.BOLD),
    ]
    if filas_hoy:
        controles.append(tabla(["Id", "Fecha", "Cant.", "Total Bs"],
                               filas_hoy))
    else:
        controles.append(ft.Text("Hoy todavía no hay ventas."))
    controles.append(ft.Text(
        f"Cantidad de ventas: {len(ventas)}   |   "
        f"TOTAL RECAUDADO: Bs {mm.calcular_total(ventas):.2f}",
        weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800))

    controles.append(ft.Text("Productos más vendidos", size=18,
                             weight=ft.FontWeight.BOLD))
    if filas_top:
        controles.append(tabla(["N°", "Producto", "Unidades"], filas_top))
    else:
        controles.append(ft.Text("Todavía no hay ventas."))

    controles.append(ft.Text("Productos con stock bajo", size=18,
                             weight=ft.FontWeight.BOLD))
    if filas_bajo:
        controles.append(tabla(["Código", "Nombre", "Stock", "Mínimo"],
                               filas_bajo))
    else:
        controles.append(ft.Text(
            "Todos los productos tienen stock suficiente."))
    mostrar(controles)


# ============================================================
# 7) VENTANA PRINCIPAL
# ============================================================

def main(page: ft.Page):
    """Arma la ventana: menú a la izquierda y contenido a la derecha."""
    mm.inicializar_base_de_datos()
    page.title = "MINIMARKET"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
    page.bgcolor = ft.Colors.GREY_100

    cuerpo = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO,
                       spacing=12, controls=[])
    componentes["cuerpo"] = cuerpo

    def cambiar(e):
        indice = e.control.selected_index
        if indice == 0:
            vista_inicio()
        elif indice == 1:
            vista_productos(page)
        elif indice == 2:
            vista_clientes(page)
        elif indice == 3:
            vista_ventas(page)
        else:
            vista_reportes()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=180,
        extended=True,
        on_change=cambiar,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.HOME,
                                         label="Inicio"),
            ft.NavigationRailDestination(icon=ft.Icons.INVENTORY_2,
                                         label="Productos"),
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE,
                                         label="Clientes"),
            ft.NavigationRailDestination(icon=ft.Icons.POINT_OF_SALE,
                                         label="Ventas"),
            ft.NavigationRailDestination(icon=ft.Icons.ASSESSMENT,
                                         label="Reportes"),
        ],
    )

    page.add(ft.Row(
        expand=True,
        controls=[
            rail,
            ft.VerticalDivider(width=1),
            ft.Container(expand=True, padding=16, content=cuerpo),
        ],
    ))
    vista_inicio()


if __name__ == "__main__":
    ft.run(main)
