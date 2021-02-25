from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import random

engine = create_engine('sqlite:///card.s3db')
Base = declarative_base()


class Table(Base):
    __tablename__ = 'card'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String)
    pin = Column(String)
    balance = Column(Integer, default=0)

    def __repr__(self):
        return self.number


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def close_account(card_number):
    session.query(Table).filter_by(number=card_number).delete()
    session.commit()


def exist(card_number):
    return session.query(Table).filter(Table.number == card_number).count()


def login(card_number, card_pin):
    return session.query(Table.number, Table.pin).filter(Table.number == card_number).filter(
        Table.pin == card_pin).count()


def transfer(card_number, money_to_transfer):
    card = session.query(Table).filter_by(number=card_number).first()
    card.balance += money_to_transfer
    session.commit()


def create_account(card_number, card_pin, balances):
    new_account = Table(number=card_number, pin=card_pin, balance=balances)
    session.add(new_account)
    session.commit()


def bal(card_number):
    for instance in session.query(Table).filter(Table.number == card_number):
        return instance.balance


def adjust_bal(card_number, money):
    bala = session.query(Table).filter_by(number=card_number).first()
    bala.balance -= money
    session.commit()


def check_luhn(card_number):
    counter = 0
    var = 0
    if card_number[0] == '3':
        return True
    while counter < 16:
        if counter % 2 == 0:
            temp = int(card_number[counter]) * 2
            if temp > 9:
                var += (temp - 9)
            else:
                var += temp
        else:
            var += int(card_number[counter])

        counter += 1

    if var % 10 == 0:
        return True
    else:
        return False


class BankAccount:

    def __init__(self):
        self.card_number = "400000"
        self.card_pin = ""
        self.balance = 0

    def create_account(self):
        c = ""
        counter = 0
        count = 0
        for _ in range(9):
            self.card_number += str(random.randint(0, 9))
        while counter < 15:
            if counter % 2 == 0:
                temp = int(self.card_number[counter]) * 2
                if temp > 9:
                    c += str(temp - 9)
                else:
                    c += str(temp)
            else:
                c += self.card_number[counter]

            counter += 1

        for i in range(len(c)):
            count += int(c[i])
        tempo = count % 10
        if tempo != 0:
            self.card_number += str(abs(tempo - 10))
        else:
            self.card_number += str(tempo)
        for _ in range(4):
            self.card_pin += str(random.randint(0, 9))


def main():
    random.seed()
    while True:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        user_inp = input()
        if user_inp == "1":
            bank_account = BankAccount()
            bank_account.create_account()
            print(f'''
Your card has been created
Your card number:
{bank_account.card_number}
Your card PIN:
{bank_account.card_pin}
''')
            create_account(bank_account.card_number, bank_account.card_pin, bank_account.balance)

        elif user_inp == "2":
            print('Enter your card number:')
            card_number = input()
            print('Enter your PIN:')
            pin = input()
            if login(card_number, pin) == 1:
                print('You have successfully logged in!')
                while True:
                    print('1. Balance')
                    print('2. Add income')
                    print('3. Do transfer')
                    print('4. Close account')
                    print('5. Log out')
                    print('0. Exit')
                    inp = input()
                    if inp == '1':
                        print(f'Balance: {bal(card_number)}')
                    elif inp == '2':
                        b = int(input('Enter income: '))
                        transfer(card_number, b)
                        print('Income was added!')
                    elif inp == '3':
                        print('Transfer')
                        card = input('Enter card number: ')
                        if check_luhn(card):
                            if exist(card) == 1:
                                if card != card_number:
                                    print('Enter how much money you want to transfer: ')
                                    mon = int(input())
                                    if mon <= bal(card_number):
                                        transfer(card, mon)
                                        adjust_bal(card_number, mon)
                                        print('Success!')
                                    else:
                                        print('Not enough money!')
                                else:
                                    print("You can't transfer money to the same account!")
                            else:
                                print('Such a card does not exist.')
                        else:
                            print('Probably you made a mistake in the card number. Please try again!')
                    elif inp == '4':
                        close_account(card_number)
                        print('The account has been closed!')
                        break
                    elif inp == '5':
                        print('You have successfully logged out!')
                        break
                    elif inp == '0':
                        user_inp = '0'
                        break
            else:
                print('Wrong card number or PIN!')

        if user_inp == '0':
            print('Bye!')
            break


if __name__ == '__main__':
    main()

