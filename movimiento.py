#creo las variables
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

movimientos = [(-1,0),(1,0),(0,-1),(0,1)] #arriba abajo izquierda y derecha
profundidad = 3 #defino la profundidad

#esta funcion hace que no se pueda salir de los limites del tablero
def en_limites(pos):
    return 0 <= pos[0] < fila and 0 <= pos[1] < columna

#esta funcion verifica si no se puede pasar por ahi
def es_transitable(pos):
    return tablero[pos[0]][pos[1]] != '0'

#esta funcion verifica si los movimientos son validos
def movs_validos(pos):
    #creo una lista vacia para meter los movimientos validos q el jugador pueda hacer
    resultado = []
    #recorre los cambios en la fila y la columna de la lista de movimienros
    for dx, dy in movimientos:
        #la nueva posicion es igual a la posicion actual mas la nueva direccion
        nueva_pos = [pos[0] + dx, pos[1] + dy]
        # si la nueva posicion esta dentro de los limites y puede pasar por ahi permite el movimiento
        if en_limites(nueva_pos) and es_transitable(nueva_pos):
            #si el movimiento es valido se agrega a la lista vacia de resultado
            resultado.append(nueva_pos)
    #devuelve la lista con todas las posiciones posibles desde la nueva pos
    return resultado

#esta funcion evalua la posicion del gato y el raton
def evaluar(pos_gato, pos_raton):
    #si el gato y el raton estan en la misma casilla significa q el gato atrapo al raton
    if pos_gato == pos_raton:
        #es el peor valor posible para el raton
        return -999
    #calcula la diferencia de distancia entre el gato y el raton / abs: es el valor absoluto para evitar numeros negativos
    return abs(pos_gato[0] - pos_raton[0]) + abs(pos_gato[1] - pos_raton[1])

#implemento el minimax
def minimax(pos_gato, pos_raton, depth, turno_max):
    # turno_max = True -> mueve el ratón (MAX)
    # turno_max = False -> mueve el gato (MIN)
    #si la profundidad es iguala 0 oel gato atrapo al raton
    if depth == 0 or pos_gato == pos_raton:
        #vuelve a evaluar la posicion del gato y el raton
        return evaluar(pos_gato, pos_raton), pos_raton  # no importa mover ahora

#si es el turno del raton
    if turno_max:
        # RATÓN (MAX)
        #cualquier movimiento valido siempre sera mejor que el mejor valor indicado
        mejor_val = -999
        #mejor_r es la mejor posicion del raton hasta ahora
        mejor_r = pos_raton
        #recorre tdas las posicion posibles al q el raton pueda moverse
        for nuevo_raton in movs_validos(pos_raton):
            #por cada posicion posible se llama de nuevo al minimax
            val, _ = minimax(pos_gato, nuevo_raton, depth - 1, False)
            #si el valor actual es superior al mejor valor anteriormente definido
            if val > mejor_val:
                #el mejor valor pasa a ser el valor actual
                mejor_val = val
                #se actualiza con el puntaje y guarda la nueva posicion del raton
                mejor_r = nuevo_raton
        #vuelve a hacer lo mismo pero con las posiciones y puntajes actualizados
        return mejor_val, mejor_r
    else:
        # GATO (MIN)
        #cualquier puntaje sera mejor al puntaje ya definido
        peor_val = 999
        #recorre las posicuones posibles para el gato
        for nuevo_gato in movs_validos(pos_gato):
            #por cada posicion posible llama al minimax 
            val, _ = minimax(nuevo_gato, pos_raton, depth - 1, True)
            #si el valor nuevo es menor al valor ya definido
            if val < peor_val:
                #el valor definido se actualiza y pasa a ser el nuevo valor
                peor_val = val
        #vuelve a hacer lo mismo pero actualizando el puntaje y la posicion del raton
        return peor_val, pos_raton
#esta funcion calcula el mejor movimiento del raton
def mejor_movimiento_raton(pos_gato, pos_raton, depth):
    #llama al minimax para calcular la mejor jugada para el raton
    _, mejor_r = minimax(pos_gato, pos_raton, depth, True)
    #actualiza la mejor jugada del raton cada que la posicion del raton cambia
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
        print()

 # ----- mueve el RATÓN (IA con Minimax) -----
    # (solo si el juego sigue)
    if continuar and gato != raton:
        # quitar 'r' de su posición actual
        tablero[raton[0]][raton[1]] = '.'

        # elegir mejor movimiento del ratón mirando profundidad turnos
        nueva_r = mejor_movimiento_raton(gato, raton, profundidad)

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
    print()