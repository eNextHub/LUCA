import pandas as pd
import yaml
from luca.core import Equation,Parameter,Converter

def parse_context(io:str):

    # if not io.endswith(".yaml") or not isinstance(io,dict):
    #     raise ValueError("Only yaml file and dict are accepted.")
    
    if isinstance(io,dict):
        content = io.copy()
    else:
        with open(io,"r") as stream:
            content = yaml.safe_load(stream)


    contexes = {}
    for k,v in content["context"].items():
        contexes[k] = {}
        equations = []
        parameters = []
        essentials = {}


        for ee,kwargs in v["equations"].items():
            equations.append(
                Equation(**kwargs)
            )
            
        for pp,kwargs in v["parameters"].items():

           parameters.append(
                Parameter(name=pp,**kwargs)
            )
           
        essentials["item_type"] = k
        essentials["parameters"] = parameters
        essentials["equations"] = equations
           
        contexes[k] = Converter(**essentials)

    return contexes

        


            
            
