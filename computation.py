import numpy as np
from numba import jit, float64, boolean, int32, int64
import scipy
B = 3.0
SIGMA = 1.0
SHIFT = 4.0

@jit('float64[:](float64[:], float64, float64, float64)', nopython=True)
def double_gauss_func(x, B, SIGMA, SHIFT):
    g1 = np.divide(np.subtract(x,B),SIGMA)
    g2 = np.divide(np.subtract(x, B+SHIFT), SIGMA)
    return np.exp( -0.5 * np.power(g1, 2.0)) + np.exp( -0.5 * np.power(g2, 2.0))


def P_2(x,a,b,c):
    return (x-b)*(x-c)/((a-b)*(a-c))


def P_3(x,a,b,c,d,e):
    return (x-b)*(x-c)*(x-d)*(x-e)/((a-b)*(a-c)*(a-d)*(a-e))


"""
  #
###
схема для проверки
"""
def laying_L(u1, r, h,STEPS=1):
    u2 = np.zeros(u1.size)
    for _ in range(STEPS):
        for i in range(u1.size):
            xa = i*h-r*h
            u2[i] = u1[i-2]*P_2(xa,h*(i-2),h*(i-1),h*(i)) + u1[i-1]*P_2(xa,h*(i-1),h*(i-2),h*(i)) + u1[i]*P_2(xa,h*(i),h*(i-1),h*(i-2))
        u1 = np.copy(u2)
    return u1


"""
  #
 ##
###
схема для проверки
"""
def stairs_step(u1, u2, r, h,STEPS=1):
    u3 = np.zeros(u1.size)
    for _ in range(STEPS):
        for i in range(u3.size):
            xa = (i+1-r)*h
            xb = (i-1+r)*h
            xc = (i+r)*h
            xd = (i+1+r)*h
            xe = i*h
            xf = (i+1)*h
            u3[(i+1)%u3.size] = u1[i-1]*P_3(xa,xb,xc,xd,xe,xf) + u2[i]*P_3(xa,xe,xb,xc,xd,xf) + u1[i]*P_3(xa,xc,xb,xd,xe,xf) \
                    + u2[(i+1)%u3.size]*P_3(xa,xf,xb,xc,xd,xe) + u1[(i+1)%u3.size]*P_3(xa,xd,xb,xc,xe,xf)
        u1 = np.copy(u2)
        u2 = np.copy(u3)
    return u1, u2


#святой говнокод(зато понятно нумбе)
@jit('float64(float64, int64, float64[:])', nopython=True)
def P(x: float, idx: int, coords: np.ndarray)->float:
    res = 1
    for i in range(0, idx):
        if coords[i]!=0:
            res *= (x - coords[i]) / (coords[idx] - coords[i])
    for i in range(idx + 1, coords.size):
        if coords[i] != 0:
            res *= (x - coords[i]) / (coords[idx] - coords[i])
    return res


@jit('float64[:](float64[:], float64[:], int64[:,:], float64[:])', nopython=True, parallel=True)
def fill_C(u1: np.ndarray, u2: np.ndarray, dots_arr: np.ndarray, P_arr: np.ndarray)->np.ndarray:
    C = np.zeros(u1.size)
    for i in range(C.size):
        dots = dots_arr[i]
        u1_i = u1[dots]
        u2_i = u2[dots]
        for j in range(dots.size):
            C[i] += u1_i[j] * P_arr[j]
            C[i] += u2_i[j] * P_arr[dots.size + j]
    return C


@jit('int64[:,:](int64)', nopython=True, parallel=True)
def fill_dots_arr(n: int)->np.ndarray:
    dots_arr = np.zeros((n, 4), dtype=int64)
    for i in range(n):
        dots_arr[i] = np.arange(i - 2, i + 2, dtype=int64) % n
    return dots_arr


@jit('float64[:,:](int64, int64, float64[:])', nopython=True, parallel=True)
def fill_matrix(n: int, u_shift: int, u3_P: np.ndarray)->np.ndarray:
    u_matrix = np.zeros((n, n), dtype=float64)
    for i in range(n):
        for k in range(5):
            u_matrix[i, i - 2 + k] = -u3_P[k]
        u_matrix[i, i+u_shift] = 1
    return u_matrix


#@jit('UniTuple(float64[:], 2)(float64[:], float64[:], boolean[:,:], float64, float64, int64)',nopython=True)
def scheme_step(u1: np.ndarray, u2: np.ndarray, scheme: np.ndarray, r: float, h: float, STEPS: int = 1)->tuple[np.ndarray, np.ndarray]:
    u3 = np.zeros(u1.size)
    dots_arr = fill_dots_arr(u3.size)
    initial_dots = np.arange(1, 5, dtype=np.int64)
    level_modifications = [r,0,-r]
    scheme_coords = np.zeros(initial_dots.size * 3, dtype=np.float64)
    P_arr = np.zeros(initial_dots.size * 3, dtype=np.float64)
    third_level_cnt = 0
    for i in range(3):
        for j in range(initial_dots.size):
            if scheme[i,j]:
                scheme_coords[initial_dots.size*i+j] = (initial_dots[j]+level_modifications[i])*h
                if i==2:
                    third_level_cnt+=1
    ax = 0
    last_idx = scheme_coords.size-1
    while(ax == 0):
        last_idx-=1
        ax = scheme_coords[last_idx]
    for i in range(last_idx):
        if scheme_coords[i]!=0:
            P_arr[i] = P(ax,i, scheme_coords[:last_idx])
    #print(P_arr)
    shift_arr = [-2, -1, 0, 1]
    u_shift = shift_arr[last_idx-8]
    if third_level_cnt == 1:
        for _ in range(STEPS):
            C = fill_C(u1, u2, dots_arr, P_arr)
            u3 = np.roll(C, u_shift)
            u1 = np.copy(u2)
            u2 = np.copy(u3)
    else:
        u_matrix = fill_matrix(u3.size, u_shift, P_arr[8:])
        for step in range(STEPS):
            C = fill_C(u1,u2,dots_arr,P_arr)
            #u3 = scipy.linalg.solve_banded(u_matrix, C)
            u3 = np.linalg.solve(u_matrix, C)
            #print(u3)
            u1 = np.copy(u2)
            u2 = np.copy(u3)
    return u1, u2


if __name__ == '__main__':
    import time
    r = 0.8
    h = 0.1
    X_MAX = 30
    X = np.linspace(0, X_MAX, int(X_MAX/h))
    U2 = double_gauss_func(X, B, SIGMA, SHIFT)
    start = time.time()
    U2_test1 = laying_L(U2,r, h, 1000)
    print(time.time() - start, U2_test1[:10])
    test_scheme = np.array([[False, False, False, False],
       [ True,  True,  True, False],
       [False, False,  True, False]])
    start = time.time()
    _, U2_test2 = scheme_step(U2, U2, test_scheme, r, h, 1000)
    print(time.time() - start, U2_test2[:10])

    start = time.time()
    U1_test2 = U2
    U2_test2 = laying_L(U2, r, h, 1)
    _, U3_test2 = stairs_step(U1_test2, U2_test2, r, h, 1000)
    print(time.time() - start, U3_test2[:10])
    test_scheme = np.array([[ True,  True,  True, False],
                            [False,  True,  True, False],
                            [False, False,  True, False]])
    start = time.time()
    _, U3_test2 = scheme_step(U2, U2_test2, test_scheme, r, h, 1000)
    print(time.time() - start, U3_test2[:10])