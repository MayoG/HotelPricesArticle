# import pickle
import dill as pickle
import json
import pandas as pd

def save_object(obj, file_name="siteData"):
    with open(f'{file_name}.pkl', 'wb') as output_file:
        pickle.dump(obj=obj, file=output_file, protocol=pickle.HIGHEST_PROTOCOL)

def load_object(file_name="siteData"):
    with open(f'{file_name}.pkl', 'rb') as input_file:
        return pickle.load(file=input_file)
   
def save_to_json(data, file_path="data/jsonData"):
    with open(f'{file_path}.json', 'w') as fp:
        json.dump(data, fp)

def load_from_json(file_path="data/jsonData"):
    with open(f'{file_path}.json', 'r') as fp:
        return json.load(fp)

def create_csv(data: dict, file_path="data/csvData.csv"):
    data_frame = pd.DataFrame.from_dict(data)
    data_frame.to_csv(file_path)