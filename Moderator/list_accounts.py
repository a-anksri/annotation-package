import pickle
import os
import pandas as pd

if(os.path.exists('accounts')):
    f = open('accounts', 'rb')
    accounts = pickle.load(f)
    f.close()
else:
    print("no accounts exist")

print(accounts)
