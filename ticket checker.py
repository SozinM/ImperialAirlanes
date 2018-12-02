import mysql.connector
connect = mysql.connector.connect(user='root', password='777maikl',
                              host='127.0.0.1',
                              database='passengers')
crs = connect.cursor()
while True:
    id = input("Введите id")
    crs.execute('SELECT * from passengers.tickets where tickets.TicketNumber = {}'.format(id))
    data = crs.fetchall()
    print(data)
