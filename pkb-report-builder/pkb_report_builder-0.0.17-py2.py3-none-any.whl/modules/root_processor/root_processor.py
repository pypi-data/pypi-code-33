import logging


# get to contracts without counter
def get_to_contracts_without_counter(root_models):
    try:
        root_contracts = []

        for root_model in root_models:
            if (root_model.aggreement_counter == ''):
                root_contracts.append(root_model)

        clean_data = []

        for root_model in root_models:
            found = False
            for root_contract in root_contracts:
                if (root_model.aggreement_value == root_contract.aggreement_value):
                    found = True
                    break

            if (found == False):
                clean_data.append(root_model)

        return root_contracts,clean_data

    except Exception as e:
        logging.error("Error. " + str(e))



#get to child contracts
def get_child_contracts(root_contracts, contracts):
    try:
        results = []

        contract_added = []
        for root_contract in root_contracts:
            child_contracts = []
            for contract in contracts:
                if (str(contract.aggreement_number)==str(root_contract.aggreement_number)):
                    child_contracts.append(contract)
                    contract_added.append(child_contracts)

            results.append([root_contract, child_contracts])

        #detect not comparer contracts

        ext_contracts = []
        for contract in contracts:
            found = False
            for result in results:
                eq_contracts = result[1]
                if (len(eq_contracts)>0):
                    for eq_contract in eq_contracts:
                        if (contract.aggreement_value==eq_contract.aggreement_value):
                            found = True
                            break

            if (found==False):
                ext_contracts.append(contract)





        return results,ext_contracts
    except Exception as e:
        logging.error("Error. " + str(e))

#group extension contracts
def group_ext_contracts(contracts):
    try:
        aggreement_roots = []

        for contract in contracts:
            t = contract.aggreement_number in aggreement_roots
            if (t==False):
                aggreement_roots.append(contract.aggreement_number)


        aggreement_roots.sort()

        groups =[]
        for aggreement_root in aggreement_roots:
            group =[]
            for contract in contracts:
                if (contract.aggreement_number==aggreement_root):
                    group.append(contract)

            if (len(group)>0):
                groups.append(group)
        return groups
    except Exception as e:
        logging.error("Error. " + str(e))

#check if all counters is int
def check_sort_counter_int(counters):
    try:
        result = []
        for counter in counters:
            i_counter = int(counter)
            result.append(i_counter)


        result.sort()
        return result,True

    except Exception as e:
        logging.error("Error. " + str(e))
        return None,False

#sort contracts by counters
def sort_contracts(contracts):
    try:
        contract_counters = []
        for contract in contracts:
            contract_counters.append(contract.aggreement_counter)
        sorted_contract_counters, is_int = check_sort_counter_int(contract_counters)

        if (sorted_contract_counters==None):
            return contracts
        sorted_values = []


        for sorted_contract in sorted_contract_counters:

            for contract in contracts:
                if (str(contract.aggreement_counter)==str(sorted_contract)):
                    sorted_values.append(contract)

        return sorted_values
    except Exception as e:
        logging.error("Error. " + str(e))
        return contracts

# order root models
def order_roots(root_models):
    try:
        roots = []
        # get to head contracts
        root_contracts,clean_data = get_to_contracts_without_counter(root_models)
        child_contracts,ext_contracts = get_child_contracts(root_contracts,clean_data)

        ext_contract_groups = group_ext_contracts(ext_contracts)


        for child_contract in child_contracts:
            contracts =child_contract[1]

            if (len(contracts)>0):
                _contracts = sort_contracts(contracts)
                child_contract[1] = _contracts

        for ext_contract_group in ext_contract_groups:

            ext_contract_group = sort_contracts(ext_contract_group)

            t=0


        for child_contract in child_contracts:
            roots.append([child_contract, True])


        for ext_contract_group in ext_contract_groups:
            roots.append([ext_contract_group, False])

        return roots
    except Exception as e:
        logging.error("Error. " + str(e))
