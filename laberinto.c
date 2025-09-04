#include <stdio.h>    // Se incluye para funciones de entrada/salida (printf, scanf).
#include <stdlib.h>   // Se incluye para malloc, free, rand, srand y otras utilidades.
#include <time.h>     // Se incluye para manejar la semilla aleatoria con time().
#include <unistd.h>   // Se incluye para usleep(), que pausa la ejecución en microsegundos.

// Símbolos visuales que usa el laberinto en pantalla.
// PARED representa lo que no se puede atravesar.
// CAMINO representa espacios transitables.
// VISITADO se usa temporalmente para animar la exploración (puntos).
// INICIO y SALIDA marcan los extremos del recorrido.
// RUTA marca el camino correcto encontrado al final.
#define PARED   '#'
#define CAMINO  ' '
#define VISITADO '.'
#define INICIO  'S'
#define SALIDA  'E'
#define RUTA    '*'

// Matriz de movimientos: arriba, abajo, izquierda, derecha.
// Cada elemento es un par {deltaFila, deltaColumna}.
int movimientos[4][2] = {
    {-1, 0}, // arriba    -> fila-1, misma columna
    {1, 0},  // abajo     -> fila+1, misma columna
    {0, -1}, // izquierda -> misma fila, columna-1
    {0, 1}   // derecha   -> misma fila, columna+1
};

/* Función: imprimir_laberinto
   Parámetros:
     laberinto -> matriz de caracteres (char**) que representa el mapa.
     filas     -> número de filas del mapa.
     columnas  -> número de columnas del mapa.
     pausa_ms  -> pausa en milisegundos para la animación.
   Comportamiento:
     - Limpia la pantalla usando secuencias ANSI (evita system("clear") y warnings TERM).
     - Imprime todas las filas y columnas carácter por carácter.
     - Pausa la ejecución el tiempo indicado para que la animación sea visible. */
void imprimir_laberinto(char **laberinto, int filas, int columnas, int pausa_ms) {
    printf("\033[H\033[J");                 // Se mueve el cursor al inicio y borra pantalla.
    for (int fila = 0; fila < filas; fila++) {        // Se recorre cada fila.
        for (int columna = 0; columna < columnas; columna++) { // Se recorre cada columna.
            printf("%c", laberinto[fila][columna]);  // Se imprime el carácter actual.
        }
        printf("\n");                         // Se pasa a la siguiente línea (fila).
    }
    usleep(pausa_ms * 1000);                  // Se convierte ms a µs y se duerme ese tiempo.
}

/* Función: generar_laberinto (DFS recursivo)
   Parámetros:
     laberinto -> matriz de caracteres con paredes iniciales.
     fila, columna -> celda actual desde la que se excava.
     filas, columnas -> dimensiones de la matriz.
   Comportamiento:
     - Baraja las cuatro direcciones para hacer la generación aleatoria.
     - Intenta "saltar" dos celdas en cada dirección (para mantener paredes entre celdas),
       y si la celda destino es PARED, abre la pared intermedia y marca la celda destino como CAMINO.
     - Llama recursivamente a sí misma desde la celda destino, hasta agotar opciones.
     - Resultado: laberinto "perfecto" (conectado y sin ciclos). */
void generar_laberinto(char **laberinto, int fila, int columna, int filas, int columnas) {
    int direcciones[4] = {0, 1, 2, 3};       // Se prepara un array con índices de direcciones.

    // Barajar direcciones con un intercambio simple (Fisher–Yates parcial).
    for (int i = 0; i < 4; i++) {
        int j = rand() % 4;                  // Se elige posición aleatoria j en 0..3.
        int temp = direcciones[i];           // Se intercambian direcciones[i] y direcciones[j].
        direcciones[i] = direcciones[j];
        direcciones[j] = temp;
    }

    // Para cada dirección barajada:
    for (int i = 0; i < 4; i++) {
        int direccion = direcciones[i];                              // Dirección escogida.
        int nueva_fila = fila + movimientos[direccion][0] * 2;       // Objetivo 2 pasos en fila.
        int nueva_columna = columna + movimientos[direccion][1] * 2; // Objetivo 2 pasos en columna.

        // Validación: la celda objetivo debe estar dentro del área útil (no en el borde).
        if (nueva_fila > 0 && nueva_fila < filas - 1 &&
            nueva_columna > 0 && nueva_columna < columnas - 1) {
            // Si la celda objetivo aún es pared, se abre camino hacia ella.
            if (laberinto[nueva_fila][nueva_columna] == PARED) {
                // Abrir la pared intermedia (un paso) convirtiéndola en CAMINO.
                laberinto[fila + movimientos[direccion][0]][columna + movimientos[direccion][1]] = CAMINO;
                // Marcar la celda destino como CAMINO.
                laberinto[nueva_fila][nueva_columna] = CAMINO;
                // Repetir recursivamente desde la nueva celda.
                generar_laberinto(laberinto, nueva_fila, nueva_columna, filas, columnas);
            }
        }
    }
}

/* Función: bfs (Breadth-First Search) con animación de expansión y reconstrucción de ruta
   Parámetros:
     laberinto -> matriz del laberinto.
     filas, columnas -> tamaños del laberinto.
     inicio_fila, inicio_columna -> coordenadas del inicio (S).
     salida_fila, salida_columna -> coordenadas de la salida (E).
   Comportamiento:
     - Implementa una cola FIFO para explorar en capas (niveles de distancia).
     - Mantiene matriz "visitado" para no re-enqueuear.
     - Mantiene matriz "padre" para reconstruir el camino una vez alcanzada la salida.
     - Marca nodos explorados con VISITADO durante la animación.
     - Al encontrar la salida, reconstruye el camino y lo marca con RUTA ('*'). */
int bfs(char **laberinto, int filas, int columnas, int inicio_fila, int inicio_columna, int salida_fila, int salida_columna) {
    // Cola de pares [fila, columna], tamaño máximo filas*columnas.
    int cola[filas * columnas][2];
    int frente = 0, fin = 0;                  // Índices de cabeza y cola.

    // Matriz visitado inicializada a 0.
    int visitado[filas][columnas];
    for (int i = 0; i < filas; i++)
        for (int j = 0; j < columnas; j++)
            visitado[i][j] = 0;

    // Matriz padre para reconstruir; cada celda guarda {filaPadre, colPadre}.
    int padre[filas][columnas][2];
    for (int i = 0; i < filas; i++)
        for (int j = 0; j < columnas; j++) {
            padre[i][j][0] = -1;               // Inicialmente sin padre.
            padre[i][j][1] = -1;
        }

    // Encolar el nodo inicial y marcarlo visitado.
    cola[fin][0] = inicio_fila;
    cola[fin][1] = inicio_columna;
    fin++;
    visitado[inicio_fila][inicio_columna] = 1;

    // Bucle principal: mientras la cola no esté vacía.
    while (frente < fin) {
        int fila_actual = cola[frente][0];    // Se saca el elemento en el frente.
        int columna_actual = cola[frente][1];
        frente++;                             // Se avanza el frente.

        // Si la celda actual es la salida, reconstruir la ruta usando 'padre' y terminar.
        if (fila_actual == salida_fila && columna_actual == salida_columna) {
            int f = fila_actual;
            int c = columna_actual;
            // Mientras no volvamos al inicio, pintar la ruta.
            while (!(f == inicio_fila && c == inicio_columna)) {
                if (laberinto[f][c] != INICIO && laberinto[f][c] != SALIDA) {
                    laberinto[f][c] = RUTA;   // Marcar el camino final con '*'.
                }
                int pf = padre[f][c][0];     // Consultar fila del padre.
                int pc = padre[f][c][1];     // Consultar columna del padre.
                f = pf;                      // Avanzar al padre.
                c = pc;
            }
            return 1;                       // Se retorna éxito.
        }

        // Explorar los 4 vecinos ortogonales.
        for (int i = 0; i < 4; i++) {
            int nueva_fila = fila_actual + movimientos[i][0];   // Calcular fila del vecino.
            int nueva_columna = columna_actual + movimientos[i][1]; // Calcular columna del vecino.

            // Condiciones: dentro de límites, no visitado, y no pared.
            if (nueva_fila >= 0 && nueva_fila < filas &&
                nueva_columna >= 0 && nueva_columna < columnas &&
                !visitado[nueva_fila][nueva_columna] &&
                laberinto[nueva_fila][nueva_columna] != PARED) {

                // Encolar vecino y marcar padre.
                cola[fin][0] = nueva_fila;
                cola[fin][1] = nueva_columna;
                fin++;
                visitado[nueva_fila][nueva_columna] = 1;
                padre[nueva_fila][nueva_columna][0] = fila_actual;
                padre[nueva_fila][nueva_columna][1] = columna_actual;

                // Si es un CAMINO, marcarlo como VISITADO para la animación.
                if (laberinto[nueva_fila][nueva_columna] == CAMINO) {
                    laberinto[nueva_fila][nueva_columna] = VISITADO;
                }
                // Redibujar el laberinto para mostrar la expansión (pausa larga para apreciar).
                imprimir_laberinto(laberinto, filas, columnas, 300);
            }
        }
    }
    // No debería llegar aquí porque el laberinto generado garantiza conectividad.
    return 0;
}

/* Función principal (main)
   Flujo general:
     - Leer tamaño deseado por el usuario.
     - Asegurar dimensiones mínimas y que sean impares.
     - Reservar memoria y inicializar todo como paredes.
     - Generar laberinto a partir de (1,1).
     - Colocar INICIO y SALIDA.
     - Mostrar laberinto y ejecutar BFS con animación.
     - Liberar memoria y terminar. */
int main() {
    srand(time(NULL));                         // Semilla para rand() basada en tiempo real.

    int filas, columnas;
    printf("Ingrese filas (>=5, impar): ");    // Solicitar número de filas al usuario.
    scanf("%d", &filas);                       // Leer entero para filas.
    printf("Ingrese columnas (>=5, impar): "); // Solicitar número de columnas al usuario.
    scanf("%d", &columnas);                    // Leer entero para columnas.

    // Asegurar valores mínimos y que sean impares para la construcción del laberinto.
    if (filas < 5) filas = 5;                  // Mínimo 5 filas.
    if (columnas < 5) columnas = 5;            // Mínimo 5 columnas.
    if (filas % 2 == 0) filas++;               // Hacer impar si fue par.
    if (columnas % 2 == 0) columnas++;         // Hacer impar si fue par.

    // Reservar matriz dinámica de punteros: cada fila es un char*.
    char **laberinto = malloc(filas * sizeof(char *));
    for (int i = 0; i < filas; i++) {
        laberinto[i] = malloc(columnas * sizeof(char));  // Reservar cada fila.
        for (int j = 0; j < columnas; j++) {
            laberinto[i][j] = PARED;    // Inicializar todas las celdas como PARED.
        }
    }

    // Preparar punto de inicio para generar el laberinto: (1,1) (celda interna).
    laberinto[1][1] = CAMINO;                // Habilitar la celda inicial como camino.
    generar_laberinto(laberinto, 1, 1, filas, columnas); // Generar todo el laberinto.

    // Definir coordenadas explícitas para INICIO y SALIDA dentro de los bordes internos.
    int inicio_fila = 1, inicio_columna = 1;                  // Esquina superior interna.
    int salida_fila = filas - 2, salida_columna = columnas - 2; // Esquina inferior interna.
    laberinto[inicio_fila][inicio_columna] = INICIO;          // Marcar 'S'.
    laberinto[salida_fila][salida_columna] = SALIDA;          // Marcar 'E'.

    // Mostrar inicialmente el laberinto generado (pausa larga para observar).
    imprimir_laberinto(laberinto, filas, columnas, 1000);

    // Ejecutar BFS con animación; el resultado se mostrará en pantalla.
    if (bfs(laberinto, filas, columnas, inicio_fila, inicio_columna, salida_fila, salida_columna)) {
        imprimir_laberinto(laberinto, filas, columnas, 0);   // Mostrar mapa final sin pausa.
        printf("✅ Camino BFS encontrado y marcado con '%c'\n", RUTA); // Mensaje final.
    }

    // Liberar la memoria dinámica asignada para cada fila y luego el puntero de filas.
    for (int i = 0; i < filas; i++) free(laberinto[i]);    // Liberar cada fila.
    free(laberinto);                                      // Liberar el arreglo de punteros.

    return 0; // Fin del programa, devolver 0 indica terminación exitosa.
}