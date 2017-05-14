# the driver program for the atm(s)
# user enters their credentials locally, atm validates against the remote bank server
# credentials sent over the network are encrypted with RSA, of course!
# once validated, user is able to make the following requests:
# view balance
# withdraw
# deposit
# exit
# view account history
# Execution: python atm.py <ATM NUMBER (1/2)> <port>
import sys
import os
import re
from getpass import getpass
from Crypto.PublicKey import RSA
from socket import *
from misc_functions import displayMenu
import datetime



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


MESSAGE_SIZE = 256
AUTH_SUCCESS = '1'
AUTH_FAILURE = '0'

atm_num = sys.argv[1]
serverPort = int(sys.argv[2])
serverName = sys.argv[3]

# load the atm private key and bank server public key
if atm_num == '1' or atm_num == '2':
	file_handlers = (open('keys/atm{}_PRkey.pem'.format(atm_num), 'r'),
					 open('keys/server_PUBkey.pem'.format(atm_num), 'r'))
	pubKey = RSA.importKey(file_handlers[1].read())
	privKey = RSA.importKey(file_handlers[0].read())
else:
	print "ERROR: {} is not a valid atm number.".format(atm_num)
	exit(-1)


# initiate the socket for atm-server communications
controlSocket = socket(AF_INET, SOCK_STREAM)

# attempt to connect to the atm server
controlSocket.connect((serverName, serverPort))

while 1:
	while 1:
		# prompt the user for credentials and authenticate against the bank server
		# reprompt the user for an account number if their input doesnt match the
		# 6-digit format
		while 1:
			username = raw_input("Enter your 6-digit account number: ")
			result = re.match(r'^[0-9]{6}$', username)
			if result:
				break
			else:
				print "Please enter a 6-digit account number."
				continue
		# prevent password from being echo'd to the terminal using getpass()
		password = getpass()
		#NOTE: now that we're using argon2, we're no longer hashing passwords before sending them.
		credentials = (username, password)
		creds = ' '.join(credentials)

		print "Validating..."
		#generate a timestamp for this login request
		timestamp = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')
		#send credentials to the server(encrypted with the server's public key)
		send_message_enc(controlSocket, creds + ' ' + timestamp, MESSAGE_SIZE, pubKey)

		#not quite sure if this adequately clears the password provided from memory, more research required
		password = None
		credentials = None

		#get the server's response
		response = receive_message_dec(controlSocket, MESSAGE_SIZE, privKey)

		if response == AUTH_SUCCESS:
			print "Authentication Successful!"
			break
		else:
			print "Authentication failed: account number does not exist or incorrect password or request timed out."
			continue #go through the process again
	#now to do the actual banking stuff.
	while 1:
		displayMenu(username)
		choice = raw_input('Choice: ')
		#the input should be a single integer
		try:
			int(choice)
		except ValueError:
			print 'Invalid.'
			continue
		if len(choice) != 1:
			print 'Invalid.'
			continue
		amount = ''
		#get additional info for withdraws and deposits
		if choice == '2':
			while 1:
				amount = ' ' + raw_input('Please enter an amount to withdraw: $')
				try:
					float(amount)
				except ValueError:
					print ('Please enter a non-negative number')
					continue
				break
		if choice == '3':
			while 1:
				amount = ' ' + raw_input('Please enter an amount to deposit: $')
				try:
					float(amount)
				except ValueError:
					print ('Please enter a non-negative number')
					continue
				break


		#encrypt the user's choice using the server's public key and send it to the server
		send_message_enc(controlSocket, choice + amount, MESSAGE_SIZE, pubKey)
		#get the response from the server
		response = receive_message_dec(controlSocket, MESSAGE_SIZE, privKey)
		print  '\n' + response
		if choice == '4':
			#keep getting more responses until we get an empty string
			while response != ' ':
				response = receive_message_dec(controlSocket, MESSAGE_SIZE, privKey)
				print response
		if choice == '5':
			#clear the atm screen, we dont want subsequent customers viewing previous transactions!
			#of course, you could just scroll up on the terminal window
			#perhaps there's a better way of doing this.
			print '\n' * 100
			break
		if choice == '6':
			controlSocket.close()
			exit(0)
