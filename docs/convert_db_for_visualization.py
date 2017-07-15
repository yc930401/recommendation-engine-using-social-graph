# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 00:15:12 2017

@author: User
"""

import pandas as pd

# Read the CSV into a pandas data frame (df)
#   With a df you can do many things
#   most important: visualize data with Seaborn
df = pd.read_csv('nodesedgestry.csv', delimiter=',')

# Or export it in many ways, e.g. a list of tuples
tuples = [tuple(x) for x in df.values]

data = [(str(x), str(y), int(z), int(q)) for x,y,z,q in tuples]
# or export it as a list of dicts
dicts = df.to_dict().values()