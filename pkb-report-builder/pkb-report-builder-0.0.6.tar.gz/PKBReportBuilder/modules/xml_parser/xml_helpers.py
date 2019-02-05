import xml.etree.ElementTree as ET

#find block
def find_block(current_block, element_name):
    try:
        results =[]
        for result in current_block.findall(element_name):
            results.append(result)
        return results
    except Exception as e:
        pass