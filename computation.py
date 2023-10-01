import numpy as np
from numba import jit, float32, boolean, int32

B = 3.0
SIGMA = 1.0
SHIFT = 4.0


def double_gauss_func(x, B, SIGMA, SHIFT):
    return (np.exp( -0.5 * np.power(((x - B)/SIGMA), 2.0)) + np.exp( -0.5 * pow(((x - B - SHIFT)/SIGMA), 2.0)))


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


#святой говнокод
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


@jit('float64[:](float64[:], float64[:], int32[:,:], float64[:])', nopython=True, parallel=True)
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


#@jit('UniTuple(float64[:], 2)(float64[:], float64[:], boolean[:,:], float64, float64, int64)',nopython=True)
def scheme_step(u1: np.ndarray, u2: np.ndarray, scheme: np.ndarray, r: float, h: float, STEPS: int = 1):
    u3 = np.zeros(u1.size)
    dots_arr = np.zeros((u3.size, 4), dtype=int)
    for i in range(u3.size):
        dots_arr[i] = np.arange(i-2, i+2, dtype=int)%u3.size
    initial_dots = np.arange(1, 5, dtype=int)
    level_modifications = [r,0,-r]
    scheme_coords = np.zeros(initial_dots.size * 3, dtype=float)
    P_arr = np.zeros(initial_dots.size * 3, dtype=float)
    third_level_cnt = 0
    for i in range(3):
        for j in range(initial_dots.size):
            if scheme[i,j]:
                scheme_coords[initial_dots.size*i+j] = (initial_dots[j]+level_modifications[i])*h
                if i==3:
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

    for _ in range(STEPS):
        C = fill_C(u1,u2,dots_arr,P_arr)
        if third_level_cnt == 1:
                u3 = C
        else:
                #TODO: слау
                u3 = C
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