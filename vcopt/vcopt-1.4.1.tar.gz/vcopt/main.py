# -*- coding: utf-8 -*-
import numpy as np
import numpy.random as nr
import math, time
np.set_printoptions(threshold=np.inf, precision=8, suppress=True, floatmode='maxprec')




class GA:
    def __init__(self):
        pass

    def __del__(self):
        pass
    
    def rcGA(self, para_range, func, aim, seed=None, verbose=0, visible=1, maxgen=5000):
        #
        para_range = np.array(para_range)
        para_num = len(para_range)
        
        #hyper parameter
        pool_num = para_num * 10 #10n~50n
        parent_num = para_num * 2 #1.5n~3.0n
        child_num = para_num * 10
        rate = 0.99
        
        if verbose == 1:
            pool_num = para_num * 50 #10n~50n
            parent_num = para_num * 3 #1.5n~3.0n
            child_num = para_num * 10
            rate = 0.999
        
        #seed
        nr.seed(seed)
        
        #
        pool, pool_score = np.zeros((pool_num, para_num)), np.zeros(pool_num)
        parent, parent_score = np.zeros((parent_num, para_num)), np.zeros(parent_num)
        child, child_score = np.zeros((child_num, para_num)), np.zeros(child_num)

        #
        ave = np.zeros(para_num)
        sd = 1 / math.sqrt(parent_num)
        
        #start time
        start = time.time()
        
        #gen 1 pool
        pool = nr.rand(pool_num, para_num)
        for j in range(para_num):
            pool[:, j] = pool[:, j] * (para_range[j, 1] - para_range[j, 0]) + para_range[j, 0]
        
        
        #gen 1 pool score
        for i in range(pool_num):            
            para = pool[i]
            pool_score[i] = func(para)
        
        #save best
        best_select = np.argmin(np.abs(aim - pool_score))
        best_score, best_para = pool_score[best_select], pool[best_select]
        
        if visible == 1:
            print('Opt {} params, {}()->{}, maxgen={}, seed={}, verbose={}'.format(para_num, func.__name__, aim, maxgen, seed, verbose))
        
        #gen 2
        
        n_max = maxgen + 1
        v_i = maxgen // 100
        
        for n in range(1, n_max):
            #
            if visible == 1 and n % v_i == 0:
                n0 = int(20 * (n/n_max)) + 1
                n1 = 20 - n0
                t = time.time() - start
                bar = '\r{}% [{}{}] time:{}s gen:{}  φ(□　□;)'.format(n//v_i, '#'*n0, ' '*n1, np.round(t, 1), n)
                print(bar, end='')
            
            #select parent
            pool_select = nr.choice(range(pool_num), parent_num, replace = False)
            
            #copy pool to parant
            parent = pool[pool_select]
            parent_score = pool_score[pool_select]
            
            #parant average
            ave = np.mean(parent, axis=0)
            
            #REX
            #==============================================================
            #child
            child[:, :] = float('inf')
            for i in range(child_num):
                for j in range(para_num):
                    while child[i, j] < para_range[j, 0] or para_range[j, 1] < child[i, j]:
                        #average
                        child[i, j] = ave[j]
                        #perturbation
                        for k in range(parent_num):
                            child[i, j] += nr.normal(0, sd) * (parent[k][j] - ave[j])
            #==============================================================
            
            #child score
            for i in range(child_num):
                para = child[i]
                child_score[i] = func(para)
            
            #family
            family = np.append(child, parent, axis=0)
            family_score = np.append(child_score, parent_score)
            
            #JGG
            #==============================================================  
            #select best from family
            #np.argpartition(-array, K)[:K] returns max K index
            #np.argpartition(array, K)[:K] returns min K index
            family_id = np.argpartition(np.abs(aim - family_score), parent_num)[:parent_num]
            
            #return to pool
            pool[pool_select] = family[family_id]
            pool_score[pool_select] = family_score[family_id]
            #==============================================================
        
            #save best
            best_select = np.argmin(np.abs(aim - pool_score))
            if np.abs(aim - pool_score[best_select]) < np.abs(aim - best_score):
                best_score, best_para = pool_score[best_select], pool[best_select]
                #print(n, best_para, best_score)
            
            #if n % 100 == 0:
            #    print(np.min(np.abs(aim - pool_score)), np.mean(np.abs(aim - pool_score)))
            
            #end check
            if np.min(np.abs(aim - pool_score)) > np.mean(np.abs(aim - pool_score)) * rate or np.min(np.abs(aim - pool_score)) < 10e-10:
                break
            
            #if np.min(np.abs(aim - pool_score)) < 10e-10:
            #    break

        
        if visible == 1:
            n0 = int(20 * (n/n_max)) + 1
            n1 = 20 - n0
            t = time.time() - start
            bar = '\r{}% [{}{}] time:{}s gen:{} φ(□　□*)!!'.format(n//v_i, '#'*n0, ' '*n1, np.round(t, 1), n)
            print(bar)
        return best_para, best_score
    






def rastrigin(para):
    k = 0
    for x in para:
        k += 10 + (x*x - 10 * math.cos(2*math.pi*x))
    return k
    

if __name__ == '__main__':
    tmp = GA()

    para, score = tmp.rcGA([[-5, 5], [-5, 5], [-5, 5], [-5, 5]], rastrigin, 0.0, seed=None, verbose=0, visible=1, maxgen=2000)
    
    print('para:{}'.format(para))
    print('score:{}'.format(score))
    