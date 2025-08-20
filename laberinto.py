
import copy

# Laberintos estratégicos
LABERINTOS = {
    7: [
        [".", "#", ".", ".", ".", "#", "."],
        [".", "#", "#", "#", ".", "#", "."],
        [".", ".", ".", "#", ".", ".", "."],
        ["#", ".", ".", ".", ".", "#", "."],
        [".", ".", "#", "#", ".", "#", "."],
        [".", ".", ".", "#", ".", "#", "#"],
        [".", "#", ".", ".", ".", ".", "."],
    ],
    9: [
        [".","#",".",".","#",".",".",".","."],
        [".","#",".","#","#",".","#","#","."],
        [".",".",".",".","#",".","#","#","."],
        ["#",".","#",".","#",".","#",".","."],
        [".",".","#",".",".",".","#",".","#"],
        [".","#","#","#","#","#","#",".","#"],
        [".",".",".","#",".","#","#",".","#"],
        [".",".","#","#",".",".",".",".","#"],
        ["#",".",".",".",".","#","#",".","."]
    ],
    12: [
        [".","#",".","#",".",".",".","#",".",".",".","."],
        [".","#",".","#",".","#",".","#",".","#","#","."],
        [".",".",".",".","#","#",".","#",".",".","#","."],
        ["#",".","#",".","#",".",".",".","#",".","#","."],
        [".",".","#",".",".",".","#",".",".",".","#","#"],
        [".","#","#","#",".","#",".","#","#",".",".","."],
        [".",".","#",".",".","#",".",".",".",".","#","."],
        ["#",".","#",".","#","#",".","#","#","#","#","."],
        [".",".",".",".",".","#",".",".",".",".","#","#"],
        [".","#",".","#",".","#","#","#","#",".",".","."],
        [".",".",".","#",".","#",".",".",".",".","#","."],
        [".","#",".","#",".",".",".","#","#","#","#","."]
    ]
}

# Posición fija de los quesos en cada tablero
QUESOS = {
    7: [3,3],
    9: [4,4],
    12: [1,1]
}

MOVS = [(0,1),(0,-1),(1,0),(-1,0)]

# Copiar tablero
def crear_tablero_fijo(n):
    return copy.deepcopy(LABERINTOS[n])

# Mostrar tablero
def mostrar(tablero, gato, raton, queso=None):
    n = len(tablero)
    for i in range(n):
        fila = []
        for j in range(n):
            if [i,j]==gato==raton:
                fila.append("💥")
            elif [i,j]==gato:
                fila.append("😺")
            elif [i,j]==raton:
                fila.append("🐭")
            elif queso and [i,j]==queso:
                fila.append("🧀")
            else:
                fila.append(tablero[i][j])
        print(" ".join(fila))
    print()

# Mover jugador humano
def mover_jugador(pos, tecla, n, tablero):
    movimientos = {"w":(-1,0),"s":(1,0),"a":(0,-1),"d":(0,1)}
    if tecla in movimientos:
        dx, dy = movimientos[tecla]
        nx, ny = pos[0]+dx, pos[1]+dy
        if 0<=nx<n and 0<=ny<n and tablero[nx][ny]!="#":
            return [nx, ny]
    return pos

# Evaluación heurística para el ratón
def evaluar_raton(gato, raton, queso):
    if gato == raton:
        return -999
    dist_queso = abs(raton[0]-queso[0]) + abs(raton[1]-queso[1])
    dist_gato = abs(raton[0]-gato[0]) + abs(raton[1]-gato[1])
    return dist_gato - dist_queso  # alejarse del gato y acercarse al queso

# Minimax ratón (objetivo: queso + evitar gato)
def minimax_raton(gato, raton, queso, depth, max_turno, n, tablero):
    if depth == 0 or gato == raton or raton == queso:
        return evaluar_raton(gato, raton, queso), raton

    if max_turno:  # turno gato
        mejor_valor = -999
        mejor_mov = gato
        for dx, dy in MOVS:
            nx, ny = gato[0]+dx, gato[1]+dy
            if 0 <= nx < n and 0 <= ny < n and tablero[nx][ny] != "#":
                val, _ = minimax_raton([nx, ny], raton, queso, depth-1, False, n, tablero)
                if val > mejor_valor:
                    mejor_valor = val
                    mejor_mov = [nx, ny]
        return mejor_valor, mejor_mov
    else:  # turno ratón
        mejor_valor = -999
        mejor_mov = raton
        for dx, dy in MOVS:
            nx, ny = raton[0]+dx, raton[1]+dy
            if 0 <= nx < n and 0 <= ny < n and tablero[nx][ny] != "#":
                val, _ = minimax_raton(gato, [nx, ny], queso, depth-1, True, n, tablero)
                if val > mejor_valor:
                    mejor_valor = val
                    mejor_mov = [nx, ny]
        return mejor_valor, mejor_mov

# Minimax gato normal
def evaluar_gato(gato, raton):
    if gato == raton:
        return 999
    return -(abs(gato[0]-raton[0]) + abs(gato[1]-raton[1]))

def minimax_gato(gato, raton, depth, max_turno, n, tablero):
    if depth==0 or gato==raton:
        return evaluar_gato(gato, raton), gato

    if max_turno:
        mejor_valor=-999
        mejor_mov=gato
        for dx, dy in MOVS:
            nx, ny = gato[0]+dx, gato[1]+dy
            if 0 <= nx < n and 0 <= ny < n and tablero[nx][ny]!="#":
                val, _ = minimax_gato([nx,ny], raton, depth-1, False, n, tablero)
                if val > mejor_valor:
                    mejor_valor = val
                    mejor_mov = [nx, ny]
        return mejor_valor, mejor_mov
    else:
        peor_valor = 999
        peor_mov = raton
        for dx, dy in MOVS:
            nx, ny = raton[0]+dx, raton[1]+dy
            if 0<=nx<n and 0<=ny<n and tablero[nx][ny]!="#":
                val, _ = minimax_gato(gato, [nx, ny], depth-1, True, n, tablero)
                if val<peor_valor:
                    peor_valor = val
                    peor_mov = [nx, ny]
        return peor_valor, peor_mov

# -----------------------
# Elegir dificultad
# -----------------------
print("Elige dificultad:")
print("1. Fácil (7x7)")
print("2. Medio (9x9)")
print("3. Difícil (12x12)")
opcion=input("Opción: ").strip()

if opcion=="1":
    n=7
    turnos_para_ganar=40
elif opcion=="2":
    n=9
    turnos_para_ganar=50
else:
    n=12
    turnos_para_ganar=60

# -----------------------
# Elegir personaje
# -----------------------
eleccion=input("¿Quieres ser el Gato (G) o el Ratón (R)? ").strip().upper()
jugador="G" if eleccion=="G" else "R"

# Crear tablero fijo
tablero = crear_tablero_fijo(n)

# Posiciones iniciales
gato = [0,0]
raton = [n-1,n-1]
tablero[gato[0]][gato[1]]="."
tablero[raton[0]][raton[1]]="."

# Queso
queso = QUESOS[n]
print(f"🧀 El queso está en la posición {queso}. El ratón debe llegar al queso para ganar.")

# -----------------------
# Simulación
# -----------------------
for turno in range(1, turnos_para_ganar+1):
    print(f"Turno {turno}:")
    mostrar(tablero, gato, raton, queso)

    if gato == raton:
        print("💥 ¡El gato atrapó al ratón!")
        break
    if raton == queso:
        print("🏆 ¡El ratón comió el queso y ganó!")
        break

    if jugador=="R":
        # Ratón controlado por jugador
        tecla = input("Mueve al Ratón (w/a/s/d): ").strip().lower()
        raton = mover_jugador(raton, tecla, n, tablero)
        # IA gato
        _, gato = minimax_gato(gato, raton, 3, True, n, tablero)
    else:
        # Gato controlado por jugador
        tecla = input("Mueve al Gato (w/a/s/d): ").strip().lower()
        gato = mover_jugador(gato, tecla, n, tablero)
        # Ratón automático: intenta el queso y evita al gato
        _, raton = minimax_raton(gato, raton, queso, 3, False, n, tablero)

    print("\n" + "="*30 + "\n")
