import socket
from time import sleep

import pandas as pd

host = 'spark-master'
port = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
while True:
    print('\nListening for a client at',host , port)
    conn, addr = s.accept()
    print('\nConnected by', addr)
    sent_count = 0
    if(addr):
        try:
            print('\nReading file...\n')
            df = pd.read_csv('./data/animal-crossing.csv')
            textLines = df.text
            for line in textLines:
                out = (line + '\n').encode('utf-8')
                print('Sending line: -',line)
                conn.send(out)
                sent_count += 1
                sleep(0.3)
            print('End Of Stream, total lines sent: ', sent_count)
        except socket.error:
            print ('Error Occured.\n\nClient disconnected.\n')
conn.close()
