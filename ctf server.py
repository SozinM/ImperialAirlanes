import socket
import logging
import pickle
import re
import mysql.connector
from threading import Thread
import qrcode



adminIP = ['127.0.0.1']
commands = ['buyTicket', 'adminPanel', 'sendTicket', 'showFlights']
db_list = []
db_users = []
db_legacy_users = []

class Server():

    def __init__(self):
        self.connections = {}
        self.db = Database()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('', 10000)
        print('starting up on {} port {}'.format(*self.server_address))
        self.sock.bind(self.server_address)
        self.sock.listen(10000)
        self.handler()

    def handler(self):
        while True:
            user_conn, user_addr = self.sock.accept()
            if self.connections.get(user_addr):
                self.connections.update({user_addr: [user_conn,self.connections.get(user_addr)[1]]})
            else:
                self.connections.update({user_addr: [user_conn,10000]})
            thread = Thread(target = self.userThread, args=(user_conn, user_addr))
            thread.start()

    def userThread(self,user_conn, user_addr):
        print('client {} connected'.format(user_addr))
        while True:
            try:
                command = pickle.loads(user_conn.recv(1024))['command']
            except:
                continue
            if command.replace("'","").replace('"','') in commands:
                print('client {} command {}'.format(user_addr,command))
                eval('self.{}(user_conn)'.format(command))


    def buyTicket(self,user_conn):
        checking_state = True
        user_conn.send(pickle.dumps('Enter SecondName'))
        SecondName = pickle.loads(user_conn.recv(1024))
        if not re.match('[a-zA-Z]+',SecondName):
            user_conn.send(pickle.dumps("Error {} is invalid".format(SecondName)))
            return False

        user_conn.send(pickle.dumps('Enter FirstName'))
        FirstName = pickle.loads(user_conn.recv(1024))
        if not re.match('[a-zA-Z]+', FirstName):
            user_conn.send(pickle.dumps("Error {} is invalid".format(FirstName)))
            return False

        user_conn.send(pickle.dumps('Enter Patronymic'))
        Patronymic = pickle.loads(user_conn.recv(1024))
        if not re.match('[a-zA-Z]+', Patronymic):
            user_conn.send(pickle.dumps("Error {} is invalid".format(Patronymic)))
            return False

        user_conn.send(pickle.dumps('Enter Passport'))
        Passport = pickle.loads(user_conn.recv(1024))
        if not re.match('[0-9]{10}', Passport):
            user_conn.send(pickle.dumps("Error {} is invalid".format(Passport)))
            return False

        user_conn.send(pickle.dumps('Enter TelephoneNumber'))
        TelephoneNumber = pickle.loads(user_conn.recv(1024))
        if not re.match('[0-9]{10}', Passport):
            user_conn.send(pickle.dumps("Error {} is invalid".format(Passport)))
            return False

        user_conn.send(pickle.dumps('Enter PlaceNumber'))
        try:
            PlaceNumber = int(pickle.loads(user_conn.recv(1024)))
        except:
            user_conn.send(pickle.dumps("Error {} is invalid".format(PlaceNumber)))
            return False

        user_conn.send(pickle.dumps('Enter privileges'))
        try:
            Privileges_Privilege = int(pickle.loads(user_conn.recv(1024)))
        except:
            user_conn.send(pickle.dumps("Error {} is invalid".format(Privileges_Privilege)))
            return False

        user_conn.send(pickle.dumps('Enter flight'))
        try:
            Flight_VoyageCode = int(pickle.loads(user_conn.recv(1024)))
        except:
            user_conn.send(pickle.dumps("Error {} is invalid".format(Flight_VoyageCode)))
            return False

        try:
            id = int((self.db.addTicket(SecondName, FirstName, Patronymic, PlaceNumber, Passport,
                                                      TelephoneNumber, Privileges_Privilege,Flight_VoyageCode)))
            user_conn.send(pickle.dumps('Complete'))
            self.sendTicket(user_conn, id)
        except:
            user_conn.send(pickle.dumps('Error'))



    def adminPanel(self,user_conn,user_addr):
        if user_addr not in adminIP:
            return
        query = pickle.loads(user_conn.recv(1024))
        user_conn.send(pickle.dumps(self.db.rawQuery()))

    def sendTicket(self,user_conn,ticket_id):
        ticket = self.db.getTicket(ticket_id)
        print(ticket)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(ticket)
        qr.make(fit=True)
        img = qr.make_image()
        img.save('{}'.format(ticket))
        f = open('{}'.format(ticket),'rb')
        data = f.read(1000000)
        f.close()
        user_conn.send(data)

    def showFlights(self,user_conn):
        planes = self.db.getPlanes()
        print(planes)
        user_conn.send(pickle.dumps(planes))

class Database():
    def __init__(self):

        self.connect = mysql.connector.connect(user='root', password='777maikl',
                              host='127.0.0.1',
                              database='Passengers')
        self.crs = self.connect.cursor()

        self.connect2 = mysql.connector.connect(user='root', password='777maikl',
                                               host='127.0.0.1',
                                               database='mydb')
        self.crs2 = self.connect.cursor()

    def getTicket(self,id):
        self.crs.execute('''SELECT * FROM tickets where TicketNumber={}'''.format(id))
        try:
            ticket = self.crs.fetchall()
            return ticket
        except:
            return 'Error'
    def rawQuery(self,query): #legacy delete it
        connect = mysql.connector.connect(user='john', password='12345678',
                                          host='127.0.0.1',
                                          database='mydb')
        crs = connect.cursor()
        crs.execute(query)
        try:
            return crs.fetchall()
        except:
            return []

    def addTicket(self,SecondName, FirstName, Patronymic, PlaceNumber, Passport,TelephoneNumber, Privileges_Privilege, Flight_VoyageCode):
        self.crs.execute('''INSERT INTO tickets
                         (SecondName, FirstName, Patronymic, PlaceNumber, Passport,
                         TelephoneNumber, Privileges_Privilege, Flight_VoyageCode) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}');'''
                         .format(SecondName, FirstName, Patronymic, PlaceNumber, Passport,TelephoneNumber, Privileges_Privilege, Flight_VoyageCode))
        idticket = self.crs.lastrowid
        self.connect.commit()
        return idticket

        #return self.crs.fetchall()

    def getPlanes(self):
        self.crs2.execute('''SELECT `flight`.`VoyageCode`,
                         `flight`.`AirplaneCode`,
                         `flight`.`AirportOfDeparture`,
                         `flight`.`AirportOfArrival`,
                         `flight`.`DepartureDate`,
                         `flight`.`ArrivalDate`
                         FROM `passengers`.`flight`;''')
        return self.crs2.fetchall()




def main():
    srv = Server()

if __name__ == '__main__': main()