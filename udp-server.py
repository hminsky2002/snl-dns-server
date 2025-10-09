import socketserver
import threading
import sys
import time
from dnslib import DNSRecord, RR, A

class UDPHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        request = DNSRecord.parse(data)
        print(request)

        reply = request.reply()
        
        qname = request.q.qname 
        reply.add_answer(RR(qname, rdata=A("34.171.194.225")))
        
        socket.sendto(reply.pack(), self.client_address)


HOST, PORT = "localhost", 5004
with socketserver.ThreadingUDPServer((HOST, PORT), UDPHandler) as server:
    server_uptime = 0
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    try:
        while True:
            server_uptime += 1
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()