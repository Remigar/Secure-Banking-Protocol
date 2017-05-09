#create the account password hash files, as well as initiate the account balances


import os
from passlib.hash import argon2
from subprocess import call

accounts = [('123456', 'password'),
			('123457', 'letmein'),
			('004570', 'itshighnoon'),
			('000011', 'iminchargenow'),
			('654321', 'icecream420'),
			('735132', 'idontreallythinktheresalimittohowlongthesepasswordscanbesoletsjustseehowthisturnsout')]

account_balances = [('123456', 1234.56),
					('123457', 56.00),
					('004570', 12.00),
					('000011', 100.00),
					('654321', 654321.00),
					('735132', 1931.69)]


with open('server/accountdb.txt', 'w') as fh:
	for account in accounts:
		fh.write(account[0] + ' ')
		#hash the password
		#NOTE:after some research, I determined that there are better methods of password hashing
		#here we will use the fairly new argon2 hashing algorithm to handle passwords
		#Although new, argon2 has been heavily scrutinized and found to have no vulnerabilities thusfar
		#In additon, argon2 was specifically designed for hashing passwords.
		hasher = argon2.hash(account[1])
		fh.write(hasher + '\n')

with open('server/account_balances.txt', 'w') as fh:
	for account in account_balances:
		fh.write(account[0] + ' ' + '{:.2f}'.format(account[1]) + '\n')

#encrypt the newly created files via AES
cmd = 'openssl aes-128-cbc -e -in server/accountdb.txt -out server/accountdb.txt.enc'.split()
call(cmd)

cmd2 = 'openssl aes-128-cbc -e -in server/account_balances.txt -out server/account_balances.txt.enc'.split()
call(cmd2)

#clean up the plaintext files
os.remove('server/accountdb.txt')
os.remove('server/account_balances.txt')
