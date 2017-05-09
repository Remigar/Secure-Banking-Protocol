# the driver program for the central bank server
# listens for validation connection requests from atms
# handle requests from atms once connection is established

from Crypto.PublicKey import RSA
from passlib.hash import argon2
from socket import *
import sys
import threading
from misc_functions import recordHistory, loadAccounts, writeAccountBalances

MESSAGE_SIZE = 256
AUTH_SUCCESS = '1'
AUTH_FAILURE = '0'

#functions to send/receive messages through a socket
def receive_message_dec(sock, size, decKey):
	result = ""
	tmpBuffer = ""
	while len(result) != size:
		tmpBuffer = sock.recv(size)
		if not tmpBuffer:
			return -1
		result += tmpBuffer
	#once the message is received, use the provided key to decrypt it.
	result_dec = decKey.decrypt(result)
	return result_dec
def send_message_enc(sock, msg, size, encKey):
	#encrypt the message before it is sent out
	enc_msg = encKey.encrypt(msg, 0L)[0]
	bytes_sent = 0
	while bytes_sent < size:
		bytes_sent += sock.send(enc_msg[bytes_sent:])

def service_connection(sock, atm_num):
	connectionSocket, addr = sock.accept()
	print "Connection {} established.".format(atm_num)

	# load the keys pertinent to this thread
	file_handlers = (open('keys/atm{}_PUBkey.pem'.format(atm_num), 'r'),
					 open('keys/server_PRkey.pem'.format(atm_num), 'r'))
	pubKey = RSA.importKey(file_handlers[0].read())
	privKey = RSA.importKey(file_handlers[1].read())
	for fh in file_handlers:
		fh.close()
	while 1:
		while 1:
			# receive credentials from the atm
			dec_creds = receive_message_dec(connectionSocket, MESSAGE_SIZE, privKey)

			print "Credentials received."
			# the credentials were encrypted with the server's public key
			# so we decrypt it with out private key.
			# NOTE:I've defined new functions that also do the encrypting/decrypting in message exchange
			#dec_creds = privKey.decrypt(credentials)

			dec_creds = dec_creds.split()
			creds = (dec_creds[0], dec_creds[1])
			#erase the decrypted credentials
			dec_creds = None

			#authenticaion: check the credentials against the account list.
			found = False
			for tup in accounts:
				if creds[0] == tup[0]:
					#attempt to verify the password against the argon2 hash
					if argon2.verify(creds[1], tup[1]):
						found = True
					else:
						break
			if found:
				print ("Credential Match!")
				send_message_enc(connectionSocket, AUTH_SUCCESS, MESSAGE_SIZE, pubKey)
				recordHistory(creds[0], 'login', False)
			else:
				print "No Match."
				#send a message back to the atm refusing the credentials
				send_message_enc(connectionSocket, AUTH_FAILURE, MESSAGE_SIZE, pubKey)
				recordHistory(creds[0], 'login', True)
				continue
			break
		#at this point, the user is authenticated, we should ensure the password is no longer in memory
		#all that is required from here on is the user's 6-digit account number
		username = creds[0]
		creds = None

		#now we're expecting a request from the user
		while 1:
			#get a request from the server
			print "Ready to receive requests from user {} from atm {}".format(username, atm_num)
			dec_request = receive_message_dec(connectionSocket, MESSAGE_SIZE, privKey)
			print "request received: {} from user {} from atm {}".format(dec_request, username, atm_num)

			args = dec_request.split()
			#the customer wishes to see their balance

			if dec_request[0] == '1':
				#retrieve balance
				balance = 0
				for tup in account_balances:
					if username == tup[0]:
						balance = tup[1]
				response_str = "Your balance: ${:.2f}".format(balance)
				send_message_enc(connectionSocket, response_str, MESSAGE_SIZE, pubKey)
				print 'BALANCE: SUCCESS'
				recordHistory(username, 'view_balance')
			#the customer wishes to make a withdrawal

			elif dec_request[0] == '2':
				#search the account list by id and retrieve the balance
				amount = round(float(args[1]),2)
				count = 0
				for account in account_balances:
					if username == account[0]:
						break
					count += 1
				#test whether the withdrawal is valid or not
				if (round(account_balances[count][1] - amount, 2) >= 0):#valid
					account_balances[count] = (account_balances[count][0], account_balances[count][1] - amount)
					response_str = 'Withdraw Successful! Your new balance is: ${:.2f}'.format(round(account_balances[count][1],2))
					print 'WITHDRAW: SUCCESS'
					recordHistory(username, 'withdraw', (True, amount))
				else:
					response_str = 'Withdraw failed: insufficient funds. Your balance remains at ${:.2f}'.format(account_balances[count][1])
					print 'WITHDRAW: FAILURE'
					recordHistory(username, 'withdraw', (False, amount))
				send_message_enc(connectionSocket, response_str, MESSAGE_SIZE, pubKey)

			#the customer wishes to make a deposit
			elif dec_request[0] == '3':
				amount = round(float(args[1]),2)
				count = 0
				for account in account_balances:
					if username == account[0]:
						break
					count += 1
				account_balances[count] = (account_balances[count][0], account_balances[count][1] + amount)
				response_str = 'Deposit Successful! Your new balance is: ${:.2f}'.format(round(account_balances[count][1],2))
				print 'DEPOSIT: SUCCESS'
				recordHistory(username, 'deposit', amount)
				send_message_enc(connectionSocket, response_str, MESSAGE_SIZE, pubKey)

			#the customer wishes to view their account history
			elif dec_request[0] == '4':
				#open the customer's banking history, count the number of records
				count = 0
				fh = open('customer_records/{}.txt'.format(username))
				for line in fh:
					send_message_enc(connectionSocket, line, MESSAGE_SIZE, pubKey)
				#send an encrypted empty string to signal that we're done
				end_msg = ' '
				send_message_enc(connectionSocket, end_msg, MESSAGE_SIZE, pubKey)

			#the customer wishes to logoff
			elif dec_request[0] == '5':
				response_str = "You have been logged off, have a nice day!"
				send_message_enc(connectionSocket, response_str, MESSAGE_SIZE, pubKey)
				print 'LOGOFF: SUCCESS'
				recordHistory(username, 'logoff')
				break

			#the atm is to be shutdown
			elif dec_request[0] == '6':
				#send a message of acknowledgement, then close the sockets.
				send_message_enc(connectionSocket, 'OK', MESSAGE_SIZE, pubKey)
				connectionSocket.close()
				sock.close()
				recordHistory(username, 'shutdown')
				print 'ATM {} has been shut down.'.format(atm_num)
				return


# kind of a hack solution for storing accounts, this can definitely be improved on.
# store records in an encrypted file, no plaintext!
# even if the file is encrypted, dont store the actual passwords!
# store a hash of the passwords.
'''accounts = [('123456', 'password'),
			('123457', 'letmein'),
			('004570', 'itshighnoon'),
			('000011', 'iminchargenow'),
			('654321', 'icecream'),
			('735132', 'idontreallythinktheresalimittohowlongthesepasswordscanbesoletsjustseehowthisturnsout')]
#TODO: store this info in an encrypted file, decrpyt and load into memory on start up
#on shutdown, write back into file and encrypt once more
account_balances = [('123456', 1234.56),
					('123457', 56.00),
					('004570', 12.00),
					('000011', 100.00),
					('654321', 654321.00),
					('735132', 245735612341275684567.00)]'''

#instead of hardcoded accounts and balances, we now load them from files
accounts, account_balances = loadAccounts()

# the server will listen for incoming connections on this port, supplied
# on the command line
serverPort = int(sys.argv[1])

#TODO: it seems easy enough to modify this to have 2..n atms connected, specs require at least 2 atms concurrently connected
# create two sockets to handle two atm connections
serverSocket1 = socket(AF_INET, SOCK_STREAM)
serverSocket1.bind(('', serverPort))
serverSocket1.listen(0)

serverSocket2 = socket(AF_INET, SOCK_STREAM)
serverSocket2.bind(('', serverPort + 1))
serverSocket2.listen(0)
# do some multithreading black magic to service each connection
thread1 = threading.Thread(target=service_connection, args=(serverSocket1, 1,))
thread2 = threading.Thread(target=service_connection, args=(serverSocket2, 2,))
thread1.start()
thread2.start()

print "Reporting for duty."

thread1.join()
thread2.join()

writeAccountBalances(account_balances)

print "Goodnight..."
