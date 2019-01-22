def select(item, key):
    """ Returns all values under the `key` from `item`. If item contains
    refrences to x-to-many field, the items in that field will be traversed,
    example:
    
        .. code-block:: Python
        
            item_one = ItemOne()
            # 'two_1_x' is a one-to-many relation
            item_two = item['two_1_x'].gen()
            # 'one_x_x' is a many-to-many relation
            item_two['one_x_x'].gen(integer_value=1)
            item_two['one_x_x'].gen(integer_value=2)
            
            result = item_one.select('two_1_x__one_x_x__integer_value')
            print(result)  # outputs: `[1, 2]`

    :param item: An instance of :py:class:`~.item.Item` or
        :py:class:`~.bulk_item.BulkItem`
    :param key: A key under which all values will be collected.
    :returns: List of collected values.
    """
    if not isinstance(key, list):
        if item.is_bulk_item():
            key = item.item_cls._get_real_keys(key)
        else:
            key = item._get_real_keys(key)
    
    result = []
    first_key = key[0]
    if len(key) > 1:
        for one_item in item.as_list():
            if item.is_bulk_item():
                result.extend(select(one_item, key))
            else:
                result.extend(select(one_item[first_key], key[1:]))
    else:
        for one_item in item.as_list():
            if first_key in one_item:
                result.append(one_item[first_key])
        
    return result
        
    
    