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
        chained_call_name = self.parent_w.parent_cm.cm_name
        o_id = id(self.o)
        ret = self.method_o(*args, **kwargs)
        print("__call__ ", chained_call_name, o_id, self.method_name, args, kwargs, id(ret))
        return Wrapper(ret, self.parent_w.parent_cm)

class Wrapper:
    def __init__(self, o, parent_cm):
        self.o = o
        self.parent_cm = parent_cm

    def __getattr__(self, attr):
        o = self.__getattribute__('o')
        method_name = attr
        method_o = getattr(o, method_name)
        return CallWrapper(self, o, method_name, method_o)

    def __str__(self):
        o = self.__getattribute__('o')        
        return str(o)
    
class ChainedMethodsGroup:
    def __init__(self, cm_name):
        self.cm_name = cm_name

    def __enter__(self):
        print(f"enter cmc {self.cm_name}")
        return self

    def __exit__(self, type, value, traceback):
        print(f"exit cmc {self.cm_name}")

    def head(self, cm_head_obj):
        print("head id:", id(cm_head_obj))
        return Wrapper(cm_head_obj, self)
        
company_sales = {
        'SalesMonth': ['Jan', 'Feb', 'Mar', 'April'],
        'Company1': [150.0, 200.0, 300.0, 400.0],
        'Company2': [180.0, 250.0, np.nan, 500.0],
        'Company3': [400.0, 500.0, 600.0, 675.0]
    }

pn = "pyjanitor-helloworld"
with ChainedMethodsGroup(pn) as cc:
    df = (
        cc.head(pd.DataFrame.from_dict(company_sales))
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

