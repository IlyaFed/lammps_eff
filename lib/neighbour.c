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

int* neighbour_list( double* x, double* y, double* z, int* type, double* wall, double cut, int n){
    int* list = new int[n*2 + 7]; // here we will return bonding molecules[n], types of every particle[n], distribution[7 (e, H+, H, H2+, H2, H3+, H3]
    int* k_list_ion = new int[n];
    int* k_list_el = new int[n];
    for (int l = 0; l < n*2 + 7; l ++)
        list[l] = 0;

    for (int l = 0; l < n; l ++)
        k_list_el = 0;
        k_list_ion = 0;

    double dist;
    int k = 1;
    for (int i = 0; i < n; i ++){
        //std::cerr << "i = " << i << "\n";
        if (list[i] == 0){
            list[i] = k;
            //std::cerr << "list = " << list[i] << "\n";
            k++;
            if (type[i] == 1)
                k_list_ion[list[i]] ++;
                //std::cerr << "1 = " << k_list_ion[list[i]] << "\n";

            if (type[i] == 2)
                k_list_el[list[i]] ++;
                //std::cerr << "2 = " << k_list_el[list[i]] << "\n";
        }
        for (int j = i+1; j < n; j++){
            //std::cerr << "j = " << j << "\n";
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
        std::cerr << "list_i = " << list[i] << "\n";
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
    }

    return list;
}

void free_mem(double* a)
{
 delete[] a;
}
