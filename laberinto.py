import copy
import heapq

# Laberintos estratégicos (emojis)
LABERINTOS = {
    7: [
        ["⬜", "🟥", "⬜", "⬜", "⬜", "🟥", "⬜"],
        ["⬜", "🟥", "⬜", "🟥", "⬜", "🟥", "⬜"],
        ["⬜", "⬜", "⬜", "🟥", "⬜", "⬜", "⬜"],
        ["🟥", "⬜", "⬜", "⬜", "⬜", "🟥", "⬜"],
        ["⬜", "⬜", "🟥", "🟥", "⬜", "🟥", "⬜"],
        ["⬜", "⬜", "⬜", "🟥", "⬜", "🟥", "🟥"],
        ["⬜", "🟥", "⬜", "⬜", "⬜", "⬜", "⬜"],
    ],
    9: [
        ["⬜","🟥","⬜","⬜","⬜","⬜","⬜","⬜","⬜"],
        ["⬜","🟥","⬜","🟥","🟥","⬜","🟥","🟥","⬜"],
        ["⬜","⬜","⬜","⬜","🟥","⬜","🟥","🟥","⬜"],
        ["🟥","⬜","🟥","⬜","🟥","⬜","🟥","⬜","⬜"],
        ["⬜","⬜","🟥","⬜","⬜","⬜","🟥","⬜","🟥"],
        ["⬜","🟥","🟥","🟥","🟥","🟥","🟥","⬜","🟥"],
        ["⬜","⬜","⬜","⬜","⬜","🟥","🟥","⬜","🟥"],
        ["🟥","⬜","🟥","🟥","⬜","⬜","⬜","⬜","🟥"],
        ["🟥","⬜","⬜","⬜","⬜","🟥","🟥","⬜","⬜"]
    ],
    12: [
        ["⬜","🟥","⬜","🟥","⬜","⬜","⬜","🟥","⬜","⬜","⬜","⬜"],
        ["⬜","🟥","⬜","🟥","⬜","🟥","⬜","🟥","⬜","🟥","🟥","⬜"],
        ["⬜","⬜","⬜","⬜","🟥","🟥","⬜","🟥","⬜","⬜","🟥","⬜"],
        ["🟥","⬜","🟥","⬜","🟥","⬜","⬜","⬜","🟥","⬜","🟥","⬜"],
        ["⬜","⬜","🟥","⬜","⬜","⬜","🟥","⬜","⬜","⬜","🟥","🟥"],
        ["⬜","🟥","🟥","🟥","⬜","🟥","⬜","🟥","🟥","⬜","⬜","⬜"],
        ["⬜","⬜","🟥","⬜","⬜","🟥","⬜","⬜","⬜","⬜","🟥","⬜"],
        ["🟥","⬜","🟥","⬜","🟥","🟥","⬜","🟥","🟥","🟥","🟥","⬜"],
        ["⬜","⬜","⬜","⬜","⬜","🟥","⬜","⬜","⬜","⬜","🟥","🟥"],
        ["⬜","🟥","⬜","🟥","⬜","🟥","🟥","🟥","🟥","⬜","⬜","⬜"],
        ["⬜","⬜","⬜","🟥","⬜","🟥","⬜","⬜","⬜","⬜","🟥","⬜"],
        ["⬜","🟥","⬜","🟥","⬜","⬜","⬜","🟥","🟥","🟥","🟥","⬜"]
    ]
}

# Posición de los quesos
QUESOS = {7: [3,2], 9: [4,4], 12: [1,1]}
MOVS = [(0,1),(0,-1),(1,0),(-1,0)]

def crear_tablero_fijo(n):
    return copy.deepcopy(LABERINTOS[n])

def mostrar(tablero, gato, raton, queso=None):
    n = len(tablero)
    for i in range(n):
        fila = []
        for j in range(n):
            if [i,j]==gato==raton:
                fila.append("🪦 ")
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

def mover_jugador(pos, tecla, n, tablero):
    movimientos = {"w":(-1,0),"s":(1,0),"a":(0,-1),"d":(0,1)}
    if tecla in movimientos:
        dx, dy = movimientos[tecla]
        nx, ny = pos[0]+dx, pos[1]+dy
        if 0<=nx<n and 0<=ny<n and tablero[nx][ny]!="🟥":
            return [nx, ny]
    return pos

def evaluar_gato(gato, raton):
    if gato==raton: return 999
    return -(abs(gato[0]-raton[0]) + abs(gato[1]-raton[1]))

def minimax_gato(gato, raton, depth, max_turno, n, tablero):
    if depth==0 or gato==raton: return evaluar_gato(gato, raton), gato
    if max_turno:
        mejor_valor=-999
        mejor_mov=gato
        for dx, dy in MOVS:
            nx, ny = gato[0]+dx, gato[1]+dy
            if 0<=nx<n and 0<=ny<n and tablero[nx][ny]!="🟥":
                val,_ = minimax_gato([nx,ny], raton, depth-1, False, n, tablero)
                if val>mejor_valor:
                    mejor_valor=val
                    mejor_mov=[nx,ny]
        return mejor_valor, mejor_mov
    else:
        peor_valor=999
        peor_mov=raton
        for dx, dy in MOVS:
            nx, ny = raton[0]+dx, raton[1]+dy
            if 0<=nx<n and 0<=ny<n and tablero[nx][ny]!="🟥":
                val,_=minimax_gato(gato,[nx,ny],depth-1,True,n,tablero)
                if val<peor_valor:
                    peor_valor=val
                    peor_mov=[nx,ny]
        return peor_valor, peor_mov

def heuristica(pos,obj):
    return abs(pos[0]-obj[0])+abs(pos[1]-obj[1])

# --- A* ratón mejorado ---
def astar_raton(tablero, raton, queso, gato):
    n=len(tablero)
    heap=[]
    heapq.heappush(heap,(0+heuristica(raton,queso),0,raton,[raton]))
    visitado=set()
    while heap:
        f,g,actual,path=heapq.heappop(heap)
        if tuple(actual) in visitado: continue
        visitado.add(tuple(actual))
        if actual==queso: return path[1] if len(path)>1 else actual
        for dx,dy in MOVS:
            nx,ny=actual[0]+dx,actual[1]+dy
            if 0<=nx<n and 0<=ny<n and tablero[nx][ny]!="🟥":
                # Evitar casilla del gato y adyacentes
                if abs(nx-gato[0]) + abs(ny-gato[1]) <= 1: 
                    continue
                if tuple([nx,ny]) not in visitado:
                    h=heuristica([nx,ny],queso)
                    heapq.heappush(heap,(g+1+h,g+1,[nx,ny],path+[[nx,ny]]))
    return raton

def cerrar_camino(tablero, raton, gato, queso):
    n=len(tablero)
    print("🔒 Puedes bloquear una casilla para acorralar al ratón.")
    while True:
        try:
            fila,col=map(int,input("Fila Columna: ").split())
            if 0<=fila<n and 0<=col<n and tablero[fila][col]=="⬜" and [fila,col]!=raton and [fila,col]!=gato and [fila,col]!=queso:
                tablero[fila][col]="🟥"
                print(f"Casilla ({fila},{col}) bloqueada.")
                break
            else: print("No se puede bloquear esa casilla.")
        except: print("Entrada inválida.")

# --- Juego principal ---
print("Elige dificultad:\n1. Fácil (7x7)\n2. Medio (9x9)\n3. Difícil (12x12)")
opcion=input("Opción: ").strip()
if opcion=="1": n=7; turnos_para_ganar=60
elif opcion=="2": n=9; turnos_para_ganar=80
else: n=12; turnos_para_ganar=90

eleccion=input("¿Quieres ser el Gato (G) o el Ratón (R)? ").strip().upper()
jugador="G" if eleccion=="G" else "R"

POSICIONES_INICIALES={7:{"gato":[0,0],"raton":[6,6]},
                      9:{"gato":[0,0],"raton":[8,8]},
                      12:{"gato":[0,0],"raton":[11,11]}}
tablero=crear_tablero_fijo(n)
gato=POSICIONES_INICIALES[n]["gato"]
raton=POSICIONES_INICIALES[n]["raton"]

# Evitar empezar en muro
if tablero[gato[0]][gato[1]]=="🟥": tablero[gato[0]][gato[1]]="⬜"
if tablero[raton[0]][raton[1]]=="🟥": tablero[raton[0]][raton[1]]="⬜"

# Queso
queso=QUESOS[n]
if tablero[queso[0]][queso[1]]=="🟥":
    for i in range(n):
        for j in range(n):
            if tablero[i][j]=="⬜":
                queso=[i,j]
                break
print(f"🧀 Queso en {queso}")

# Simulación
turnos_sin_captura=0
max_sin_captura=20
for turno in range(1,turnos_para_ganar+1):
    print(f"\nTurno {turno}:")
    mostrar(tablero,gato,raton,queso)

    if gato==raton: print("💥 ¡El gato atrapó al ratón!"); break
    if raton==queso: print("🏆 ¡El ratón comió el queso!"); break

    if jugador=="R":
        tecla=input("Mueve al Ratón (w/a/s/d): ").strip().lower()
        raton=mover_jugador(raton,tecla,n,tablero)
        _,gato=minimax_gato(gato,raton,3,True,n,tablero)
    else:
        tecla=input("Mueve al Gato (w/a/s/d): ").strip().lower()
        gato=mover_jugador(gato,tecla,n,tablero)
        raton=astar_raton(tablero,raton,queso,gato)

    if gato!=raton: turnos_sin_captura+=1
    else: turnos_sin_captura=0

    if turnos_sin_captura>=max_sin_captura and jugador=="G":
        cerrar_camino(tablero,raton,gato,queso)
        turnos_sin_captura=0
