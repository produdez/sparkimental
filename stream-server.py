import socket
from time import sleep

import pandas as pd

HOST = 'spark-master'
PORT = 9999

# open socket
stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
stream_socket.bind((HOST, PORT))
stream_socket.listen(1)

'''
    NOTE:
    Currently, this server listens for incoming connections indefinitely
    and every time spark connects to the server
    the whole data file is re-read and sent over
    -> This is just for the sake of easy testing 
    and not having to re-run the server every time spark disconnects
'''

while True:
    print('Listening for a client at', HOST, PORT)
    conn, addr = stream_socket.accept()
    print('Connected by', addr)
    sent_count = 0
    if(addr): # send all data with delay if connected by spark
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
            # close connection when client disconnects
            print ('Error Occured.\n\nClient disconnected.\n')
            conn.close()
