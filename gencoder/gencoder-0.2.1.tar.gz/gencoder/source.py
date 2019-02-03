def encoder(query):
    query_list = query.split(',')
    query1, query2 = float(query_list[0]), float(query_list[1])
    encoded1, encoded2 = polyline(query1), polyline(query2)
    final = encoded1 + encoded2
    return final


def polyline(ops_query):
    if ops_query == 0:
        return '?'
    binary = bin_converter(int(ops_query))
    left_shift = binary[1:] + '0'
    if ops_query < 0:
        inverted = bin_inversion(left_shift)
    else:
        inverted = left_shift
    binary_chunk = bin_chunk(inverted)
    binary_chunk_clean = bin_chunk_cleaner(binary_chunk)
    binary_chunk_reversed = binary_chunk_clean[::-1]
    binary_or = bin_or_0x20(binary_chunk_reversed)
    decimal_or = decimal_or_0x20(binary_or)
    final_decimal = decimal_add_63(decimal_or)
    final_polyline = decimal_to_char(final_decimal)
    return final_polyline


def bin_converter(query):
    if query >= 0:
        final = bin(query)[2:]
        for num in list(range(8 - (len(final) % 8)))[::-1]:
            final = '0' + final
    else:
        dummy = bin(query)[3:]
        for num in list(range(8 - (len(dummy) % 8)))[::-1]:
            dummy = '0' + dummy
        mid_response = ""
        for char in dummy:
            if char == '0':
                mid_response += '1'
            else:
                mid_response += '0'
        final = bin_add(mid_response, 1)
    return final


def bin_add(query, num):
    while True:
        if num == 0:
            break
        if query == '':
            query = '1'
            break
        for index in range(len(query))[::-1]:
            if query[index] == '0':
                if index != (len(query) - 1):
                    query = query[:index] + '1' + query[(index+1):]
                else:
                    query = query[:index] + '1'
                break
            else:
                query = bin_add(query[:index], 1) + '0'
                break
        num -= 1
    return query


def bin_inversion(query):
    final = ''
    for char in query:
        if char == '0':
            final += '1'
        elif char == '1':
            final += '0'
        else:
            raise ValueError("The provided query has something other than 0 and 1.")
    return final


def bin_chunk(query):
    final = []
    current_num = 0
    current = ''
    index = 0
    for char in query[::-1]:
        if current_num == 5:
            current_num = 0
            final = [current] + final
            index += 1
            current = ''
        current = char + current
        current_num += 1
    if int(current) != 0:
        for num in range(5 - len(current)):
            current = '0' + current
        final = [current] + final
    return final


def bin_or_0x20(query):
    final = []
    for chunk in query[:-1]:
        final += ['1' + chunk]
    final += ['0' + query[-1]]
    return final


def decimal_or_0x20(query):
    final = []
    for num in query:
        final += [int(num, 2)]
    return final


def decimal_add_63(query):
    final = []
    for num in query:
        final.append(num + 63)
    return final


def decimal_to_char(query):
    final = ''
    for num in query:
        final += chr(num)
    return final


def bin_chunk_cleaner(query):
    index = 0
    for num in query:
        if num == '00000':
            index += 1
        else:
            break
    final = query[index:]
    return final
