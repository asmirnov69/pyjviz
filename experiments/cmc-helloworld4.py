import numpy as np
import pandas as pd
import janitor

class CallWrapper:
    def __init__(self, o, method_name, method_o):
        self.o = o
        self.method_name = method_name
        self.method_o = method_o

    def __call__(self, *args, **kwargs):
        o_id = id(self.o)
        ret = self.method_o(*args, **kwargs)
        print("__call__ ", o_id, self.method_name, args, kwargs, id(ret))
        return Wrapper(ret)

class Wrapper:
    def __init__(self, o):
        self.o = o

    def __getattr__(self, attr):
        o = self.__getattribute__('o')
        method_name = attr
        method_o = getattr(o, method_name)
        return CallWrapper(o, method_name, method_o)

    def __str__(self):
        o = self.__getattribute__('o')        
        return str(o)
    
class ChainedMethodHead:
    def __init__(self, cmc_name, cmc_head_obj):
        self.name = cmc_name
        self.head_obj = cmc_head_obj

    def __enter__(self):
        head_obj_id = id(self.head_obj)
        print(f"enter cmc {self.name}", head_obj_id)
        return Wrapper(self.head_obj)

    def __exit__(self, type, value, traceback):
        head_obj_id = id(self.head_obj)
        print(f"exit cmc {self.name}", head_obj_id)

        
company_sales = {
        'SalesMonth': ['Jan', 'Feb', 'Mar', 'April'],
        'Company1': [150.0, 200.0, 300.0, 400.0],
        'Company2': [180.0, 250.0, np.nan, 500.0],
        'Company3': [400.0, 500.0, 600.0, 675.0]
    }

with ChainedMethodHead("pyjanitor-helloworld", pd.DataFrame.from_dict(company_sales)) as source_df:
#if 1:
#    source_df = pd.DataFrame.from_dict(company_sales)
    df = (
        source_df
        .remove_columns(["Company1"])
        .dropna(subset=["Company2", "Company3"])
        .rename_column("Company2", "Amazon")
        .rename_column("Company3", "Facebook")
        .add_column("Google", [450.0, 550.0, 800.0])
    )
    

# Output looks like this:
# Out[15]:
#   SalesMonth  Amazon  Facebook  Google
# 0        Jan   180.0     400.0   450.0
# 1        Feb   250.0     500.0   550.0
# 3      April   500.0     675.0   800.0

print(df)

