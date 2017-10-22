import socket
import time
from base64 import b64decode, b64encode
import os

BUFSIZE = 4096

def recv(client):    
    data = ''
    while True:
        r = client.recv(BUFSIZE)
        data += r
        if len(r) < BUFSIZE:
            break
    return data

def hex_bytes():
    for i in range(256):
        yield chr(i).encode('hex')

def play_round(client, hex_payload):
    recv(client)
    client.send('1')
    recv(client)
    client.send(hex_payload.decode('hex'))
    a = recv(client).strip('\n')
    while 'answer' not in a:
        a = recv(client).strip('\n')
    decoded = a[a.index(':')+2:].encode('hex')
    print '==> %s' % hex_payload
    print '<== %s' % decoded
    return decoded

def send_secret(client, secret):
    recv(client)
    client.send('2')
    recv(client)
    client.send(secret)
    flag = recv(client)
    return flag

abort = False
while 1:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect( ('flatearth.fluxfingers.net', 1718) )
    # client.connect(('localhost', 1235))
    banner = recv(client)
    payload = '00'*8
    server_response = play_round(client, payload)
    total = 1
    if len(server_response) < 8:
        time.sleep(.5)
        continue
    for i in range(0, 16, 2):
        for hb in hex_bytes():
            if hb != '00':
                candidate = payload[0:i] + hb + payload[i+2:] 
                result = play_round(client, candidate)
                print result
                total += 1
                if total == 1024:
                    abort = True
                    break
                if len(result) < len(server_response):
                    break
                elif len(result) > len(server_response):
                    server_response = result
                    payload = candidate
                    break
                if len(result) == len(server_response) and result != server_response:
                    break
        if len(server_response) == 12:
            secret = ''.join(map(lambda c: chr(((ord(c[1])-64)%256)^ord(c[0])),zip(payload.decode('hex'), b64encode(server_response.decode('hex'))))).encode('hex')
            print send_secret(client, secret)        
            exit()
        if abort:
            abort = False
            break
    print 'Reconnecting...'
    client.close()
    time.sleep(.5)
