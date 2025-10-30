# Importo librerias
from collections import deque
import random

# Constantes del terreno
CAMINO_LIBRE = 0
EDIFICIO = 1
AGUA = 2
ZONA_BLOQUEADA = 3

# Funciones del mapa
def crear_mapa_vacio(cantidad_filas, cantidad_columnas, valor_relleno=CAMINO_LIBRE):
    "Crea y devuelve una matriz de tamaño filas x columnas con un valor inicial"

    return [[valor_relleno for _ in range(cantidad_columnas)] for _ in range(cantidad_filas)]

def generar_obstaculos_aleatorios(mapa, probabilidad_edificio=0.15, probabilidad_agua=0.10, probabilidad_bloqueo=0.05):
    "Llena el mapa con obstáculos aleatorios según las probabilidades dadas"

    total_filas = len(mapa)
    total_columnas = len(mapa[0])

    for indice_fila in range(total_filas):
        for indice_columna in range(total_columnas):
            numero_aleatorio = random.random()
            if numero_aleatorio < probabilidad_edificio: 
                mapa[indice_fila][indice_columna] = EDIFICIO
            elif numero_aleatorio < probabilidad_edificio + probabilidad_agua:
                mapa[indice_fila][indice_columna] = AGUA
            elif numero_aleatorio < probabilidad_edificio + probabilidad_agua + probabilidad_bloqueo:
                mapa[indice_fila][indice_columna] = ZONA_BLOQUEADA
            else:
                mapa[indice_fila][indice_columna] = CAMINO_LIBRE

def redimensionar_mapa(mapa, nuevas_filas, nuevas_columnas, valor_relleno=CAMINO_LIBRE):
    "Devuelve un nuevo mapa con las dimensiones especificadas"

    filas_actuales = len(mapa)
    columnas_actuales = len(mapa[0])
    nuevo_mapa = crear_mapa_vacio(nuevas_filas, nuevas_columnas, valor_relleno)

    for indice_fila in range(min(filas_actuales, nuevas_filas)):
        "copia el contenido del mapa viejo al nuevo sin pasarse de los límites"

        for indice_columna in range(min(columnas_actuales, nuevas_columnas)):
            nuevo_mapa[indice_fila][indice_columna] = mapa[indice_fila][indice_columna]

    return nuevo_mapa

def cargar_mapa_desde_archivo(ruta_archivo):
    "Carga un mapa desde un archivo de texto"

    mapa = []
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            linea = linea.strip()
            "Quita los espacios o saltos de línea al principio y al final de la línea"

            if not linea or linea.startswith('#'):
                "Si la línea está vacía o empieza con “#” se salta"

                continue
            linea = linea.replace(',', ' ')
            "reemplaza las , por espacios"

            fila = [int(valor) for valor in linea.split()]
            "Divide la línea en partes usando los espacios y convierte cada parte en número entero"

            mapa.append(fila)
            "Agrega esa fila a la lista principal del mapa"

    if not mapa:
        raise ValueError("El archivo de mapa está vacío o no contiene filas válidas")
    "Si no se leyó nada, el programa lanza un error con este mensaje"

    cantidad_columnas = len(mapa[0])
    for fila in mapa:
        if len(fila) != cantidad_columnas:
            raise ValueError("Las filas del mapa tienen diferente número de columnas")
        "Verifica que todas las filas tengan el mismo tamaño"

    return mapa

def guardar_mapa_en_archivo(mapa, ruta_archivo):
    "Guarda el mapa actual en un archivo"

    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        "Abre el archivo en modo escritura, si existe lo sobrescribe y si no, lo crea"

        for fila in mapa:
            "recorre fila por fila"

            archivo.write(' '.join(str(valor) for valor in fila) + '\n')
            "Escribe la fila en el archivo y salta de línea"

# Visualisacion del mapa
def imprimir_mapa(mapa, ruta_camino=None, posicion_inicio=None, posicion_destino=None, modo_detallado=False):
    "Imprime el mapa con símbolos más legibles."

    cantidad_filas = len(mapa)
    cantidad_columnas = len(mapa[0])
    conjunto_ruta = set(ruta_camino) if ruta_camino else set()

    for indice_fila in range(cantidad_filas):
        linea = []
        for indice_columna in range(cantidad_columnas):
            coordenada_actual = (indice_fila, indice_columna)
            if coordenada_actual == posicion_inicio:
                simbolo = 'I'
            elif coordenada_actual == posicion_destino:
                simbolo = 'D'
            elif coordenada_actual in conjunto_ruta:
                simbolo = '*'
            else:
                valor = mapa[indice_fila][indice_columna]
                if valor == CAMINO_LIBRE:
                    simbolo = '.'
                elif valor == EDIFICIO:
                    simbolo = 'X'
                elif valor == AGUA:
                    simbolo = '~' if modo_detallado else 'X'
                elif valor == ZONA_BLOQUEADA:
                    simbolo = 'T' if modo_detallado else 'X'
                else:
                    simbolo = '?'
            linea.append(simbolo)
        print(' '.join(linea))
    print()

# Validaciones
def esta_dentro_de_limites(mapa, coordenada):
    fila, columna = coordenada
    return 0 <= fila < len(mapa) and 0 <= columna < len(mapa[0])

def es_celda_transitable(mapa, coordenada, permitir_agua=False):
    fila, columna = coordenada
    valor = mapa[fila][columna]
    if valor == CAMINO_LIBRE:
        return True
    if valor == AGUA:
        return permitir_agua
    return False

# Algoritmo de busqueda bfs
def busqueda_por_anchura(mapa, coordenada_inicio, coordenada_destino, permitir_agua=False):
    "Busca una ruta entre inicio y destino usando el algoritmo BFS (anchura)."

    if not (esta_dentro_de_limites(mapa, coordenada_inicio) and esta_dentro_de_limites(mapa, coordenada_destino)):
        return None
    "verifica que inicio y destino este dentro de los limites"

    valor_inicio = mapa[coordenada_inicio[0]][coordenada_inicio[1]]
    valor_destino = mapa[coordenada_destino[0]][coordenada_destino[1]]
    "permite saber que hay dentro de las posiciones de esas coordenadas"

    if valor_inicio in (EDIFICIO, AGUA, ZONA_BLOQUEADA) or valor_destino in (EDIFICIO, AGUA, ZONA_BLOQUEADA):
        return None
    "verifica q el inicio y destino sean validos (si es 0 es camino libre y si es 1 es camino bloqueado)"

    total_filas, total_columnas = len(mapa), len(mapa[0])
    "guarda cuantas filas y columnas tiene el mapa"

    visitado = [[False] * total_columnas for _ in range(total_filas)]
    "guarda qué celdas ya fueron visitadas (evita repetir)"

    previo = [[None] * total_columnas for _ in range(total_filas)]
    "guarda de dónde venimos al llegar a una celda, para poder reconstruir el camino al final"

    cola = deque([coordenada_inicio])
    "crea una cola de dos extremos"

    visitado[coordenada_inicio[0]][coordenada_inicio[1]] = True
    "marca la celda inicial como visitada"

    direcciones_movimiento = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    "son las direcciones (arriba, abajo, izquierda, derecha)"

    while cola:
        "mientras la cola este vacia continua explorando"

        fila_actual, columna_actual = cola.popleft()
        "saca el primer elemento de la cola"

        if (fila_actual, columna_actual) == coordenada_destino:
            break
        "verifica si llegamos al destino"
        for desplazamiento_fila, desplazamiento_columna in direcciones_movimiento:
            "recorre las cuatro direcciones"

            nueva_fila = fila_actual + desplazamiento_fila
            nueva_columna = columna_actual + desplazamiento_columna
            "suma el movimiento a las posiciones actuales para tener las nuevas posiciones"

            if 0 <= nueva_fila < total_filas and 0 <= nueva_columna < total_columnas and not visitado[nueva_fila][nueva_columna]:
                "comprueba si la nueva posicion es valida"

                valor = mapa[nueva_fila][nueva_columna]
                if valor in (EDIFICIO, ZONA_BLOQUEADA):
                    continue
                "si es edificio o zona bloqueada no pasa por ahi"

                if valor == AGUA and not permitir_agua:
                    continue
                "si es agua pero no esta permitido pasar por agua, no pasa por ahi"

                visitado[nueva_fila][nueva_columna] = True
                previo[nueva_fila][nueva_columna] = (fila_actual, columna_actual)
                cola.append((nueva_fila, nueva_columna))
                "marco la celda como visitado, guarda la celda anterior y agrega a la cola"

    if not visitado[coordenada_destino[0]][coordenada_destino[1]]:
        return None
    "Si el destino nunca fue visitado, significa que no hay ruta posible"

    ruta = []
    posicion_actual = coordenada_destino
    while posicion_actual:
        ruta.append(posicion_actual)
        posicion_actual = previo[posicion_actual[0]][posicion_actual[1]]
    ruta.reverse()
    "reconstruye la ruta desde destino hasta inicio y agrega cada celda recorrida y dps lo invierte"
    return ruta

def encontrar_mejor_ruta(mapa, coordenada_inicio, coordenada_destino):
    "Intenta encontrar una ruta primero por tierra, y si no puede, por agua."

    ruta_por_tierra = busqueda_por_anchura(mapa, coordenada_inicio, coordenada_destino, permitir_agua=False)
    "llama a la funcion bfs para buscar por tierra"

    if ruta_por_tierra:
        return ruta_por_tierra, 'tierra'
    "si encontro la ruta devuelve la posicion y la palabra tierra"

    ruta_por_agua = busqueda_por_anchura(mapa, coordenada_inicio, coordenada_destino, permitir_agua=True)
    "hace lo mismo pero ahora busca por el agua"

    if ruta_por_agua:
        return ruta_por_agua, 'agua'
    "si encontro ruta por agua devuele la posicikon y la palabra agua"

    return None, None 
"si no hay camino posible"

# Bucle interactivo
def bucle_interactivo(mapa):
    posicion_inicio = None
    posicion_destino = None
    modo_detallado = False
    ultima_ruta = None

    print("Calculadora de rutas. Escribe 'ayuda' para ver los comandos.")

    while True:
        try:
            entrada_usuario = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo.")
            break
        "Si ocurre un error o interrupción el programa no se bloquea ni muestra un error, solo rompe el bucle"

        if not entrada_usuario:
            continue
        "si el usuario no escribe nada y presiona enter vuelve a pedir otro comando"

        partes_comando = entrada_usuario.split()
        comando = partes_comando[0].lower()
        "Divide el texto que escribió el usuario en partes (palabras separadas por espacios)"

        if comando in ('salir', 'exit', 'q'):
            print("Adiós.")
            break
        "Si el usuario escribió “salir”, “exit” o “q”, el programa se despide y rompe el bucle"

        if comando == 'ayuda':
            print("""Comandos disponibles:
 mostrar                       - dibuja el mapa actual
 inicio fila columna           - fija punto de inicio
 destino fila columna          - fija punto destino
 buscar                        - calcula la ruta (tierra primero, luego agua)
 agregar fila columna tipo     - pone tipo en la celda (0,1,2,3)
 quitar fila columna           - pone 0 en la celda
 redimensionar filas columnas  - cambia el tamaño del mapa
 cargar nombre_archivo         - carga mapa desde archivo
 guardar nombre_archivo        - guarda mapa en archivo
 alternar detallado            - muestra símbolos de agua y bloqueos
 salir                         - salir del programa
""")
            continue

        # Mostrar mapa
        if comando == 'mostrar':
            imprimir_mapa(mapa, ruta_camino=ultima_ruta, posicion_inicio=posicion_inicio, posicion_destino=posicion_destino, modo_detallado=modo_detallado)
            continue

        # Redimensionar mapa
        if comando == 'redimensionar' and len(partes_comando) >= 3:
            "revisa que el usuario haya puesto al menos 3 palabras"

            try:
                nuevas_filas = int(partes_comando[1])
                nuevas_columnas = int(partes_comando[2])
                "Convierte las palabras escritas por el usuario a números enteros"

                if nuevas_filas <= 0 or nuevas_columnas <= 0:
                    "Se asegura de que las dimensiones sean mayores que cero"
                    print("Tamaño inválido.")
                    continue

                mapa[:] = redimensionar_mapa(mapa, nuevas_filas, nuevas_columnas)
                "Crea un nuevo mapa con las medidas nuevas, copia las partes del mapa anterior y reemplaza el contenido de mapa con el nuevo"

                generar_obstaculos_aleatorios(mapa)
                "Después de crear el nuevo mapa, se llenan algunas celdas al azar con obstáculos"
                print(f"Mapa redimensionado a {nuevas_filas}x{nuevas_columnas} con obstáculos aleatorios.")

            except ValueError:
                "Si dentro del bloque try ocurre un error se atrapa el error con except y muestra un mensaje"
                print("Uso: redimensionar filas columnas (por ejemplo: redimensionar 15 20)")
            continue

        # Fijar inicio
        if comando == 'inicio' and len(partes_comando) >= 3:
            "Comprueba si el usuario escribió el comando y si se puso dos números"

            fila, columna = int(partes_comando[1]), int(partes_comando[2])
            "Convierte los valores de texto a números enteros"

            if not esta_dentro_de_limites(mapa, (fila, columna)):
                print("Fuera del mapa.")
                continue

            if mapa[fila][columna] in (EDIFICIO, AGUA, ZONA_BLOQUEADA):
                print("No se puede colocar inicio sobre un obstáculo.")
                continue

            posicion_inicio = (fila, columna)
            print("Inicio fijado en", posicion_inicio)
            continue

        # Fijar destino
        if comando == 'destino' and len(partes_comando) >= 3:
            "Comprueba si el usuario escribió el comando y si se puso dos números"

            fila, columna = int(partes_comando[1]), int(partes_comando[2])
            "Convierte los valores de texto a números enteros"

            if not esta_dentro_de_limites(mapa, (fila, columna)):
                print("Fuera del mapa.")
                continue

            if mapa[fila][columna] in (EDIFICIO, AGUA, ZONA_BLOQUEADA):
                print("No se puede colocar destino sobre un obstáculo.")
                continue

            posicion_destino = (fila, columna)
            print("Destino fijado en", posicion_destino)
            continue

         # Alternar modo detallado
        if comando == 'alternar' and len(partes_comando) >= 2 and partes_comando[1] == 'detallado':
            modo_detallado = not modo_detallado
            print("Modo detallado =", modo_detallado)
            continue

        # Buscar ruta
        if comando == 'buscar':
            if posicion_inicio is None or posicion_destino is None:
                print("Define primero inicio y destino.")
                continue

            ruta, tipo = encontrar_mejor_ruta(mapa, posicion_inicio, posicion_destino)
            if ruta:
                ultima_ruta = ruta
                print(f"Ruta encontrada (modo: {tipo}). Pasos: {len(ruta) - 1}")
                imprimir_mapa(mapa, ruta_camino=ruta, posicion_inicio=posicion_inicio, posicion_destino=posicion_destino, modo_detallado=modo_detallado)
            

            else:
                ultima_ruta = None
                print("No hay ruta posible.")
            continue

        print("Comando desconocido. Escribe 'ayuda' para ver los comandos.")

# Programa principal
if __name__ == "__main__":
    random.seed()
    mapa_inicial = crear_mapa_vacio(10, 10)
    generar_obstaculos_aleatorios(mapa_inicial)
    print("Mapa de ejemplo con obstáculos aleatorios generado. Usa 'ayuda' para ver comandos.")
    bucle_interactivo(mapa_inicial)
