#generate public/private keypairs for atms 1 and 2 as well as the bank server
from Crypto.PublicKey import RSA




#create keys for the two atms and write them to the appropriate directories
#write the atm public keys to the server directory


for i in range(1,3):
    key = RSA.generate(2048)
    f = open('atm/keys/atm{}_PRkey.pem'.format(i), 'w')
    f.write(key.exportKey('PEM'))
    f.close()

    pub_key = key.publickey()
    file_handlers = (open('atm/keys/atm{}_PUBkey.pem'.format(i), 'w'), open('server/keys/atm{}_PUBkey.pem'.format(i), 'w'))
    for fh in file_handlers:
        fh.write(pub_key.exportKey('PEM'))
        fh.close()

#create keypair for server
key = RSA.generate(2048)
f = open('server/keys/server_PRkey.pem', 'w')
f.write(key.exportKey('PEM'))
f.close()

pub_key = key.publickey()
file_handlers = (open('atm/keys/server_PUBkey.pem', 'w'), open('server/keys/server_PUBkey.pem', 'w'))
for fh in file_handlers:
    fh.write(pub_key.exportKey('PEM'))
    fh.close()
