# Calculadora de rutas (CLI) con BFS y obstáculos aleatorios

from collections import deque
import sys
import random

# Constantes de tipo de terreno
CAMINO_LIBRE = 0
EDIFICIO = 1
AGUA = 2
ZONA_BLOQUEADA = 3

# ---------------------------
# FUNCIONES DE MAPA
# ---------------------------

def crear_mapa_vacio(numero_filas, numero_columnas, valor_relleno=CAMINO_LIBRE):
    """Devuelve una matriz con 'numero_filas' filas y 'numero_columnas' columnas"""
    return [[valor_relleno for _ in range(numero_columnas)] for _ in range(numero_filas)]

def generar_obstaculos_aleatorios(mapa, prob_edificio=0.15, prob_agua=0.10, prob_bloqueo=0.05):
    """
    Llena el mapa con obstáculos aleatorios según las probabilidades dadas.
    """
    filas = len(mapa)
    columnas = len(mapa[0])
    for i in range(filas):
        for j in range(columnas):
            rnd = random.random()
            if rnd < prob_edificio:
                mapa[i][j] = EDIFICIO
            elif rnd < prob_edificio + prob_agua:
                mapa[i][j] = AGUA
            elif rnd < prob_edificio + prob_agua + prob_bloqueo:
                mapa[i][j] = ZONA_BLOQUEADA
            else:
                mapa[i][j] = CAMINO_LIBRE

def tamaño_mapa(mapa, nuevas_filas, nuevas_columnas, valor_relleno=CAMINO_LIBRE):
    """
    Devuelve un nuevo mapa con las dimensiones especificadas.
    Si el nuevo tamaño es mayor, se rellenan las celdas adicionales con 'valor_relleno'.
    Si es menor, se recortan las filas/columnas que sobren.
    """
    filas_actuales = len(mapa)
    columnas_actuales = len(mapa[0])
    nuevo_mapa = crear_mapa_vacio(nuevas_filas, nuevas_columnas, valor_relleno)

    for i in range(min(filas_actuales, nuevas_filas)):
        for j in range(min(columnas_actuales, nuevas_columnas)):
            nuevo_mapa[i][j] = mapa[i][j]

    return nuevo_mapa

def cargar_mapa_desde_archivo(ruta_archivo):
    """Carga un mapa desde un archivo de texto"""
    mapa = []
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith('#'):
                continue
            linea = linea.replace(',', ' ')
            fila = [int(token) for token in linea.split()]
            mapa.append(fila)
    if not mapa:
        raise ValueError("El archivo de mapa está vacío o no contiene filas válidas.")
    columnas = len(mapa[0])
    for fila in mapa:
        if len(fila) != columnas:
            raise ValueError("Las filas del mapa tienen diferente número de columnas.")
    return mapa

def guardar_mapa_en_archivo(mapa, ruta_archivo):
    """Guarda el mapa actual en un archivo"""
    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        for fila in mapa:
            archivo.write(' '.join(str(valor) for valor in fila) + '\n')

# ---------------------------
# VISUALIZACIÓN
# ---------------------------

def imprimir_mapa(mapa, ruta_camino=None, posicion_inicio=None, posicion_destino=None, modo_detallado=False):
    """Imprime el mapa con símbolos más legibles"""
    filas = len(mapa)
    columnas = len(mapa[0])
    conjunto_ruta = set(ruta_camino) if ruta_camino else set()
    for f in range(filas):
        linea = []
        for c in range(columnas):
            coord = (f, c)
            if posicion_inicio == coord:
                simbolo = 'I'
            elif posicion_destino == coord:
                simbolo = 'D'
            elif coord in conjunto_ruta:
                simbolo = '*'
            else:
                valor = mapa[f][c]
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

# ---------------------------
# VALIDACIONES
# ---------------------------

def esta_dentro_de_limites(mapa, coord):
    fila, col = coord
    return 0 <= fila < len(mapa) and 0 <= col < len(mapa[0])

def es_celda_transitable(mapa, coord, permitir_agua=False):
    fila, col = coord
    valor = mapa[fila][col]
    if valor == CAMINO_LIBRE:
        return True
    if valor == AGUA:
        return permitir_agua
    return False

# ---------------------------
# BFS Y RUTAS
# ---------------------------

def bfs_busqueda(mapa, inicio, destino, permitir_agua=False):
    """Busca una ruta entre inicio y destino usando BFS"""
    if not (esta_dentro_de_limites(mapa, inicio) and esta_dentro_de_limites(mapa, destino)):
        return None

    valor_i = mapa[inicio[0]][inicio[1]]
    valor_d = mapa[destino[0]][destino[1]]
    if valor_i in (EDIFICIO, AGUA, ZONA_BLOQUEADA) or valor_d in (EDIFICIO, AGUA, ZONA_BLOQUEADA):
        return None

    filas, columnas = len(mapa), len(mapa[0])
    visitado = [[False]*columnas for _ in range(filas)]
    previo = [[None]*columnas for _ in range(filas)]
    cola = deque([inicio])
    visitado[inicio[0]][inicio[1]] = True

    movimientos = [(1,0),(-1,0),(0,1),(0,-1)]

    while cola:
        f, c = cola.popleft()
        if (f, c) == destino:
            break
        for df, dc in movimientos:
            nf, nc = f+df, c+dc
            if 0 <= nf < filas and 0 <= nc < columnas and not visitado[nf][nc]:
                valor = mapa[nf][nc]
                if valor in (EDIFICIO, ZONA_BLOQUEADA):
                    continue
                if valor == AGUA and not permitir_agua:
                    continue
                visitado[nf][nc] = True
                previo[nf][nc] = (f, c)
                cola.append((nf, nc))

    if not visitado[destino[0]][destino[1]]:
        return None

    ruta = []
    actual = destino
    while actual:
        ruta.append(actual)
        actual = previo[actual[0]][actual[1]]
    ruta.reverse()
    return ruta

def encontrar_mejor_ruta_con_alternativas(mapa, inicio, destino):
    ruta_tierra = bfs_busqueda(mapa, inicio, destino, permitir_agua=False)
    if ruta_tierra:
        return ruta_tierra, 'tierra'
    ruta_agua = bfs_busqueda(mapa, inicio, destino, permitir_agua=True)
    if ruta_agua:
        return ruta_agua, 'agua'
    return None, None

# ---------------------------
# BUCLE INTERACTIVO
# ---------------------------

def bucle_interactivo(mapa):
    posicion_inicio = None
    posicion_destino = None
    modo_detallado = False
    ultima_ruta = None

    print("Calculadora de rutas CLI. Escribe 'ayuda' para ver los comandos.")
    while True:
        try:
            entrada = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo.")
            break

        if not entrada:
            continue

        partes = entrada.split()
        comando = partes[0].lower()

        if comando in ('salir', 'exit', 'q'):
            print("Adiós.")
            break

        if comando == 'ayuda':
            print("""Comandos disponibles:
 mostrar                       - dibuja el mapa actual
 inicio fila columna           - fija punto de inicio
 destino fila columna          - fija punto destino
 buscar                        - calcula la ruta (tierra primero, luego agua)
 agregar fila columna tipo     - pone tipo en la celda (0,1,2,3)
 quitar fila columna           - pone 0 en la celda
 redimensionar filas columnas  - cambia el tamaño del mapa (con obstáculos aleatorios)
 cargar nombre_archivo         - carga mapa desde archivo
 guardar nombre_archivo        - guarda mapa en archivo
 alternar detallado            - muestra agua y bloqueos con símbolos
 salir                         - salir del programa
""")
            continue

        if comando == 'mostrar':
            imprimir_mapa(mapa, ruta_camino=ultima_ruta, posicion_inicio=posicion_inicio, posicion_destino=posicion_destino, modo_detallado=modo_detallado)
            continue

        if comando == 'tamanho' and len(partes) >= 3:
            try:
                nuevas_filas = int(partes[1])
                nuevas_columnas = int(partes[2])
                if nuevas_filas <= 0 or nuevas_columnas <= 0:
                    print("tamaño inválido.")
                    continue
                confirmar = 's'
                if nuevas_filas < len(mapa) or nuevas_columnas < len(mapa[0]):
                    confirmar = input("⚠️ El nuevo tamaño es menor y se perderán datos. ¿Continuar? (s/n): ").strip().lower()
                if confirmar == 's':
                    mapa[:] = tamaño_mapa(mapa, nuevas_filas, nuevas_columnas)
                    generar_obstaculos_aleatorios(mapa)
                    print(f"Mapa redimensionado a {nuevas_filas}x{nuevas_columnas} con obstáculos aleatorios.")
                else:
                    print("Operación cancelada.")
            except ValueError:
                print("Uso: redimensionar filas columnas (por ejemplo: redimensionar 15 20)")
            continue

        if comando == 'inicio' and len(partes) >= 3:
            f, c = int(partes[1]), int(partes[2])
            if not esta_dentro_de_limites(mapa, (f,c)):
                print("Fuera del mapa.")
                continue
            if mapa[f][c] in (EDIFICIO, AGUA, ZONA_BLOQUEADA):
                print("No se puede colocar inicio sobre un obstáculo.")
                continue
            posicion_inicio = (f,c)
            print("Inicio fijado en", posicion_inicio)
            continue

        if comando == 'destino' and len(partes) >= 3:
            f, c = int(partes[1]), int(partes[2])
            if not esta_dentro_de_limites(mapa, (f,c)):
                print("Fuera del mapa.")
                continue
            if mapa[f][c] in (EDIFICIO, AGUA, ZONA_BLOQUEADA):
                print("No se puede colocar destino sobre un obstáculo.")
                continue
            posicion_destino = (f,c)
            print("Destino fijado en", posicion_destino)
            continue

        if comando == 'buscar':
            if posicion_inicio is None or posicion_destino is None:
                print("Define primero inicio y destino.")
                continue
            ruta, modo = encontrar_mejor_ruta_con_alternativas(mapa, posicion_inicio, posicion_destino)
            if ruta:
                ultima_ruta = ruta
                print(f"Ruta encontrada (modo: {modo}). Pasos: {len(ruta)-1}")
                imprimir_mapa(mapa, ruta_camino=ruta, posicion_inicio=posicion_inicio, posicion_destino=posicion_destino, modo_detallado=modo_detallado)
            else:
                ultima_ruta = None
                print("No hay ruta posible.")
            continue

        if comando == 'agregar' and len(partes) >= 4:
            f, c, tipo = int(partes[1]), int(partes[2]), int(partes[3])
            if not esta_dentro_de_limites(mapa, (f,c)):
                print("Fuera del mapa.")
                continue
            if tipo not in (0,1,2,3):
                print("Tipo inválido.")
                continue
            mapa[f][c] = tipo
            print(f"Celda {(f,c)} modificada a tipo {tipo}.")
            continue

        if comando == 'quitar' and len(partes) >= 3:
            f, c = int(partes[1]), int(partes[2])
            if not esta_dentro_de_limites(mapa, (f,c)):
                print("Fuera del mapa.")
                continue
            mapa[f][c] = CAMINO_LIBRE
            print(f"Celda {(f,c)} liberada.")
            continue

        if comando == 'cargar' and len(partes) >= 2:
            nombre = ' '.join(partes[1:])
            try:
                mapa[:] = cargar_mapa_desde_archivo(nombre)
                print("Mapa cargado desde", nombre)
            except Exception as e:
                print("Error:", e)
            continue

        if comando == 'guardar' and len(partes) >= 2:
            nombre = ' '.join(partes[1:])
            try:
                guardar_mapa_en_archivo(mapa, nombre)
                print("Mapa guardado en", nombre)
            except Exception as e:
                print("Error:", e)
            continue

        if comando == 'alternar' and len(partes) >= 2 and partes[1] == 'detallado':
            modo_detallado = not modo_detallado
            print("modo_detallado =", modo_detallado)
            continue

        print("Comando desconocido. Escribe 'ayuda' para ver los comandos.")

# ---------------------------
# PROGRAMA PRINCIPAL
# ---------------------------

if __name__ == '__main__':
    random.seed()  # Semilla aleatoria
    mapa_ejemplo = crear_mapa_vacio(10, 10)
    generar_obstaculos_aleatorios(mapa_ejemplo)
    print("Mapa de ejemplo con obstáculos aleatorios generado. Usa 'ayuda' para ver comandos.")
    bucle_interactivo(mapa_ejemplo)
