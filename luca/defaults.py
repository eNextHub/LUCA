
from luca.core import Converter,Parameter,Equation

class GAS(Converter):
    
    EQUATIONS = [
        Equation("mass","energy","value * LHV_{gas}"),
        Equation("volume","mass","value * dens_{gas}"),
        Equation("volume","currency","value * prv_{gas}"),
        Equation("mass","mass","value * GWP100_{gas}",False),
    ]

    PARAMETERS = [
        Parameter("Lower Heating Value","LHV","MJ / kg"),
        Parameter("Density","dens","kg / m**3"),
        Parameter("100 Year Global Warming Potential","GWP100","kgCO2eq/kg")
    ]


    def __init__(self,gas_name:str=None,gas_abbr:str=None,parameters:dict=None):
     
        super().__init__("gas",GAS.EQUATIONS,GAS.PARAMETERS)
        if all([i is not None for i in [gas_name,gas_abbr,parameters]]):
            self.initialize(item_name=gas_name,item_abbr=gas_abbr,parameters=parameters)