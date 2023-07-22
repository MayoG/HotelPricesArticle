# import pickle
import dill as pickle
import json
import pandas as pd
from requests_html import AsyncHTMLSession

async_session = AsyncHTMLSession()

class Dummy(object):
    """An object that have any attribute
    Useful for being a default value in unset parameter.

    """

    def do(self, *args, **kw): return self
    def __getattr__(self, _): return self.do
    def __call__(self, *args, **kwargs): return self.do

def get_async_session():
    return async_session

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

def create_csv(data, file_path="data/csvData"):
    data_frame = pd.DataFrame.from_dict(data)
    data_frame.to_csv(f"{file_path}.csv")
