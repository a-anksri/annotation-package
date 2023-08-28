import pickle
import os
import pandas as pd

if(os.path.exists('accounts')):
    f = open('accounts', 'rb')
    accounts = pickle.load(f)
    f.close()
else:
    accounts = {}
    

name = input("Enter Name: ")
id = len(accounts)

print("assigned id: {}".format(id))

accounts[id] = name

config = {}
config['name'] = name
config['id'] = id

f = open('root_config', 'wb')

pickle.dump(config, f)
f.close()

f = open('accounts', 'wb')
pickle.dump(accounts, f)
f.close()
