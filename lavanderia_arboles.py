# Lavaseco Angiexpress - Corte 2 (Arboles)
# Estructuras de Datos II - Fundacion Universitaria Compensar
# El arbol organiza el negocio: negocio -> clientes -> ordenes -> prendas
# Se conecta con el archivo del corte 1 (ordenes.txt) y se guarda en arbol_lavanderia.txt

import os
import sys
from datetime import datetime

# Archivos que usa el programa
ARCHIVO_ORDENES = "ordenes.txt"        # archivo del corte 1, una orden por linea separada por comas
ARCHIVO_ARBOL = "arbol_lavanderia.txt"  # arbol guardado, una linea por nodo

# Separadores
SEP_ORDENES = ","    # separador del archivo del corte 1
SEP_ARBOL = "|"      # separador de las columnas del archivo del arbol
SEP_CAMPO = ";"      # separador de los campos extra de cada nodo

# Que tipo de hijos puede tener cada tipo de nodo
HIJOS_PERMITIDOS = {
    "negocio": ["cliente"],
    "cliente": ["orden"],
    "orden": ["prenda"],
    "prenda": []
}

# Campos extra que guarda cada tipo de nodo (ademas del dato)
CAMPOS = {
    "negocio": [],
    "cliente": ["nombre", "telefono"],
    "orden": ["servicio", "fecha_entrada", "fecha_salida", "estado", "valor", "pago"],
    "prenda": ["cantidad"]
}

SERVICIOS = ["Lavado", "Planchado", "Lavaseco"]
ESTADOS = ["Pendiente", "En proceso", "Listo", "Entregado"]
PAGOS = ["Pagado", "No pagado"]

# Clase del nodo

class Nodo:
    def __init__(self, dato, tipo, info=None):
        self.dato = dato                              # texto que identifica el nodo (id del cliente, orden, prenda...)
        self.tipo = tipo                              # negocio, cliente, orden o prenda
        self.info = info if info is not None else {}  # datos extra del nodo
        self.hijos = []                               # lista de hijos

    def agregar_hijo(self, hijo):
        # Añade un nodo a la lista de hijos y lo devuelve para que sea padre de otros nodos
        self.hijos.append(hijo)
        return hijo

# Insertar un nodo (reutilizable para todos los tipos)

def insertar(padre, nuevo):
    # Revisa que haya padre, que el tipo de hijo sea valido y que no se repita entre hermanos
    if padre is None:
        raise ValueError("No hay nodo padre donde insertar")
    if nuevo.tipo not in HIJOS_PERMITIDOS[padre.tipo]:
        raise ValueError(f"Un {padre.tipo} no puede tener hijos de tipo {nuevo.tipo}")
    for hijo in padre.hijos:
        if hijo.dato == nuevo.dato:
            raise ValueError(f"'{padre.dato}' ya tiene un hijo llamado '{nuevo.dato}'")
    return padre.agregar_hijo(nuevo)

# Texto de cada nodo para mostrarlo

def descripcion_nodo(nodo):
    i = nodo.info
    if nodo.tipo == "cliente":
        return f"[cliente] {nodo.dato} - {i.get('nombre')} ({i.get('telefono')})"
    if nodo.tipo == "orden":
        return f"[orden] {nodo.dato} - {i.get('servicio')}, {i.get('estado')}, ${i.get('valor')}, {i.get('pago')}"
    if nodo.tipo == "prenda":
        return f"[prenda] {nodo.dato} x{i.get('cantidad')}"
    return f"[{nodo.tipo}] {nodo.dato}"

# mostrar el arbol con recursividad

def mostrar_arbol(nodo, nivel=0):
    # Caso base que un nodo sin hijos y el for no se ejecuta y la funcion termina despues de imprimir el nodo
    # Caso recursivo que por cada hijo se llama a la funcion con un nivel de +1
    print("    " * nivel + descripcion_nodo(nodo))
    for hijo in nodo.hijos:
        mostrar_arbol(hijo, nivel + 1)

# contar nodos con recursividad

def contar_nodos(nodo):
    # Caso base que es un nodo sin hijos cuenta 1
    # Caso recursivo es el nodo inicial 1 + los nodos de cada hijo
    if not nodo.hijos:
        return 1
    total = 1
    for hijo in nodo.hijos:
        total += contar_nodos(hijo)
    return total

# Contar hojas con recursividad

def contar_hojas(nodo):
    # Caso base que si no tiene hijos es una hoja y cuenta 1
    # Caso recursivo es la suma de las hojas de cada uno de sus hijos
    if not nodo.hijos:
        return 1
    total = 0
    for hijo in nodo.hijos:
        total += contar_hojas(hijo)
    return total

# Calcular altura con recursividad

def calcular_altura(nodo):
    # Caso base es la hoja que tiene altura 0
    # Caso recursivo es 1 + la mayor altura entre sus hijos
    if not nodo.hijos:
        return 0
    alturas = []
    for hijo in nodo.hijos:
        alturas.append(calcular_altura(hijo))
    return 1 + max(alturas)

# Contar los nodos de un tipo (clientes, ordenes, prendas)

def contar_por_tipo(nodo, tipo):
    # Caso base que un nodo sin hijos cuenta 1 solo si es del tipo buscado
    # Caso recursivo es lo del nodo actual + lo que cuente cada hijo
    total = 0
    if nodo.tipo == tipo:
        total = 1
    for hijo in nodo.hijos:
        total += contar_por_tipo(hijo, tipo)
    return total

# Sumar la cantidad de prendas recibidas

def sumar_prendas(nodo):
    # Caso base que un nodo sin hijos suma su cantidad solo si es una prenda
    # Caso recursivo es lo del nodo actual + las prendas de cada hijo
    total = 0
    if nodo.tipo == "prenda":
        total = int(nodo.info.get("cantidad", 0))
    for hijo in nodo.hijos:
        total += sumar_prendas(hijo)
    return total

# Sumar el valor de las ordenes (con un filtro de pago opcional)

def sumar_valor(nodo, pago=None):
    # Si se manda el pago solo suma las ordenes con ese pago (Pagado o No pagado)
    # Caso base que un nodo sin hijos suma su valor solo si es una orden que cumple el filtro
    # Caso recursivo es lo del nodo actual + el valor de cada hijo
    total = 0
    if nodo.tipo == "orden" and (pago is None or nodo.info.get("pago") == pago):
        total = float(nodo.info.get("valor", 0))
    for hijo in nodo.hijos:
        total += sumar_valor(hijo, pago)
    return total

# Contar ordenes segun un campo (servicio, estado o pago)

def contar_ordenes(nodo, campo, valor, igual=True):
    # igual=True cuenta las ordenes con ese valor, igual=False cuenta las que son distintas
    # Caso base que un nodo sin hijos cuenta 1 solo si es una orden que cumple la condicion
    # Caso recursivo es lo del nodo actual + lo de cada hijo
    total = 0
    if nodo.tipo == "orden" and (nodo.info.get(campo) == valor) == igual:
        total = 1
    for hijo in nodo.hijos:
        total += contar_ordenes(hijo, campo, valor, igual)
    return total

# Juntar los pendientes recursivamente (ordenes sin entregar y pagos pendientes)

def recopilar_pendientes(nodo, pendientes, cliente=""):
    # Caso base que un nodo sin hijos solo agrega algo si es una orden pendiente
    # Caso recursivo es recorrer cada hijo recordando de que cliente va
    if nodo.tipo == "cliente":
        cliente = f"{nodo.dato} {nodo.info.get('nombre')}"
    if nodo.tipo == "orden":
        if nodo.info.get("estado") != "Entregado":
            pendientes.append(f"{nodo.dato} ({cliente}): servicio {nodo.info.get('estado')}")
        if nodo.info.get("pago") == "No pagado":
            pendientes.append(f"{nodo.dato} ({cliente}): pago pendiente de ${nodo.info.get('valor')}")
    for hijo in nodo.hijos:
        recopilar_pendientes(hijo, pendientes, cliente)
    return pendientes

# Recorrido de preorden con recursividad

def preorden(nodo):
    # Preorden primero visita el nodo y despues sus hijos de izquierda a derecha
    # Caso base es el nodo sin hijos devuelve una lista con solo su dato
    # Caso recursivo es dato + el preorden de cada hijo
    resultado = [nodo.dato]
    for hijo in nodo.hijos:
        resultado = resultado + preorden(hijo)
    return resultado

# Recorrido de posorden con recursividad

def posorden(nodo):
    # Posorden primero visita los hijos y al final el nodo
    # Caso base es el nodo sin hijos devuelve una lista con solo su dato
    # Caso recursivo es el posorden de cada hijo + dato
    resultado = []
    for hijo in nodo.hijos:
        resultado = resultado + posorden(hijo)
    resultado.append(nodo.dato)
    return resultado

# Busqueda recursiva

def buscar(nodo, dato, tipo=None):
    # Devuelve el nodo si el dato existe en el arbol y None si no
    # Si se manda el tipo solo cuenta si el nodo es de ese tipo
    # Caso base 1 el dato del nodo actual es el buscado = devuelve el nodo
    # Caso base 2 el nodo no tiene mas hijos por revisar = None
    # Caso recursivo es buscar en cada hijo si alguno lo encuentra = devuelve ese nodo
    if nodo.dato == dato and (tipo is None or nodo.tipo == tipo):
        return nodo
    for hijo in nodo.hijos:
        encontrado = buscar(hijo, dato, tipo)
        if encontrado is not None:
            return encontrado
    return None

# Buscar el padre de un nodo

def buscar_padre(nodo, dato, tipo=None):
    # Caso base 1 alguno de los hijos del nodo actual es el buscado = devuelve el nodo actual
    # Caso base 2 el nodo no tiene hijos = None
    # Caso recursivo es buscar el padre dentro de cada hijo
    for hijo in nodo.hijos:
        if hijo.dato == dato and (tipo is None or hijo.tipo == tipo):
            return nodo
    for hijo in nodo.hijos:
        padre = buscar_padre(hijo, dato, tipo)
        if padre is not None:
            return padre
    return None

# Eliminar un nodo y su rama recursivamente

def eliminar(nodo, dato, tipo=None):
    # Elimina el nodo con ese dato y toda su rama buscandolo en todo el arbol
    # Devuelve cuantos nodos se eliminaron (0 si no lo encuentra)
    # Caso base 1 alguno de los hijos del nodo actual es el buscado se quita de la lista
    # Caso base 2 el nodo no tiene hijos entonces no hay nada que eliminar = 0
    # Caso recursivo es intentar eliminarlo dentro de cada hijo
    for hijo in nodo.hijos:
        if hijo.dato == dato and (tipo is None or hijo.tipo == tipo):
            cantidad = contar_nodos(hijo)
            nodo.hijos.remove(hijo)
            return cantidad
    for hijo in nodo.hijos:
        cantidad = eliminar(hijo, dato, tipo)
        if cantidad > 0:
            return cantidad
    return 0

# Guardar el arbol en archivo (una linea por nodo: nivel|tipo|dato|campos)

def info_a_texto(nodo):
    valores = []
    for campo in CAMPOS[nodo.tipo]:
        valores.append(str(nodo.info.get(campo, "")))
    return SEP_CAMPO.join(valores)

def arbol_a_lineas(nodo, nivel=0):
    # Caso base es el nodo sin hijos devuelve una lista con solo su linea
    # Caso recursivo es su linea + las lineas de cada hijo (en preorden)
    linea = f"{nivel}{SEP_ARBOL}{nodo.tipo}{SEP_ARBOL}{nodo.dato}{SEP_ARBOL}{info_a_texto(nodo)}"
    lineas = [linea]
    for hijo in nodo.hijos:
        lineas = lineas + arbol_a_lineas(hijo, nivel + 1)
    return lineas

def guardar_arbol(raiz, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        for linea in arbol_a_lineas(raiz):
            archivo.write(linea + "\n")

# Reconstruir el arbol desde el archivo

def cargar_arbol(ruta):
    # ultimo_por_nivel guarda el ultimo nodo leido en cada nivel
    # ese nodo es el padre de la siguiente linea que tenga un nivel mas
    raiz = None
    ultimo_por_nivel = []
    with open(ruta, "r", encoding="utf-8") as archivo:
        for numero, linea in enumerate(archivo, start=1):
            linea = linea.rstrip("\r\n")
            if linea.strip() == "":
                continue
            partes = linea.split(SEP_ARBOL)
            if len(partes) != 4:
                raise ValueError(f"Linea {numero}: formato incorrecto")
            nivel = int(partes[0])
            tipo = partes[1]
            dato = partes[2]
            if tipo not in CAMPOS:
                raise ValueError(f"Linea {numero}: tipo '{tipo}' no existe")
            valores = partes[3].split(SEP_CAMPO)
            info = {}
            for i, campo in enumerate(CAMPOS[tipo]):
                info[campo] = valores[i] if i < len(valores) else ""
            nodo = Nodo(dato, tipo, info)

            if nivel == 0:
                if raiz is not None:
                    raise ValueError(f"Linea {numero}: hay mas de una raiz")
                raiz = nodo
            else:
                if nivel > len(ultimo_por_nivel):
                    raise ValueError(f"Linea {numero}: el nivel {nivel} no tiene padre")
                insertar(ultimo_por_nivel[nivel - 1], nodo)

            # Se actualiza el ultimo nodo visto en este nivel
            del ultimo_por_nivel[nivel:]
            ultimo_por_nivel.append(nodo)
    if raiz is None:
        raise ValueError("El archivo esta vacio")
    return raiz

# Agregar una orden al arbol (crea el cliente si no existe)

def agregar_orden(raiz, id_cliente, nombre, telefono, prenda, cantidad,
                  servicio, fecha_entrada, fecha_salida, estado, valor, pago):
    cliente = buscar(raiz, id_cliente, "cliente")
    if cliente is None:
        cliente = insertar(raiz, Nodo(id_cliente, "cliente", {"nombre": nombre, "telefono": telefono}))
    # el numero de la orden es el siguiente que no este usado por ese cliente
    numero = len(cliente.hijos) + 1
    while buscar(cliente, f"Orden {id_cliente}-{numero}", "orden") is not None:
        numero += 1
    info = {"servicio": servicio, "fecha_entrada": fecha_entrada, "fecha_salida": fecha_salida,
            "estado": estado, "valor": valor, "pago": pago}
    orden = insertar(cliente, Nodo(f"Orden {id_cliente}-{numero}", "orden", info))
    insertar(orden, Nodo(prenda, "prenda", {"cantidad": cantidad}))
    return orden

# Conexion con el archivo del corte 1 (ordenes.txt)
# id,nombre,telefono,prenda,cantidad,servicio,fecha_entrada,fecha_salida,estado,valor,pago

def crear_archivo_ejemplo(ruta):
    # Si no existe el archivo de ordenes se crea con los datos de prueba del corte 1
    datos = [
        "101,Juan Perez,3001234567,Camisa,3,Lavado,16/09/2026,17/09/2026,Pendiente,15000,No pagado",
        "102,Maria Gonzalez,3012345678,Pantalon,2,Planchado,16/09/2026,18/09/2026,Entregado,10000,Pagado",
        "103,Carlos Ramirez,3023456789,Chaqueta,1,Lavaseco,15/09/2026,19/09/2026,En proceso,25000,No pagado",
        "104,Laura Martinez,3034567890,Vestido,2,Lavaseco,16/09/2026,20/09/2026,Entregado,40000,Pagado",
        "105,Andres Rodriguez,3045678901,Cobija,1,Lavado,14/09/2026,18/09/2026,Pendiente,30000,No pagado",
    ]
    with open(ruta, "w", encoding="utf-8") as archivo:
        for linea in datos:
            archivo.write(linea + "\n")

def cargar_ordenes_desde_archivo(raiz, ruta):
    # Lee cada linea del archivo y agrega la orden al arbol (crea el cliente si no existe)
    cargadas = 0
    if not os.path.exists(ruta):
        return 0
    with open(ruta, "r", encoding="utf-8") as archivo:
        for numero, linea in enumerate(archivo, start=1):
            linea = linea.strip()
            if linea == "":
                continue
            partes = linea.split(SEP_ORDENES)
            if len(partes) != 11:
                print(f"  Linea {numero} omitida: debe tener 11 campos")
                continue
            id_cliente, nombre, telefono, prenda, cantidad, servicio, f_entrada, f_salida, estado, valor, pago = partes
            if not cantidad.isdigit() or not valor.isdigit():
                print(f"  Linea {numero} omitida: cantidad y valor deben ser numeros")
                continue
            # en el archivo hay datos con mayusculas distintas (lavado, Lavado), se normalizan
            agregar_orden(raiz, id_cliente, nombre, telefono, prenda, int(cantidad),
                          servicio.capitalize(), f_entrada, f_salida,
                          estado.capitalize(), int(valor), pago.capitalize())
            cargadas += 1
    return cargadas

def recopilar_lineas_ordenes(nodo, lineas, cliente=None, orden=None):
    # Caso base que un nodo sin hijos agrega su linea solo si es una prenda
    # (una orden sin prendas no se exporta)
    # Caso recursivo es recorrer cada hijo recordando el cliente y la orden donde va
    if nodo.tipo == "cliente":
        cliente = nodo
    if nodo.tipo == "orden":
        orden = nodo
    if nodo.tipo == "prenda":
        o = orden.info
        lineas.append(SEP_ORDENES.join([cliente.dato, cliente.info["nombre"], cliente.info["telefono"],
                                        nodo.dato, str(nodo.info["cantidad"]), o["servicio"], o["fecha_entrada"],
                                        o["fecha_salida"], o["estado"], str(o["valor"]), o["pago"]]))
    for hijo in nodo.hijos:
        recopilar_lineas_ordenes(hijo, lineas, cliente, orden)
    return lineas

def guardar_ordenes_en_archivo(raiz, ruta):
    lineas = recopilar_lineas_ordenes(raiz, [])
    with open(ruta, "w", encoding="utf-8") as archivo:
        for linea in lineas:
            archivo.write(linea + "\n")
    return len(lineas)

# Funciones para pedir datos por consola

def limpiar(texto):
    # Quita los separadores para que no dañen los archivos
    return texto.replace(SEP_ARBOL, " ").replace(SEP_CAMPO, " ").replace(SEP_ORDENES, " ").strip()

def pedir_texto(mensaje):
    while True:
        texto = limpiar(input(mensaje))
        if texto != "":
            return texto
        print("  No puede estar vacio")

def pedir_entero(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto.isdigit() and int(texto) > 0:
            return int(texto)
        print("  Escribe un numero entero mayor que 0")

def pedir_fecha(mensaje):
    while True:
        texto = input(mensaje).strip()
        try:
            datetime.strptime(texto, "%d/%m/%Y")
            return texto
        except ValueError:
            print("  Usa el formato dd/mm/aaaa")

def pedir_de_lista(mensaje, opciones):
    # Muestra las opciones numeradas y devuelve la que elija el usuario
    print(f"  {mensaje}: " + "  ".join(f"{i + 1}) {o}" for i, o in enumerate(opciones)))
    while True:
        eleccion = input("  Opcion: ").strip()
        if eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones):
            return opciones[int(eleccion) - 1]
        print(f"  Escribe un numero entre 1 y {len(opciones)}")

def confirmar(mensaje):
    return input(mensaje + " (s/n): ").strip().lower() == "s"

# Opciones del menu

def opcion_registrar_orden(raiz):
    id_cliente = pedir_texto("ID del cliente (ej. 106): ")
    cliente = buscar(raiz, id_cliente, "cliente")
    if cliente is None:
        nombre = pedir_texto("Nombre: ")
        telefono = pedir_texto("Telefono: ")
    else:
        nombre, telefono = cliente.info["nombre"], cliente.info["telefono"]
        print(f"  Cliente existente: {nombre} ({telefono}), se agrega una nueva orden")
    prenda = pedir_texto("Prenda: ")
    cantidad = pedir_entero("Cantidad: ")
    servicio = pedir_de_lista("Servicio", SERVICIOS)
    fecha_entrada = pedir_fecha("Fecha entrada (dd/mm/aaaa): ")
    fecha_salida = pedir_fecha("Fecha salida (dd/mm/aaaa): ")
    estado = pedir_de_lista("Estado", ESTADOS)
    valor = pedir_entero("Valor: ")
    pago = pedir_de_lista("Pago", PAGOS)
    orden = agregar_orden(raiz, id_cliente, nombre, telefono, prenda, cantidad,
                          servicio, fecha_entrada, fecha_salida, estado, valor, pago)
    print(f"  Se guardo la {orden.dato}")

def opcion_agregar_prenda(raiz):
    dato = pedir_texto("Orden (ej. Orden 101-1): ")
    orden = buscar(raiz, dato, "orden")
    if orden is None:
        print("  No existe esa orden")
        return
    prenda = pedir_texto("Prenda: ")
    cantidad = pedir_entero("Cantidad: ")
    try:
        insertar(orden, Nodo(prenda, "prenda", {"cantidad": cantidad}))
        print("  Prenda agregada")
    except ValueError as error:
        print(f"  No se pudo agregar: {error}")

def opcion_actualizar(raiz, campo):
    # campo es "estado" o "pago"
    dato = pedir_texto("Orden (ej. Orden 101-1): ")
    orden = buscar(raiz, dato, "orden")
    if orden is None:
        print("  No existe esa orden")
        return
    opciones = ESTADOS if campo == "estado" else PAGOS
    print(f"  Valor actual de {campo}: {orden.info[campo]}")
    orden.info[campo] = pedir_de_lista(f"Nuevo {campo}", opciones)
    print("  Actualizado")

def opcion_dashboard(raiz):
    print(f"\n=== {raiz.dato.upper()} (resumen general) ===")
    print(f"  Total de clientes: {contar_por_tipo(raiz, 'cliente')}")
    print(f"  Total de ordenes: {contar_por_tipo(raiz, 'orden')}")
    print(f"  Total de prendas recibidas: {sumar_prendas(raiz)}")
    print(f"  Ordenes sin entregar: {contar_ordenes(raiz, 'estado', 'Entregado', False)}")
    print(f"  Pagos pendientes: {contar_ordenes(raiz, 'pago', 'No pagado')}")
    print(f"  Ingresos cobrados: ${sumar_valor(raiz, 'Pagado'):.0f}")
    print(f"  Por cobrar: ${sumar_valor(raiz, 'No pagado'):.0f}")
    print("  Ordenes por servicio:")
    for servicio in SERVICIOS:
        print(f"    - {servicio}: {contar_ordenes(raiz, 'servicio', servicio)}")

def opcion_pendientes(raiz):
    pendientes = recopilar_pendientes(raiz, [])
    print("  PENDIENTES:")
    if not pendientes:
        print("    (no hay pendientes)")
    for texto in pendientes:
        print(f"    * {texto}")

def opcion_buscar(raiz):
    dato = pedir_texto("Dato a buscar (id, orden o prenda): ")
    nodo = buscar(raiz, dato)
    if nodo is None:
        print(f"  '{dato}' NO existe en el arbol")
        return
    padre = buscar_padre(raiz, dato)
    print(f"  '{dato}' SI existe: {descripcion_nodo(nodo)}")
    if padre is not None:
        print(f"  Su padre es: {descripcion_nodo(padre)}")
    print(f"  Nodos en su rama: {contar_nodos(nodo)}")

def opcion_eliminar(raiz):
    print("  Que quieres eliminar: 1) Cliente  2) Orden  3) Prenda")
    tipos = {"1": "cliente", "2": "orden", "3": "prenda"}
    tipo = tipos.get(input("  Opcion: ").strip())
    if tipo is None:
        print("  Opcion no valida")
        return
    dato = pedir_texto(f"Dato del {tipo} a eliminar: ")
    nodo = buscar(raiz, dato, tipo)
    if nodo is None:
        print(f"  No existe ese {tipo}")
        return
    print(f"  Se eliminaran {contar_nodos(nodo)} nodo(s) (el nodo y toda su rama)")
    if confirmar("  Seguro que quieres continuar?"):
        print(f"  Eliminados: {eliminar(raiz, dato, tipo)} nodo(s)")
    else:
        print("  Eliminacion cancelada")

def opcion_recorridos(raiz):
    print("  Preorden: " + " -> ".join(preorden(raiz)))
    print("  Posorden: " + " -> ".join(posorden(raiz)))

def opcion_estadisticas(raiz):
    print(f"  Altura del arbol: {calcular_altura(raiz)}")
    print(f"  Total de nodos: {contar_nodos(raiz)}")
    print(f"  Total de hojas: {contar_hojas(raiz)}")
    print(f"  Clientes: {contar_por_tipo(raiz, 'cliente')} | Ordenes: {contar_por_tipo(raiz, 'orden')} | "
          f"Prendas: {contar_por_tipo(raiz, 'prenda')}")

# Pruebas automaticas (sirven de evidencia para el documento)

def construir_arbol_prueba():
    raiz = Nodo("Lavaseco Angiexpress", "negocio")
    agregar_orden(raiz, "101", "Juan Perez", "3001234567", "Camisa", 3, "Lavado",
                  "16/09/2026", "17/09/2026", "Pendiente", 15000, "No pagado")
    agregar_orden(raiz, "102", "Maria Gonzalez", "3012345678", "Pantalon", 2, "Planchado",
                  "16/09/2026", "18/09/2026", "Entregado", 10000, "Pagado")
    agregar_orden(raiz, "103", "Carlos Ramirez", "3023456789", "Chaqueta", 1, "Lavaseco",
                  "15/09/2026", "19/09/2026", "En proceso", 25000, "No pagado")
    return raiz

def probar(nombre, esperado, obtenido, resultados):
    estado = "OK" if esperado == obtenido else "FALLA"
    resultados.append(estado == "OK")
    print(f"  {nombre}")
    print(f"     esperado = {esperado}")
    print(f"     obtenido = {obtenido} -> {estado}")

def ejecutar_pruebas():
    print("\n=== PRUEBAS DEL ARBOL ===")
    resultados = []
    raiz = construir_arbol_prueba()
    orden = buscar(raiz, "Orden 103-1", "orden")

    # Caso 1 insertar un nodo
    insertar(orden, Nodo("Corbata", "prenda", {"cantidad": 1}))
    probar("1. Insertar la prenda Corbata en la Orden 103-1", True,
           buscar(orden, "Corbata", "prenda") is not None, resultados)

    # Caso 2 recorrer el arbol
    esperado = ["Lavaseco Angiexpress", "101", "Orden 101-1", "Camisa", "102", "Orden 102-1",
                "Pantalon", "103", "Orden 103-1", "Chaqueta", "Corbata"]
    probar("2. Recorrido en preorden", esperado, preorden(raiz), resultados)

    # Caso 3 altura, nodos y hojas
    probar("3. Altura, nodos y hojas", (3, 11, 4),
           (calcular_altura(raiz), contar_nodos(raiz), contar_hojas(raiz)), resultados)

    # Caso 4 y 5 busqueda
    probar("4. Buscar un dato que existe (Chaqueta)", True, buscar(raiz, "Chaqueta") is not None, resultados)
    probar("5. Buscar un dato que no existe (Zapatos)", False, buscar(raiz, "Zapatos") is not None, resultados)

    # Caso 6 eliminar un nodo con descendencia (el cliente 103 tiene una orden y dos prendas)
    eliminados = eliminar(raiz, "103", "cliente")
    probar("6. Eliminar el cliente 103 con toda su rama", (4, 7, False),
           (eliminados, contar_nodos(raiz), buscar(raiz, "Chaqueta") is not None), resultados)

    # Caso 7 guardar el arbol en archivo
    ruta = "prueba_arbol.txt"
    guardar_arbol(raiz, ruta)
    with open(ruta, "r", encoding="utf-8") as archivo:
        lineas = len([l for l in archivo if l.strip() != ""])
    probar("7. Guardar el arbol (una linea por nodo)", 7, lineas, resultados)

    # Caso 8 reconstruir el arbol desde el archivo
    cargado = cargar_arbol(ruta)
    probar("8. Reconstruir el arbol desde el archivo", (preorden(raiz), calcular_altura(raiz)),
           (preorden(cargado), calcular_altura(cargado)), resultados)
    os.remove(ruta)

    print(f"\n  Pruebas correctas: {sum(resultados)} de {len(resultados)}")

# Menu principal

def mostrar_menu():
    print("\n===== LAVASECO ANGIEXPRESS =====")
    print(" 1. Ver el arbol completo")
    print(" 2. Resumen del negocio (dashboard)")
    print(" 3. Registrar orden")
    print(" 4. Agregar prenda a una orden")
    print(" 5. Buscar un dato")
    print(" 6. Actualizar estado de una orden")
    print(" 7. Actualizar pago de una orden")
    print(" 8. Eliminar cliente, orden o prenda")
    print(" 9. Pendientes (sin entregar y por cobrar)")
    print("10. Recorridos (preorden y posorden)")
    print("11. Altura, nodos y hojas")
    print("12. Guardar el arbol en archivo")
    print("13. Cargar el arbol desde archivo")
    print("14. Exportar ordenes a ordenes.txt")
    print("15. Ejecutar pruebas")
    print(" 0. Salir")

def iniciar_arbol():
    # Si ya hay un arbol guardado se carga, si no se arma desde ordenes.txt del corte 1
    if os.path.exists(ARCHIVO_ARBOL):
        try:
            raiz = cargar_arbol(ARCHIVO_ARBOL)
            print(f"Arbol cargado desde {ARCHIVO_ARBOL}")
            return raiz
        except (ValueError, OSError) as error:
            print(f"No se pudo leer {ARCHIVO_ARBOL}: {error}")
    if not os.path.exists(ARCHIVO_ORDENES):
        crear_archivo_ejemplo(ARCHIVO_ORDENES)
        print(f"Se creo {ARCHIVO_ORDENES} con datos de ejemplo")
    raiz = Nodo("Lavaseco Angiexpress", "negocio")
    cantidad = cargar_ordenes_desde_archivo(raiz, ARCHIVO_ORDENES)
    print(f"Arbol construido con {cantidad} ordenes del archivo")
    return raiz

def main():
    if "--pruebas" in sys.argv:
        ejecutar_pruebas()
        return
    raiz = iniciar_arbol()
    while True:
        mostrar_menu()
        opcion = input("Elige una opcion: ").strip()
        print()
        if opcion == "1":
            mostrar_arbol(raiz)
        elif opcion == "2":
            opcion_dashboard(raiz)
        elif opcion == "3":
            opcion_registrar_orden(raiz)
        elif opcion == "4":
            opcion_agregar_prenda(raiz)
        elif opcion == "5":
            opcion_buscar(raiz)
        elif opcion == "6":
            opcion_actualizar(raiz, "estado")
        elif opcion == "7":
            opcion_actualizar(raiz, "pago")
        elif opcion == "8":
            opcion_eliminar(raiz)
        elif opcion == "9":
            opcion_pendientes(raiz)
        elif opcion == "10":
            opcion_recorridos(raiz)
        elif opcion == "11":
            opcion_estadisticas(raiz)
        elif opcion == "12":
            guardar_arbol(raiz, ARCHIVO_ARBOL)
            print(f"  Arbol guardado en {ARCHIVO_ARBOL}")
        elif opcion == "13":
            try:
                raiz = cargar_arbol(ARCHIVO_ARBOL)
                print(f"  Arbol cargado desde {ARCHIVO_ARBOL}")
            except (OSError, ValueError) as error:
                print(f"  No se pudo cargar: {error}")
        elif opcion == "14":
            cantidad = guardar_ordenes_en_archivo(raiz, ARCHIVO_ORDENES)
            print(f"  {cantidad} lineas guardadas en {ARCHIVO_ORDENES}")
        elif opcion == "15":
            ejecutar_pruebas()
        elif opcion == "0":
            if confirmar("Quieres guardar el arbol antes de salir?"):
                guardar_arbol(raiz, ARCHIVO_ARBOL)
                print(f"  Arbol guardado en {ARCHIVO_ARBOL}")
            print("Hasta luego")
            break
        else:
            print("Opcion no valida")

if __name__ == "__main__":
    main()
