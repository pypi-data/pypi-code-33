import json
import pandas as pd


def get_data(folder):
    document_list = list(folder.glob('*.json'))
    json_list = []
    for item in document_list:  
        try:
            json_text = item.read_text(encoding='utf-8')
            json_text = json.loads(json_text)
        except:
            json_text = item.read_text(encoding='utf-16')
            json_text = json.loads(json_text)
        json_list.append(json_text)
    df = pd.DataFrame(json_list)
    df_dict = df['header'].to_dict()
    df = pd.DataFrame.from_dict(df_dict, orient='index')
    return df


def get_errors(folder):
    document_list = list(folder.glob('*.json'))
    json_list = []
    for item in document_list:  
        try:
            json_text = item.read_text(encoding='utf-8')
            json_text = json.loads(json_text)
        except:
            json_text = item.read_text(encoding='utf-16')
            json_text = json.loads(json_text)
        json_list.append(json_text)
    df = pd.DataFrame(json_list)
    df_dict = df['Ellipse_Messages'].to_dict()
    df = pd.DataFrame.from_dict(df_dict, orient='index')
    return df