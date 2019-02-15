from collections import defaultdict
from save_to_db.adapters.utils.relation_type import RelationType
from save_to_db.core.exceptions import MultipleModelsMatch
from save_to_db.core.item_base import ItemBase
from save_to_db.core import signals
from .match_items_to_models import match_items_to_models


def db_persist(adapter, item, adapter_settings):
    top_item = item
    result_items = item.as_list()
    
    # emitting `before_db_persist` signal
    item_structure = item.process()
    signals.before_db_persist.emit(top_item, item_structure)
    
    # creating process keeper
    process_keeper = defaultdict(list)
    for item_cls, items in item_structure.items():
        for item in items:
            process_keeper[item_cls].append(__ItemProcessTracker(item))
    
    def keeper_is_empty(process_keeper):
        for value in process_keeper.values():
            if value:
                return False
        return True
    
    # --- getting and updating initial models ---
    getter_process_keeper = process_keeper
    while not keeper_is_empty(getter_process_keeper):
        all_items, all_models = [], []
        for item_cls in getter_process_keeper:
            if not getter_process_keeper[item_cls]:
                continue
            
            items_and_fkeys = []
            new_items, new_models = [], []
            
            for item_track in getter_process_keeper[item_cls]:
                items_and_fkeys.append([item_track.item,
                                        item_track.fkeys])
            
            batch_size = item_cls.batch_size \
                if item_cls.batch_size is not None \
                else adapter.BATCH_SIZE
            got_models = []
            for batch_start in range(0, len(items_and_fkeys), batch_size):
                got_models.extend(
                    adapter.get(
                        items_and_fkeys[batch_start:batch_start+batch_size],
                        adapter_settings
                    )
                )
            if not got_models:
                continue
            got_items, got_models = match_items_to_models(adapter,
                                                          items_and_fkeys,
                                                          got_models,
                                                          adapter_settings)
            all_items.extend(got_items)
            all_models.extend(got_models)

        getter_process_keeper = __update_relationships(
            adapter, adapter_settings, all_items, all_models, process_keeper)[1]
    
    
    for item_cls in process_keeper:
        for item_track in process_keeper[item_cls]:
            item = item_track.item
            models = item_track.models
            for model in models:
                item.before_model_update(model)  # hook
                
                # cleaning x-to-many relations if needed
                for fkey in item_cls.relations:
                    relation = item_cls.relations[fkey]
                    if not relation['relation_type'].is_x_to_many() or \
                            not relation['replace_x_to_many'] or \
                            fkey not in item:
                        continue
                    __clear_related_models(adapter, adapter_settings,
                                           item, relation,
                                           model, fkey, process_keeper)
                
                __update_model_fields(adapter, adapter_settings,
                                      item_track, model, process_keeper)
            
    # --- creation loop ---
    create_process_keeper = process_keeper
    while not keeper_is_empty(create_process_keeper):
        new_items, new_models = [], []
        for item_cls in create_process_keeper:
            for item_track in create_process_keeper[item_cls]:
                if item_track.models:
                    continue
                item = item_track.item
                if item not in new_items and item.can_create(item_track.fkeys):
                    new_items.append(item)
                    model = adapter.create_blank_model(item.model_cls,
                                                       adapter_settings)
                    new_models.append([model])
                    item.before_model_update(model)  # hook
                    __update_model_fields(adapter, adapter_settings,
                                          item_track, model, process_keeper,
                                          created=True)

        create_process_keeper = __update_relationships(
            adapter, adapter_settings, new_items, new_models, process_keeper)[0]
    
    # emitting `item_dropped` signal
    for item_cls in process_keeper:
        for item_track in process_keeper[item_cls]:
            if item_track.models:
                continue
            item = item_track.item
            if item.update_only_mode:
                reason = \
                    signals.item_dropped.reason_cannot_create_update_only_mode
            else:
                reason = \
                    signals.item_dropped.reason_cannot_create_not_enough_data
            
            signals.item_dropped.emit(item, reason)
    
    # after_model_save hook
    for item_cls in process_keeper:
        for item_track in process_keeper[item_cls]:
            item = item_track.item
            for model in item_track.models:
                if adapter.SAVE_MODEL_BEFORE_COMMIT:
                    adapter.save_model(model, adapter_settings)
                item.after_model_save(model)
    
    # return the result
    items, models = [], []
    for item in result_items:
        # looking for models
        for item_track in process_keeper[type(item)]:
            if item is item_track.item:
                if item_track.models:
                    items.append(item_track.item)
                    models.append(item_track.models)
                break
    
    # emitting `after_db_persist` signal
    signals.after_db_persist.emit(top_item, items, models)
    
    return items, models


# functions for model updates --------------------------------------------------

def __can_set(adapter, item, field_name, model, created):
    if created or field_name not in item.norewrite_fields:
        return True
    
    relation_type = None
    if field_name in item.relations:
        relation_type = item.relations[field_name]['relation_type']
    
    rewrite_none = item.norewrite_fields[field_name]
    
    if not relation_type or relation_type.is_x_to_one():
        model_value = getattr(model, field_name)
        if model_value is not None:
            return False
    else:
        model_value = adapter.related_x_to_many_exists(model, field_name)
        if model_value is True:
            return False
        
    return rewrite_none


def __clear_related_models(adapter, adapter_settings,
                           item, relation,
                           model, fkey, process_keeper):
    
    if not adapter.REVERSE_MODEL_AUTOUPDATE_SUPPORTED and \
            relation['reverse_key'] and relation['item_cls'] and \
            relation['relation_type'] is RelationType.ONE_TO_MANY:
        item_cls = relation['item_cls']
        
        models_to_check = []
        for item_track in process_keeper[item_cls]:
            models_to_check.extend(item_track.models)
        contained_models = adapter.related_x_to_many_contains(
            model, fkey, models_to_check, adapter_settings)
         
        for contained_model in contained_models:
            __set_related_model(adapter, adapter_settings,
                                process_keeper, item_track,
                                contained_model,
                                relation['reverse_key'], None)

    adapter.clear_related_models(model, fkey)


def __set_related_model(adapter, adapter_settings, process_keeper, item_track,
                        model, fkey, fmodel):
    
    def clean_relation(model, fkey, fmodel, item_cls, reverse_key):
        if reverse_key and hasattr(model, fkey):
            related_model = getattr(model, fkey)
            if related_model and related_model != fmodel:
                setattr(related_model, reverse_key, None)
                adapter.save_model(related_model, adapter_settings)
         
        for item_track in process_keeper[item_cls]:
            found = False
            for track_model in item_track.models:
                if track_model == model:
                    continue
                if hasattr(track_model, fkey) and \
                        getattr(track_model, fkey) == fmodel:
                    found = True
                    setattr(track_model, fkey, None)
                    adapter.save_model(track_model, adapter_settings)
                    break
             
            if found:
                break
             
    relation = item_track.item.relations[fkey]
    if relation['relation_type'] is RelationType.ONE_TO_ONE and \
            ((not hasattr(model, fkey) and fmodel is not None) or
             (hasattr(model, fkey) and getattr(model, fkey) != fmodel)):
        # forward relation
        clean_relation(model, fkey, fmodel, type(item_track.item),
                       relation['reverse_key'])
        # backward
        if relation['reverse_key']:
            clean_relation(fmodel, relation['reverse_key'], model,
                           relation['item_cls'],
                           fkey)
                
    setattr(model, fkey, fmodel)
    
    

def __add_related_models(adapter, model, fkey, fmodels):
    adapter.add_related_models(model, fkey, fmodels)

# process tracker --------------------------------------------------------------
    
class __ItemProcessTracker(object):
    def __init__(self, item):
        self.item = item
        self.models = []
        self.fkeys = defaultdict(list)


def __update_model_fields(adapter, adapter_settings, item_track,
                          model, process_keeper, created=False):

    for field_name in item_track.item.data:
        if field_name in item_track.item.fields:
            if __can_set(adapter, item_track.item, field_name, model, created):
                setattr(model, field_name, item_track.item[field_name])
        
    # many to one before saving
    for fkey in item_track.fkeys:
        relation_type = item_track.item.relations[fkey]['relation_type']
        if relation_type.is_x_to_one():
            __set_related_model(adapter, adapter_settings,
                                process_keeper, item_track,
                                model, fkey, item_track.fkeys[fkey][0])
    
    # for the rest model has to be saved
    if created and adapter.SAVE_MODEL_BEFORE_COMMIT:
        adapter.save_model(model, adapter_settings)

    for fkey, fmodels in item_track.fkeys.items():
        relation_type = item_track.item.relations[fkey]['relation_type']
        if not relation_type.is_x_to_one():
            __add_related_models(adapter, model, fkey, fmodels)
            

def __update_relationships(adapter, adapter_settings,
                           items, models, process_keeper):
    original_items, original_models = items, models
    
    creator_keeper = defaultdict(list)
    getter_keeper = defaultdict(list)
    
    # update_fkey --------------------------------------------------------------
    
    def update_fkey(item_track, fkey, foreign_item_track):

        def update_result_keepers():
            item_cls = type(item)
            for keeper, groups in [[creator_keeper[item_cls], item.creators],
                                   [getter_keeper[item_cls], item.getters]]:
                if groups is None:
                    continue
                
                for group in groups:
                    if fkey not in group:
                        continue
                    
                    do_add = True
                    for field in group:
                        if field not in item:
                            do_add = False
                            break
                    if do_add:
                        keeper.append(item_track)
                        break
        
        foreign_models = foreign_item_track.models
        if not foreign_models:
            return
        
        item = item_track.item
        models = item_track.models
        fkeys = item_track.fkeys[fkey]
        
        relation = item.relations[fkey]
        is_x_to_one = relation['relation_type'].is_x_to_one()
        
        keepers_updated = False
        for foreign_model in foreign_models:
            if foreign_model not in fkeys:
                fkeys.append(foreign_model)
                if not keepers_updated:
                    update_result_keepers()
        
#         print('     REF:', item.__class__.__name__, '[{}]->'.format(fkey),
#               foreign_item_track.item.__class__.__name__,
#               '(is_x_to_one: {})'.format(is_x_to_one))
        
        for model in models:
            if is_x_to_one:
                if len(foreign_models) > 1:
                    raise MultipleModelsMatch(item, fkey, foreign_models)
                __set_related_model(adapter, adapter_settings,
                                    process_keeper, item_track,
                                    model, fkey, foreign_models[0])
            else:
                __add_related_models(adapter, model, fkey, foreign_models)
    
    
    # saving models to process_keeper ------------------------------------------
    
    for item, models in zip(original_items, original_models):
        if not models:
            continue
        item_cls = type(item)
        
        # getting item_track
        for item_track in process_keeper[item_cls]:
            if item_track.item is item:
                break
            
        for model in models:
            if model not in item_track.models:
                item_track.models.append(model)
                
                if len(item_track.models) > 1 and \
                        not item_cls.allow_multi_update:
                    raise MultipleModelsMatch(
                        item, item_track.models)
            
    # updating relationships ---------------------------------------------------
    
    for item, models in zip(original_items, original_models):
        if not models:
            continue
        item_cls = type(item)
        
        # getting item_track
        for item_track in process_keeper[item_cls]:
            if item_track.item is item:
                break
               
        # --- forward relations ---
        for f_fkey in item_cls.relations:
            if f_fkey not in item:
                continue
            
            for f_item in item[f_fkey].as_list():
                
                # looking for f_item_track
                found = False
                for f_item_cls in process_keeper:
                    for f_item_track in process_keeper[f_item_cls]:
                        if f_item_track.item is f_item:
                            update_fkey(item_track, f_fkey, f_item_track)
                            found = True
                            break
                    if found:
                        break

                # updating f_fkey
                
            
        # --- backward relations ---
        for b_item_cls in process_keeper:
            # looking for b_item_track
            for b_item_track in process_keeper[b_item_cls]:
                b_item = b_item_track.item

                for b_fkey, b_value in b_item.data.items():
                    # not an item?
                    if not isinstance(b_value, ItemBase):
                        continue
                     
                    # not referenced?
                    if b_value.is_single_item():
                        if not (b_value is item):
                            continue
                    else:
                        if item not in b_value.bulk:
                            continue
                    
                    # updating b_fkey
                    update_fkey(b_item_track, b_fkey, item_track)
    
    return creator_keeper, getter_keeper