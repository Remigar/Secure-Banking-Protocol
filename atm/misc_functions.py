import datetime


def displayMenu(id):
    print '\n\n\n'
    print 'Welcome, user {}.'.format(id)
    print 'Select an option:'
    print '\t1) View Balance'
    print '\t2) Withdraw'
    print '\t3) Deposit'
    print '\t4) View Account History'
    print '\t5) Log Off'
    #I guess every customer can just shut down the ATM if they want to LUL
    print '\t6) [DEBUG]Shut Down ATM'
