
from demyst.df.df2 import df2
import os

@df2
def data_function(df):
    inputs = df.connectors.get("pass_through", '', {})
    return {'inputs': inputs, 'env': str(os.environ), 'output_field_example': "Hello World"}

def required_inputs():
    return [
        {
            "name": "email_address",
            "description": "An example of how to list required input",
            "type": "String"
        }
    ]

def optional_inputs():
    return [
        {
            "name": "optional_input_example",
            "description": "An example of how to list optional input",
            "type": "String"
        }
    ]

def output():
    """
    DemystType is one of
    ["Blob", "Boolean", "BusinessName", "City", "Country", "Date", "DateTime",
    "Dictionary", "Domain", "EmailAddress", "FirstName", "FullName", "Gender",
    "Ip4", "LastName", "Latitude", "List", "Longitude", "MaritalStatus",
    "MiddleName", "Number", "Percentage", "Phone", "PostCode", "Range",
    "SicCode", "State", "Street", "String", "Url", "UsEin", "UsSsn", "UsSsn4",
    "Year", "YearMonth"]
    """
    return [
        {
            "name": "output_field_example",
            "type": "String",
            "description": "An example of how to list the outputs of the data function",
            "sample": "blue"
        }
    ]

def metadata():
    return {
        "create_provider": True,
        "category": "Finance",
        "data_provider_name": "Provider name",
        "data_product_name": "Data Function Name",
        "data_product_description": "Purpose of the data function, when to use, what it provides",
        "beta": True,
        "price_final": True,
        "fcra": False,
        "region": "us",
        "data_provider_website": "www.example.com"
    }

def tile_data():
    req_in = required_inputs()
    outs = output()
    opt_in = optional_inputs()
    meta = metadata()
    result_dict = {}
    result_dict.update(meta)
    result_dict.update({'optional_inputs': opt_in})
    result_dict.update({'required_inputs': req_in})
    result_dict.update({'output': outs})
    return result_dict
