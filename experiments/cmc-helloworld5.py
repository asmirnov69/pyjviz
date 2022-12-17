import ipdb
import numpy as np
import pandas as pd
import janitor

class CallWrapper:
    def __init__(self, parent_w, o, method_name, method_o):
        self.parent_w = parent_w
        self.o = o        
        self.method_name = method_name
        self.method_o = method_o

    def __call__(self, *args, **kwargs):
        #ipdb.set_trace()
        mc_is_active = self.parent_w.parent_mc.is_active
        if mc_is_active:
            chained_call_name = self.parent_w.parent_mc.mc_name
            o_id = id(self.o)
            ret = self.method_o(*args, **kwargs)
            print("__call__ ", chained_call_name, o_id, self.method_name, args, kwargs, id(ret))
            ret = Wrapper(ret, self.parent_w.parent_mc)
        else:
            ret = Wrapper(self.method_o(*args, **kwargs), self.parent_w.parent_mc)
            
        return ret

class Wrapper:
    def __init__(self, o, parent_mc):
        self.o = o
        self.parent_mc = parent_mc

    def __getattr__(self, attr):
        o = self.__getattribute__('o')
        method_name = attr
        method_o = getattr(o, method_name)
        return CallWrapper(self, o, method_name, method_o)

    def __str__(self):
        o = self.__getattribute__('o')
        return str(o)
    
class MethodsChain:
    def __init__(self, mc_name):
        self.is_active = False
        self.mc_name = mc_name

    def __enter__(self):
        self.is_active = True
        print(f"enter methods chain {self.mc_name}")
        return self

    def __exit__(self, type, value, traceback):
        self.is_active = False
        print(f"exit methods chain {self.mc_name}")

    def __del__(self):
        print(f"deleting methods chain {self.mc_name} {id(self)}")
        
    def head(self, mc_head_obj):
        print("head id:", id(mc_head_obj))
        return Wrapper(mc_head_obj, self)

company_sales = {
        'SalesMonth': ['Jan', 'Feb', 'Mar', 'April'],
        'Company1': [150.0, 200.0, 300.0, 400.0],
        'Company2': [180.0, 250.0, np.nan, 500.0],
        'Company3': [400.0, 500.0, 600.0, 675.0]
    }

pn = "pyjanitor-helloworld"
with MethodsChain(pn) as mc:
    df = (
        mc.head(pd.DataFrame.from_dict(company_sales))
        #pd.DataFrame.from_dict(company_sales).head(mc)
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
print(df.describe())

#ipdb.set_trace()
with mc:
    print(df.add_column("Netflix", 1000.0).describe())
    
    
