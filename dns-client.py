import socket
import os
from dnslib import DNSRecord
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("DNS_HOST", "localhost")
PORT = int(os.getenv("DNS_PORT", "5053"))

d = DNSRecord.question('snl-columbia-university.github.io')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(d.pack(), (HOST, PORT))
received = DNSRecord.parse(sock.recv(1024))

print("Outgoing DNS Query: ", d)
print("Received DNS Query:", received)