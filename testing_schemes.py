import numpy as np
import time


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


def test_method(func, ret_cnt, args):
    start = time.time()
    if ret_cnt == 1:
        u_test = func(*args)
    elif ret_cnt == 2:
        _, u_test = func(*args)
    print(time.time() - start, u_test[:5])



