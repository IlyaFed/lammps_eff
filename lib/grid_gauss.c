#include "grid_gauss.h"
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

double* grid_gauss( double* x, double* y, double* z, double* s, double* wall, int n, int grid_n){
    double* grid = new double[grid_n * grid_n * grid_n];
    for (int l = 0; l < grid_n * grid_n * grid_n; l ++)
        grid[l] = 0;
    double x_g, y_g, z_g, s_2, r_dist_2;
    for (int i = 0; i < grid_n; i++){
        x_g = wall[0] / grid_n * i;
        for (int j = 0; j < grid_n; j++){
            y_g = wall[1] / grid_n * j;
            for (int k = 0; k < grid_n; k++){
                z_g = wall[2] / grid_n * k;
                for (int m = 0; m < n; m++){
                    // std::cerr << x[m] << " "<< y[m] << " " << z[m] << " " << s[m] << "\n";
                    r_dist_2 = get_r(x[m], y[m], z[m], x_g, y_g, z_g,  wall);
                    s_2 = s[m] * s[m];
                    // std::cerr << r_dist_2 << " ";
                    if ( r_dist_2 < 9.0 * s_2 ){
                        // std::cerr << "append\n";
                        grid [i * grid_n * grid_n + j *grid_n + k] += exp( - r_dist_2/s_2) / sqrt( 3.14159 * s_2 );
                    }
                }
            }
        }
    }
    return grid;
}

void free_mem(double* a)
{
 delete[] a;
}
