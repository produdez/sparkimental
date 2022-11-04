import socket
from time import sleep

host = 'spark-master'
port = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
while True:
    print('\nListening for a client at',host , port)
    conn, addr = s.accept()
    print('\nConnected by', addr)
    try:
        print('\nReading file...\n')
        with open('./data/animal-crossing.csv') as f:
            for line in f:
                out = line.encode('utf-8')
                print('Sending line',line)
                conn.send(out)
                sleep(0.1)
            print('End Of Stream.')
    except socket.error:
        print ('Error Occured.\n\nClient disconnected.\n')
conn.close()
