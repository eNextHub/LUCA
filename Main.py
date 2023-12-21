#%%

def fuel_context(path='Input/LUCA Table.xlsx', save='Output/LUCA for pint.txt'):
    """
    Reads an Excel file located at `path` and extracts data to generate a list of contexts.
    Each context is a string that defines a set of conversion rules between different units of measurement.
    The contexts are written to a text file named 'LUCA.txt'.

    Parameters:
    path (str): The path to the Excel file containing the data.

    Returns:
    None
    """
    
    import pandas as pd
    file_name = path

    df = pd.read_excel(file_name, header=[0,1,2], index_col=[0,1,2])

    sN = slice(None)
    contexts = ["EUR = [currency] = euro\ntonnes_service = 1 * tonnes"] # The currency must be added manually

    for c in range(len(df.columns)):
        name = df.columns.get_level_values(0)[c]
        cont = df.columns.get_level_values(1)[c]
        code = df.columns.get_level_values(2)[c]

        context = f"""
# {name}
LHV_{code} = {df.loc[(sN,'LHV'),name].values[0][0]} {df.loc[(sN,'LHV'),name].index.get_level_values(2)[0]}
den_{code} = {df.loc[(sN,'den'),name].values[0][0]} {df.loc[(sN,'den'),name].index.get_level_values(2)[0]}
prV_{code} = {df.loc[(sN,'prV'),name].values[0][0]} {df.loc[(sN,'prV'),name].index.get_level_values(2)[0]}
prM_{code} = {df.loc[(sN,'prM'),name].values[0][0]} {df.loc[(sN,'prM'),name].index.get_level_values(2)[0]}
GWP100_{code} = {df.loc[(sN,'GWP100'),name].values[0][0]} {df.loc[(sN,'prM'),name].index.get_level_values(2)[0]}
Sden_{code} = {df.loc[(sN,'Sden'),name].values[0][0]} {df.loc[(sN,'Sden'),name].index.get_level_values(2)[0]}
prDM_{code} = {df.loc[(sN,'prDM'),name].values[0][0]} {df.loc[(sN,'prDM'),name].index.get_level_values(2)[0]}

@context {cont} = {code}
    [mass] -> [energy]: value * LHV_{code}
    [energy] -> [mass]: value / LHV_{code}
    [volume] -> [mass]: value * den_{code}
    [mass] -> [volume]: value / den_{code}
    [volume] -> [currency]: value * prV_{code}
    [currency] -> [volume]: value / prV_{code}
    [mass] -> [mass]: value * GWP100_{code}
    [area] -> [mass]: value * Sden_{code}
    [mass] * [length] -> [currency]: value * prDM_{code}
@end
        """
        contexts.append(context)

    with open(save, 'w') as f:
        f.write('\n'.join(contexts))
# %%

fuel_context()
# %%
import pint
ureg = pint.UnitRegistry()

ureg.load_definitions('Output\LUCA for pint.txt')
# %%

mass_NG = 91 * ureg('kton')
# %%

TJ_NG = 5050.55 * ureg('TJ')
# %% Tesla Semi

eff = 1.8 * ureg('kWh/mile')
eff_ = eff.to('kWh/km')

cap = 500 * ureg('mile')
cap_ = cap.to('km')

bat = 850 * ureg('kWh') # may be 900


spee = 70 * ureg('mile/hour')
spee_ = spee.to('km/hour')

print(spee_)
# %% Battery weight

# Model S 2022 data
bat_weight = 537 * ureg('kg')
spec_energy = 186 * ureg('Wh/kg')

# Tesla Semi data
bat_weight = (bat / spec_energy).to('kg')

# %%
