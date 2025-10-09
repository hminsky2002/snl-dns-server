import time
import schedule
import subprocess
import re
import threading
import socketserver
import threading
import time
from dnslib import DNSRecord, RR, A
import logging

logging.basicConfig(filename="dns-server.log", level=logging.INFO)

SERVER_A = "34.171.194.225"
SERVER_B = "34.174.196.10"

avg_rtt_regex = r"round-trip min/avg/max/stddev = [\d.]+/([\d.]+)/"

latency_dict = {"A": [0.0, SERVER_A], "B": [0.0, SERVER_B]}
latency_lock = threading.Lock()
logging_lock = threading.Lock()


def ping():
    a_ping = subprocess.run(["ping", "-c", "1", SERVER_A], capture_output=True)
    b_ping = subprocess.run(["ping", "-c", "1", SERVER_B], capture_output=True)
    a_match = re.search(avg_rtt_regex, str(a_ping.stdout))
    b_match = re.search(avg_rtt_regex, str(b_ping.stdout))
    if a_match and b_match:

        a_avg = float(a_match.group(1))
        b_avg = float(b_match.group(1))

        logging_lock.acquire()

        logging.info(f"RTT on ping to {SERVER_A}: {a_avg}")
        logging.info(f"RTT on ping to {SERVER_B}: {b_avg}")

        logging_lock.release()

        latency_lock.acquire()
        latency_dict["A"][0] = a_avg
        latency_dict["B"][0] = b_avg
        latency_lock.release()


def initialize_latency_dict():
    ping()


def ping_scheduler():
    schedule.every(10).seconds.do(ping)
    while True:
        schedule.run_pending()
        time.sleep(1)


class UDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        request = DNSRecord.parse(data)

        logging_lock.acquire()
        logging.info(f"Incoming DNS Query: {str(request)}")

        reply = request.reply()
        qname = request.q.qname

        latency_lock.acquire()
        server_ip = (
            latency_dict["A"][1]
            if latency_dict["A"][0] <= latency_dict["B"][0]
            else latency_dict["B"][1]
        )
        latency_lock.release()

        reply.add_answer(RR(qname, rdata=A(server_ip)))
        socket.sendto(reply.pack(), self.client_address)
        logging.info(f"Outgoing DNS Query: {str(reply)}")
        logging_lock.release()


HOST, PORT = "localhost", 5004
with socketserver.ThreadingUDPServer((HOST, PORT), UDPHandler) as server:

    initialize_latency_dict()
    ping_thread = threading.Thread(target=ping_scheduler)
    ping_thread.daemon = True
    ping_thread.start()

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
