#Implementar la funcion de creacion
def agregar_tarea(id, tarea, materia,fecha_limite,estado):
    with open("tareas.txt", "a",encoding="utf-8") as archivo:
        linea = f"{id},{tarea},{materia},{fecha_limite},{estado}\n"
        archivo.write(linea)

#Datos de prueba
agregar_tarea(1, "entregar informe de laboratorio", "estructura de datos II", "2026-08-20", "Pendiente")
agregar_tarea(2, "entregar informe de aula", "estructura de datos II", "2026-08-20", "Pendiente")
agregar_tarea(3, "entregar documento", "estructura de datos II", "2026-08-20", "Pendiente")


#Implementar la funcion de lectura
def listar_tareas():
    with open("tareas.txt", "r",encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.strip().split(",")
            print(campos)

listar_tareas()


#Implementar la funcion de actualizar
def actualizar_estado(id_buscado,nuevo_estado):
    lineas_nuevas = []
    with open("tareas.txt","r",encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.strip().split(",")
            if campos[0] == str(id_buscado):
                campos[4] = nuevo_estado
                lineas_nuevas.append(",".join(campos))

    with open("tareas.txt","w",encoding="utf-8") as archivo:
        for linea in lineas_nuevas:
            archivo.write(linea + "\n")

actualizar_estado(2, "Completada")


#Implementar la funcion de eliminar
def eliminar_tarea(id_buscado):
    lineas_nuevas = []
    with open("tareas.txt","r",encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.strip().split(",")
            if campos[0] != str(id_buscado):
                lineas_nuevas.append(linea.strip())

    with open("tareas.txt","w",encoding="utf-8") as archivo:
        for linea in lineas_nuevas:
            archivo.write(linea + "\n")

eliminar_tarea(1)