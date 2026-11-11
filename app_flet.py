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

# Controles y datos de la interfaz que usan varias funciones
componentes = {}

# A partir de este ancho (px) se muestra el menú lateral;
# más angosto: barra inferior, más cómoda en el navegador.
ANCHO_ESCRITORIO = 800

# Paleta del minimarket (verde de verdulería + acento ámbar)
VERDE = ft.Colors.GREEN_800
VERDE_SUAVE = ft.Colors.GREEN_50
FONDO = "#F3F6F4"
AMBAR = ft.Colors.AMBER_800


# ============================================================
# 1) AYUDAS DE INTERFAZ
# ============================================================

def snack(page, texto, color):
    """Muestra un mensaje corto abajo (éxito, error o aviso)."""
    page.show_dialog(ft.SnackBar(
        content=ft.Text(texto, color=ft.Colors.WHITE),
        bgcolor=color,
        behavior=ft.SnackBarBehavior.FLOATING,
        duration=ft.Duration(seconds=3),
        show_close_icon=True,
    ))


def snack_resultado(page, exito, mensaje):
    """Verde si salió bien, rojo si hubo error."""
    snack(page, mensaje, VERDE if exito else ft.Colors.RED_700)


def cerrar_dialogo(page):
    """Cierra el diálogo que está abierto."""
    page.pop_dialog()


def confirmar(page, titulo, mensaje, al_aceptar):
    """Diálogo Sí/Cancelar. Si el usuario acepta, llama a al_aceptar()."""
    def aceptar(e):
        cerrar_dialogo(page)
        al_aceptar()

    page.show_dialog(ft.AlertDialog(
        modal=True,
        icon=ft.Icon(ft.Icons.WARNING_AMBER, color=AMBAR, size=36),
        title=ft.Text(titulo, weight=ft.FontWeight.BOLD),
        content=ft.Text(mensaje),
        actions=[
            ft.TextButton(content="Cancelar",
                          on_click=lambda e: cerrar_dialogo(page)),
            ft.FilledButton(content="Sí, eliminar",
                            bgcolor=ft.Colors.RED_700,
                            on_click=aceptar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    ))


def tabla(columnas, filas, colores=None):
    """Arma un DataTable. 'colores' pinta filas (ej. stock bajo)."""
    cols = [ft.DataColumn(label=ft.Text(c, color=ft.Colors.WHITE))
            for c in columnas]
    rows = []
    for i, fila in enumerate(filas):
        celdas = []
        for valor in fila:
            if isinstance(valor, ft.Control):
                celdas.append(ft.DataCell(content=valor))
            else:
                celdas.append(ft.DataCell(content=ft.Text(str(valor))))
        color_fila = None
        if colores is not None and i < len(colores):
            color_fila = colores[i]
        rows.append(ft.DataRow(cells=celdas, color=color_fila))
    return ft.DataTable(
        columns=cols,
        rows=rows,
        heading_row_color=VERDE,
        heading_row_height=44,
        data_row_min_height=44,
        heading_text_style=ft.TextStyle(color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_600),
        border=ft.Border.all(1, ft.Colors.GREEN_100),
        border_radius=ft.BorderRadius.all(8),
        horizontal_margin=16,
        column_spacing=18,
    )


def envolver_tabla(columnas, filas, colores=None, vacio="Sin datos",
                   en_tarjeta=True):
    """Tabla con scroll horizontal. en_tarjeta=False si ya va dentro de un Card."""
    if not filas:
        return ft.Text(vacio, color=ft.Colors.GREY_700)
    contenido = ft.Row(
        scroll=ft.ScrollMode.AUTO,
        controls=[tabla(columnas, filas, colores)],
    )
    if not en_tarjeta:
        return contenido
    return ft.Card(
        variant=ft.CardVariant.OUTLINED,
        content=ft.Container(padding=8, content=contenido),
    )


def tarjeta_kpi(icono, numero, etiqueta, color_icono, col):
    """Tarjeta del panel: un número grande y su etiqueta."""
    return ft.Container(
        col=col,
        content=ft.Card(
            elevation=1,
            content=ft.Container(
                padding=16,
                content=ft.Row(controls=[
                    ft.CircleAvatar(
                        content=ft.Icon(icono, color=ft.Colors.WHITE),
                        bgcolor=color_icono,
                        radius=22,
                    ),
                    ft.Column(spacing=2, expand=True, controls=[
                        ft.Text(str(numero), size=22,
                                weight=ft.FontWeight.BOLD,
                                color=VERDE),
                        ft.Text(etiqueta, size=13,
                                color=ft.Colors.GREY_700),
                    ]),
                ]),
            ),
        ),
    )


def encabezado_pagina(titulo, subtitulo, boton=None):
    """Título de cada pantalla, con un botón opcional a la derecha."""
    fila = [
        ft.Column(spacing=2, expand=True, controls=[
            ft.Text(titulo, size=24, weight=ft.FontWeight.BOLD,
                    color=VERDE),
            ft.Text(subtitulo, size=13, color=ft.Colors.GREY_700),
        ]),
    ]
    if boton is not None:
        fila.append(boton)
    return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  vertical_alignment=ft.CrossAxisAlignment.CENTER,
                  controls=fila)


def barra_buscar(etiqueta, valor, al_buscar, al_limpiar):
    """Caja de búsqueda + botones Buscar y Ver todos."""
    caja = ft.TextField(
        label=etiqueta,
        value=valor,
        prefix_icon=ft.Icons.SEARCH,
        on_submit=al_buscar,
        expand=True,
    )
    return caja, ft.ResponsiveRow(
        spacing=8,
        run_spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(col={"xs": 12, "md": 7}, content=caja),
            ft.Container(
                col={"xs": 12, "md": 5},
                content=ft.Row(wrap=True, spacing=8, controls=[
                    ft.FilledButton(content="Buscar",
                                    icon=ft.Icons.SEARCH,
                                    on_click=al_buscar),
                    ft.OutlinedButton(content="Ver todos",
                                      icon=ft.Icons.FILTER_LIST_OFF,
                                      on_click=al_limpiar),
                ]),
            ),
        ],
    )


def mostrar(controles):
    """Reemplaza el contenido de la zona principal."""
    componentes["cuerpo"].controls = controles


def botones_fila(editar, eliminar):
    """Iconos Editar / Eliminar para cada fila de la tabla."""
    return ft.Row(spacing=0, controls=[
        ft.IconButton(icon=ft.Icons.EDIT, icon_color=VERDE,
                      tooltip="Editar", icon_size=20,
                      on_click=editar),
        ft.IconButton(icon=ft.Icons.DELETE_OUTLINE,
                      icon_color=ft.Colors.RED_700,
                      tooltip="Eliminar", icon_size=20,
                      on_click=eliminar),
    ])


# ============================================================
# 2) INICIO (panel de resumen)
# ============================================================

def vista_inicio():
    """Tarjetas de totales y alertas de stock bajo."""
    ventas_hoy = mm.ventas_de_hoy()
    alertas = mm.productos_con_stock_bajo()
    col = {"xs": 12, "sm": 6, "lg": 4, "xl": 2}

    tarjetas = ft.ResponsiveRow(
        spacing=8,
        run_spacing=8,
        controls=[
            tarjeta_kpi(ft.Icons.INVENTORY_2,
                        len(mm.obtener_productos()),
                        "Productos", VERDE, col),
            tarjeta_kpi(ft.Icons.PEOPLE,
                        len(mm.obtener_clientes()),
                        "Clientes", ft.Colors.TEAL_700, col),
            tarjeta_kpi(ft.Icons.RECEIPT_LONG,
                        len(ventas_hoy),
                        "Ventas del día", ft.Colors.BLUE_700, col),
            tarjeta_kpi(ft.Icons.ATTACH_MONEY,
                        f"Bs {mm.calcular_total(ventas_hoy):.2f}",
                        "Ingresos de hoy", ft.Colors.ORANGE_700, col),
            tarjeta_kpi(ft.Icons.WARNING_AMBER,
                        len(alertas),
                        "Con stock bajo", AMBAR, col),
        ],
    )

    if alertas:
        filas = [[p["codigo"], p["nombre"], p["stock"], p["stock_minimo"]]
                 for p in alertas]
        bloque_alertas = envolver_tabla(
            ["Código", "Nombre", "Stock", "Mínimo"], filas,
            colores=[ft.Colors.AMBER_50] * len(filas))
    else:
        bloque_alertas = ft.Text("Todos los productos tienen stock "
                                 "suficiente.")

    mostrar([
        encabezado_pagina(
            "Panel de inicio",
            "Resumen del día · los mismos datos que la terminal"),
        tarjetas,
        ft.Text("Alertas de stock bajo", size=18,
                weight=ft.FontWeight.BOLD, color=VERDE),
        bloque_alertas,
    ])


# ============================================================
# 3) PRODUCTOS
# ============================================================

def abrir_dialogo_producto(page, producto=None):
    """Formulario de alta o edición dentro de un diálogo."""
    es_edicion = producto is not None
    codigo = ft.TextField(
        label="Código",
        value=producto["codigo"] if es_edicion else "",
        prefix_icon=ft.Icons.QR_CODE_2)
    nombre = ft.TextField(
        label="Nombre",
        value=producto["nombre"] if es_edicion else "",
        prefix_icon=ft.Icons.INVENTORY_2)
    categoria = ft.TextField(
        label="Categoría",
        value=producto["categoria"] if es_edicion else "",
        prefix_icon=ft.Icons.CATEGORY)
    precio = ft.TextField(
        label="Precio (Bs)",
        value=producto["precio"] if es_edicion else "",
        prefix_icon=ft.Icons.ATTACH_MONEY)
    stock = ft.TextField(
        label="Stock",
        value=producto["stock"] if es_edicion else "",
        prefix_icon=ft.Icons.INVENTORY)
    minimo = ft.TextField(
        label="Stock mínimo",
        value=producto["stock_minimo"] if es_edicion else "",
        prefix_icon=ft.Icons.PRODUCTION_QUANTITY_LIMITS)

    def guardar(e):
        p_num = mm.convertir_precio(precio.value or "")
        s_num = mm.convertir_entero(stock.value or "")
        m_num = mm.convertir_entero(minimo.value or "")
        if p_num is None or s_num is None or m_num is None:
            snack(page, "Precio, stock y stock mínimo deben ser números.",
                  ft.Colors.RED_700)
            return
        datos = {
            "codigo": (codigo.value or "").strip(),
            "nombre": (nombre.value or "").strip(),
            "categoria": (categoria.value or "").strip(),
            "precio": p_num,
            "stock": s_num,
            "stock_minimo": m_num,
        }
        if es_edicion:
            exito, mensaje = mm.modificar_producto(producto["id"], datos)
        else:
            exito, mensaje = mm.agregar_producto(datos)
        if not exito:
            snack(page, mensaje, ft.Colors.RED_700)
            return
        cerrar_dialogo(page)
        snack_resultado(page, True, mensaje)
        vista_productos(page)

    page.show_dialog(ft.AlertDialog(
        modal=True,
        title=ft.Text("Editar producto" if es_edicion else "Nuevo producto",
                      weight=ft.FontWeight.BOLD),
        content=ft.Column(
            tight=True, width=420, spacing=8, scroll=ft.ScrollMode.AUTO,
            controls=[codigo, nombre, categoria, precio, stock, minimo],
        ),
        actions=[
            ft.TextButton(content="Cancelar",
                          on_click=lambda e: cerrar_dialogo(page)),
            ft.FilledButton(content="Guardar", icon=ft.Icons.SAVE,
                            on_click=guardar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    ))


def vista_productos(page, texto=""):
    """Búsqueda, tabla y botones para el CRUD de productos."""
    texto = (texto or "").strip().lower()

    def pedir_borrar(id_producto, nombre):
        def borrar():
            exito, mensaje = mm.borrar_producto(id_producto)
            snack_resultado(page, exito, mensaje)
            vista_productos(page, componentes.get("p_filtro", ""))
        confirmar(page, "Eliminar producto",
                  f"¿Seguro que desea eliminar {nombre}?", borrar)

    caja, barra = barra_buscar(
        "Buscar por nombre o código",
        texto,
        lambda e: vista_productos(page, caja.value),
        lambda e: vista_productos(page, ""),
    )
    componentes["p_filtro"] = texto

    filas = []
    colores = []
    for p in mm.obtener_productos():
        if texto and texto not in p["nombre"].lower() \
                and texto not in p["codigo"].lower():
            continue
        pid, nom = p["id"], p["nombre"]
        filas.append([
            p["id"], p["codigo"], p["nombre"], p["categoria"],
            f"{float(p['precio']):.2f}", p["stock"], p["stock_minimo"],
            botones_fila(
                lambda e, prod=p: abrir_dialogo_producto(page, prod),
                lambda e, i=pid, n=nom: pedir_borrar(i, n)),
        ])
        colores.append(ft.Colors.AMBER_50 if mm.stock_bajo(p) else None)

    mostrar([
        encabezado_pagina(
            "Productos",
            "Alta, baja, modificación y búsqueda",
            ft.FilledButton(content="Nuevo producto",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: abrir_dialogo_producto(page))),
        barra,
        envolver_tabla(
            ["Id", "Código", "Nombre", "Categoría", "Precio Bs",
             "Stock", "Mínimo", ""],
            filas, colores,
            vacio="No se encontraron productos."),
    ])


# ============================================================
# 4) CLIENTES
# ============================================================

def abrir_dialogo_cliente(page, cliente=None):
    """Formulario de alta o edición de un cliente."""
    es_edicion = cliente is not None
    ci = ft.TextField(
        label="CI/NIT",
        value=cliente["ci_nit"] if es_edicion else "",
        prefix_icon=ft.Icons.BADGE)
    nombre = ft.TextField(
        label="Nombre",
        value=cliente["nombre"] if es_edicion else "",
        prefix_icon=ft.Icons.PERSON)
    telefono = ft.TextField(
        label="Teléfono",
        value=cliente["telefono"] if es_edicion else "",
        prefix_icon=ft.Icons.PHONE)

    def guardar(e):
        datos = {
            "ci_nit": (ci.value or "").strip(),
            "nombre": (nombre.value or "").strip(),
            "telefono": (telefono.value or "").strip(),
        }
        if es_edicion:
            exito, mensaje = mm.modificar_cliente(cliente["id"], datos)
        else:
            exito, mensaje = mm.agregar_cliente(datos)
        if not exito:
            snack(page, mensaje, ft.Colors.RED_700)
            return
        cerrar_dialogo(page)
        snack_resultado(page, True, mensaje)
        vista_clientes(page)

    page.show_dialog(ft.AlertDialog(
        modal=True,
        title=ft.Text("Editar cliente" if es_edicion else "Nuevo cliente",
                      weight=ft.FontWeight.BOLD),
        content=ft.Column(
            tight=True, width=420, spacing=8,
            controls=[ci, nombre, telefono],
        ),
        actions=[
            ft.TextButton(content="Cancelar",
                          on_click=lambda e: cerrar_dialogo(page)),
            ft.FilledButton(content="Guardar", icon=ft.Icons.SAVE,
                            on_click=guardar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    ))


def vista_clientes(page, texto=""):
    """Búsqueda, tabla y CRUD de clientes."""
    texto = (texto or "").strip().lower()

    def pedir_borrar(id_cliente, nombre):
        def borrar():
            exito, mensaje = mm.borrar_cliente(id_cliente)
            snack_resultado(page, exito, mensaje)
            vista_clientes(page, componentes.get("c_filtro", ""))
        confirmar(page, "Eliminar cliente",
                  f"¿Seguro que desea eliminar {nombre}?", borrar)

    caja, barra = barra_buscar(
        "Buscar por nombre o CI/NIT",
        texto,
        lambda e: vista_clientes(page, caja.value),
        lambda e: vista_clientes(page, ""),
    )
    componentes["c_filtro"] = texto

    filas = []
    for c in mm.obtener_clientes():
        if texto and texto not in c["nombre"].lower() \
                and texto not in c["ci_nit"]:
            continue
        cid, nom = c["id"], c["nombre"]
        filas.append([
            c["id"], c["ci_nit"], c["nombre"], c["telefono"],
            botones_fila(
                lambda e, cli=c: abrir_dialogo_cliente(page, cli),
                lambda e, i=cid, n=nom: pedir_borrar(i, n)),
        ])

    mostrar([
        encabezado_pagina(
            "Clientes",
            "Registro con CI/NIT único",
            ft.FilledButton(content="Nuevo cliente",
                            icon=ft.Icons.PERSON_ADD,
                            on_click=lambda e: abrir_dialogo_cliente(page))),
        barra,
        envolver_tabla(
            ["Id", "CI/NIT", "Nombre", "Teléfono", ""],
            filas, vacio="No se encontraron clientes."),
    ])


# ============================================================
# 5) VENTAS
# ============================================================

def abrir_dialogo_venta(page):
    """Elige cliente, producto y cantidad; muestra la factura al vender."""
    combo_cli = ft.Dropdown(
        label="Cliente",
        options=[ft.DropdownOption(key=c["id"],
                                   text=f"{c['id']} - {c['nombre']}")
                 for c in mm.obtener_clientes()],
    )
    combo_pro = ft.Dropdown(
        label="Producto",
        options=[ft.DropdownOption(
            key=p["id"],
            text=f"{p['id']} - {p['nombre']} (stock {p['stock']})")
            for p in mm.obtener_productos()],
    )
    caja_cant = ft.TextField(label="Cantidad", prefix_icon=ft.Icons.TAG)

    def vender(e):
        if not combo_cli.value or not combo_pro.value:
            snack(page, "Elija un cliente y un producto.",
                  ft.Colors.RED_700)
            return
        cantidad = mm.convertir_entero(caja_cant.value or "")
        if cantidad is None:
            snack(page, "La cantidad debe ser un número entero.",
                  ft.Colors.RED_700)
            return
        exito, mensaje, venta = mm.realizar_venta(
            combo_cli.value, combo_pro.value, cantidad)
        if not exito:
            snack(page, mensaje, ft.Colors.RED_700)
            return
        factura = "\n".join(mm.lineas_factura(venta))
        producto = mm.buscar_por_id(mm.obtener_productos(),
                                    combo_pro.value)
        if producto is not None and mm.stock_bajo(producto):
            factura += (f"\n\n¡AVISO! Stock bajo de '{producto['nombre']}': "
                        f"quedan {producto['stock']} unidades.")
        cerrar_dialogo(page)
        vista_ventas(page)
        snack(page, mensaje, VERDE)
        page.show_dialog(ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.Icons.RECEIPT_LONG, color=VERDE, size=36),
            title=ft.Text("Factura", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                bgcolor=VERDE_SUAVE,
                padding=16,
                border_radius=ft.BorderRadius.all(8),
                content=ft.Text(factura, selectable=True),
            ),
            actions=[ft.FilledButton(
                content="Cerrar",
                on_click=lambda e: cerrar_dialogo(page))],
        ))

    page.show_dialog(ft.AlertDialog(
        modal=True,
        title=ft.Text("Nueva venta", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            tight=True, width=420, spacing=8,
            controls=[combo_cli, combo_pro, caja_cant],
        ),
        actions=[
            ft.TextButton(content="Cancelar",
                          on_click=lambda e: cerrar_dialogo(page)),
            ft.FilledButton(content="Vender",
                            icon=ft.Icons.POINT_OF_SALE,
                            on_click=vender),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    ))


def vista_ventas(page):
    """Lista de ventas y botón para registrar una nueva."""
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
        encabezado_pagina(
            "Ventas",
            "Registra una venta y se descuenta el stock",
            ft.FilledButton(content="Nueva venta",
                            icon=ft.Icons.ADD_SHOPPING_CART,
                            on_click=lambda e: abrir_dialogo_venta(page))),
        envolver_tabla(
            ["Id", "Fecha", "Cliente", "Producto", "Cant.", "Total Bs"],
            filas, vacio="No hay ventas registradas."),
    ])


# ============================================================
# 6) REPORTES
# ============================================================

def tarjeta_reporte(titulo, cuerpo, col=None):
    """Una tarjeta con título para el área de reportes."""
    if col is None:
        col = {"xs": 12}
    return ft.Container(
        col=col,
        content=ft.Card(
            variant=ft.CardVariant.OUTLINED,
            content=ft.Container(
                padding=16,
                content=ft.Column(spacing=10, controls=[
                    ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD,
                            color=VERDE),
                    cuerpo,
                ]),
            ),
        ),
    )


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

    cuerpo_hoy = ft.Column(spacing=8, controls=[
        envolver_tabla(["Id", "Fecha", "Cant.", "Total Bs"], filas_hoy,
                       vacio="Hoy todavía no hay ventas.",
                       en_tarjeta=False),
        ft.Text(
            f"Cantidad: {len(ventas)}   ·   "
            f"TOTAL RECAUDADO: Bs {mm.calcular_total(ventas):.2f}",
            weight=ft.FontWeight.BOLD, color=VERDE),
    ])
    cuerpo_top = envolver_tabla(["N°", "Producto", "Unidades"], filas_top,
                                vacio="Todavía no hay ventas.",
                                en_tarjeta=False)
    cuerpo_bajo = envolver_tabla(
        ["Código", "Nombre", "Stock", "Mínimo"], filas_bajo,
        colores=[ft.Colors.AMBER_50] * len(filas_bajo) if filas_bajo else None,
        vacio="Todos los productos tienen stock suficiente.",
        en_tarjeta=False)

    mostrar([
        encabezado_pagina(
            "Reportes",
            "Los mismos tres reportes que el menú de terminal"),
        tarjeta_reporte("Ventas del día", cuerpo_hoy),
        ft.ResponsiveRow(spacing=8, run_spacing=8, controls=[
            tarjeta_reporte("Productos más vendidos", cuerpo_top,
                            {"xs": 12, "md": 6}),
            tarjeta_reporte("Productos con stock bajo", cuerpo_bajo,
                            {"xs": 12, "md": 6}),
        ]),
    ])


# ============================================================
# 7) VENTANA PRINCIPAL
# ============================================================

def ir_a(page, indice):
    """Cambia de pantalla y deja el menú marcado en el mismo índice."""
    componentes["indice"] = indice
    componentes["rail"].selected_index = indice
    componentes["nav"].selected_index = indice
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


def ajustar_navegacion(page):
    """Menú lateral en pantalla ancha; barra inferior si es angosta."""
    ancho = page.width or 1200
    escritorio = ancho >= ANCHO_ESCRITORIO
    componentes["rail"].visible = escritorio
    componentes["separador"].visible = escritorio
    page.navigation_bar = None if escritorio else componentes["nav"]


def main(page: ft.Page):
    """Arma la ventana: AppBar, menú y contenido."""
    mm.inicializar_base_de_datos()
    page.title = "Minimarket UNICEN"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.GREEN,
        use_material3=True,
        appbar_theme=ft.AppBarTheme(bgcolor=VERDE, color=ft.Colors.WHITE),
    )
    page.bgcolor = FONDO
    page.padding = 0

    # Barra superior con el nombre del negocio
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.STOREFRONT, color=ft.Colors.WHITE),
        leading_width=48,
        title=ft.Column(spacing=0, controls=[
            ft.Text("MINIMARKET", size=18, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Text("UNICEN · Bolivia  ·  precios en Bs", size=11,
                    color=ft.Colors.GREEN_100),
        ]),
        bgcolor=VERDE,
        color=ft.Colors.WHITE,
        toolbar_height=64,
        center_title=False,
    )

    cuerpo = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO,
                       spacing=16, controls=[])
    componentes["cuerpo"] = cuerpo
    componentes["indice"] = 0

    destinos_rail = [
        ft.NavigationRailDestination(
            icon=ft.Icons.DASHBOARD_OUTLINED,
            selected_icon=ft.Icons.DASHBOARD, label="Inicio"),
        ft.NavigationRailDestination(
            icon=ft.Icons.INVENTORY_2_OUTLINED,
            selected_icon=ft.Icons.INVENTORY_2, label="Productos"),
        ft.NavigationRailDestination(
            icon=ft.Icons.PEOPLE_OUTLINE,
            selected_icon=ft.Icons.PEOPLE, label="Clientes"),
        ft.NavigationRailDestination(
            icon=ft.Icons.POINT_OF_SALE_OUTLINED,
            selected_icon=ft.Icons.POINT_OF_SALE, label="Ventas"),
        ft.NavigationRailDestination(
            icon=ft.Icons.ASSESSMENT_OUTLINED,
            selected_icon=ft.Icons.ASSESSMENT, label="Reportes"),
    ]
    destinos_bar = [
        ft.NavigationBarDestination(
            icon=ft.Icons.DASHBOARD_OUTLINED,
            selected_icon=ft.Icons.DASHBOARD, label="Inicio"),
        ft.NavigationBarDestination(
            icon=ft.Icons.INVENTORY_2_OUTLINED,
            selected_icon=ft.Icons.INVENTORY_2, label="Productos"),
        ft.NavigationBarDestination(
            icon=ft.Icons.PEOPLE_OUTLINE,
            selected_icon=ft.Icons.PEOPLE, label="Clientes"),
        ft.NavigationBarDestination(
            icon=ft.Icons.POINT_OF_SALE_OUTLINED,
            selected_icon=ft.Icons.POINT_OF_SALE, label="Ventas"),
        ft.NavigationBarDestination(
            icon=ft.Icons.ASSESSMENT_OUTLINED,
            selected_icon=ft.Icons.ASSESSMENT, label="Reportes"),
    ]

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=84,
        min_extended_width=200,
        extended=True,
        bgcolor=ft.Colors.WHITE,
        indicator_color=VERDE_SUAVE,
        on_change=lambda e: ir_a(page, e.control.selected_index),
        destinations=destinos_rail,
        leading=ft.Container(
            padding=ft.Padding.only(top=8, bottom=8),
            content=ft.Text("Menú", size=12, color=ft.Colors.GREY_700),
        ),
    )
    nav = ft.NavigationBar(
        selected_index=0,
        destinations=destinos_bar,
        indicator_color=VERDE_SUAVE,
        on_change=lambda e: ir_a(page, e.control.selected_index),
    )
    separador = ft.VerticalDivider(width=1, color=ft.Colors.GREEN_100)
    componentes["rail"] = rail
    componentes["nav"] = nav
    componentes["separador"] = separador

    page.add(ft.Row(
        expand=True,
        controls=[
            rail,
            separador,
            ft.Container(expand=True, padding=20, content=cuerpo),
        ],
    ))
    page.on_resize = lambda e: ajustar_navegacion(page)
    ajustar_navegacion(page)
    vista_inicio()


if __name__ == "__main__":
    ft.run(main)
