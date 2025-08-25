
x = int(input('agregar coordenada x '))
y = int(input('agregar coordenada y '))
fila = 10
columna = 10
tablero = []

for i in range(fila):
    fila = []
    for j in range(columna):
        fila.append('.')
    tablero.append(fila)

tablero[x][y] = 'g'
tablero[-1][-1] = 'r'

for fila in tablero:
    print(' '.join(fila))

movimiento = {}

movimiento['w'] = (-1,0)
movimiento['s'] = (1,0)
movimiento['a'] = (0,-1)
movimiento['d'] = (0,1)

#continuar = True
#while continuar:

    #print('ingresa la tecla de movimiento')
    #print('movimientos: w:arriba, s:abajo, a:izquierda, d:derecha')
