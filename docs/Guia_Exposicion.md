# Guía de exposición – Sistema de Minimarket (Python)

## 1. ¿Qué hace el sistema?
Es un programa de terminal para administrar un minimarket: registrar **productos** y **clientes**, hacer **ventas** (con factura en pantalla) y ver **reportes** (ventas del día, productos más vendidos y productos con stock bajo). Se ejecuta con:

```
python minimarket.py
```

> **Importante:** la versión de **terminal** (`minimarket.py`) es la que cumple la consigna. La versión Flet (`app_flet.py`) es un **extra** que reutiliza el mismo código y la misma base SQLite, tanto en escritorio como en el navegador.

## 2. La base de datos SQLite (`minimarket.db`)
Un solo archivo con tres tablas. Lo crea `base_datos.py` la primera vez que se ejecuta cualquier versión.

| Tabla | Columnas |
|---|---|
| `productos` | id (PK AUTOINCREMENT), codigo (UNIQUE), nombre, categoria, precio (CHECK > 0), stock (CHECK >= 0), stock_minimo |
| `clientes` | id (PK AUTOINCREMENT), ci_nit (UNIQUE), nombre, telefono |
| `ventas` | id, fecha, id_cliente (FK), id_producto (FK), cantidad, precio_unitario, total |

**Relación:** cada venta guarda `id_cliente` e `id_producto`. Son **llaves foráneas**: no se puede vender a un cliente que no existe ni un producto que no existe. SQLite las apaga por defecto, por eso cada conexión hace `PRAGMA foreign_keys = ON`.

Si el archivo está vacío, se insertan datos de ejemplo de un minimarket boliviano (precios en Bs, CI/NIT, ventas de hoy y de días anteriores).

## 3. Cómo se cumple la consigna
- **Terminal:** todo funciona con menús numerados usando `input()` y `print()`.
- **Base de datos:** módulo `sqlite3` (viene con Python). No hace falta instalar un servidor.
- **CRUD completo:** productos y clientes tienen Crear (`INSERT`), Listar/Buscar (`SELECT`), Actualizar (`UPDATE`) y Eliminar (`DELETE`). Las ventas se crean y se consultan.
- **Sin IA:** biblioteca estándar (`sqlite3`, `os`, `datetime`) más Flet solo en el extra.

## 4. Recorrido por el código

**`base_datos.py`.** `conectar()` abre el archivo y enciende las FOREIGN KEY. `inicializar()` crea las tablas (`CREATE TABLE IF NOT EXISTS`) y, si están vacías, llama a `cargar_datos_de_ejemplo()`. Las consultas usan `?` para separar el valor del comando SQL y evitar la **inyección SQL**. `fila_a_dict()` convierte cada fila en un diccionario de textos, para que el resto del programa se lea fácil (`p["nombre"]`).

**`minimarket.py` – lógica (secciones 4 y 5).** Aquí están las reglas, **sin `input()` ni `print()`**. `validar_producto()` y `validar_cliente()` devuelven el texto del error (o `""`). `agregar_producto()`, `modificar_producto()` y `borrar_producto()` (y las de clientes) devuelven `(exito, mensaje)` y llaman a los `INSERT`/`UPDATE`/`DELETE` de `base_datos.py`. `realizar_venta()` verifica cliente, producto y stock, guarda la venta y descuenta el stock en **una sola transacción**.

**`minimarket.py` – pantallas y menús.** Piden los datos con `pedir_texto()`, `pedir_entero()` y `pedir_precio()`, llaman a la lógica y pintan el resultado en verde o rojo. `ejecutar_menu()` recibe una lista de `[texto, función]`.

**Ayudas visuales de terminal.** Colores ANSI (`ROJO`, `VERDE`, `AMARILLO`), `limpiar_pantalla()` (`cls` o `clear`) e `imprimir_tabla()` con bordes `+---+`.

## 5. Reglas de negocio y dónde están
| Regla | Dónde |
|---|---|
| Código de producto no se repite | `codigo_repetido()` → `SELECT` + UNIQUE en la tabla |
| CI/NIT de cliente no se repite | `ci_repetido()` → `SELECT` + UNIQUE |
| Precio > 0 y stock >= 0 | `validar_producto()` + `CHECK` en la tabla |
| No vender más del stock | `realizar_venta()` |
| Al vender se descuenta el stock | `guardar_venta_y_descontar_stock()` |
| Aviso de stock bajo después de vender | `stock_bajo()` |
| No eliminar producto/cliente con ventas | `tiene_ventas()` |

## 6. Demostración sugerida (en vivo)
1. Productos → registrar "Leche PIL" extra (otro código) y probar un precio inválido (`abc` o `0`).
2. Intentar registrar otro producto con el mismo código → error.
3. Listar productos → tabla con bordes.
4. Clientes → registrar 1 cliente; intentar repetir un CI/NIT → error.
5. Ventas → vender 99 unidades de Leche PIL → error de stock insuficiente.
6. Vender 2 de Pan francés → factura en recuadro.
7. Reportes → ventas del día, más vendidos, stock bajo.
8. Intentar eliminar un producto con ventas → no lo permite.
9. (Extra) Abrir `python app_flet.py` o `flet run --web app_flet.py` y mostrar los mismos datos.

## 7. Versión Flet (extra)
**Qué es:** `app_flet.py` es una sola interfaz que corre en **ventana** (`python app_flet.py` / `flet run app_flet.py`) y en **navegador** (`flet run --web app_flet.py`). Tiene un `NavigationRail` (menú izquierdo) con Inicio, Productos, Clientes, Ventas y Reportes.

**Controles usados:** `TextField` (formularios), `Button` / `TextButton`, `DataTable` (tablas), `Dropdown` (cliente y producto), `SnackBar` (mensajes) y `AlertDialog` (confirmar eliminar y mostrar la factura).

**Cómo reutiliza el código:** hace `import minimarket as mm` y llama a `mm.agregar_producto()`, `mm.realizar_venta()`, etc. Las reglas están escritas una sola vez. Importar no abre el menú de terminal gracias a `if __name__ == "__main__":`.

**Qué decir:** "La lógica está separada de la interfaz. La terminal y Flet son dos caras del mismo programa y usan el mismo `minimarket.db`. Los controles los guardo en un diccionario `componentes` para que los botones puedan leer el formulario."

## 8. Preguntas probables del profesor
- **¿Por qué SQLite y no un servidor?** Porque es un archivo, viene con Python (`sqlite3`) y alcanza para un minimarket pequeño.
- **¿Qué es AUTOINCREMENT?** SQLite pone el siguiente id solo; no hay que calcular `máximo + 1`.
- **¿Qué es `?` en las consultas?** Es un marcador: el valor se manda aparte. Si alguien escribe `' OR 1=1 --` en el código, no se ejecuta como SQL (inyección).
- **¿Por qué `PRAGMA foreign_keys = ON`?** En SQLite las llaves foráneas vienen apagadas; hay que encenderlas en cada conexión.
- **¿Por qué una transacción al vender?** Así no queda una venta guardada si falló el descuento de stock (o al revés).
- **¿Por qué hay que convertir con `int()` y `float()`?** Porque al leer la fila la pasamos a texto para que se use igual en todas partes.
- **¿Cómo funciona `ejecutar_menu()`?** En Python una función se puede guardar en una lista; se guarda sin paréntesis y se ejecuta después con `funcion()`.
- **(Flet) ¿Por qué no se abre el menú de terminal al importar?** Porque `menu_principal()` solo corre dentro de `if __name__ == "__main__":`.
- **(Flet) ¿Escritorio y web son dos programas?** No: es el mismo `app_flet.py`. `flet run --web` lo sirve en el navegador.

## 9. Nota sobre los otros archivos de `docs/`
Los `.docx` y el video `demo_minimarket.mp4` se hicieron con una versión anterior (CSV + tkinter + Flask). **Esa descripción ya no coincide con el código actual.** Hoy la base es SQLite y el extra es Flet.
