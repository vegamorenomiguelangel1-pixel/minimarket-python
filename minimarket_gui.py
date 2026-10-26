"""
Sistema de Minimarket - versión gráfica (extra).

Usa tkinter (viene con Python) y REUTILIZA las funciones de minimarket.py:
los mismos archivos CSV y las mismas reglas de negocio.
Ejecutar con:  python minimarket_gui.py
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import minimarket as mm   # importa la lógica; NO arranca el menú de terminal

# Diccionario donde guardamos los widgets que usan varias funciones
componentes = {}


# ============================================================
# 1) FUNCIONES DE AYUDA PARA LA INTERFAZ
# ============================================================

def crear_formulario(marco, etiquetas):
    """Crea una etiqueta y una caja de texto por campo.

    Devuelve un diccionario {etiqueta: caja_de_texto}.
    """
    campos = {}
    for fila, etiqueta in enumerate(etiquetas):
        ttk.Label(marco, text=etiqueta).grid(row=fila, column=0,
                                             sticky="w", pady=2)
        caja = ttk.Entry(marco, width=30)
        caja.grid(row=fila, column=1, pady=2)
        campos[etiqueta] = caja
    return campos


def crear_tabla(marco, columnas):
    """Crea un Treeview (tabla) con las columnas indicadas."""
    tabla = ttk.Treeview(marco, columns=columnas, show="headings",
                         height=12)
    for columna in columnas:
        tabla.heading(columna, text=columna)
        tabla.column(columna, width=110)
    return tabla


def llenar_tabla(tabla, filas):
    """Borra el contenido de la tabla y agrega las filas nuevas."""
    for item in tabla.get_children():
        tabla.delete(item)
    for fila in filas:
        tabla.insert("", "end", values=fila)


def limpiar_campos(campos):
    """Vacía todas las cajas de texto de un formulario."""
    for caja in campos.values():
        caja.delete(0, "end")


def cargar_campos(campos, valores):
    """Escribe los valores en las cajas de texto (en el mismo orden)."""
    limpiar_campos(campos)
    for caja, valor in zip(campos.values(), valores):
        caja.insert(0, valor)


def id_seleccionado(tabla):
    """Devuelve el id (primera columna) de la fila elegida, o ""."""
    seleccion = tabla.selection()
    if len(seleccion) == 0:
        return ""
    return str(tabla.item(seleccion[0])["values"][0])


def mostrar_resultado(exito, mensaje):
    """Muestra un mensaje de éxito o de error."""
    if exito:
        messagebox.showinfo("Minimarket", mensaje)
    else:
        messagebox.showerror("Error", mensaje)


# ============================================================
# 2) PESTAÑA PRODUCTOS
# ============================================================

ETIQUETAS_PRODUCTO = ["Código", "Nombre", "Categoría", "Precio (Bs)",
                      "Stock", "Stock mínimo"]


def leer_formulario_producto():
    """Lee el formulario y devuelve (datos, error)."""
    campos = componentes["campos_producto"]
    precio = mm.convertir_precio(campos["Precio (Bs)"].get())
    stock = mm.convertir_entero(campos["Stock"].get())
    minimo = mm.convertir_entero(campos["Stock mínimo"].get())
    if precio is None or stock is None or minimo is None:
        return None, "Precio, stock y stock mínimo deben ser números."
    datos = {
        "codigo": campos["Código"].get().strip(),
        "nombre": campos["Nombre"].get().strip(),
        "categoria": campos["Categoría"].get().strip(),
        "precio": precio,
        "stock": stock,
        "stock_minimo": minimo,
    }
    return datos, ""


def refrescar_productos():
    """Recarga la tabla de productos aplicando el texto de búsqueda."""
    texto = componentes["buscar_producto"].get().strip().lower()
    filas = []
    for p in mm.leer_datos(mm.ARCHIVO_PRODUCTOS):
        if texto in p["nombre"].lower() or texto in p["codigo"].lower():
            filas.append([p["id"], p["codigo"], p["nombre"], p["categoria"],
                          f"{float(p['precio']):.2f}", p["stock"],
                          p["stock_minimo"]])
    llenar_tabla(componentes["tabla_productos"], filas)
    refrescar_combos()


def registrar_producto():
    """Botón Registrar: valida y guarda un producto nuevo."""
    datos, error = leer_formulario_producto()
    if error != "":
        mostrar_resultado(False, error)
        return
    exito, mensaje = mm.agregar_producto(datos)
    mostrar_resultado(exito, mensaje)
    if exito:
        limpiar_campos(componentes["campos_producto"])
        refrescar_productos()


def actualizar_producto():
    """Botón Actualizar: modifica el producto elegido en la tabla."""
    id_producto = id_seleccionado(componentes["tabla_productos"])
    if id_producto == "":
        mostrar_resultado(False, "Seleccione un producto de la tabla.")
        return
    datos, error = leer_formulario_producto()
    if error != "":
        mostrar_resultado(False, error)
        return
    exito, mensaje = mm.modificar_producto(id_producto, datos)
    mostrar_resultado(exito, mensaje)
    refrescar_productos()


def eliminar_producto():
    """Botón Eliminar: borra el producto elegido (si no tiene ventas)."""
    id_producto = id_seleccionado(componentes["tabla_productos"])
    if id_producto == "":
        mostrar_resultado(False, "Seleccione un producto de la tabla.")
        return
    if messagebox.askyesno("Confirmar", "¿Eliminar el producto?"):
        exito, mensaje = mm.borrar_producto(id_producto)
        mostrar_resultado(exito, mensaje)
        limpiar_campos(componentes["campos_producto"])
        refrescar_productos()


def limpiar_producto():
    """Vacía el formulario de productos."""
    limpiar_campos(componentes["campos_producto"])


def al_elegir_producto(evento):
    """Al hacer clic en una fila, copia los datos del CSV al formulario."""
    id_producto = id_seleccionado(componentes["tabla_productos"])
    p = mm.buscar_por_id(mm.leer_datos(mm.ARCHIVO_PRODUCTOS), id_producto)
    if p is not None:
        cargar_campos(componentes["campos_producto"],
                      [p["codigo"], p["nombre"], p["categoria"],
                       p["precio"], p["stock"], p["stock_minimo"]])


def crear_pestana_productos(cuaderno):
    """Arma la pestaña de productos: formulario, botones, búsqueda y tabla."""
    marco = ttk.Frame(cuaderno, padding=10)
    cuaderno.add(marco, text="Productos")
    formulario = ttk.Frame(marco)
    formulario.pack(side="left", anchor="n", padx=10)
    componentes["campos_producto"] = crear_formulario(formulario,
                                                      ETIQUETAS_PRODUCTO)
    botones = ttk.Frame(formulario)
    botones.grid(row=len(ETIQUETAS_PRODUCTO), column=0, columnspan=2,
                 pady=10)
    ttk.Button(botones, text="Registrar",
               command=registrar_producto).pack(side="left", padx=2)
    ttk.Button(botones, text="Actualizar",
               command=actualizar_producto).pack(side="left", padx=2)
    ttk.Button(botones, text="Eliminar",
               command=eliminar_producto).pack(side="left", padx=2)
    ttk.Button(botones, text="Limpiar",
               command=limpiar_producto).pack(side="left", padx=2)
    derecha = ttk.Frame(marco)
    derecha.pack(side="left", fill="both", expand=True)
    barra = ttk.Frame(derecha)
    barra.pack(fill="x", pady=5)
    ttk.Label(barra, text="Buscar:").pack(side="left")
    componentes["buscar_producto"] = ttk.Entry(barra, width=25)
    componentes["buscar_producto"].pack(side="left", padx=5)
    ttk.Button(barra, text="Buscar",
               command=refrescar_productos).pack(side="left")
    tabla = crear_tabla(derecha, ["Id", "Código", "Nombre", "Categoría",
                                  "Precio", "Stock", "Mínimo"])
    tabla.pack(fill="both", expand=True)
    tabla.bind("<<TreeviewSelect>>", al_elegir_producto)
    componentes["tabla_productos"] = tabla


# ============================================================
# 3) PESTAÑA CLIENTES
# ============================================================

ETIQUETAS_CLIENTE = ["CI/NIT", "Nombre", "Teléfono"]


def leer_formulario_cliente():
    """Devuelve un diccionario con los datos del formulario de cliente."""
    campos = componentes["campos_cliente"]
    return {
        "ci_nit": campos["CI/NIT"].get().strip(),
        "nombre": campos["Nombre"].get().strip(),
        "telefono": campos["Teléfono"].get().strip(),
    }


def refrescar_clientes():
    """Recarga la tabla de clientes aplicando el texto de búsqueda."""
    texto = componentes["buscar_cliente"].get().strip().lower()
    filas = []
    for c in mm.leer_datos(mm.ARCHIVO_CLIENTES):
        if texto in c["nombre"].lower() or texto in c["ci_nit"]:
            filas.append([c["id"], c["ci_nit"], c["nombre"], c["telefono"]])
    llenar_tabla(componentes["tabla_clientes"], filas)
    refrescar_combos()


def registrar_cliente():
    """Botón Registrar: valida y guarda un cliente nuevo."""
    exito, mensaje = mm.agregar_cliente(leer_formulario_cliente())
    mostrar_resultado(exito, mensaje)
    if exito:
        limpiar_campos(componentes["campos_cliente"])
        refrescar_clientes()


def actualizar_cliente():
    """Botón Actualizar: modifica el cliente elegido en la tabla."""
    id_cliente = id_seleccionado(componentes["tabla_clientes"])
    if id_cliente == "":
        mostrar_resultado(False, "Seleccione un cliente de la tabla.")
        return
    exito, mensaje = mm.modificar_cliente(id_cliente,
                                          leer_formulario_cliente())
    mostrar_resultado(exito, mensaje)
    refrescar_clientes()


def eliminar_cliente():
    """Botón Eliminar: borra el cliente elegido (si no tiene ventas)."""
    id_cliente = id_seleccionado(componentes["tabla_clientes"])
    if id_cliente == "":
        mostrar_resultado(False, "Seleccione un cliente de la tabla.")
        return
    if messagebox.askyesno("Confirmar", "¿Eliminar el cliente?"):
        exito, mensaje = mm.borrar_cliente(id_cliente)
        mostrar_resultado(exito, mensaje)
        limpiar_campos(componentes["campos_cliente"])
        refrescar_clientes()


def limpiar_cliente():
    """Vacía el formulario de clientes."""
    limpiar_campos(componentes["campos_cliente"])


def al_elegir_cliente(evento):
    """Al hacer clic en una fila, copia los datos del CSV al formulario."""
    id_cliente = id_seleccionado(componentes["tabla_clientes"])
    c = mm.buscar_por_id(mm.leer_datos(mm.ARCHIVO_CLIENTES), id_cliente)
    if c is not None:
        cargar_campos(componentes["campos_cliente"],
                      [c["ci_nit"], c["nombre"], c["telefono"]])


def crear_pestana_clientes(cuaderno):
    """Arma la pestaña de clientes (misma estructura que productos)."""
    marco = ttk.Frame(cuaderno, padding=10)
    cuaderno.add(marco, text="Clientes")
    formulario = ttk.Frame(marco)
    formulario.pack(side="left", anchor="n", padx=10)
    componentes["campos_cliente"] = crear_formulario(formulario,
                                                     ETIQUETAS_CLIENTE)
    botones = ttk.Frame(formulario)
    botones.grid(row=len(ETIQUETAS_CLIENTE), column=0, columnspan=2,
                 pady=10)
    ttk.Button(botones, text="Registrar",
               command=registrar_cliente).pack(side="left", padx=2)
    ttk.Button(botones, text="Actualizar",
               command=actualizar_cliente).pack(side="left", padx=2)
    ttk.Button(botones, text="Eliminar",
               command=eliminar_cliente).pack(side="left", padx=2)
    ttk.Button(botones, text="Limpiar",
               command=limpiar_cliente).pack(side="left", padx=2)
    derecha = ttk.Frame(marco)
    derecha.pack(side="left", fill="both", expand=True)
    barra = ttk.Frame(derecha)
    barra.pack(fill="x", pady=5)
    ttk.Label(barra, text="Buscar:").pack(side="left")
    componentes["buscar_cliente"] = ttk.Entry(barra, width=25)
    componentes["buscar_cliente"].pack(side="left", padx=5)
    ttk.Button(barra, text="Buscar",
               command=refrescar_clientes).pack(side="left")
    tabla = crear_tabla(derecha, ["Id", "CI/NIT", "Nombre", "Teléfono"])
    tabla.pack(fill="both", expand=True)
    tabla.bind("<<TreeviewSelect>>", al_elegir_cliente)
    componentes["tabla_clientes"] = tabla


# ============================================================
# 4) PESTAÑA VENTAS
# ============================================================

def refrescar_combos():
    """Actualiza las listas desplegables de clientes y productos."""
    if "combo_cliente" not in componentes:
        return   # la pestaña de ventas todavía no se creó
    opciones_clientes = []
    for c in mm.leer_datos(mm.ARCHIVO_CLIENTES):
        opciones_clientes.append(f"{c['id']} - {c['nombre']}")
    opciones_productos = []
    for p in mm.leer_datos(mm.ARCHIVO_PRODUCTOS):
        opciones_productos.append(f"{p['id']} - {p['nombre']} "
                                  f"(stock {p['stock']})")
    componentes["combo_cliente"]["values"] = opciones_clientes
    componentes["combo_producto"]["values"] = opciones_productos


def refrescar_ventas():
    """Recarga la tabla de ventas."""
    clientes = mm.leer_datos(mm.ARCHIVO_CLIENTES)
    productos = mm.leer_datos(mm.ARCHIVO_PRODUCTOS)
    filas = []
    for v in mm.leer_datos(mm.ARCHIVO_VENTAS):
        cliente = mm.buscar_por_id(clientes, v["id_cliente"])
        producto = mm.buscar_por_id(productos, v["id_producto"])
        filas.append([v["id"], v["fecha"], mm.nombre_o_eliminado(cliente),
                      mm.nombre_o_eliminado(producto), v["cantidad"],
                      f"{float(v['total']):.2f}"])
    llenar_tabla(componentes["tabla_ventas"], filas)


def vender():
    """Toma los datos elegidos y llama a realizar_venta() de minimarket.py."""
    texto_cliente = componentes["combo_cliente"].get()
    texto_producto = componentes["combo_producto"].get()
    cantidad = mm.convertir_entero(componentes["cantidad"].get())
    if texto_cliente == "" or texto_producto == "":
        mostrar_resultado(False, "Elija un cliente y un producto.")
        return
    if cantidad is None:
        mostrar_resultado(False, "La cantidad debe ser un número entero.")
        return
    id_cliente = texto_cliente.split(" - ")[0]     # "1 - Juan" -> "1"
    id_producto = texto_producto.split(" - ")[0]
    exito, mensaje, venta = mm.realizar_venta(id_cliente, id_producto,
                                              cantidad)
    if not exito:
        mostrar_resultado(False, mensaje)
        return
    factura = "\n".join(mm.lineas_factura(venta))
    componentes["texto_factura"].delete("1.0", "end")
    componentes["texto_factura"].insert("1.0", factura)
    refrescar_productos()
    refrescar_ventas()
    producto = mm.buscar_por_id(mm.leer_datos(mm.ARCHIVO_PRODUCTOS),
                                id_producto)
    if mm.stock_bajo(producto):
        messagebox.showwarning("Stock bajo",
                               f"Quedan {producto['stock']} unidades de "
                               f"{producto['nombre']}.")


def crear_pestana_ventas(cuaderno):
    """Arma la pestaña de ventas: listas desplegables, factura y tabla."""
    marco = ttk.Frame(cuaderno, padding=10)
    cuaderno.add(marco, text="Ventas")
    izquierda = ttk.Frame(marco)
    izquierda.pack(side="left", anchor="n", padx=10)
    ttk.Label(izquierda, text="Cliente").grid(row=0, column=0, sticky="w")
    componentes["combo_cliente"] = ttk.Combobox(izquierda, width=30,
                                                state="readonly")
    componentes["combo_cliente"].grid(row=0, column=1, pady=2)
    ttk.Label(izquierda, text="Producto").grid(row=1, column=0, sticky="w")
    componentes["combo_producto"] = ttk.Combobox(izquierda, width=30,
                                                 state="readonly")
    componentes["combo_producto"].grid(row=1, column=1, pady=2)
    ttk.Label(izquierda, text="Cantidad").grid(row=2, column=0, sticky="w")
    componentes["cantidad"] = ttk.Entry(izquierda, width=10)
    componentes["cantidad"].grid(row=2, column=1, sticky="w", pady=2)
    ttk.Button(izquierda, text="Vender", command=vender).grid(
        row=3, column=0, columnspan=2, pady=10)
    componentes["texto_factura"] = tk.Text(izquierda, width=40, height=10,
                                           font=("Courier New", 10))
    componentes["texto_factura"].grid(row=4, column=0, columnspan=2)
    tabla = crear_tabla(marco, ["Id", "Fecha", "Cliente", "Producto",
                                "Cantidad", "Total"])
    tabla.pack(side="left", fill="both", expand=True)
    componentes["tabla_ventas"] = tabla


# ============================================================
# 5) PESTAÑA REPORTES
# ============================================================

def escribir_reporte(lineas):
    """Muestra una lista de líneas en el cuadro de texto de reportes."""
    caja = componentes["texto_reporte"]
    caja.delete("1.0", "end")
    caja.insert("1.0", "\n".join(lineas))


def ver_ventas_del_dia():
    """Botón Ventas del día: lista las ventas de hoy y el total."""
    ventas = mm.ventas_de_hoy()
    lineas = ["VENTAS DEL DÍA", ""]
    for v in ventas:
        lineas.append(f"Venta {v['id']}  {v['fecha']}  "
                      f"Bs {float(v['total']):.2f}")
    lineas.append("")
    lineas.append(f"Cantidad de ventas: {len(ventas)}")
    lineas.append(f"TOTAL RECAUDADO: Bs {mm.calcular_total(ventas):.2f}")
    escribir_reporte(lineas)


def ver_mas_vendidos():
    """Botón Más vendidos: ranking de unidades vendidas."""
    lineas = ["PRODUCTOS MÁS VENDIDOS", ""]
    for posicion, par in enumerate(mm.calcular_mas_vendidos(), start=1):
        lineas.append(f"{posicion}. {par[1]}: {par[0]} unidades")
    escribir_reporte(lineas)


def ver_stock_bajo():
    """Botón Stock bajo: productos con stock <= mínimo."""
    lineas = ["PRODUCTOS CON STOCK BAJO", ""]
    for p in mm.productos_con_stock_bajo():
        lineas.append(f"{p['codigo']}  {p['nombre']}: stock {p['stock']} "
                      f"(mínimo {p['stock_minimo']})")
    escribir_reporte(lineas)


def crear_pestana_reportes(cuaderno):
    """Arma la pestaña de reportes: tres botones y un cuadro de texto."""
    marco = ttk.Frame(cuaderno, padding=10)
    cuaderno.add(marco, text="Reportes")
    botones = ttk.Frame(marco)
    botones.pack(fill="x")
    ttk.Button(botones, text="Ventas del día",
               command=ver_ventas_del_dia).pack(side="left", padx=5)
    ttk.Button(botones, text="Más vendidos",
               command=ver_mas_vendidos).pack(side="left", padx=5)
    ttk.Button(botones, text="Stock bajo",
               command=ver_stock_bajo).pack(side="left", padx=5)
    componentes["texto_reporte"] = tk.Text(marco, height=18,
                                           font=("Courier New", 11))
    componentes["texto_reporte"].pack(fill="both", expand=True, pady=10)


# ============================================================
# 6) VENTANA PRINCIPAL
# ============================================================

def crear_ventana():
    """Crea la ventana con sus cuatro pestañas y carga los datos."""
    mm.inicializar_base_de_datos()
    ventana = tk.Tk()
    ventana.title("MINIMARKET")
    ventana.geometry("1100x520")
    ttk.Label(ventana, text="MINIMARKET",
              font=("Arial", 18, "bold")).pack(pady=5)
    cuaderno = ttk.Notebook(ventana)
    cuaderno.pack(fill="both", expand=True, padx=10, pady=5)
    crear_pestana_productos(cuaderno)
    crear_pestana_clientes(cuaderno)
    crear_pestana_ventas(cuaderno)
    crear_pestana_reportes(cuaderno)
    refrescar_productos()
    refrescar_clientes()
    refrescar_ventas()
    return ventana


if __name__ == "__main__":
    crear_ventana().mainloop()
