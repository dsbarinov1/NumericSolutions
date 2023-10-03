import numpy as np
from numba import jit, float64, boolean, int32, int64
from testing_schemes import *
B = 3.0
SIGMA = 1.0
SHIFT = 4.0

@jit('float64[:](float64[:], float64, float64, float64)', nopython=True)
def double_gauss_func(x, B, SIGMA, SHIFT):
    g1 = np.divide(np.subtract(x,B),SIGMA)
    g2 = np.divide(np.subtract(x, B+SHIFT), SIGMA)
    return np.exp( -0.5 * np.power(g1, 2.0)) + np.exp( -0.5 * np.power(g2, 2.0))


#святой говнокод(зато понятно нумбе)
#Автоматическое заполнение P для метода прогонки
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


#вычисление части, не зависящей от точек на верхнем слое в методе обратной характеристики
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


#просто индексы точек по x, которых мы рассматриваем на каждом шаге
@jit('int64[:,:](int64)', nopython=True, parallel=True)
def fill_dots_arr(n: int)->np.ndarray:
    dots_arr = np.zeros((n, 4), dtype=int64)
    for i in range(n):
        dots_arr[i] = np.arange(i - 2, i + 2, dtype=int64) % n
    return dots_arr


#если точек на верхнем слое больше одной, придется решать слау, заполнение ее матрицы
@jit('float64[:,:](int64, int64, float64[:])', nopython=True, parallel=True)
def fill_matrix(n: int, u_shift: int, u3_P: np.ndarray)->np.ndarray:
    u_matrix = np.zeros((n, n), dtype=float64)
    for i in range(n):
        for k in range(5):
            u_matrix[i, i - 2 + k] = -u3_P[k]
        u_matrix[i, i+u_shift] = 1
    return u_matrix


#Основная функция для метода обратной характеристики
#Не включайте jit, из-за него в неявных методах откуда-то возникают Nan
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
    last_idx = scheme_coords.size-1
    ax = scheme_coords[last_idx]
    #print(scheme_coords)
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


#Для отдельного тестирования запустите сам файл computation.py
if __name__ == '__main__':
    import time
    r = 0.8
    h = 0.1
    X_MAX = 30
    X = np.linspace(0, X_MAX, int(X_MAX/h))
    U2 = double_gauss_func(X, B, SIGMA, SHIFT)
    test_scheme1 = np.array([[False, False, False, False],
                            [True, True, True, False],
                            [False, False, True, False]])
    test_method(laying_L, 1, [U2, r, h, 1000])
    test_method(scheme_step, 2, [U2, U2, test_scheme1, r, h, 1000])

    U1_test2 = U2
    U2_test2 = laying_L(U2, r, h, 1)
    test_scheme2 = np.array([[ True,  True,  True, False],
                            [False,  True,  True, False],
                            [False, False,  True, False]])
    test_method(stairs_step, 2, [U1_test2, U2_test2, r, h, 1000])
    test_method(scheme_step, 2, [U2, U2_test2, test_scheme2, r, h, 1000])