Name: Eric Lara
email: remigar@csu.fullerton.edu
Contributions:
This project was written entirely by myself.

RUNNING THE PROJECT:
  This project requires the passlib and argon2 libraries, which may be installed via pip:
    sudo pip install passlib
    sudo pip install argon2_cffi

  i) Run the init.py script to initialize the account login and balance files, as well as generate keypairs for the atm and server.
    e.g. python init.py
    NOTE: you will be prompted for passwords to encrypt both the id/password file and the id/balance files

  1. start the server python script with a port number
    e.g. python server.py 3000
    NOTE: you will be prompted for the same passwords you used earlier to encrypt the account files

  2. Once the server has been started, start the atm program in separate terminal windows, specify an atm number and port number
    e.g. python atm.py 1 3000
         python atm.py 2 3001
    NOTE: The port supplied to atm 1 must be the port supplied to the server program. The port for the second atm is the same number incremented by 1.

  3. From the atm program, you may enter your credentials to authenticate against the bank server
    example credentials: ID: 123456 password: 'password'
                         ID: 004570 password: 'itshighnoon'
    more ID/password pairs may be found in the init_accounts.py files

  4. Once authenticated, you will have the following options as a user:
      a)View your current balances
      b)Withdraw from your account
      c)Make a Deposit
      d)View your account history
      e)Log off
      f)Shut down the ATM

  5. Once both ATMs have been shut down, you will be prompted from the server program to provide a password to encrypt the account balance file. This password will be used the next time the server is started.
