#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>


int P, R; // Processes, Resources
int *avail;
int **alloc, **max, **need;

// --- Memory Management ---
void init_memory(int p, int r) {
    P = p; R = r;
    avail = (int*)malloc(R * sizeof(int));
    alloc = (int**)malloc(P * sizeof(int*));
    max = (int**)malloc(P * sizeof(int*));
    need = (int**)malloc(P * sizeof(int*));
    for(int i=0; i<P; i++) {
        alloc[i] = (int*)malloc(R * sizeof(int));
        max[i] = (int*)malloc(R * sizeof(int));
        need[i] = (int*)malloc(R * sizeof(int));
    }
}

void free_memory() {
    free(avail);
    for(int i=0; i<P; i++) { free(alloc[i]); free(max[i]); free(need[i]); }
    free(alloc); free(max); free(need);
}

// --- Banker's Algorithm (Safety Check) ---
bool is_safe(bool verbose, double *cpu_time) {
    clock_t start = clock();
    
    int *work = (int*)malloc(R * sizeof(int));
    bool *finish = (bool*)malloc(P * sizeof(bool));
    for(int i=0; i<R; i++) work[i] = avail[i];
    for(int i=0; i<P; i++) finish[i] = false;

    int count = 0;
    while (count < P) {
        bool found = false;
        for (int p = 0; p < P; p++) {
            if (!finish[p]) {
                int j;
                for (j = 0; j < R; j++)
                    if (need[p][j] > work[j]) break;
                
                if (j == R) { // Process p can finish
                    for (int k = 0; k < R; k++) work[k] += alloc[p][k];
                    finish[p] = true;
                    found = true;
                    count++;
                }
            }
        }
        if (!found) break; // Deadlock detection 
    }

    if (cpu_time) *cpu_time = ((double)(clock() - start)) / CLOCKS_PER_SEC;
    
    free(work);
    free(finish);
    return (count == P);
}

// --- RAG (Resource Allocation Graph) Visualization ---
void print_rag() {
    printf("\n--- Resource Allocation Graph (RAG) Edges ---\n");
    // Assignment Edges: Resource -> Process (based on Allocation)
    for(int i=0; i<P; i++) {
        for(int j=0; j<R; j++) {
            if(alloc[i][j] > 0) 
                printf("  R%d --(%d)--> P%d (Assignment)\n", j, alloc[i][j], i);
        }
    }
    // Request Edges: Process to Resource (based on Need)
    for(int i=0; i<P; i++) {
        for(int j=0; j<R; j++) {
            if(need[i][j] > 0) 
                printf("  P%d --(%d)--> R%d (Request)\n", i, need[i][j], j);
        }
    }
    printf("---------------------------------------------\n");
}

// --- Single Run Analysis ---
void single_run_analysis(int tp, int tr) {
    init_memory(tp, tr);
    
    // Filling with dummy safe data for benchmarking
    for(int j=0; j<tr; j++) avail[j] = 1000;
    for(int i=0; i<tp; i++) {
        for(int j=0; j<tr; j++) {
            alloc[i][j] = 1;
            max[i][j] = 2;
            need[i][j] = max[i][j] - alloc[i][j];
        }
    }

    double time_taken;
    is_safe(false, &time_taken);
    
    // Only print RAG if dataset is small enough to be readable
    if (tp * tr <= 5000) {
        print_rag();
    } else {
        printf("\n[RAG omitted for very large dataset > 5000 interactions]\n");
    }

    long mem_usage = (tp * tr * 3 * sizeof(int)) + (tr * sizeof(int)); // approx matrices + avail
    printf("%-10d %-10d %-15.6f %-15ld\n", tp, tr, time_taken, mem_usage);
    
    free_memory();
}

// --- Main ---
int main(int argc, char *argv[]) {
    srand(time(NULL));
    
    // Only Mode 3 (Manual Single Run) is used by the server
    if (argc == 4 && atoi(argv[1]) == 3) {
        printf("%-10s %-10s %-15s %-15s\n", "Procs(N)", "Res(M)", "CPU Time(s)", "Memory(bytes)");
        single_run_analysis(atoi(argv[2]), atoi(argv[3]));
        return 0;
    }
    return 0;
}
