fila = 10
columna = 10
tablero = []

# bucle que recorre la fila y crea el tablero vacío
for i in range(fila):
    fila_temp = []
    for j in range(columna):
        fila_temp.append('.')
    tablero.append(fila_temp)

# posición inicial del gato y el ratón
gato = [0, 0]
raton = [9, 9]
tablero[gato[0]][gato[1]] = 'g'
tablero[raton[0]][raton[1]] = 'r'

# obstáculos
tablero[3][3] = '0'
tablero[4][5] = '0'
tablero[3][8] = '0'
tablero[7][5] = '0'
tablero[6][2] = '0'
tablero[4][4] = '0'
tablero[6][1] = '0'
tablero[9][5] = '0'
tablero[8][0] = '0'
tablero[8][1] = '0'
tablero[1][9] = '0'

# mostrar tablero inicial
for fila_temp in tablero:
    print(' '.join(fila_temp))

# movimientos 
movimiento = {}
movimiento['w'] = (-1, 0)   # arriba
movimiento['s'] = (1, 0)    # abajo
movimiento['a'] = (0, -1)   # izquierda
movimiento['d'] = (0, 1)    # derecha

#funciones minimax para el raton

MOVS = [(-1,0),(1,0),(0,-1),(0,1)] #arriba abajo izquierda y derecha
PROFUNDIDAD = 3 #defino la profundidad

def en_limites(p):
    return 0 <= p[0] < fila and 0 <= p[1] < columna

def es_transitable(p):
    return tablero[p[0]][p[1]] != '0'

def movs_validos(pos):
    res = []
    for dx, dy in MOVS:
        np = [pos[0] + dx, pos[1] + dy]
        if en_limites(np) and es_transitable(np):
            res.append(np)
    return res

def evaluar(pos_gato, pos_raton):
    if pos_gato == pos_raton:
        return -999
    return abs(pos_gato[0] - pos_raton[0]) + abs(pos_gato[1] - pos_raton[1])

def minimax(pos_gato, pos_raton, depth, turno_max):
    # turno_max = True -> mueve el ratón (MAX)
    # turno_max = False -> mueve el gato (MIN)
    if depth == 0 or pos_gato == pos_raton:
        return evaluar(pos_gato, pos_raton), pos_raton  # no importa mover ahora

    if turno_max:
        # RATÓN (MAX)
        mejor_val = -999
        mejor_r = pos_raton
        for nr in movs_validos(pos_raton):
            val, _ = minimax(pos_gato, nr, depth - 1, False)
            if val > mejor_val:
                mejor_val = val
                mejor_r = nr
        return mejor_val, mejor_r
    else:
        # GATO (MIN)
        peor_val = 999
        for ng in movs_validos(pos_gato):
            val, _ = minimax(ng, pos_raton, depth - 1, True)
            if val < peor_val:
                peor_val = val
        # en turno del gato no movemos al ratón ahora
        return peor_val, pos_raton

def mejor_movimiento_raton(pos_gato, pos_raton, depth):
    _, mejor_r = minimax(pos_gato, pos_raton, depth, True)
    return mejor_r

#bucle
continuar = True
while continuar:
    tecla = input('ingrese la tecla w/s/d/a o "q" para salir: ')

    if tecla == 'q':
        continuar = False
        break

    if tecla in movimiento:
        dx, dy = movimiento[tecla]
        nueva_pos = [gato[0] + dx, gato[1] + dy]

        # verificar q esta dentro de los límites
        if 0 <= nueva_pos[0] < fila and 0 <= nueva_pos[1] < columna:

            # verificar que no hay obstáculo
            if tablero[nueva_pos[0]][nueva_pos[1]] != '0':
                tablero[gato[0]][gato[1]] = '.'   # borrar posicion anterior
                gato = nueva_pos                  # actualizar la posicion
                tablero[gato[0]][gato[1]] = 'g'   # colocar gato

                # verificar si atrapo al raton
                if gato == raton:
                    print('El gato atrapo al raton!')
                    continuar = False  # opa el juego
                    for fila_temp in tablero:
                        print(' '.join(fila_temp))
            else:
                print("Movimiento bloqueado, hay un obstáculo ahi.")
        else:
            print("Movimiento invalido, fuera del tablero.")

        # mostrar tablero actualizado
        for fila_temp in tablero:
            print(' '.join(fila_temp))

 # ----- mueve el RATÓN (IA con Minimax) -----
    # (solo si el juego sigue)
    if continuar and gato != raton:
        # quitar 'r' de su posición actual
        tablero[raton[0]][raton[1]] = '.'

        # elegir mejor movimiento del ratón mirando PROFUNDIDAD turnos
        nueva_r = mejor_movimiento_raton(gato, raton, PROFUNDIDAD)

        # mover ratón
        raton = nueva_r
        tablero[raton[0]][raton[1]] = 'r'

        # si por alguna razón se encontró con el gato, termina
        if gato == raton:
            print('El gato atrapó al ratón!')
            for fila_temp in tablero:
                print(' '.join(fila_temp))
            break

    # mostrar tablero actualizado tras ambos movimientos
    for fila_temp in tablero:
        print(' '.join(fila_temp))