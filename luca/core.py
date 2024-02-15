
from luca.utils import equation_separator,operator_sperator
import pandas as pd
import pint


class Equation:
    """Generates a general equation that can be duplicated for different items for a specific case
    """
    
    def __init__(self,lh:str,rh:str,eq:str,reverse=True,switched_on=True):
        """Initializing an Equation class

        Parameters
        ----------
        lh : str
            left hand side of the context equation
        rh : str
            right hand side of the context equation
        eq : str
            parametric equation
        reverse : boolean
            if True, the reverse equation will be checked and added automatically

        Raises
        ------
        ValueError
            string 'value' should be present for the pint registery

        .. code-block:: python

            equation = Equation('mass','energy','value * LHV_{gas}')
            print(equation)

            >> [mass] -> [energy]: value * LHV_{gas}
        """
        if "value" not in eq:
            raise ValueError("value not present")
        
        self.lh = lh
        self.rh = rh
        self.eq = eq
        self._reverse = reverse
        self._switched_on = True

    def fill(self,*args,**kwargs):
        """fills an equation with the parameter values

        Returns
        -------
        Equation
            return a new Equation object with the filled parameters
        """
        return Equation(self.lh,self.rh,self.eq.format(*args,**kwargs)) 


    def __str__(self):
        
        rh = " ".join(equation_separator(self.rh))
        lh = " ".join(equation_separator(self.lh))

        equation = f"   {lh} -> {rh}: {self.eq}"

        return equation        

    def __repr__(self):

        return self.__str__()
    
    def is_reversible(self):
        """checks if an equation can be reversed or not. The criterion is to have only one operation of * or / in equation

        Returns
        -------
        boolean
            True if the equation can be reversed unless False
        """
        if not self._reverse:
            return False
        operators = operator_sperator(self.eq)
        if len(operators) == 1 and operators[0] in ("*/"):
            return True
        return False 
    
    def reverse(self):
        """Returns the reverse equation

        .. note::

            to be consistent, the function should be used only when is_reversible() == True.

        Returns
        -------
        Equation
            a new Equation instance with the reversed calculations
        """
        eq = self.eq

        if "/" in eq:
            eq = eq.replace("/","*")
        elif "*" in eq:
            eq = eq.replace("*","/")
        
        return Equation(lh=self.rh,rh=self.lh,eq=eq)
    


class Parameter:

    """A Parameter object that can be constructed with or without a value assigned to it.
    """

    def __init__(self,name:str,abbr:str,unit:str,value:float=None,source:str=None):
        """_summary_

        Parameters
        ----------
        name : str
            name of the parameter
        abbr : str
            abbreviation of parameter that is corresponding to the equation naming
        unit : str
            unit of measure
        value : float, optional
            value of the parameter for a specific item, when assigned, by default None
        source : str, optional
            source of data when the value is assigned, by default None
        """
        self.name = name
        self.unit = unit
        self.abbr = abbr
        self.source = source

        if value is not None:
            self.value = value

    @property
    def all(self):
        return self
    
    @property
    def value(self):

        return self._val

    @value.setter
    def value(self,val):
        self._val = val

    def get_str(self,item:str):
        """Retruns the parameter context value

        Parameters
        ----------
        item : str
            specific item that the parameter is assigned with a value for the pint context

        Returns
        -------
        str
            parameter context value
        """
        return f"{self.abbr}_{item} = {self.value} {self.unit}"
    
    def __str__(self):
        if hasattr(self,"value"):
            return f"{self.abbr} = {self.value} [{self.unit}]"

        return f"{self.abbr} [{self.unit}]"
    
    def __repr__(self):

        return str(self)


class Converter:

    """Creates the pint Registery format for an item with collecting Equations, Parameters and assigned values
    """


    def __init__(self,item_type,equations:list[Equation],parameters:list[Parameter]):
        """Initialize a Converter object

        Parameters
        ----------
        item_type : str
            the type of the item for registery, that is correspondant to the parameter place holder in the Equation objects
        equations : list[Equation]
            a list of all the equations in the registery
        parameters : list[Parameter]
            a list of all the parameters in the registery
        """
        self.equations = []
        self.off_equations = []
        self.parameters = {}
        self.item_type = item_type

        for equation in equations:
            self.set_equation(equation)
        for parameter in parameters:
            self.set_parameter(parameter)


    def set_parameter(self,parameter:Parameter):
        """stores a Parameter object

        Parameters
        ----------
        parameter : Parameter
            the parameter object to be added to the list of parameters.
        """
        self.parameters[parameter.abbr] = parameter


    def get_parameter(self,parameter:str,what="all"):
        """Returns a parameter of the Converter object with the requested level of info

        Parameters
        ----------
        parameter : str
            the abbreviation of the requrested parameter
        what : str, optional
            level of informatio reequested,'value' for the value and 'all' for the whole object, by default "all"

        Returns
        -------
        Parameter, float
            Parameter if what == 'all', value of the parameter if what == 'value'

        Raises
        ------
        ValueError
            if parameter is not in added to the Converter
        """
        if parameter not in self.parameters:
            raise ValueError(f"{parameter} is not a valid parameter")
        
        return getattr(self.parameters[parameter],what)

    def set_equation(self,equation:Equation):
        """Adds an equation and its reverse if possible

        Parameters
        ----------
        equation : Equation
            the new equation to be added
        """

        if not isinstance(equation,Equation):
            raise ValueError("only Equation object is acceptable.")
        
        if equation._switched_on:
            self.equations.append(equation)

            if equation.is_reversible():
                self.equations.append(equation.reverse())
        
        else:
            self.off_equations.append(equation)

            if equation.is_reversible():
                self.off_equations.append(equation.reverse())

    # def switch_on_equation(self,lh,rh):
    #     to_remove = []
    #     for i,equation in enumerate(self.equations):
    #         if equation.lh == lh and equation.rh == rh:
    #             equation._switch_on = True
    #             self.equations.add


    def initialize(self,item_name:str,item_abbr:str,parameters:dict):
        """Initialize the equations with assigning the parameters values

        Parameters
        ----------
        item_name : str
            _description_
        item_abbr : str
            _description_
        parameters : dict
            _description_
        """
        self.item_name = item_name
        self.item_abbr = item_abbr
        for parameter,val in parameters.items():
            self.parameters[parameter].value = val
        kwargs = {self.item_type:self.item_abbr}
        self.equations = [equation.fill(**kwargs) for equation in self.equations]

    def is_ready(self):
        """Checks the pint Regsterty can be generated or not

        Returns
        -------
        boolean
            True if the object is properly built, unless False, with printing the issues in the console
        """
        ready = True
        error = "the context could not be initialized due to this errors: \n"
        if not hasattr(self,"item_name"):
            error+="    . Item is not initialized using the specific case.\n"
            ready = False

        for par in self.parameters.values():

            if not hasattr(par,"value"):
                error+=f"   . Parameter '{par}' is not assigned with a value.\n"
                ready = False

        if not ready:
            print(error)

        return ready
        
    def to_txt(self,path:str):
        """writes the registery into a txt file

        Parameters
        ----------
        path : str
            path to save the txt file of registery
        """
        with open(path, 'w') as f:
            f.write(str(self))

    def to_frame(self,items:dict):
        """Generates a pd.DataFrame of the case database to be filled

        Parameters
        ----------
        items : dict[item_name:item_abbr]
            represents a specific case of registtery

        Returns
        -------
        pd.DataFrame
            a database of the parameters to be filled for different cases of registery

        """

        frames = []
        empty_frame = self._empty_frame()
        for item_name,item_abbr in items.items():
            df = empty_frame.copy()
            df["item_name"] = item_name
            df["item_abbr"] = item_abbr

            frames.append(df)

        return pd.concat(frames)
    
    def _empty_frame(self):

        frame = pd.DataFrame(
            columns = ["Parameter","ParAbbreviation","Unit","item_type","item_name","item_abbr","value","source"],
        )
        parameters = []
        abbreviations = []
        units = []

        for par in self.parameters.values():

            parameters.append(par.name)
            abbreviations.append(par.abbr)
            units.append(par.unit)

        frame["Parameter"]=parameters
        frame["ParAbbreviation"]=abbreviations
        frame["Unit"]=units

        return frame

    def parse_from_file(self,path:str,**kwargs):

        """Reads the parameter values from a file database

        Parameters
        ----------
        path : str
            the path of the file to read from
        kwargs: dict
            specific inputs to the pd.read_excel or pd.read_csv function
        
        Returns
        -------
        Collector, dict[Collector]
            if only one item is spotted, a Collector object is returned, otherwise, a dict of Collector objects

        Raises
        ------
        ValueError
            only csv or xlsx files are accepted.
        """

        if path.endswith(".xlsx"):
            engine = pd.read_excel
        elif path.endswith(".csv"):
            engine = pd.read_csv
        else:
            raise ValueError("only csv and xlsx files are accepted.")
        
        file = engine(path,index_col=None,header=0,**kwargs)
        
        file = file.set_index(["item_abbr","item_name"])

        converters = []
        dd = {}
        for item,data in file.iterrows():
            if item not in dd:
                dd[item] = {}
            
            parameter = data.loc["ParAbbreviation"]
            if parameter not in self.parameters:
                continue

            dd[item][parameter] = data.loc["value"]

        for k,v in dd.items():
            cc = self.copy()
            
            cc.initialize(k[1],k[0],v)
            converters.append(
                cc                
            )

        if len(converters) == 1:
            self = converters[0]

        else:
            return Collector(*converters)


    def copy(self):
        """Reutrns a copy of the object

        Returns
        -------
        Converter
            a copy of the object
        """
        return Converter(item_type=self.item_type,equations=self.equations,parameters=list(self.parameters.values()))

    def __str__(self):

        if self.is_ready():
            string = f"""# {self.item_name} \n"""

            # add parameters
            pars = [par.get_str(self.item_abbr) for par in self.parameters.values()]
            string += "\n".join(pars)

            context = f"\n@context {self.item_name} = {self.item_abbr} \n"
            equations = [str(equation) for equation in self.equations]
            context += "\n".join(equations)
            context += "\n@end"

            return string + context
        else:
            return ""


class Units:

    def __init__(self,input):

        self.input = input
    
    def is_ready(self):
        return True
    
    def __str__(self):
        return self.input



class Collector:
    """Collects different Converter objects for a unified pint registery
    """

    def __init__(self,*convertors:Converter):
        """Initializes the Collector object

        Parameters
        ----------
        convertors : Converter
            convertor object
        """
        self.convertors = convertors

    
    def to_txt(self,path:str):
        """writes the registery into a txt file

        Parameters
        ----------
        path : str
            path to save the txt file of registery

        Raises
        ------
        ValueError
            if the Convertor objects are not properly built
        """
        txts = []
        errors = []
        for converter in self.convertors:
            if not converter.is_ready():
                errors.append(converter)

            else:
                txts.append(str(converter))

        if errors:
            raise ValueError("the pint registry could not be created due to the following errors: \n{}".format("\n".join(errors)))
        

        with open(path, 'w') as f:
            f.write('\n'.join(txts))


    def to_pint(self,path:str):
        """writes the registery file and returns a pint.UniteRegistry

        Parameters
        ----------
        path : str
            path to store the registry file 

        Returns
        -------
        pint.UnitRegistry
            a pint registry object
        """

        self.to_txt(path)

        registry = pint.UnitRegistry()

        registry.load_definitions(path)

        return registry

    def __str__(self):

        return "\n".join([str(i) for i in self.convertors])

    def __repr__(self):
        return self.__str__()
    
    def add_convertor(self,convertor:Converter):
        """Adds new Converter

        Parameters
        ----------
        convertor : Converter
            converter object to be added to the registry

        Raises
        ------
        ValueError
            if any object rather than Converter is passed
        """
        if not isinstance(convertor,Converter):
            raise ValueError("only converter object is acceptable.")
        self.convertors.append(convertor)

    def __add__(self,other):
        convertors = [convertor for convertor in self.convertors]

        if isinstance(other,Collector):
            convertors.extend(other.convertors)
        
        elif isinstance(other,Converter):
            convertors.append(other)

        else:
            raise ValueError()
        
        return Collector(*convertors)


    




        
        


