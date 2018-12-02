import socket
import pickle

class Client():
    def __init__(self):
        self.connection = ('172.24.1.1',10000)
        self.sock = socket.socket()
        self.sock.connect(self.connection)

    def interface(self):
        print('''Добро пожаловать в пользовательский интерфейс аэропорта.
                 Список команд:
                 1. buy ticket - произвести покупку билета
                 2. send ticket - отправить билет
                 3. show flights - показать доступные рейсы
                 4. exit
                 ''')
        command = 0
        while command != 4:
            command = int(input('Введите команду\n'))
            if command == 1:
                self.sock.send(pickle.dumps({'command':'buyTicket'}))
                self.handle_connections()

            elif command == 2:#in process
                pass
                self.sock.send(pickle.dumps({'command': 'sendTicket'}))
                self.handle_connections()


            elif command == 3:
                self.sock.send(pickle.dumps({'command': 'showFlights'}))
                print(pickle.loads(self.sock.recv(10240)))

    def handle_connections(self):
        data = 'Not initialized'
        while not "Error" in data or not "Complete" in data:
            data = pickle.loads(self.sock.recv(1024))
            if "Enter" in data:
                output = input('{}\n'.format(data))
                self.sock.send(pickle.dumps(output))
            else:
                break
        print('{}'.format(data))

        if "Complete" in data:
            name = input("Введите имя для файла с билетом\n")
            f = open('{}.png'.format(name),'wb')
            qr = self.sock.recv(409600000)
            print(qr)
            f.write(qr)
            f.close()
            print('Ваш билет находится в файле {}.png'.format(name))


def main():
    client = Client()
    client.interface()
if __name__ == '__main__': main()

