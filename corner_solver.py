import numpy as np
def TDMCorners(a0:int,b0:int,c0:int,q:int) -> list:
    '''
    a0 - нижняя диагональ
    b0 - средняя диагональ
    c0 - верхняя диагональ
    q - целевой вектор
    return - вектор x-ов
    '''
    size_ = len(q)
    a = [b0 for i in range(size_)]
    b = [a0 for i in range(size_)]
    c = [c0 for i in range(size_)]
    # Формируем вспомогательный target-вектор
    target2 = [0 for i in range(size_-1)]
    target2[-1] = -c[-2] # n-ый элемент 
    target2[0]  = -b[0] # 1-ый элемент
    
    aa = a[:-1] # Без a_n+1
    bb = b[1:-1] # Без b_1 и b_n+1
    cc = c[:-2] # Без c_n и c_n+1
    qq = q[:-1] #Без q_n+1
    tt = [i for i in target2] # Без ласт элемента

    x_1 = TDMAsolver(bb,aa,cc,qq)
    x_2 = TDMAsolver(bb,aa,cc,tt)
    
    x_last = (q[-1]-c[-1]*x_1[0]-b[-1]*x_1[-1])/(a[-1]+c[-1]*x_2[0]+b[-1]*x_2[-1])
    
    x = [x_1[i]+x_2[i]*x_last for i in range(len(x_1))]
    x = x + [x_last]
    
    return x

# TriDiagonal Matrix Algorithm(a.k.a Thomas algorithm) solver
def TDMAsolver(a, b, c, d):
    '''
    TDMA solver, a b c d can be NumPy array type or Python list type.
    refer to http://en.wikipedia.org/wiki/Tridiagonal_matrix_algorithm
    and to http://www.cfd-online.com/Wiki/Tridiagonal_matrix_algorithm_-_TDMA_(Thomas_algorithm)
    '''
    nf = len(d) # number of equations
    ac = [i for i in a]
    bc = [i for i in b]
    cc = [i for i in c]
    dc = [i for i in d]
    # print(ac)
    # print(bc)
    # print(cc)
    # print(dc)
    for it in range(1, nf):
        mc = ac[it-1]/bc[it-1]
        bc[it] = bc[it] - mc*cc[it-1] 
        dc[it] = dc[it] - mc*dc[it-1]
        	    
    xc = [i for i in bc]
    xc[-1] = dc[-1]/bc[-1]
    for il in range(nf-2, -1, -1):
        xc[il] = (dc[il]-cc[il]*xc[il+1])/bc[il]

    return xc

