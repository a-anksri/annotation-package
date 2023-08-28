import pickle
import os
import pandas as pd

if(os.path.exists('accounts')):
    f = open('accounts', 'rb')
    accounts = pickle.load(f)
    f.close()
else:
    print("No accounts")
    
print(accounts)
a = int(input("Enter Id to regenerate config: "))




config = {}
config['id'] = a
config['name'] = accounts[a]

f = open('root_config', 'wb')
pickle.dump(config, f)
f.close()
