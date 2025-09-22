// Incluyo librerías necesarias
#include <stdio.h>   // printf, putchar
#include <stdlib.h>  // malloc, free, rand, strtol
#include <time.h>    // time (semilla aleatoria), clock
#include <unistd.h>  // usleep (pausa en ms)
#include <string.h>  // fgets, strchr

// Defino símbolos para el laberinto
#define PARED    '#'   // pared
#define CAMINO   ' '   // camino libre
#define VISITADO '.'   // rastro temporal
#define INICIO   'I'   // inicio
#define SALIDA   'S'   // salida
#define RUTA     '*'   // mejor ruta encontrada
#define PERSONAJE 'P'  // personaje en movimiento

// Movimientos posibles: arriba, abajo, izquierda, derecha
int movimientos[4][2] = {
    {-1, 0}, {1, 0}, {0, -1}, {0, 1}
};

// -------------------- FUNCIONES --------------------

// esta funcion recibe el laberinto, la posición del personaje, lo dibuja en pantalla, y se pausa un momento para que parezca animado
void imprimir_laberinto(char **laberinto, int filas, int columnas, int pausa_ms, int fila_actual, int columna_actual) {
    printf("\033[H\033[J"); // limpia pantalla
    for (int i = 0; i < filas; i++) { // despues de cada bucle incrementa i en 1
        for (int j = 0; j < columnas; j++) { // despues de cada bucle incrementa j en 1
            if (i == fila_actual && j == columna_actual) {
                putchar(PERSONAJE); // dibuja P
            } else {
                putchar(laberinto[i][j]); // dibuja el laberinto  
            }
        }
        putchar('\n'); // salto de línea
    }
    usleep(pausa_ms * 1000); // pausa para animación
}

// Genera el laberinto usando DFS recursivo
void generar_laberinto(char **laberinto, int fila, int columna, int filas, int columnas) {
    int direcciones[4] = {0,1,2,3}; // posibles direcciones

    // esta funcion lq hace es mezclar aletaroriamente las 4 direcciones
    for (int i = 0; i < 4; i++) {
        int j = rand() % 4;
        int tmp = direcciones[i];
        direcciones[i] = direcciones[j];
        direcciones[j] = tmp;
    }

    // Intentar moverse en cada dirección
    for (int contador = 0; contador < 4; contador++) { // bucle que se repite 4 veces 
        int dir = direcciones[contador]; // toma una direccion de la lista
        int nueva_fila = fila + movimientos[dir][0] * 2; // calcula la nueva fila
        int nueva_columna = columna + movimientos[dir][1] * 2; // calcula la nueva columna

        // Si está dentro del laberinto y es pared se abre camino
        if (nueva_fila > 0 && nueva_fila < filas - 1 && nueva_columna > 0 && nueva_columna < columnas - 1) { // comprueba si esta dentro del laberinto
            if (laberinto[nueva_fila][nueva_columna] == PARED) { // verifica si la celda es una pared
                laberinto[fila + movimientos[dir][0]][columna + movimientos[dir][1]] = CAMINO; // abre la pared intermedia entre la celda destino
                laberinto[nueva_fila][nueva_columna] = CAMINO; // abrir celda destino luego
                generar_laberinto(laberinto, nueva_fila, nueva_columna, filas, columnas); // repito lo mismo pero con la nueva posicion
            }
        }
    }
}

// uso busqueda por profundidad para encontrar la ruta más corta
int bfs_find_path(char **laberinto, int filas, int columnas, int inicio_i, int inicio_j, int salida_i, int salida_j,
    int **out_path, int *out_len) {
    int total = filas * columnas; // total de celdas
    int *visitado = calloc(total, sizeof(int)); // visitados
    int *padre_fila = malloc(total * sizeof(int)); // padre fila
    int *padre_columna = malloc(total * sizeof(int)); // padre col
    for (int i = 0; i < total; i++) { padre_fila[i] = -1; padre_columna[i] = -1; }

    // Cola BFS
    int *cola_fila = malloc(total * sizeof(int)); // guarda las posiciones de las filas visitadas
    int *cola_columna = malloc(total * sizeof(int)); // guarda las posiciones de las columnas visitadas
    int frente = 0, fin = 0; // indices vacios para manejar la cola

    // Encolar inicio
    cola_fila[fin] = inicio_i; cola_columna[fin] = inicio_j; fin++; // agrego las posiciones iniciales a la cola 
    visitado[inicio_i * columnas + inicio_j] = 1; // marca la celda inicial como visitada 

    int found = 0; // encontrado
    while (frente < fin) { // empiezo un bucle mientras la cola no este vacia
        int fila_actual = cola_fila[frente]; // lee la fila del elemento q esta en el frente de la cola
        int columna_actual = cola_columna[frente]; // lee la columna del elemnto q esta en el frente de la cola
        frente++; // incrementa el frente en 1

        if (fila_actual == salida_i && columna_actual == salida_j) { found = 1; break; } // llegó a la salida

        // Revisar vecinos
        for (int direcc = 0; direcc < 4; direcc++) { // recorre las 4 direcciones 
            int nuevafila = fila_actual + movimientos[direcc][0]; // calcula la fila del vecino en esa dirreccion
            int nuevacolumna = columna_actual + movimientos[direcc][1]; // hace lo mismo pero con la columna
            if (nuevafila >= 0 && nuevafila < filas && nuevacolumna >= 0 && nuevacolumna < columnas) { // verifica que este dentro del tablero
                int idx = nuevafila * columnas + nuevacolumna; // convierte las 2 coordenadas a 1
                if (!visitado[idx] && laberinto[nuevafila][nuevacolumna] != PARED) { // comprueba si no fue visitado y si no es una pared
                    visitado[idx] = 1; // marca el vecino como visitado para no marcarlo otra vez
                    padre_fila[idx] = fila_actual; // guarda el padre fila
                    padre_columna[idx] = columna_actual; // guarda el padre columna
                    cola_fila[fin] = nuevafila; cola_columna[fin] = nuevacolumna; fin++; // guarda la fila y la columna en posición en fin y Luego aumenta fin
                }
            }
        }
    }

    // Si no encontró ruta
    if (!found) {
        free(visitado); free(padre_fila); free(padre_columna); free(cola_fila); free(cola_columna); // se devuelve esa memoria al sistema y se evita una fuga de memoria
        *out_path = NULL; *out_len = 0; // significa que no hay ruta y q no hay camino
        return 0;
    }

    // Reconstruir ruta en reversa
    int *reversa = malloc(total * 2 * sizeof(int)); // guardao el camino desde la salida hasta el inicio
    int cont = 0; // indica cuántos pasos del camino hemos guardado
    int camino_fila = salida_i, camino_columna = salida_j; // InicializO las variables de posición en la salida del laberinto
    while (!(camino_fila == inicio_i && camino_columna == inicio_j)) { // creo un bucle que recorra el camino en reversa hasta lleagr al inicio
        reversa[cont*2] = camino_fila; // guardo la posicion de fila actual
        reversa[cont*2 + 1] = camino_columna; // lo mismo pero con columna
        cont++; // incremento el contador
        int idx = camino_fila * columnas + camino_columna; // Calcula el índice lineal de la celda en los arrays padre_fila y padre_columna
        camino_fila = padre_fila[idx]; camino_columna = padre_columna[idx]; // Retrocedemos al padre de la celda actual
    }
    reversa[cont*2] = inicio_i; reversa[cont*2 + 1] = inicio_j; cont++; // guardo elcamino completo de salida a inicio en  reversa

    // Invertir ruta para que vaya de inicio a salida
    int *camino = malloc(cont * 2 * sizeof(int)); // guardo la ruta desde inicio a salida
    for (int i = 0; i < cont; i++) { // invierte el array reversa 
        camino[i*2]     = reversa[(cont-1-i)*2]; // recorre reversa desde el final hasta el inicio.
        camino[i*2 + 1] = reversa[(cont-1-i)*2 + 1]; // guarda la fila y la columna para cada paso
    }

    // Libero memoria de arrays temporales
    free(reversa);
    free(visitado); free(padre_fila); free(padre_columna); free(cola_fila); free(cola_columna);

    *out_path = camino; // asigno la ruta final al puntero que recibirá el programa principal
    *out_len = cont;   // guarda la cantidad de pasos de la ruta
    return 1; // Devuelve 1 para indicar que sí se encontró un camino desde inicio hasta salida
}

// Anima al personaje moviéndose por la ruta
void animar_personaje(char **laberinto, int filas, int columnas,int *camino, int path_len, int pausa_ms,
    int inicio_i, int inicio_j, int salida_i, int salida_j) {
    if (path_len <= 0) return; // Si la ruta está vacía, no hace nada y sale de la función

    // Recorrido con puntos "."
    for (int i = 0; i < path_len; i++) { // Bucle que recorre cada paso del camino
        if (i > 0) {
            int padre_fila = camino[(i-1)*2], padre_columna = camino[(i-1)*2 + 1]; // Obtiene la celda anterior (padre_fila, padre_columna)
            if (!(padre_fila == inicio_i && padre_columna == inicio_j) && !(padre_fila == salida_i && padre_columna == salida_j)) { 
                laberinto[padre_fila][padre_columna] = VISITADO; // marca con . el recorrido
            }
        }
        int camino_fila = camino[i*2], camino_columna = camino[i*2 + 1];
        imprimir_laberinto(laberinto, filas, columnas, pausa_ms, camino_fila, camino_columna);
    }

    // Marcar la mejor ruta con "*"
    for (int i = 0; i < path_len; i++) {
        int fila_actual = camino[i*2], columna_actual = camino[i*2 + 1];
        if (!(fila_actual == inicio_i && columna_actual == inicio_j) && !(fila_actual == salida_i && columna_actual == salida_j)) {
            laberinto[fila_actual][columna_actual] = RUTA;
        }
    }

    // Imprimir resultado final
    imprimir_laberinto(laberinto, filas, columnas, 0, -1, -1);
}

// -------------------- MAIN --------------------

int main() {
    srand(time(NULL)); // semilla aleatoria
    int filas, columnas;
    char buf[64];

    clock_t start_total = clock();  // medir tiempo total

    // Pedir filas
    printf("Ingrese filas (>=5, impar) [enter = 10]: ");
    fflush(stdout);
    if (fgets(buf, sizeof(buf), stdin) == NULL || buf[0] == '\n') {
        filas = 10;
    } else {
        filas = atoi(buf);
    }

    // Pedir columnas
    printf("Ingrese columnas (>=5, impar) [enter = 10]: ");
    fflush(stdout);
    if (fgets(buf, sizeof(buf), stdin) == NULL || buf[0] == '\n') {
        columnas = 10;
    } else {
        columnas = atoi(buf);
    }

    // Ajustar valores mínimos e impares
    if (filas < 5) filas = 5;
    if (columnas < 5) columnas = 5;
    if (filas % 2 == 0) filas++;
    if (columnas % 2 == 0) columnas++;

    // Crear matriz dinámica
    char **laberinto = malloc(filas * sizeof(char*));
    for (int i = 0; i < filas; i++) {
        laberinto[i] = malloc(columnas * sizeof(char));
        for (int j = 0; j < columnas; j++) laberinto[i][j] = PARED;
    }

    // Generar laberinto
    clock_t start_gen = clock();
    laberinto[1][1] = CAMINO;
    generar_laberinto(laberinto, 1, 1, filas, columnas);
    clock_t end_gen = clock();

    // Marcar inicio y salida
    int inicio_i = 1, inicio_j = 1;
    int salida_i = filas - 2, salida_j = columnas - 2;
    laberinto[inicio_i][inicio_j] = INICIO;
    laberinto[salida_i][salida_j] = SALIDA;

    imprimir_laberinto(laberinto, filas, columnas, 800, -1, -1);

    // Buscar camino con BFS
    int *camino = NULL; int path_len = 0;
    clock_t start_bfs = clock();
    if (bfs_find_path(laberinto, filas, columnas, inicio_i, inicio_j, salida_i, salida_j, &camino, &path_len)) {
        clock_t end_bfs = clock();
        printf("Ruta encontrada. Longitud: %d pasos\n", path_len);
        printf("Tiempo BFS: %.4f segundos\n",
               (double)(end_bfs - start_bfs) / CLOCKS_PER_SEC);

        animar_personaje(laberinto, filas, columnas, camino, path_len, 180, inicio_i, inicio_j, salida_i, salida_j);
        free(camino);
    } else {
        clock_t end_bfs = clock();
        printf("No se encontró ruta.\n");
        printf("Tiempo BFS: %.4f segundos\n",
               (double)(end_bfs - start_bfs) / CLOCKS_PER_SEC);
    }

    // Mostrar laberinto final
    imprimir_laberinto(laberinto, filas, columnas, 0, -1, -1);
    printf("Fin.\n");

    // Liberar memoria
    for (int i = 0; i < filas; i++) free(laberinto[i]);
    free(laberinto);

    clock_t end_total = clock();

    // Reportar tiempos
    printf("\n--- Mediciones ---\n");
    printf("Tiempo generación laberinto: %.4f segundos\n",
           (double)(end_gen - start_gen) / CLOCKS_PER_SEC);
    printf("Tiempo total del programa: %.4f segundos\n",
           (double)(end_total - start_total) / CLOCKS_PER_SEC);

    return 0;
}