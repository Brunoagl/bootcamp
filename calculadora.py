# Calculadora de rutas (CLI) con BFS y alternativas por agua

# Importaciones
from collections import deque              # deque: cola eficiente para BFS
import sys                                 # sys: utilidades del sistema 

# Constantes de tipo de terreno
CAMINO_LIBRE = 0                          # 0: camino libre (se puede transitar)
EDIFICIO = 1                              # 1: edificio (obstáculo permanente)
AGUA = 2                                  # 2: agua (obstáculo que puede usarse como alternativa)
ZONA_BLOQUEADA = 3                        # 3: zona bloqueada temporal (obstáculo)

# Funciones para crear, cargar y guardar mapas

def crear_mapa_vacio(numero_filas, numero_columnas, valor_relleno=CAMINO_LIBRE):
    # Devuelve una matriz con 'numero_filas' filas y 'numero_columnas' columnas
    return [[valor_relleno for _ in range(numero_columnas)] for _ in range(numero_filas)]

def cargar_mapa_desde_archivo(ruta_archivo):
    # Lee un archivo de texto donde cada línea representa una fila de números separados por espacios o comas
    mapa = []                                       # lista que contendrá las filas
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            linea = linea.strip()                   # quita espacios y saltos de línea al principio/final
            if not linea or linea.startswith('#'):   # ignora líneas vacías o comentarios que empiecen con '#'
                continue
            linea = linea.replace(',', ' ')          # permite comas o espacios como separadores
            fila = [int(token) for token in linea.split()]  # convierte cada token en entero
            mapa.append(fila)                        # agrega la fila al mapa
    if not mapa:
        raise ValueError("El archivo de mapa está vacío o no contiene filas válidas.")
    numero_columnas = len(mapa[0])
    for fila in mapa:
        if len(fila) != numero_columnas:
            # todas las filas deben tener la misma cantidad de columnas para evitar errores al indexar
            raise ValueError("Las filas del mapa tienen diferente número de columnas.")
    return mapa

def guardar_mapa_en_archivo(mapa, ruta_archivo):
    # Guarda el mapa en formato legible (cada fila en una línea)
    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        for fila in mapa:
            archivo.write(' '.join(str(valor) for valor in fila) + '\n')

# Visualización del mapa en la consola

def imprimir_mapa(mapa, ruta_camino=None, posicion_inicio=None, posicion_destino=None, modo_detallado=False):
    # Muestra el mapa en la consola con símbolos amigables
    # ruta_camino: lista de (fila, columna) que representan la ruta; posicion_inicio y posicion_destino son tuplas
    filas = len(mapa)
    columnas = len(mapa[0])
    conjunto_ruta = set(ruta_camino) if ruta_camino else set()  # conjunto para búsqueda rápida
    for indice_fila in range(filas):
        linea_visual = []
        for indice_columna in range(columnas):
            coordenada_actual = (indice_fila, indice_columna)
            if posicion_inicio == coordenada_actual:
                simbolo = 'I'                               # Inicio
            elif posicion_destino == coordenada_actual:
                simbolo = 'D'                               # Destino
            elif coordenada_actual in conjunto_ruta:
                simbolo = '*'                               # Ruta encontrada
            else:
                valor_celda = mapa[indice_fila][indice_columna]
                if valor_celda == CAMINO_LIBRE:
                    simbolo = '.'                           # camino libre
                elif valor_celda == EDIFICIO:
                    simbolo = 'X'                           # edificio (obstáculo)
                elif valor_celda == AGUA:
                    simbolo = '~' if modo_detallado else 'X'  # agua se muestra como '~' en modo detallado, sino como 'X'
                elif valor_celda == ZONA_BLOQUEADA:
                    simbolo = 'T' if modo_detallado else 'X'  # zona temporal 'T' en modo detallado, sino 'X'
                else:
                    simbolo = '?'                           # valor desconocido
            linea_visual.append(simbolo)
        print(' '.join(linea_visual))
    print()  # salto de línea final

# Validaciones de coordenadas y celdas

def esta_dentro_de_limites(mapa, coordenada):
    # Comprueba que una coordenada (fila, columna) esté dentro del mapa.
    fila_objetivo, columna_objetivo = coordenada
    return 0 <= fila_objetivo < len(mapa) and 0 <= columna_objetivo < len(mapa[0])

def es_celda_transitable(mapa, coordenada, permitir_agua=False):
    # Devuelve True si la celda en 'coordenada' es transitable según 'permitir_agua'.
    fila_objetivo, columna_objetivo = coordenada
    valor = mapa[fila_objetivo][columna_objetivo]
    if valor == CAMINO_LIBRE:
        return True
    if valor == AGUA:
        return bool(permitir_agua)
    # EDIFICIO y ZONA_BLOQUEADA no son transitables
    return False

# Algoritmo BFS (búsqueda por anchura)

def bfs_busqueda(mapa, posicion_inicio, posicion_destino, permitir_agua=False):
    """
    Realiza BFS desde posicion_inicio hasta posicion_destino.
    Si no existe ruta devuelve None; si existe devuelve la lista de coordenadas [inicio,...,destino].
    """
    # validación básica: inicio y destino deben estar dentro del mapa
    if not (esta_dentro_de_limites(mapa, posicion_inicio) and esta_dentro_de_limites(mapa, posicion_destino)):
        return None

    # Evitamos iniciar si inicio o destino están sobre un obstáculo (según política del programa)
    valor_inicio = mapa[posicion_inicio[0]][posicion_inicio[1]]
    valor_destino = mapa[posicion_destino[0]][posicion_destino[1]]
    # no permitimos inicio ni destino sobre EDIFICIO, AGUA ni ZONA_BLOQUEADA.
    # (Si quisieras permitir inicio o destino sobre AGUA, quita la siguiente condición.)
    if valor_inicio in (EDIFICIO, AGUA, ZONA_BLOQUEADA) or valor_destino in (EDIFICIO, AGUA, ZONA_BLOQUEADA):
        return None

    numero_filas = len(mapa)
    numero_columnas = len(mapa[0])
    visitado = [[False for _ in range(numero_columnas)] for _ in range(numero_filas)]  # matriz de visitados
    previo = [[None for _ in range(numero_columnas)] for _ in range(numero_filas)]      # para reconstruir ruta

    cola = deque()                         # cola FIFO para BFS
    cola.append(posicion_inicio)           # encolamos la posición de inicio
    visitado[posicion_inicio[0]][posicion_inicio[1]] = True  # marcamos el inicio como visitado

    # desplazamientos en las cuatro direcciones: abajo, arriba, derecha, izquierda
    lista_desplazamientos = [(1,0), (-1,0), (0,1), (0,-1)]

    while cola:
        fila_actual, columna_actual = cola.popleft()  # desencolamos siguiente nodo a explorar
        if (fila_actual, columna_actual) == posicion_destino:
            break  # encontramos el destino, podemos salir del bucle y reconstruir ruta

        # exploramos vecinos
        for desplazamiento_fila, desplazamiento_columna in lista_desplazamientos:
            fila_vecina = fila_actual + desplazamiento_fila
            columna_vecina = columna_actual + desplazamiento_columna
            # verificamos límites y si ya fue visitada
            if 0 <= fila_vecina < numero_filas and 0 <= columna_vecina < numero_columnas and not visitado[fila_vecina][columna_vecina]:
                valor_vecina = mapa[fila_vecina][columna_vecina]
                # saltamos edificios y zonas bloqueadas siempre
                if valor_vecina == EDIFICIO or valor_vecina == ZONA_BLOQUEADA:
                    continue
                # si es agua y no permitimos agua, la saltamos
                if valor_vecina == AGUA and not permitir_agua:
                    continue
                # marcamos como visitada, guardamos previo y encolamos
                visitado[fila_vecina][columna_vecina] = True
                previo[fila_vecina][columna_vecina] = (fila_actual, columna_actual)
                cola.append((fila_vecina, columna_vecina))

    # si al final no visitamos el destino, no hay ruta
    if not visitado[posicion_destino[0]][posicion_destino[1]]:
        return None

    # reconstrucción de la ruta desde destino hacia inicio usando 'previo'
    ruta = []
    coordenada_actual = posicion_destino
    while coordenada_actual is not None:
        ruta.append(coordenada_actual)
        coordenada_actual = previo[coordenada_actual[0]][coordenada_actual[1]]
    ruta.reverse()  # invertir para tener orden desde inicio hasta destino
    return ruta

def encontrar_mejor_ruta_con_alternativas(mapa, posicion_inicio, posicion_destino):
    # Primero intento sin usar agua (modo normal)
    ruta_terreno = bfs_busqueda(mapa, posicion_inicio, posicion_destino, permitir_agua=False)
    if ruta_terreno:
        return ruta_terreno, 'tierra'
    # Si no encuentro ruta por tierra, intento permitiendo agua como alternativa
    ruta_agua = bfs_busqueda(mapa, posicion_inicio, posicion_destino, permitir_agua=True)
    if ruta_agua:
        return ruta_agua, 'agua'
    # si tampoco con agua, no hay ruta
    return None, None

# Bucle interactivo (REPL) para comandos 

def bucle_interactivo(mapa):
    posicion_inicio = None
    posicion_destino = None
    modo_detallado = False
    ultima_ruta = None
    ultimo_modo = None

    print("Calculadora de rutas CLI. Escribe 'ayuda' para ver los comandos disponibles.")
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

        if comando in ('salir', 'quit', 'exit', 'q'):
            print("Adiós.")
            break

        if comando == 'ayuda':
            print("""Comandos disponibles:
 mostrar                       - dibuja el mapa actual
 inicio fila columna           - fija punto de inicio (ej: inicio 0 0)
 destino fila columna          - fija punto destino (ej: destino 4 6)
 buscar                        - calcula la ruta (intenta tierra primero y luego agua)
 agregar fila columna tipo     - pone tipo en la celda (tipo en {0,1,2,3})
 quitar fila columna           - pone 0 en la celda (libera la celda)
 cargar nombre_archivo         - carga mapa desde archivo
 guardar nombre_archivo        - guarda mapa en archivo
 alternar detallado            - alterna vista detallada (muestra agua y bloqueos con símbolos)
 ayuda                         - muestra este texto
 salir                         - salir del programa
""")
            continue

        if comando == 'mostrar':
            imprimir_mapa(mapa, ruta_camino=ultima_ruta, posicion_inicio=posicion_inicio, posicion_destino=posicion_destino, modo_detallado=modo_detallado)
            continue

        if comando == 'inicio' and len(partes) >= 3:
            indice_fila = int(partes[1])
            indice_columna = int(partes[2])
            coordenada = (indice_fila, indice_columna)
            if not esta_dentro_de_limites(mapa, coordenada):
                print("Coordenadas fuera del mapa.")
                continue
            valor_celda = mapa[indice_fila][indice_columna]
            # Validamos que inicio no esté sobre ningún tipo de obstáculo (1,2,3)
            if valor_celda in (EDIFICIO, AGUA, ZONA_BLOQUEADA):
                print("No puedes fijar inicio sobre un obstáculo (EDIFICIO, AGUA o ZONA_BLOQUEADA).")
                continue
            posicion_inicio = coordenada
            print("Inicio fijado en", posicion_inicio)
            continue

        if comando == 'destino' and len(partes) >= 3:
            indice_fila = int(partes[1])
            indice_columna = int(partes[2])
            coordenada = (indice_fila, indice_columna)
            if not esta_dentro_de_limites(mapa, coordenada):
                print("Coordenadas fuera del mapa.")
                continue
            valor_celda = mapa[indice_fila][indice_columna]
            # Validamos que destino no esté sobre ningún tipo de obstáculo (1,2,3)
            if valor_celda in (EDIFICIO, AGUA, ZONA_BLOQUEADA):
                print("No puedes fijar destino sobre un obstáculo (EDIFICIO, AGUA o ZONA_BLOQUEADA).")
                continue
            posicion_destino = coordenada
            print("Destino fijado en", posicion_destino)
            continue

        if comando == 'buscar':
            if posicion_inicio is None or posicion_destino is None:
                print("Define primero inicio y destino con los comandos 'inicio' y 'destino'.")
                continue
            ruta, modo = encontrar_mejor_ruta_con_alternativas(mapa, posicion_inicio, posicion_destino)
            if ruta:
                ultima_ruta = ruta
                ultimo_modo = modo
                print(f"Ruta encontrada (modo: {modo}). Longitud (pasos): {len(ruta)-1}")
                imprimir_mapa(mapa, ruta_camino=ruta, posicion_inicio=posicion_inicio, posicion_destino=posicion_destino, modo_detallado=modo_detallado)
            else:
                ultima_ruta = None
                print("No existe ruta posible (ni por tierra ni por agua).")
            continue

        if comando == 'agregar' and len(partes) >= 4:
            indice_fila = int(partes[1])
            indice_columna = int(partes[2])
            tipo_valor = int(partes[3])
            coordenada = (indice_fila, indice_columna)
            if not esta_dentro_de_limites(mapa, coordenada):
                print("Coordenadas fuera del mapa.")
                continue
            if tipo_valor not in (CAMINO_LIBRE, EDIFICIO, AGUA, ZONA_BLOQUEADA):
                print("Tipo inválido; usa 0 para CAMINO_LIBRE, 1 para EDIFICIO, 2 para AGUA, 3 para ZONA_BLOQUEADA.")
                continue
            mapa[indice_fila][indice_columna] = tipo_valor
            print(f"Celda {coordenada} ahora tiene valor = {tipo_valor}.")
            # Recalculo automático si ya hay inicio y destino definidos
            if posicion_inicio and posicion_destino:
                ruta, modo = encontrar_mejor_ruta_con_alternativas(mapa, posicion_inicio, posicion_destino)
                if ruta:
                    ultima_ruta = ruta
                    ultimo_modo = modo
                    print(f"Se recalculó la ruta automáticamente (modo: {modo}).")
                else:
                    ultima_ruta = None
                    print("Después de la modificación no hay ruta disponible.")
            continue

        if comando == 'quitar' and len(partes) >= 3:
            indice_fila = int(partes[1])
            indice_columna = int(partes[2])
            coordenada = (indice_fila, indice_columna)
            if not esta_dentro_de_limites(mapa, coordenada):
                print("Coordenadas fuera del mapa.")
                continue
            mapa[indice_fila][indice_columna] = CAMINO_LIBRE
            print(f"Celda {coordenada} puesta en CAMINO_LIBRE (0).")
            continue

        if comando == 'cargar' and len(partes) >= 2:
            nombre_archivo = ' '.join(partes[1:])
            try:
                nuevo_mapa = cargar_mapa_desde_archivo(nombre_archivo)
                mapa = nuevo_mapa
                posicion_inicio = None
                posicion_destino = None
                ultima_ruta = None
                print("Mapa cargado desde", nombre_archivo)
            except Exception as error:
                print("Error cargando archivo:", error)
            continue

        if comando == 'guardar' and len(partes) >= 2:
            nombre_archivo = ' '.join(partes[1:])
            try:
                guardar_mapa_en_archivo(mapa, nombre_archivo)
                print("Mapa guardado en", nombre_archivo)
            except Exception as error:
                print("Error al guardar:", error)
            continue

        if comando == 'alternar' and len(partes) >= 2 and partes[1] == 'detallado':
            modo_detallado = not modo_detallado
            print("modo_detallado =", modo_detallado)
            continue

        print("Comando desconocido. Escribe 'ayuda' para ver los comandos disponibles.")

# ---------- Bloque principal: ejemplo de mapa y arranque del REPL ----------

if __name__ == '__main__':
    # Mapa de ejemplo (puedes editarlo, guardarlo y luego 'cargar' otro archivo sin tocar el código)
    mapa_ejemplo = [
        [0,0,0,0,0,0,0],
        [0,1,1,0,2,2,0],
        [0,0,0,0,2,1,0],
        [0,3,3,0,0,0,0],
        [0,0,0,1,1,0,0]
    ]
    mapa_actual = mapa_ejemplo
    print("Mapa de ejemplo cargado. Usa 'ayuda' para ver comandos.")
    bucle_interactivo(mapa_actual)
