def sub_array(arr, m, n):
    row = len(arr)
    col = len(arr[0])
    if m and n and (m <= row and n <= col):        
        results = []
        for a in range(col-m+1):    
            for i in range(row-n+1):
                x = i
                result = []
                while x < (i+n):
                    y = a
                    p = []
                    while y < m+a:
                        p.append(arr[x][y])
                        y += 1
                    x+= 1
                    result.append(p)
                results.append(result)
        return results
    else:
        raise Exception('Invalid sub array requested.')
