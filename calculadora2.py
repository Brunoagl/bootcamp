from collections import deque
import random

# ---------------------------
# CONSTANTES
# ---------------------------
CAMINO_LIBRE = 0
EDIFICIO = 1
AGUA = 2
ZONA_BLOQUEADA = 3


# ---------------------------
# CLASE MAPA
# ---------------------------
class Mapa:
    def __init__(self, filas, columnas, valor_relleno=CAMINO_LIBRE):
        self.filas = filas
        self.columnas = columnas
        self.matriz = [[valor_relleno for _ in range(columnas)] for _ in range(filas)]

    def generar_obstaculos_aleatorios(self, prob_edificio=0.15, prob_agua=0.10, prob_bloqueo=0.05):
        for i in range(self.filas):
            for j in range(self.columnas):
                rnd = random.random()
                if rnd < prob_edificio:
                    self.matriz[i][j] = EDIFICIO
                elif rnd < prob_edificio + prob_agua:
                    self.matriz[i][j] = AGUA
                elif rnd < prob_edificio + prob_agua + prob_bloqueo:
                    self.matriz[i][j] = ZONA_BLOQUEADA
                else:
                    self.matriz[i][j] = CAMINO_LIBRE

    def dentro_de_limites(self, f, c):
        return 0 <= f < self.filas and 0 <= c < self.columnas

    def es_transitable(self, f, c, permitir_agua=False):
        valor = self.matriz[f][c]
        if valor == CAMINO_LIBRE:
            return True
        if valor == AGUA and permitir_agua:
            return True
        return False

    def agregar_obstaculo(self, f, c, tipo):
        if self.dentro_de_limites(f, c):
            self.matriz[f][c] = tipo

    def quitar_obstaculo(self, f, c):
        if self.dentro_de_limites(f, c):
            self.matriz[f][c] = CAMINO_LIBRE

    def redimensionar(self, nuevas_filas, nuevas_columnas, valor_relleno=CAMINO_LIBRE):
        nuevo_mapa = [[valor_relleno for _ in range(nuevas_columnas)] for _ in range(nuevas_filas)]
        for i in range(min(self.filas, nuevas_filas)):
            for j in range(min(self.columnas, nuevas_columnas)):
                nuevo_mapa[i][j] = self.matriz[i][j]
        self.filas, self.columnas, self.matriz = nuevas_filas, nuevas_columnas, nuevo_mapa

    def guardar(self, ruta):
        with open(ruta, 'w', encoding='utf-8') as f:
            for fila in self.matriz:
                f.write(' '.join(str(x) for x in fila) + '\n')

    @staticmethod
    def cargar(ruta):
        matriz = []
        with open(ruta, 'r', encoding='utf-8') as f:
            for linea in f:
                if linea.strip():
                    matriz.append([int(x) for x in linea.split()])
        filas, columnas = len(matriz), len(matriz[0])
        mapa = Mapa(filas, columnas)
        mapa.matriz = matriz
        return mapa

    def mostrar(self, ruta=None, inicio=None, destino=None, modo_detallado=False):
        ruta_set = set(ruta) if ruta else set()
        for f in range(self.filas):
            linea = []
            for c in range(self.columnas):
                coord = (f, c)
                if coord == inicio:
                    simbolo = 'I'
                elif coord == destino:
                    simbolo = 'D'
                elif coord in ruta_set:
                    simbolo = '*'
                else:
                    valor = self.matriz[f][c]
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
# CLASE CALCULADORA DE RUTAS
# ---------------------------
class CalculadoraDeRutas:
    def __init__(self, mapa):
        self.mapa = mapa

    def bfs(self, inicio, destino, permitir_agua=False):
        if not (self.mapa.dentro_de_limites(*inicio) and self.mapa.dentro_de_limites(*destino)):
            return None

        if not self.mapa.es_transitable(*inicio, permitir_agua) or not self.mapa.es_transitable(*destino, permitir_agua):
            return None

        visitado = [[False]*self.mapa.columnas for _ in range(self.mapa.filas)]
        previo = [[None]*self.mapa.columnas for _ in range(self.mapa.filas)]
        cola = deque([inicio])
        visitado[inicio[0]][inicio[1]] = True

        movimientos = [(1,0),(-1,0),(0,1),(0,-1)]

        while cola:
            f, c = cola.popleft()
            if (f, c) == destino:
                break
            for df, dc in movimientos:
                nf, nc = f+df, c+dc
                if self.mapa.dentro_de_limites(nf, nc) and not visitado[nf][nc]:
                    if self.mapa.es_transitable(nf, nc, permitir_agua):
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

    def encontrar_mejor_ruta(self, inicio, destino):
        ruta_tierra = self.bfs(inicio, destino, permitir_agua=False)
        if ruta_tierra:
            return ruta_tierra, 'tierra'
        ruta_agua = self.bfs(inicio, destino, permitir_agua=True)
        if ruta_agua:
            return ruta_agua, 'agua'
        return None, None


# ---------------------------
# CLASE INTERFAZ CLI
# ---------------------------
class InterfazCLI:
    def __init__(self, mapa):
        self.mapa = mapa
        self.calculadora = CalculadoraDeRutas(mapa)
        self.inicio = None
        self.destino = None
        self.ultima_ruta = None
        self.modo_detallado = False

    def ejecutar(self):
        print("Calculadora de rutas CLI (OOP). Escribe 'ayuda' para ver comandos.")
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
 mostrar                       - dibuja el mapa
 inicio f c                    - fija punto de inicio
 destino f c                   - fija punto de destino
 buscar                        - calcula la mejor ruta
 agregar f c tipo              - cambia celda
 quitar f c                    - borra obstáculo
 redimensionar f c             - cambia tamaño del mapa
 guardar archivo.txt           - guarda mapa
 cargar archivo.txt            - carga mapa
 alternar detallado            - alterna símbolos de agua/bloqueo
 salir                         - salir
""")
                continue

            if comando == 'mostrar':
                self.mapa.mostrar(self.ultima_ruta, self.inicio, self.destino, self.modo_detallado)
                continue

            if comando == 'inicio' and len(partes) >= 3:
                f, c = int(partes[1]), int(partes[2])
                if not self.mapa.dentro_de_limites(f, c):
                    print("Fuera del mapa.")
                    continue
                self.inicio = (f, c)
                print("Inicio fijado en", self.inicio)
                continue

            if comando == 'destino' and len(partes) >= 3:
                f, c = int(partes[1]), int(partes[2])
                if not self.mapa.dentro_de_limites(f, c):
                    print("Fuera del mapa.")
                    continue
                self.destino = (f, c)
                print("Destino fijado en", self.destino)
                continue

            if comando == 'buscar':
                if self.inicio is None or self.destino is None:
                    print("Define primero inicio y destino.")
                    continue
                ruta, modo = self.calculadora.encontrar_mejor_ruta(self.inicio, self.destino)
                if ruta:
                    self.ultima_ruta = ruta
                    print(f"Ruta encontrada (modo: {modo}). Pasos: {len(ruta)-1}")
                    self.mapa.mostrar(ruta, self.inicio, self.destino, self.modo_detallado)
                else:
                    print("No hay ruta posible.")
                continue

            if comando == 'agregar' and len(partes) >= 4:
                f, c, tipo = int(partes[1]), int(partes[2]), int(partes[3])
                self.mapa.agregar_obstaculo(f, c, tipo)
                print(f"Celda {(f,c)} modificada.")
                continue

            if comando == 'quitar' and len(partes) >= 3:
                f, c = int(partes[1]), int(partes[2])
                self.mapa.quitar_obstaculo(f, c)
                print(f"Celda {(f,c)} liberada.")
                continue

            if comando == 'redimensionar' and len(partes) >= 3:
                f, c = int(partes[1]), int(partes[2])
                self.mapa.redimensionar(f, c)
                self.mapa.generar_obstaculos_aleatorios()
                print(f"Mapa redimensionado a {f}x{c}.")
                continue

            if comando == 'guardar' and len(partes) >= 2:
                nombre = partes[1]
                self.mapa.guardar(nombre)
                print("Mapa guardado en", nombre)
                continue

            if comando == 'cargar' and len(partes) >= 2:
                nombre = partes[1]
                self.mapa = Mapa.cargar(nombre)
                self.calculadora = CalculadoraDeRutas(self.mapa)
                print("Mapa cargado desde", nombre)
                continue

            if comando == 'alternar' and len(partes) >= 2 and partes[1] == 'detallado':
                self.modo_detallado = not self.modo_detallado
                print("Modo detallado =", self.modo_detallado)
                continue

            print("Comando desconocido. Escribe 'ayuda'.")


# ---------------------------
# PROGRAMA PRINCIPAL
# ---------------------------
if __name__ == "__main__":
    random.seed()
    mapa = Mapa(10, 10)
    mapa.generar_obstaculos_aleatorios()
    interfaz = InterfazCLI(mapa)
    interfaz.ejecutar()
