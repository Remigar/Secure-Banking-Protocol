import datetime
import os
from Crypto.Cipher import AES
from subprocess import call

#record a customer transaction
def recordHistory(id, request, value=None):
    fh = open('customer_records/{}.txt'.format(id), 'a')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if request == 'login':
        #value contains True or False, depending on if the login attempt was successful
        if value == True:
            fh.write("{}: FAILED access for account {}\n".format(timestamp, id))
        else:
            fh.write("{}: Successful access for account {}\n".format(timestamp, id))
    elif request == 'view_balance':
        fh.write ("{}: Balance accessed for account {}\n".format(timestamp, id))
    elif request == 'logoff':
        fh.write("{}: User {} logged off.\n".format(timestamp, id))
    elif request == 'withdraw':
        #value should contain a tuple of 2 items:
        #1) whether or not the withdraw was successful
        #2) how much the user attempted to withdraw
        if value[0] == True:
            fh.write("{}: User {} withdrew ${:.2f}.\n".format(timestamp, id, value[1]))
        else:
            fh.write("{}: User {} failed to withdraw ${:.2f} due to insufficient balance\n".format(timestamp, id, value[1]))
    elif request == 'deposit':
        #value contains the amount the user deposited.
        fh.write("{}: User {} deposited ${:.2f}.\n".format(timestamp, id, value))
    elif request == 'shutdown':
        fh.write("{}: User {} logged off and shut down the ATM.\n".format(timestamp, id))
    fh.close()

#load account id/hash pairs and id/balance pairs into memory
def loadAccounts():
    #account credentials and account balances are now stored in encrypted files!
    #we must decrypt them first.
    cmd = 'openssl aes-128-cbc -d -in accountdb.txt.enc -out accountdb.txt'.split()
    call(cmd)
    cmd2 = 'openssl aes-128-cbc -d -in account_balances.txt.enc -out account_balances.txt'.split()
    call(cmd2)

    accounts = []
    with open('accountdb.txt', 'r') as fh:
        for line in fh:
            line_t = line.rstrip()
            line_t_s = line_t.split()
            account = (line_t_s[0], line_t_s[1])
            accounts.append(account)
    account_balances = []
    with open('account_balances.txt', 'r') as fh:
        for line in fh:
            line_t = line.rstrip()
            line_t_s = line_t.split()
            balance = (line_t_s[0], float(line_t_s[1]))
            account_balances.append(balance)
    #once the accounts are in memory, clean up the plaintext files
    os.remove('accountdb.txt')
    os.remove('account_balances.txt')

    return accounts, account_balances


#write updated account balances back to the text file
def writeAccountBalances(balances):

    with open('account_balances.txt', 'w') as fh:
        for balance in balances:
            fh.write(balance[0] + ' {:.2f}\n'.format(balance[1]))
    cmd = 'openssl aes-128-cbc -e -in account_balances.txt -out account_balances.txt.enc'.split()
    call(cmd)
    #clean up the plaintext
    os.remove('account_balances.txt')
