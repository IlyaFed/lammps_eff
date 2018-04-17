#include "rdf_c.h"
#include <cmath>
#include <iostream>

double get_r(double x, double y, double z, double x_g, double y_g, double z_g, double *wall){
    double dx = fmin( fabs(x - x_g), fabs( x + wall[0] - x_g) );
    dx = fmin( dx, fabs( x - wall[0] - x_g) );
    
    double dy = fmin( fabs(y - y_g), fabs( y + wall[1] - y_g) );
    dy = fmin( dy, fabs( y - wall[1] - y_g) );

    double dz = fmin( fabs(z - z_g), fabs( z + wall[2] - z_g) );
    dz = fmin( dz, fabs( z - wall[2] - z_g) );

    return pow(dz*dz + dy*dy + dx*dx, 0.5);
}

double* rdf( double* x, double* y, double* z, double* s, double* type, double* wall, int n, int grid){
    double* rdf_distribution = new double[grid*3]; // we devide [0.5, wall/2] into {grid} parts, create to distribution for ion and electron
    // structure of massive [r, g_ion(r), g_el(r)]
    double r;
    double min_r = 0.5;
    double Volume = wall[0] * wall[1] * wall[2];
    double max_r = fmin( wall[0], wall[1]);
    max_r = fmin( max_r, wall[2] );
    max_r /= 2; // because of periodic conditions
    double dr = (max_r - min_r)/grid;

    for (int l = 0; l < grid; l ++){
        rdf_distribution[l] = min_r + dr * (l + 0.5);
        rdf_distribution[grid + l] = 0;
        rdf_distribution[grid*2 + l] = 0;
    }


    double dist;
    int n_ions = 0;
    for (int i = 0; i < n; i ++){
        if ( type[i] == 2 )
            continue;
        n_ions ++;
        for (int j = 0; j < n; j++){
            if ( ( type[j] == 1 ) && (i != j) ){
                dist = get_r(x[i], y[i], z[i], x[j], y[j], z[j],  wall);
                if ( (dist - min_r) < (max_r - min_r) )
                    rdf_distribution[ grid +  int( ( dist - min_r) / (max_r - min_r) * grid ) ] += 1;
            }
            if ( type[j] == 2 ){
                dist = get_r(x[i], y[i], z[i], x[j], y[j], z[j],  wall);
                for (int l = 0; l < grid; l ++){
                    r = rdf_distribution[l];
                    rdf_distribution[ grid*2 + l ] += 1.0/ 3.14 / s[j] / s[j] * exp( - 2 * (r - dist) * (r - dist) / s[j] / s[j]  );
                }

            }
        }
    }
    int n_electrons = n - n_ions;
    //std::cerr << "n_ions" << n_ions << " n_el" << n_electrons << "\n" ;
    // create RDF: N(r, r+dr) V/(4 pi r^2 dr N)
    for (int l = 0; l < grid; l ++){
        r = rdf_distribution[l];
        //std::cerr << "r = " << r << "dr = " << " n = " << n << "\n";
        rdf_distribution[ grid + l] = rdf_distribution[ grid + l] * Volume / (4 * 3.14 * r * r * dr * n_ions ) / n_ions; // /n - beacuause we average result
        rdf_distribution[ grid*2 + l] = rdf_distribution[ grid*2 + l] * Volume / (4 * 3.14 * r * r * dr * n_electrons ) / n_ions; // /n - beacuause we average result
        
    }


    return rdf_distribution;
}

void free_mem(double* a)
{
    delete[] a;
}