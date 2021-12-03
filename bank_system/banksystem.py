import pymysql as pms
import traceback

connection = pms.connect(
	host = "localhost",
	port = 3306,
	user = "root",
	password = "1415",
	db = "banksystem",
	charset = 'utf8'
	)

cursor = connection.cursor()

def get_tuple(cursor, table_name,ignore):
    tuple = []
    cursor.execute('''SELECT column_name, character_maximum_length, data_type, column_default
                    from information_schema.columns
                    where table_schema = "banksystem"
                    and table_name = %s
                    ''', table_name)
    for attr in cursor.fetchall():
        if attr[0] in ignore:
            continue
        if attr[3] != None:
            print(f"※default value of {attr[0]} is {attr[3]}. skip? (y/n)", end='')
            if input() == "y":
                tuple.append(attr[3])
                continue

        print(f"input {attr[0]}", end='')
        if attr[1] != None:
            print(f"(length : {attr[1]}) : ", end='')
        else:
            print(" : ",end='')
        if "int" in attr[2]:
            tuple.append(int(input()))
        else:
            tuple.append(input())
    return tuple


def print_log(logs, s, format):
    print("------log start--------")
    print(format % s)
    for i, log in enumerate(logs):
        print(i, end='\t')
        for l in log:
            from datetime import datetime
            if type(l) is datetime:
                print(l.strftime("%Y-%m-%d %H:%M:%S"), end='\t')
            else:
                print(str(l), end='\t')
        print("")
    print("------log end--------")



def user():
    while True:
        print("1. Make New...\n2. Delete...\n3. Transaction...\n...Other for go back...")
        s1 = input()
        if s1 == '1':
            print("1. Make New User\n2. Make New Account\n3. Set New Protector...Other for go back...")
            s2 = input()
            # Make New User
            if s2 == '1':
                #make new user
                new_user = get_tuple(cursor,'user',['u_id','protector_id'])
                cursor.execute("INSERT INTO user(name,ssn,location,birth_date,credit) VALUES (%s, %s, %s, %s, %s)", new_user)
                cursor.execute("SELECT u_id from user where name=%s and ssn=%s", new_user[0:2])
                u_id = cursor.fetchone()[0]

                #update user phone number
                print("how many phone number do you have? : ", end='')
                n = int(input())
                phones = []
                for _ in range(n):
                    print("input phone number : ", end='')
                    phones.append([u_id, input()])
                cursor.executemany("INSERT INTO user_phone VALUES (%s, %s)", phones)
                connection.commit()

            # Make New Account
            elif s2 == '2':
                print("input Ssn : ",end='')
                ssn = input()
                cursor.execute("SELECT u_id from user where ssn=%s", ssn)
                u_id = cursor.fetchone()
                if u_id == None:
                    raise Exception("Error! No such User!")
                else:
                    u_id = u_id[0]

                cursor.execute("SELECT check_can_make_account(%s)",u_id)
                check = cursor.fetchone()[0]
                if check == 0:
                    raise Exception("Error! Account Creation Failed! you should update protector_id!")

                else:
                    new_account = [u_id]
                    new_account += get_tuple(cursor, 'account', ['u_id', 'acc_number', 'acc_date', 'validity'])

                    cursor.execute('''INSERT INTO account(acc_number, u_id, password, acc_type, balance)
                        VALUES (UUID(), %s, %s, %s, %s)''', new_account)
                connection.commit()



            #Update Protector
            elif s2 == '3':

                print("input protectee's Ssn : ",end='')
                ssn1 = input()
                cursor.execute("SELECT u_id from user where ssn=%s",ssn1)
                if cursor.fetchone()[0] == None:
                    raise Exception("Error! No Such User!")
                print("input protector's Ssn : ",end='')
                ssn2 = input()
                cursor.execute("SELECT u_id from user where ssn=%s", ssn2)
                if cursor.fetchone()[0] == None:
                    raise Exception("Error! No Such User!")

                cursor.execute('''SELECT TIMESTAMPDIFF(YEAR, birth_date, CURDATE())
                                from user where ssn = %s''', ssn2)

                ssn2_age = cursor.fetchone()[0]

                if ssn2_age >= 19: #protector should be over 19
                    cursor.execute('''UPDATE user, (SELECT u_id
                                                    FROM user
                                                    WHERE ssn = %s) as P
                                    SET protector_id = P.u_id
                                    where ssn=%s''',[ssn2,ssn1])
                    connection.commit()
                else:
                    raise Exception("Error! protector should be over 19!")

            else:
                continue
            print("Make New Complete!")
        elif s1 == '2':
            print("1. Delete User\n2. Delete Account\n...Other for go back...")
            s2 = input()

            #Delete User
            if s2 == '1':
                print("WARNING! If you have accounts, they will be also deleted!")
                print("input Ssn of user who you want to delete : ", end='')
                ssn = input()

                cursor.execute("DELETE from user where ssn=%s",[ssn])
                connection.commit()

            #Delete Account
            elif s2 == '2':
                print("input your Ssn and account_number")
                cursor.execute('''DELETE from account where
                                (SELECT user.u_id from user where ssn = %s) = account.u_id
                                and account_number = %s 
                                ''' , input().split())
                connection.commit()
            else:
                continue
            print("Delete Complete!")

        elif s1 == '3':
            print("1. Deposit\n2. Withdrawal\n3. Transfer\n4. lookup\n...Other for go back...")
            s2 = input()
            #Deposit or Withdrawal -> transaction
            if s2 == '1' or s2 == '2':
                transaction = []
                print("input account_number of account & password : ",end='')
                cursor.execute('''SELECT acc_number from account
                                where acc_number=%s and password=%s
                                and validity = 1''',input().split()) #validity = 1 -> locked!
                transaction.append(cursor.fetchone())
                if transaction[0] == None:
                    raise Exception("Error! invalid account_number or password!")
                else:
                    transaction[0][0] = transaction[0][0]

                print("input bank code & branch_name : ", end='')
                cursor.execute("SELECT branch_id from bank where bank_code=%s and branch_name=%s",input().split())
                transaction.append(cursor.fetchone())
                if transaction[1] == None:
                    raise Exception("Error! invalid bank information!")
                else:
                    transaction[1] = transaction[1][0]

                if s2 == '1':
                    print("input how much money to deposit? : ",end='')
                    transaction.append(int(input()))
                    cursor.execute("UPDATE account set balance = balance + %s where acc_number = %s",
                                   [transaction[2],transaction[0]])
                    transaction.append('SUCCESS')
                    cursor.execute('''insert into transaction(acc_number, branch_id, price, result)
                                    values (%s, %s, %s, %s)''', transaction) #log 기록
                    connection.commit()
                else:
                    print("input how much money to withdraw? : ", end='')
                    transaction.append(-int(input())) #minus
                    cursor.execute("UPDATE account set balance = balance + %s where acc_number = %s",
                                   [transaction[2], transaction[0]])
                    cursor.execute("SELECT balance from account where acc_number=%s",transaction[0])

                    if cursor.fetchone()[0] < 0: #under balance

                        connection.rollback() #update 무효
                        transaction.append('FAILED')
                        cursor.execute('''insert into transaction(acc_number, branch_id, price, result)
                                        values (%s, %s, %s, %s)''', transaction) #log 기록
                        connection.commit()
                        raise Exception("Error! Not enough money in your account!")
            #Transfer
            elif s2 == '3':
                transfer = []
                print("input account_number of sender's account & password : ", end='')
                cursor.execute('''SELECT acc_number from account
                                                where acc_number=%s and password=%s
                                                and validity = 1''', input().split())  # validity = 1 -> locked!
                transfer.append(cursor.fetchone())
                if transfer[0] == None:
                    raise Exception("Error! invalid account_number or password!")
                else:
                    transfer[0] = transfer[0][0]

                print("input account_number of receiver's account : ", end='')
                cursor.execute("SELECT acc_number from account where acc_number=%s and validity = 1",input())
                transfer.append(cursor.fetchone())
                if transfer[1] == None:
                    raise Exception("Error! invalid account_numer!")
                else:
                    transfer[1] = transfer[1][0]

                if transfer[0] == transfer[1]:
                    raise Exception("Error! Account_number of sender and receiver are the same!")

                print("input how much money to deposit? : ", end='')
                transfer.append(int(input()))
                cursor.execute("UPDATE account set balance = balance - %s where acc_number = %s",
                                [transfer[2], transfer[0]])
                cursor.execute("SELECT balance from account where acc_number=%s", transfer[0])
                if cursor.fetchone()[0] < 0:  # under balance -> transfer 무효
                    connection.rollback()  # update 무효
                    transfer.append('FAILED')
                    cursor.execute('''insert into transfer
                                    (acc_number_from, acc_number_to, price, result)
                                    values (%s, %s, %s, %s)''',
                                   transfer)  # log 기록
                    connection.commit()
                    raise Exception("Error! Not enough money in your account!")
                else: #transfer 성공
                    cursor.execute("UPDATE account set balance = balance + %s where acc_number = %s",
                                   [transfer[2], transfer[1]])
                    transfer.append("SUCCESS")
                    cursor.execute('''insert into transfer
                                    (acc_number_from, acc_number_to, price, result)
                                    values (%s, %s, %s, %s)''',
                                   transfer)  # log 기록
                    connection.commit()

            elif s2 == '4':
                print("1. lookup balance\n2. lookup transaction log\n3. lookup transfer log\n...Other for go back...")
                s3 = input()
                if s3 == '1':
                    print("input account_number & password : ",end='')
                    cursor.execute('''SELECT balance from account
                                                    where acc_number=%s and password=%s
                                                    and validity = 1''', input().split())  # validity = 1 -> locked!
                    balance = cursor.fetchone()
                    if balance == None:
                        raise Exception("Error! invalid account_number or password!")
                    else:
                        balance = balance[0]
                        print(f"--------------------------\nYour balance is {balance}\n--------------------------")

                elif s3 == '2':
                    print("input account_number & password : ", end='')
                    cursor.execute('''SELECT acc_number from account
                                        where acc_number=%s and password=%s
                                        and validity = 1''',
                                   input().split())  # validity = 1 -> locked!
                    acc_number = cursor.fetchone()
                    if acc_number == None:
                        raise Exception("Error! invalid account_number or password!")
                    else:
                        acc_number = acc_number[0]
                    print("how much log do you want to see? : ",end='')
                    limit = int(input())
                    print("input 1 for show all, 2 for show only success, 3 for show only failed : ",end='')
                    case = {'1':('SUCCESS','FAILED'), '2':('SUCCESS',), '3':('FAILED',)}[input()]
                    cursor.execute('''SELECT acc_number, branch_name, price, result, date
                                    from transaction
                                    natural join bank
                                    where acc_number = %s
                                    and result in %s
                                    LIMIT %s''',[acc_number,case,limit])
                    print_log(cursor.fetchall(),
                              ('#','acc_number','branch_name','price','result','date'),
                              '%-2s%-36s%-15s%-10s%-7s%s')

                elif s3 == '3':
                    print("input account_number & password : ", end='')
                    cursor.execute('''SELECT acc_number from account
                                                            where acc_number=%s and password=%s
                                                            and validity = 1''',
                                   input().split())  # validity = 1 -> locked!
                    acc_number = cursor.fetchone()
                    if acc_number == None:
                        raise Exception("Error! invalid account_number or password!")
                    else:
                        acc_number = acc_number[0]
                    print("how much log do you want to see? : ", end='')
                    limit = int(input())
                    print("input 1 for show all, 2 for show only success, 3 for show only failed : ", end='')
                    case = {'1': ('SUCCESS', 'FAILED'), '2': ('SUCCESS',), '3': ('FAILED',)}[input()]
                    cursor.execute('''SELECT acc_number_from, acc_number_to, price, result, date
                                                        from transfer
                                                        where (acc_number_from = %s or acc_number_to = %s)
                                                        and result in %s
                                                        LIMIT %s''', [acc_number, acc_number, case, limit])
                    print_log(cursor.fetchall(),
                              ('#', 'acc_number_from', 'acc_number_to', 'price', 'result', 'date'),
                              '%-2s%-36s%-36s%-10s%-7s%s')
                else:
                    continue
            else:
                continue

        elif s1 == '4':
            pass
         
        else:
            break


def manager():
    while True:

        ####### 나중에 반드시 주석 해제할 것!!!!!!!!!!!!!!
        '''
        print("input your Ssn")
        cursor.execute("SELECT name from manager where manager_ssn=%s", input())
        m_name = cursor.fetchone()
        if m_name == None:
            raise Exception("Error! you're not Manager!")
        else:
            m_name = m_name[0]

        print(f"Hi, {m_name} manager!")
        '''
        print("1. Make New...\n2. Delete...\n3. Managing...\n...Other for go back...")
        s1 = input()
        if s1 == '1':
            print("1. Make New Bank\n2. Make New Manager\n...Other for go back...")
            s2 = input()
            #make new bank
            if s2 == '1':
                new_bank = get_tuple(cursor, 'bank', ['branch_id'])
                cursor.execute("INSERT INTO bank(bank_code, branch_name, location) VALUES (%s, %s, %s)",new_bank)
                connection.commit()

            #make new manager
            elif s2 == '2':
                new_manager = get_tuple(cursor, 'manager', ['manager_id'])
                cursor.execute("INSERT INTO manager(manager_ssn, name, birth_date) VALUES (%s, %s, %s)", new_manager)
                cursor.execute("SELECT manager_id, TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) as age from manager where manager_ssn=%s", new_manager[0])
                m_id, m_age = cursor.fetchone()
                if m_age < 19:
                    raise Exception("Error! Manager should be older than 19!")

                # update manager phone number
                print("how many phone number do you have? : ", end='')
                n = int(input())
                phones = []
                for _ in range(n):
                    print("input phone number : ", end='')
                    phones.append([m_id, input()])
                cursor.executemany("INSERT INTO manager_phone VALUES (%s, %s)", phones)

                print("which bank do you work on? (input bank_code & branch_name) : ", end='')
                cursor.execute('''INSERT INTO bank_on values
                                (%s, (SELECT branch_id from bank where bank_code=%s and branch_name=%s))
                               ''', [m_id] + input().split())
                connection.commit()
            else:
                continue
            print("Make New Complete!")
        elif s1 == '2':
            print("1. Delete Bank\n2. Delete Manager\n...Other for go back...")
            s2 = input()

            # Delete Bank
            if s2 == '1':
                print("WARNING! If bank have transaction logs, it will be faild!")
                print("WARNING! If bank have managers, it will be also deleted!")
                print("input branch_id of bank who you want to delete : ", end='')
                cursor.execute("DELETE from bank where branch_id=%s", input())
                connection.commit()

            # Delete Manager
            elif s2 == '2':
                print("input your Ssn")
                cursor.execute("DELETE from manager where manager_ssn=%s",input())
                connection.commit()
            else:
                continue
            print("Delete Complete!")
        elif s1 == '3':
            print("1. Managing Accounts\n2. Lookup transaction Logs\n3. Lookup Transfer Logs\n4. Lookup Managing Logs\n...Other for go back...")
            s2 = input()
            if s2 == '1':
                pass
            elif s2 == '2':
                pass
            else:
                continue
            pass
        else:
            break
    
def main(): #main

    
    while True:
        print("1. User mode\n2. Manager mode\n...Other for quit...")
        s = input()
        if s == '1':
            try:
                user()
            except Exception as e:
                print("Error", e.args)
                traceback.print_exc() #나중에 주석 해제할 것!
                continue
            finally:
                connection.rollback()
        elif s == '2':
            try:
                manager()
            except Exception as e:
                print("Error", e.args)
                traceback.print_exc() #나중에 주석 해제할 것!
                continue
            finally:
                connection.rollback()
        else:
            break
    connection.close()

if __name__ == "__main__":
    main()
