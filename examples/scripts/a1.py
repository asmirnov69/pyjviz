#import ipdb
import janitor
import pandas_flavor as pf
import pyjviz
import os.path, sys

import typing
import pandas as pd

TestDF = typing.NewType('TestDF', pd.DataFrame)
TestDF.columns = ['a']

@pf.register_dataframe_method
def a0(df: pd.DataFrame) -> TestDF:
    print("a0")
    return pd.DataFrame(df)

if __name__ == "__main__":
    # configure pyjrdf
    rdflog_fn = pyjviz.get_rdflog_filename(sys.argv[0])
    pyjviz.RDFLogger.init(rdflog_fn)

    print(TestDF, TestDF.__name__, TestDF.__supertype__)
    print(TestDF.columns)

    with pyjviz.Chain("c") as c:
        df = pd.DataFrame({'a': range(10)})
        df1 = c.pin(df).a0()
    print(df1.describe())
        
    with c:
        df2 = c.pin(df).a0()
    print(df2.describe())
        
    with c, pyjviz.Chain("c1") as c1:
        df3 = c.pin(df).continue_at(c1).a0()
        #df3 = df.pin(c).continue_at(c1).a0()
    print(df3.describe())

    with c, pyjviz.Chain("cc", c) as cc:
        df4 = c.pin(df).continue_at(cc).a0()
    print(df4.describe())

    pyjviz.render_rdflog(rdflog_fn)
