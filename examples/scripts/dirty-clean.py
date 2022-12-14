#
# first example from https://github.com/samukweku/pyjanitor_presentation/blob/main/janitor/pyjanitor_PyData_Sydney.ipynb
#

import pandas as pd
import janitor
import pyjviz

if __name__ == "__main__":
    if 0:
        # configure pyjrdf
        rdflog_fn = pyjviz.get_rdflog_filename(sys.argv[0])
        RDFLogger.init(rdflog_fn)
    
    if 1:
        url = "https://github.com/pyjanitor-devs/pyjanitor/blob/dev/examples/notebooks/dirty_data.xlsx?raw=true"
        dirty = pd.read_excel(url, engine = 'openpyxl')        
    else:
        dirty = pd.read_excel("../data/dirty_data.xlsx")
        
    print(dirty)

    with pyjviz.MethodsChain("from_dirty_to_clean") as c:
        clean = (c.head(dirty)
                 .clean_names()
                 .dropna(axis='columns', how='all')
                 .dropna(axis='rows', how='all')
                 .rename(columns={"%_allocated": "percent_allocated", "full_time_": "full_time"})
                 .assign(certification = lambda df: df.certification.combine_first(df.certification_1))
                 .drop(columns='certification_1')
                 .assign(hire_date = lambda df: pd.to_datetime(df.hire_date, unit='D', origin='1899-12-30'))
                 )
    print(clean)

    if 0:
        pyjviz.render_rdflog(rdflog_fn)