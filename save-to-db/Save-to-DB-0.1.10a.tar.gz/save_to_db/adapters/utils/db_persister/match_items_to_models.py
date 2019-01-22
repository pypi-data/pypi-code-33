from save_to_db.core.exceptions import (MultipleItemsMatch,
                                        MultipleModelsMatch)


def match_items_to_models(adapter, items_and_fkeys, models, adapter_settings):
    """ Matches items to models and returns two lists, one with items and
    another with models. Items in first list match with models from the
    second with the same index in the list.
     
    :param items: List of single items.
    :param models: List of ORM models.
    :returns: Lists of matched items and list of matched models for each
        item (returns a list and a list of lists).
    """
    if not items_and_fkeys or not models:
        return [], []
    
    matched_items = []
    matched_models = []  # list of lists
     
    def add_matched(item, model):
        if not item.allow_multi_update and item in matched_items:
            index = matched_items.index(item)
            other_models = matched_models[index]
            if model == other_models[0]:
                return  # Some ORMs can return same model twice
            raise MultipleModelsMatch(item, model, other_models[0])
         
        for i, model_list in enumerate(matched_models):
            if model in model_list:
                other_item = matched_items[i]
                if item is not other_item:
                    raise MultipleItemsMatch(model, item, other_item)
         
        if item not in matched_items:
            matched_items.append(item)
            matched_models.append([model])
        else:
            index = matched_items.index(item)
            matched_models[index].append(model)
     
    for item, fkeys in items_and_fkeys:
        getters = item.getters
        relations = item.relations
        
        for model in models:
            for getter_fields in getters:
                same = True
                for field_name in getter_fields:
                    if field_name not in item or item[field_name] is None:
                        same = False
                        break
                     
                    if field_name in item.fields:
                        model_field_value = getattr(model, field_name)
                        if item[field_name] != model_field_value:
                            same = False
                            break
                    elif field_name in relations:
                        if field_name not in fkeys:  # not persisted
                            same = False
                            break
                             
                        relation = relations[field_name]
                        if not relation['relation_type'].is_x_to_many():
                            model_field_value = getattr(model, field_name)
                            if fkeys[field_name][0] != model_field_value:
                                same = False
                                break
                        else:
                            contained_models = \
                                adapter.related_x_to_many_contains(
                                    model, field_name, fkeys[field_name],
                                    adapter_settings)
                            if not contained_models:
                                break
                if same:
                    break
                     
            if not same:
                continue
            
            add_matched(item, model)
     
    return matched_items, matched_models