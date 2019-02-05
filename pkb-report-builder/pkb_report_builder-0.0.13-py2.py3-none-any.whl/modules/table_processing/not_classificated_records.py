import logging
import re
#check not classificated rows
def group_not_singled_roots(roots, single_roots):
    try:
        not_classificated_table = []

        pseudo_roots =[]

        for single_root in  single_roots:

            value = single_root
            ln_index =-1
            limit =0
            for v_index in range(len(value)-1,0,-1):

                let = value[v_index]

                if re.match("^[A-Za-z0-9_-]*$", let):
                    ln_index+=1
                    ln_index=v_index
                else:
                    break

                if (limit>2):
                    ln_index=len(value)
                    break
                limit+=1

            p = str(value)[0:ln_index]
            if (len(p)>1):
                pseudo_roots.append(p)


        clean_pseudo_roots = []

        for pseudo_root in  pseudo_roots:
            t = pseudo_root in clean_pseudo_roots
            if (t==False):
                clean_pseudo_roots.append(pseudo_root)

        result_pseudo_roots =[]
        result_single_roots = []

        for clean_pseudo_root in clean_pseudo_roots:
            t = clean_pseudo_root in single_roots
            if (t==True):
                result_single_roots.append(clean_pseudo_root)
            else:
                result_pseudo_roots.append(clean_pseudo_root)




        return result_single_roots,result_pseudo_roots
        t=0
        pass
    except Exception as e:
        logging.error("Error"+str(e))