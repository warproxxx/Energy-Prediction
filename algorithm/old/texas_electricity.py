# -*- coding: utf-8 -*-
"""
Created on Fri Aug 2 18:10:06 2018
"""

try:
    df = pd.read_csv(os.path.join(save_path, "all_data.csv"), encoding='latin1')
    print(df[-1])
except:
    pass
    

                    

