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
#define INICIO   'S'   // inicio
#define SALIDA   'E'   // salida
#define RUTA     '*'   // mejor ruta encontrada
#define PERSONAJE 'P'  // personaje en movimiento

// Movimientos posibles: arriba, abajo, izquierda, derecha
int movimientos[4][2] = {
    {-1, 0}, {1, 0}, {0, -1}, {0, 1}
};

// -------------------- FUNCIONES --------------------

// Dibuja el laberinto en pantalla
void imprimir_laberinto(char **lab, int filas, int columnas, int pausa_ms, int persona_r, int persona_c) {
    printf("\033[H\033[J"); // limpia pantalla
    for (int i = 0; i < filas; i++) {
        for (int j = 0; j < columnas; j++) {
            if (i == persona_r && j == persona_c) {
                putchar(PERSONAJE); // dibuja P
            } else {
                putchar(lab[i][j]); // dibuja el laberinto
            }
        }
        putchar('\n'); // salto de línea
    }
    usleep(pausa_ms * 1000); // pausa para animación
}

// Genera el laberinto usando DFS recursivo
void generar_laberinto(char **lab, int fila, int columna, int filas, int columnas) {
    int direcciones[4] = {0,1,2,3}; // posibles direcciones

    // Mezclar las direcciones aleatoriamente
    for (int i = 0; i < 4; i++) {
        int j = rand() % 4;
        int tmp = direcciones[i];
        direcciones[i] = direcciones[j];
        direcciones[j] = tmp;
    }

    // Intentar moverse en cada dirección
    for (int k = 0; k < 4; k++) {
        int dir = direcciones[k];
        int nf = fila + movimientos[dir][0] * 2;
        int nc = columna + movimientos[dir][1] * 2;

        // Si está dentro del laberinto y es pared se abre camino
        if (nf > 0 && nf < filas - 1 && nc > 0 && nc < columnas - 1) {
            if (lab[nf][nc] == PARED) {
                lab[fila + movimientos[dir][0]][columna + movimientos[dir][1]] = CAMINO; // abrir pared
                lab[nf][nc] = CAMINO; // abrir celda destino
                generar_laberinto(lab, nf, nc, filas, columnas); // recursión
            }
        }
    }
}

// BFS para encontrar la ruta más corta
int bfs_find_path(char **lab, int filas, int columnas,
                  int si, int sj, int ei, int ej,
                  int **out_path, int *out_len) {
    int total = filas * columnas; // total de celdas
    int *visitado = calloc(total, sizeof(int)); // visitados
    int *pr = malloc(total * sizeof(int)); // padre fila
    int *pc = malloc(total * sizeof(int)); // padre col
    for (int i = 0; i < total; i++) { pr[i] = -1; pc[i] = -1; }

    // Cola BFS
    int *qf = malloc(total * sizeof(int));
    int *qc = malloc(total * sizeof(int));
    int frente = 0, fin = 0;

    // Encolar inicio
    qf[fin] = si; qc[fin] = sj; fin++;
    visitado[si * columnas + sj] = 1;

    int found = 0; // encontrado
    while (frente < fin) {
        int r = qf[frente];
        int c = qc[frente];
        frente++;

        if (r == ei && c == ej) { found = 1; break; } // llegó a la salida

        // Revisar vecinos
        for (int d = 0; d < 4; d++) {
            int nr = r + movimientos[d][0];
            int nc = c + movimientos[d][1];
            if (nr >= 0 && nr < filas && nc >= 0 && nc < columnas) {
                int idx = nr * columnas + nc;
                if (!visitado[idx] && lab[nr][nc] != PARED) {
                    visitado[idx] = 1;
                    pr[idx] = r; // guardar padre
                    pc[idx] = c;
                    qf[fin] = nr; qc[fin] = nc; fin++; // encolar
                }
            }
        }
    }

    // Si no encontró ruta
    if (!found) {
        free(visitado); free(pr); free(pc); free(qf); free(qc);
        *out_path = NULL; *out_len = 0;
        return 0;
    }

    // Reconstruir ruta en reversa
    int *rev = malloc(total * 2 * sizeof(int));
    int cnt = 0;
    int cr = ei, cc = ej;
    while (!(cr == si && cc == sj)) {
        rev[cnt*2] = cr;
        rev[cnt*2 + 1] = cc;
        cnt++;
        int idx = cr * columnas + cc;
        cr = pr[idx]; cc = pc[idx];
    }
    rev[cnt*2] = si; rev[cnt*2 + 1] = sj; cnt++;

    // Invertir ruta para que vaya de inicio a salida
    int *path = malloc(cnt * 2 * sizeof(int));
    for (int i = 0; i < cnt; i++) {
        path[i*2]     = rev[(cnt-1-i)*2];
        path[i*2 + 1] = rev[(cnt-1-i)*2 + 1];
    }

    // Liberar temporales
    free(rev);
    free(visitado); free(pr); free(pc); free(qf); free(qc);

    *out_path = path; // devolver ruta
    *out_len = cnt;   // longitud
    return 1;
}

// Anima al personaje moviéndose por la ruta
void animar_personaje(char **lab, int filas, int columnas,
                      int *path, int path_len, int pausa_ms,
                      int si, int sj, int ei, int ej) {
    if (path_len <= 0) return;

    // Recorrido con puntos "."
    for (int i = 0; i < path_len; i++) {
        if (i > 0) {
            int pr = path[(i-1)*2], pc = path[(i-1)*2 + 1];
            if (!(pr == si && pc == sj) && !(pr == ei && pc == ej)) {
                lab[pr][pc] = VISITADO; // rastro
            }
        }
        int cr = path[i*2], cc = path[i*2 + 1];
        imprimir_laberinto(lab, filas, columnas, pausa_ms, cr, cc);
    }

    // Marcar la mejor ruta con "*"
    for (int i = 0; i < path_len; i++) {
        int r = path[i*2], c = path[i*2 + 1];
        if (!(r == si && c == sj) && !(r == ei && c == ej)) {
            lab[r][c] = RUTA;
        }
    }

    // Imprimir resultado final
    imprimir_laberinto(lab, filas, columnas, 0, -1, -1);
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
    char **lab = malloc(filas * sizeof(char*));
    for (int i = 0; i < filas; i++) {
        lab[i] = malloc(columnas * sizeof(char));
        for (int j = 0; j < columnas; j++) lab[i][j] = PARED;
    }

    // Generar laberinto
    clock_t start_gen = clock();
    lab[1][1] = CAMINO;
    generar_laberinto(lab, 1, 1, filas, columnas);
    clock_t end_gen = clock();

    // Marcar inicio y salida
    int si = 1, sj = 1;
    int ei = filas - 2, ej = columnas - 2;
    lab[si][sj] = INICIO;
    lab[ei][ej] = SALIDA;

    imprimir_laberinto(lab, filas, columnas, 800, -1, -1);

    // Buscar camino con BFS
    int *path = NULL; int path_len = 0;
    clock_t start_bfs = clock();
    if (bfs_find_path(lab, filas, columnas, si, sj, ei, ej, &path, &path_len)) {
        clock_t end_bfs = clock();
        printf("Ruta encontrada. Longitud: %d pasos\n", path_len);
        printf("Tiempo BFS: %.4f segundos\n",
               (double)(end_bfs - start_bfs) / CLOCKS_PER_SEC);

        animar_personaje(lab, filas, columnas, path, path_len, 180, si, sj, ei, ej);
        free(path);
    } else {
        clock_t end_bfs = clock();
        printf("No se encontró ruta.\n");
        printf("Tiempo BFS: %.4f segundos\n",
               (double)(end_bfs - start_bfs) / CLOCKS_PER_SEC);
    }

    // Mostrar laberinto final
    imprimir_laberinto(lab, filas, columnas, 0, -1, -1);
    printf("Fin.\n");

    // Liberar memoria
    for (int i = 0; i < filas; i++) free(lab[i]);
    free(lab);

    clock_t end_total = clock();

    // Reportar tiempos
    printf("\n--- Mediciones ---\n");
    printf("Tiempo generación laberinto: %.4f segundos\n",
           (double)(end_gen - start_gen) / CLOCKS_PER_SEC);
    printf("Tiempo total del programa: %.4f segundos\n",
           (double)(end_total - start_total) / CLOCKS_PER_SEC);

    return 0;
}
