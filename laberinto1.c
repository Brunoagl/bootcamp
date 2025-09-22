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

    // Mezclar las direcciones aleatoriamente
    for (int i = 0; i < 4; i++) {
        int j = rand() % 4;
        int tmp = direcciones[i];
        direcciones[i] = direcciones[j];
        direcciones[j] = tmp;
    }

    // Intentar moverse en cada dirección
    for (int contador = 0; contador < 4; contador++) {
        int dir = direcciones[contador];
        int nueva_fila = fila + movimientos[dir][0] * 2;
        int nueva_columna = columna + movimientos[dir][1] * 2;

        // Si está dentro del laberinto y es pared se abre camino
        if (nueva_fila > 0 && nueva_fila < filas - 1 && nueva_columna > 0 && nueva_columna < columnas - 1) {
            if (laberinto[nueva_fila][nueva_columna] == PARED) {
                laberinto[fila + movimientos[dir][0]][columna + movimientos[dir][1]] = CAMINO; // abrir pared
                laberinto[nueva_fila][nueva_columna] = CAMINO; // abrir celda destino
                generar_laberinto(laberinto, nueva_fila, nueva_columna, filas, columnas); // recursión
            }
        }
    }
}

// BFS para encontrar la ruta más corta
int bfs_find_path(char **laberinto, int filas, int columnas, int inicio_i, int inicio_j, int salida_i, int salida_j,
    int **out_path, int *out_len) {
    int total = filas * columnas; // total de celdas
    int *visitado = calloc(total, sizeof(int)); // visitados
    int *padre_fila = malloc(total * sizeof(int)); // padre fila
    int *padre_columna = malloc(total * sizeof(int)); // padre col
    for (int i = 0; i < total; i++) { padre_fila[i] = -1; padre_columna[i] = -1; }

    // Cola BFS
    int *cola_fila = malloc(total * sizeof(int));
    int *cola_columna = malloc(total * sizeof(int));
    int frente = 0, fin = 0;

    // Encolar inicio
    cola_fila[fin] = inicio_i; cola_columna[fin] = inicio_j; fin++;
    visitado[inicio_i * columnas + inicio_j] = 1;

    int found = 0; // encontrado
    while (frente < fin) {
        int fila_actual = cola_fila[frente];
        int columna_actual = cola_columna[frente];
        frente++;

        if (fila_actual == salida_i && columna_actual == salida_j) { found = 1; break; } // llegó a la salida

        // Revisar vecinos
        for (int direcc = 0; direcc < 4; direcc++) {
            int nuevafila = fila_actual + movimientos[direcc][0];
            int nuevacolumna = columna_actual + movimientos[direcc][1];
            if (nuevafila >= 0 && nuevacolumna < filas && nuevacolumna >= 0 && nuevacolumna < columnas) {
                int idx = nuevafila * columnas + nuevacolumna;
                if (!visitado[idx] && laberinto[nuevafila][nuevacolumna] != PARED) {
                    visitado[idx] = 1;
                    padre_fila[idx] = r; // guardar padre
                    padre_columna[idx] = c;
                    cola_fila[fin] = nuevafila; cola_columna[fin] = nuevacolumna; fin++; // encolar
                }
            }
        }
    }

    // Si no encontró ruta
    if (!found) {
        free(visitado); free(padre_fila); free(padre_columna); free(cola_fila); free(cola_columna);
        *out_path = NULL; *out_len = 0;
        return 0;
    }

    // Reconstruir ruta en reversa
    int *reversa = malloc(total * 2 * sizeof(int));
    int cont = 0;
    int camino_fila = salida_i, camino_columna = salida_j;
    while (!(camino_fila == inicio_i && camino_columna == inicio_j)) {
        reversa[cont*2] = camino_fila;
        reversa[cont*2 + 1] = camino_columna;
        cont++;
        int idx = camino_fila * columnas + camino_columna;
        camino_fila = padre_fila[idx]; camino_columna = padre_columna[idx];
    }
    reversa[cont*2] = inicio_i; reversa[cont*2 + 1] = inicio_j; cont++;

    // Invertir ruta para que vaya de inicio a salida
    int *path = malloc(cont * 2 * sizeof(int));
    for (int i = 0; i < cont; i++) {
        path[i*2]     = reversa[(cont-1-i)*2];
        path[i*2 + 1] = reversa[(cont-1-i)*2 + 1];
    }

    // Liberar temporales
    free(reversa);
    free(visitado); free(padre_fila); free(padre_columna); free(cola_fila); free(cola_columna);

    *out_path = path; // devolver ruta
    *out_len = cont;   // longitud
    return 1;
}

// Anima al personaje moviéndose por la ruta
void animar_personaje(char **laberinto, int filas, int columnas,int *path, int path_len, int pausa_ms,
    int inicio_i, int inicio_j, int salida_i, int salida_j) {
    if (path_len <= 0) return;

    // Recorrido con puntos "."
    for (int i = 0; i < path_len; i++) {
        if (i > 0) {
            int padre_fila = path[(i-1)*2], padre_columna = path[(i-1)*2 + 1];
            if (!(padre_fila == inicio_i && padre_columna == inicio_j) && !(padre_fila == salida_i && padre_columna == salida_j)) {
                laberinto[padre_fila][padre_columna] = VISITADO; // rastro
            }
        }
        int camino_fila = path[i*2], camino_columna = path[i*2 + 1];
        imprimir_laberinto(laberinto, filas, columnas, pausa_ms, camino_fila, camino_columna);
    }

    // Marcar la mejor ruta con "*"
    for (int i = 0; i < path_len; i++) {
        int fila_actual = path[i*2], columna_actual = path[i*2 + 1];
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
    int *path = NULL; int path_len = 0;
    clock_t start_bfs = clock();
    if (bfs_find_path(laberinto, filas, columnas, inicio_i, inicio_j, salida_i, salida_j, &path, &path_len)) {
        clock_t end_bfs = clock();
        printf("Ruta encontrada. Longitud: %d pasos\n", path_len);
        printf("Tiempo BFS: %.4f segundos\n",
               (double)(end_bfs - start_bfs) / CLOCKS_PER_SEC);

        animar_personaje(laberinto, filas, columnas, path, path_len, 180, inicio_i, inicio_j, salida_i, salida_j);
        free(path);
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
