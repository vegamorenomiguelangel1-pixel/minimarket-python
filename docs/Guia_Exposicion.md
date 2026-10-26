# Guía de exposición – Sistema de Minimarket (Python)

## 1. ¿Qué hace el sistema?
Es un programa de terminal para administrar un minimarket: registrar **productos** y **clientes**, hacer **ventas** (con factura en pantalla) y ver **reportes** (ventas del día, productos más vendidos y productos con stock bajo). Se ejecuta con:

```
python minimarket.py
```

> **Importante:** la versión de **terminal** (`minimarket.py`) es la que cumple la consigna. La versión gráfica (`minimarket_gui.py`) y la versión web (`app_web.py`) son **extras** que reutilizan el mismo código y los mismos CSV.

## 2. Los 3 archivos CSV (la "base de datos")
| Archivo | Columnas |
|---|---|
| `productos.csv` | id, codigo, nombre, categoria, precio, stock, stock_minimo |
| `clientes.csv` | id, ci_nit, nombre, telefono |
| `ventas.csv` | id, fecha, id_cliente, id_producto, cantidad, precio_unitario, total |

**Relación:** cada venta guarda `id_cliente` (apunta a un cliente) e `id_producto` (apunta a un producto). Es como una "llave foránea" en una base de datos: así sabemos quién compró qué. Los archivos se crean solos la primera vez, en la misma carpeta del programa (constante `CARPETA`).

## 3. Cómo se cumple la consigna
- **Terminal:** todo funciona con menús numerados usando `input()` y `print()`.
- **Base de datos CSV:** se usa el módulo `csv` (`DictReader` y `DictWriter`).
- **CRUD completo:** productos y clientes tienen Crear, Listar/Buscar (leer), Actualizar y Eliminar. Las ventas se crean y se consultan.
- **Sin IA:** solo biblioteca estándar de Python: `csv`, `os` y `datetime` (y `tkinter` en el extra gráfico, que también viene con Python).

## 4. Recorrido por el código de `minimarket.py`

**1) Base de datos CSV.** `inicializar_base_de_datos()` llama a `crear_archivo_si_no_existe()`, que usa `os.path.exists` y escribe el encabezado si el archivo no existe. `leer_datos()` devuelve una lista de diccionarios y `guardar_datos()` reescribe el archivo completo. `generar_id()` busca el id mayor y le suma 1; `buscar_por_id()` devuelve la fila o `None`.

**2) Estilo visual.** Constantes de color (`ROJO`, `VERDE`, `AMARILLO`, `CIAN`) y funciones para limpiar pantalla, mostrar el banner y dibujar tablas (ver sección 5 de esta guía).

**3) Utilidades de entrada.** Repiten la pregunta con `while True` hasta que el dato sea válido: `pedir_texto()` no acepta vacíos, `pedir_entero()` exige un entero mayor o igual a un mínimo y `pedir_precio()` exige un precio > 0. `pedir_opcional()` deja el valor actual si se presiona Enter y `confirmar()` pide s/n.

**4) Lógica de productos y clientes.** Aquí están las reglas, **sin `input()` ni `print()`**: `validar_producto()` y `validar_cliente()` devuelven el texto del error (o `""` si todo está bien). `agregar_producto()`, `modificar_producto()` y `borrar_producto()` (y las de clientes) devuelven una tupla `(exito, mensaje)`. Separarlo así permite usar estas mismas funciones desde la versión gráfica.

**5) Lógica de ventas y reportes.** `realizar_venta()` verifica cliente, producto y stock, guarda la venta, descuenta el stock y devuelve `(exito, mensaje, venta)`. `lineas_factura()` arma la factura como lista de textos. `ventas_de_hoy()`, `calcular_total()`, `calcular_mas_vendidos()` (diccionario que acumula unidades y luego `sort(reverse=True)`) y `productos_con_stock_bajo()` calculan los reportes.

**6) y 7) Pantallas de productos y clientes.** Son las funciones que hablan con el usuario: `crear_producto()`, `listar_productos()`, `buscar_producto()`, `actualizar_producto()`, `eliminar_producto()` (y lo mismo para clientes). Piden los datos con las utilidades de entrada, llaman a la lógica y muestran el resultado en verde o rojo con `mostrar_resultado()`.

**8) Pantallas de ventas y reportes.** `registrar_venta()` pide los ids y la cantidad, llama a `realizar_venta()`, imprime la factura con `imprimir_caja()` y, si `stock_bajo()` es verdadero, muestra un aviso amarillo. Los reportes muestran sus resultados en tablas.

**9) Menús.** `menu_principal()` muestra las 4 áreas y Salir. Cada submenú usa `ejecutar_menu()`, que recibe una lista de `[texto, función]`, muestra las opciones y llama a la función elegida; después de cada acción hace `pausar()`.

## 5. Ayudas visuales (sección 2 del código)
- **Colores ANSI:** son códigos especiales como `"\033[91m"` (rojo). Se imprime el código, el texto y luego `RESET` para volver al color normal. Verde = éxito, rojo = error, amarillo = aviso.
- **`activar_colores()`:** llama a `os.system("")`; es un truco conocido que activa los colores en la consola de Windows (cmd/PowerShell).
- **`limpiar_pantalla()`:** ejecuta `cls` en Windows (`os.name == "nt"`) o `clear` en Linux/Mac.
- **`mostrar_encabezado()`:** limpia la pantalla y dibuja el banner "MINIMARKET" con el título del menú.
- **`imprimir_tabla()`:** calcula el ancho de cada columna (el texto más largo) y dibuja bordes `+---+` con `ljust()`. **`imprimir_caja()`** hace lo mismo para la factura.

## 6. Reglas de negocio y dónde están
| Regla | Dónde |
|---|---|
| Código de producto no se repite | `codigo_repetido()` dentro de `validar_producto()` |
| CI/NIT de cliente no se repite | `ci_repetido()` dentro de `validar_cliente()` |
| Precio > 0 y stock >= 0 | `validar_producto()` (y `pedir_precio()` / `pedir_entero()`) |
| No vender más del stock | `realizar_venta()` (`if cantidad > stock`) |
| Al vender se descuenta el stock | `realizar_venta()` (`producto["stock"] = stock - cantidad`) |
| Aviso de stock bajo después de vender | `stock_bajo()`, usado en `registrar_venta()` |
| No eliminar producto/cliente con ventas | `tiene_ventas()` en `borrar_producto()` y `borrar_cliente()` |

## 7. Demostración sugerida (en vivo)
1. Productos → registrar "Leche PIL" (stock 10, mínimo 3) y "Pan" (stock 50, mínimo 5). Probar un precio inválido (`abc` o `0`) para mostrar el error en rojo.
2. Intentar registrar otro producto con el mismo código → error.
3. Listar productos → mostrar la tabla con bordes.
4. Clientes → registrar 2 clientes; intentar repetir un CI/NIT → error.
5. Ventas → vender 20 unidades de Leche → error de stock insuficiente.
6. Vender 8 de Leche → factura en recuadro y **aviso amarillo de stock bajo**.
7. Reportes → ventas del día, más vendidos, stock bajo.
8. Intentar eliminar un producto con ventas → no lo permite.
9. Abrir los archivos `.csv` para mostrar que los datos quedaron guardados.
10. (Extra) Abrir `python minimarket_gui.py` y mostrar que aparecen los mismos datos.

## 8. Versión gráfica con tkinter (extra)
**Qué es:** `minimarket_gui.py` es una ventana con 4 pestañas (Productos, Clientes, Ventas, Reportes). Se ejecuta con `python minimarket_gui.py`.

**Widgets usados:**
- `tk.Tk()` (ventana) y `ttk.Notebook` (pestañas).
- `ttk.Label` y `ttk.Entry` (formularios), `ttk.Button` (Registrar, Actualizar, Eliminar, Limpiar, Vender).
- `ttk.Treeview` (tablas); al hacer clic en una fila (`<<TreeviewSelect>>`) se cargan sus datos en el formulario.
- `ttk.Combobox` (elegir cliente y producto en Ventas), `tk.Text` (factura y reportes).
- `messagebox` para errores (`showerror`), éxitos (`showinfo`), aviso de stock bajo (`showwarning`) y confirmación al eliminar (`askyesno`).

**Cómo reutiliza el código:** hace `import minimarket as mm` y llama a `mm.agregar_producto()`, `mm.realizar_venta()`, `mm.calcular_mas_vendidos()`, etc. Las reglas de negocio están escritas una sola vez, en `minimarket.py`, y usan los mismos CSV, así que lo que se registra en la terminal aparece en la ventana y al revés. Importar no abre el menú de terminal gracias a `if __name__ == "__main__":`.

**Qué decir:** "La lógica está separada de la interfaz. La terminal y la ventana son dos 'caras' distintas que usan las mismas funciones y los mismos archivos. Para guardar los widgets uso un diccionario `componentes`, así las funciones de los botones pueden leer los formularios y tablas."

## 10. Versión web con Flask (extra)
**Qué es:** `app_web.py` es un servidor web pequeño. Se instala Flask con `pip install -r requirements.txt` y se ejecuta con `python app_web.py`. En el navegador se abre `http://127.0.0.1:5000`.

**Páginas:** Inicio (resumen y alertas de stock bajo), Productos, Clientes, Ventas (con factura) y Reportes. Las plantillas HTML están en `templates/` y el CSS en `static/estilo.css` (sin librerías externas).

**Cómo reutiliza el código:** también hace `import minimarket as mm` y llama a `mm.agregar_producto()`, `mm.realizar_venta()`, etc. Los errores de negocio se muestran con `flash()` (mensajes verdes o rojos arriba de la página). Al eliminar, hay una pantalla de confirmación.

**Qué decir:** "Es una tercera cara del mismo programa. Flask solo se encarga de las páginas; las reglas (stock, códigos repetidos, no borrar si hay ventas) siguen en `minimarket.py`."

## 9. Preguntas probables del profesor
- **¿Por qué `newline=""` al abrir el CSV?** Porque el módulo `csv` maneja los saltos de línea por su cuenta; sin esto, en Windows aparecen líneas en blanco entre filas.
- **¿Por qué `encoding="utf-8"`?** Para guardar bien tildes y la ñ (por ejemplo "Lácteos", "Panadería").
- **¿Qué hace `DictReader`?** Lee cada fila del CSV como un diccionario, usando el encabezado como claves; así se escribe `p["precio"]` en lugar de `p[4]`.
- **¿Cómo se generan los ids?** `generar_id()` recorre las filas, busca el id mayor y suma 1.
- **¿Por qué se lee y se guarda el archivo completo?** Un CSV es texto: no se puede cambiar una fila "en el medio". Lo simple es leer todo a una lista, modificarla y volver a escribirla. Para un minimarket pequeño es suficientemente rápido.
- **¿Por qué hay que convertir con `int()` y `float()`?** Porque del CSV todo se lee como texto.
- **¿Cómo funciona `ejecutar_menu()`?** En Python una función se puede guardar en una lista como cualquier dato; se guarda sin paréntesis y se ejecuta después con `funcion()`.
- **¿Qué es `"\033[91m"`?** Un código de escape ANSI: la terminal no lo muestra, sino que cambia el color del texto que viene después.
- **(GUI) ¿Por qué la versión gráfica no repite las reglas?** Porque importa `minimarket.py`; las funciones de lógica no usan `input()` ni `print()` y devuelven `(exito, mensaje)`, así cada interfaz decide cómo mostrar el mensaje (color en terminal, `messagebox` en la ventana).
- **(GUI) ¿Qué es `mainloop()`?** Es el ciclo que mantiene la ventana abierta esperando eventos (clics, teclas) y llama a la función de cada botón (`command=`).
- **(GUI) ¿Por qué al importar no se abre el menú de terminal?** Porque `menu_principal()` solo se llama dentro de `if __name__ == "__main__":`, que es verdadero solo cuando se ejecuta el archivo directamente.
