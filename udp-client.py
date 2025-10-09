import socket
import sys
from dnslib import DNSRecord

HOST, PORT = "localhost", 5004

d = DNSRecord.question('snl-columbia-university.github.io')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(d.pack(), (HOST, PORT))
received = DNSRecord.parse(sock.recv(1024))

print("Sent:    ", d)
print("Received:", received)