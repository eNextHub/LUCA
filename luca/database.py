
from luca.defaults import GAS



def NaturalGas():

    return GAS(
        gas_name="natural_gas",
        gas_abbr="NG",
        parameters= {
            "LHV": 53.2122905027933,
            "dens": 0.712,
            "GWP100": 29.8,   
        }
        )




