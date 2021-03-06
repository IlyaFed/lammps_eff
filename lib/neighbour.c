#include "neighbour.h"
#include <cmath>
#include <iostream>

double get_r(double x, double y, double z, double x_g, double y_g, double z_g, double *wall){
    double dx = fmin( fabs(x - x_g), fabs( x + wall[0] - x_g) );
    dx = fmin( dx, fabs( x - wall[0] - x_g) );
    
    double dy = fmin( fabs(y - y_g), fabs( y + wall[1] - y_g) );
    dy = fmin( dy, fabs( y - wall[1] - y_g) );

    double dz = fmin( fabs(z - z_g), fabs( z + wall[2] - z_g) );
    dz = fmin( dz, fabs( z - wall[2] - z_g) );

    return dz*dz + dy*dy + dx*dx;
}

int* neighbour_list( double* x, double* y, double* z, double* type, double* wall, double cut, int n){
    int* list = new int[n*2 + 8]; // here we will return bonding molecules[n], types of every particle[n], distribution[7 (e, H+, H, H-, H2+, H2, H3+, H3]
    int* k_list_ion = new int[n];
    int* k_list_el = new int[n];
    for (int l = 0; l < n*2 + 8; l ++)
        list[l] = 0;

    for (int l = 0; l < n; l ++){
        k_list_el[l] = 0;
        k_list_ion[l] = 0;
    }

    double dist;
    int k = 1;
    for (int i = 0; i < n; i ++){
        if (list[i] == 0){
            list[i] = k;
            k++;
            if (type[i] == 1.0)
                k_list_ion[list[i]] ++;

            if (type[i] == 2.0)
                k_list_el[list[i]] ++;
        }
        for (int j = i+1; j < n; j++){
            dist = get_r(x[i], y[i], z[i], x[j], y[j], z[j],  wall);
            if (dist < cut){
                list[j] = list[i];
                if (type[j] == 1)
                    k_list_ion[list[j]] ++;
                if (type[j] == 2)
                    k_list_el[list[j]] ++;
            }
        }
    }
    for (int i = 0; i < n; i++){
        list[i+n] = k_list_ion[list[i]];
    }

    int el, ion;
    for (int j = 0; j < k; j++){
        el = k_list_el[j];
        ion = k_list_ion[j];
        // e
        if ( (el == 1) && (ion == 0))
            list[n*2 + 0] ++;
        // H+
        if ( (el == 0) && (ion == 1))
            list[n*2 + 1] ++;
        // H
        if ( (el == 1) && (ion == 1))
            list[n*2 + 2] ++;
        // H2+
        if ( (el == 1) && (ion == 2))
            list[n*2 + 3] ++;
        // H2
        if ( (el == 2) && (ion == 2))
            list[n*2 + 4] ++;
        // H3+
        if ( (el == 2) && (ion == 3))
            list[n*2 + 5] ++;
        // H3
        if ( (el == 3) && (ion == 3))
            list[n*2 + 6] ++;

        // H-
        if ( (el == 2) && (ion == 1) ){
            list[n*2 + 7] += el + ion;
        }
    }

    return list;
}

void find_neighbour( int* list, int* k_list_ion, int* k_list_el,
    double* x, double* y, double* z,
    double* x_2, double* y_2, double* z_2,
    double* type, double* wall, double cut, int n,
    int i_initial, int k){
    // recursive algorithm to find all neigbour

    double dist, dist_2;
    for (int i = 0; i < n; i++){
        if ( list[i] != 0 )
            continue;
        dist = get_r(x[i_initial], y[i_initial], z[i_initial], x[i], y[i], z[i],  wall);
        dist_2 = get_r(x_2[i_initial], y_2[i_initial], z_2[i_initial], x_2[i], y_2[i], z_2[i],  wall);
        if ( (dist < cut) && (dist_2 < cut) ){
            list[i] = k;

            if (type[i] == 1.0)
                k_list_ion[k] ++;

            if (type[i] == 2.0)
                k_list_el[k] ++;

            find_neighbour(list, k_list_ion, k_list_el, x, y, z, x_2, y_2, z_2, type, wall, cut, n, i, k);
        }
    }
}

int* neighbour_list_two( double* x, double* y, double* z,
    double* x_2, double* y_2, double* z_2,
    double* type, double* wall, double cut, int n){

    int* list = new int[n*2 + 8]; // here we will return bonding molecules[n], types of every particle[n], distribution[7 (e, H+, H, H2+, H2, H3+, H3]
    int* k_list_ion = new int[n];
    int* k_list_el = new int[n];
    cut = cut*cut; // we will compare dist^2

    for (int l = 0; l < n*2 + 8; l ++)
        list[l] = 0;

    for (int l = 0; l < n; l ++){
        k_list_el[l] = 0;
        k_list_ion[l] = 0;
    }

    int k = 1;
    for (int i = 0; i < n; i ++){
        if (list[i] == 0){
            find_neighbour(list, k_list_ion, k_list_el, x, y, z, x_2, y_2, z_2, type, wall, cut, n, i, k);
            k++;
        }
    }

    
    
    /* we will sign molecules with their type
    e - 1
    H+ - 2
    H - 3
    H2+ - 4
    H2 - 5
    H3+ - 6
    H3 - 7
    H- - 8
    other - 0
    */
    // create a list of k-types
    int* k_types = new int[k];

    int el, ion;
    for (int j = 0; j < k; j++){
        el = k_list_el[j];
        ion = k_list_ion[j];
        k_types[j] = 0;
        // e
        if ( (el == 1) && (ion == 0) ){
            list[n*2 + 0] += el + ion;
            k_types[j] = 1;
        }
        // H+
        if ( (el == 0) && (ion == 1) ){
            list[n*2 + 1] += el + ion;
            k_types[j] = 2;
        }
        // H
        if ( (el == 1) && (ion == 1) ){
            list[n*2 + 2] += el + ion;
            k_types[j] = 3;
        }
        // H2+
        if ( (el == 1) && (ion == 2) ){
            list[n*2 + 3] += el + ion;
            k_types[j] = 4;
        }
        // H2
        if ( (el == 2) && (ion == 2) ){
            list[n*2 + 4] += el + ion;
            k_types[j] = 5;
        }
        // H3+
        if ( (el == 2) && (ion == 3) ){
            list[n*2 + 5] += el + ion;
            k_types[j] = 6;
        }
        // H3
        if ( (el == 3) && (ion == 3) ){
            list[n*2 + 6] += el + ion;
            k_types[j] = 7;
        }
        // H-
        if ( (el == 2) && (ion == 1) ){
            list[n*2 + 7] += el + ion;
            k_types[j] = 8;
        }
    }

    // names particles with their type to list[n+i]
    for (int i = 0; i < n; i++){
        list[i+n] = k_types[list[i]];
    }
    delete[] k_types;
//    for (  int i = 0; i < n*2 + 7; i++)
//        std::cerr << list[i] << " ";
//    std::cerr << "\nH2 = " << list[n*2 + 4] << "\n";
//    for (int i = 0; i < k; i++)
//       std::cerr << k_list_ion[i] << " "<< k_list_el[i] << "\n";
    delete[] k_list_el;
    delete[] k_list_ion;
    return list;
}

void free_mem(double* a)
{
 delete[] a;
}
