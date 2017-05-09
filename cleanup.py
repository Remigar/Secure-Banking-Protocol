#this utility is to remove all the keys and other files created by the project
import os

def attemptRemove(filename):
    try:
        os.remove(filename)
        print 'removed {}'.format(filename)
    except OSError:
        print 'No file {} exists'.format(filename)



#remove atm keypairs
for i in range(1,3):
    attemptRemove('atm/keys/atm{}_PUBkey.pem'.format(i))
    attemptRemove('server/keys/atm{}_PUBkey.pem'.format(i))
    attemptRemove('atm/keys/atm{}_PRkey.pem'.format(i))
#remove the server keypair
attemptRemove('server/keys/server_PUBkey.pem')
attemptRemove('atm/keys/server_PUBkey.pem')
attemptRemove('server/keys/server_PRkey.pem')

#remove the customer records
for filename in os.listdir('server/customer_records/'):
    if os.path.isfile('server/customer_records/' + filename):
        attemptRemove('server/customer_records/' + filename)

#remove the encrypted account login file and account balance files
attemptRemove('server/account_balances.txt.enc')
attemptRemove('server/accountdb.txt.enc')

#remove the python compiled bytecode files
attemptRemove('atm/misc_functions.pyc')
attemptRemove('server/misc_functions.pyc')
