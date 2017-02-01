# PSP_Csolver.pyx
# it needs Cython and a C compiler to work
# on windows you can use mingw
# to help contact:
# fausto.tomei@gmail.com 

from libc.stdlib cimport malloc, free
from libc.math cimport fabs

cdef int NOLINK = -1
cdef double *x
cdef double *b
cdef double *C
cdef double *A 
cdef int *indices
cdef int nrCells
cdef short int nrLinks 

def setArraysC(int nr_Cells, short nr_Links):
    global nrCells, nrLinks, x, b, C, A, indices
    nrCells = nr_Cells
    nrLinks = nr_Links
    x = <double *>malloc(nrCells * sizeof(double))
    b = <double *>malloc(nrCells * sizeof(double))
    C = <double *>malloc(nrCells * sizeof(double))
    A = <double *>malloc(nrCells * nrLinks * sizeof(double))
    indices = <int *>malloc(nrCells * nrLinks * sizeof(int))
    
def arrangeMatrix(int i, double deltaT, double H0, double flow):
    cdef int n
    cdef short int j
    cdef double D
    cdef double mySum = 0.0
    for j in range(nrLinks):
        n = i*nrLinks + j
        if (indices[n] == NOLINK): break       
        mySum += A[n]
        A[n] *= -1.0
    
    # diagonal and vector b     
    D = (C[i] / deltaT) + mySum
    b[i] = (C[i] / deltaT) * H0 + flow

    # matrix conditioning
    b[i] /= D
    for j in range(nrLinks):
        n = i*nrLinks + j
        if (indices[n] == NOLINK): break 
        A[n] /= D 

def GaussSeidel():
    cdef int i, n
    cdef short j
    cdef double new_x, dx
    cdef double norm = 0.0
    
    for i in range(nrCells):
        new_x = b[i]
        for j in range(nrLinks):
            n = i*nrLinks + j
            if (indices[n] == NOLINK): break
            new_x -= (A[n] * x[indices[n]])
                
        dx = fabs(new_x - x[i])
        # infinite norm
        if (dx > norm): norm = dx
        x[i] = new_x
    return norm

def set_x(int index, double value):
    x[index] = value
    
def get_x(int index):
    return x[index]
    
def set_C(int index, double value):
    C[index] = value

def set_indices(int i, short int j, int index):
    indices[i * nrLinks + j] = index
    
def set_A(int i, short int j, double value):
    A[i * nrLinks + j] = value

