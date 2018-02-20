extern "C" int* neighbour_list( double* x, double* y, double* z, double* type, double* wall, double cut, int n);
extern "C" int* neighbour_list_two( double* x, double* y, double* z, double* x_2, double* y_2, double* z_2, double* type, double* wall, double cut, int n);
extern "C" void free_mem(double*);
