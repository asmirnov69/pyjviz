#import ipdb
import janitor
import pandas_flavor as pf
import pyjviz
import os.path

import typing
import pandas as pd

TestDF = typing.NewType('TestDF', pd.DataFrame)
TestDF.columns = ['a']

@pf.register_dataframe_method
def a0(df: pd.DataFrame) -> TestDF:
    print("a0")
    return df

if __name__ == "__main__":
    # configure pyjrdf
    if 0:
        rdflog_fn = pyjviz.get_rdflog_filename(sys.argv[0])
        RDFLogger.init(rdflog_fn)

    print(TestDF, TestDF.__name__, TestDF.__supertype__)
    print(TestDF.columns)

    df = pd.DataFrame({'a': range(10)})
    with pyjviz.MethodsChain("c") as c:
        df1 = c.head(df).a0()

    print(df1)

    if 0:
        pyjviz.render_rdflog(rdflog_fn)
