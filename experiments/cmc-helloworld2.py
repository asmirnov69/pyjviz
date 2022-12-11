import ipdb
import numpy as np
import pandas as pd
import janitor
import bytecode, dis

def call_func_insert_wrapper(func, modify_code):
    ipdb.set_trace()
    if modify_code == False:
        # unmodified call
        ret = func()
    else:
        print(dis.dis(func)) # show VM disassembly
        print([str(x) for x in bytecode.Bytecode.from_code(func.__code__)][0])

        # bytecode module docs: https://bytecode.readthedocs.io/en/latest/usage.html
        instructions = bytecode.ConcreteBytecode.from_code(func.__code__)

        # we can modify instructions here, see https://bytecode.readthedocs.io/en/latest/usage.html#concrete-bytecode
        instructions.names.append('Wrapper') # appending Wrapper to names to avoid arg shift in exisiting bytecode
        instructions.insert(0, bytecode.ConcreteInstr('LOAD_GLOBAL', len(instructions.names) - 1))
        instructions.insert(2, bytecode.ConcreteInstr('CALL_FUNCTION', 1))
        
        func.__code__ = bytecode.ConcreteBytecode.to_code(instructions)
        print("modified code:")
        print(dis.dis(func)) # show VM disassembly
        ret = func()

    print("all done")
    return ret

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
    
class ChainedMethodCall:
    def __init__(self, cmc_name, cmc_lambda):
        self.name = cmc_name
        if cmc_lambda.__code__.co_name != '<lambda>':
            raise Exception("ChainedMethodCall cmc_lambda is exepted to be lambda")
        self.func = cmc_lambda

    def run(self):
        print(f"ChainedMethodCall::run: {self.name}")
        return call_func_insert_wrapper(self.func, modify_code = True)

def test():
    company_sales = {
        'SalesMonth': ['Jan', 'Feb', 'Mar', 'April'],
        'Company1': [150.0, 200.0, 300.0, 400.0],
        'Company2': [180.0, 250.0, np.nan, 500.0],
        'Company3': [400.0, 500.0, 600.0, 675.0]
    }

    s_df = pd.DataFrame.from_dict(company_sales)
    def get_s_df(o): return o
    df = ChainedMethodCall("pyjanitor-helloworld", lambda:
                       #Wrapper(pd.DataFrame.from_dict(company_sales))
                       #pd.DataFrame.from_dict(company_sales)
                       s_df
                       #get_s_df(s_df)
                       #Wrapper(s_df)
                       .remove_columns(["Company1"])
                       .dropna(subset=["Company2", "Company3"])
                       .rename_column("Company2", "Amazon")
                       .rename_column("Company3", "Facebook")
                       .add_column("Google", [450.0, 550.0, 800.0])
                       ).run()

# Output looks like this:
# Out[15]:
#   SalesMonth  Amazon  Facebook  Google
# 0        Jan   180.0     400.0   450.0
# 1        Feb   250.0     500.0   550.0
# 3      April   500.0     675.0   800.0
df = test()
print(df)

