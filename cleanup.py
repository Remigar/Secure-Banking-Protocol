#this script removes all the keys and other files created by the project
import os

def attemptRemove(filename):
    try:
        os.remove(filename)
        print 'removed file {}'.format(filename)
    except OSError:
        print 'No file {} exists'.format(filename)

def attemptRemoveDir(path):
    try:
        os.rmdir(path)
        print 'removed directory {}'.format(path)
    except OSError:
        print 'No directory {} exists or directory is not empty'.format(path)

#remove atm keypairs
for i in range(1,3):
    attemptRemove('atm/keys/atm{}_PUBkey.pem'.format(i))
    attemptRemove('server/keys/atm{}_PUBkey.pem'.format(i))
    attemptRemove('atm/keys/atm{}_PRkey.pem'.format(i))
#remove the server keypair
attemptRemove('server/keys/server_PUBkey.pem')
attemptRemove('atm/keys/server_PUBkey.pem')
attemptRemove('server/keys/server_PRkey.pem')

#remove the directories that held the keys
attemptRemoveDir('atm/keys')
attemptRemoveDir('server/keys')

#remove the customer records
for filename in os.listdir('server/customer_records/'):
    if os.path.isfile('server/customer_records/' + filename) and filename != 'README':
        attemptRemove('server/customer_records/' + filename)
#remove the customer record directory
attemptRemoveDir('server/customer_records')

#remove the encrypted account login file and account balance files
attemptRemove('server/account_balances.txt.enc')
attemptRemove('server/accountdb.txt.enc')

#remove the python compiled bytecode files
attemptRemove('atm/misc_functions.pyc')
attemptRemove('server/misc_functions.pyc')
