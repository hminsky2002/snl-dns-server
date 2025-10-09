import time
import schedule
import subprocess
from concurrent.futures import ThreadPoolExecutor
import re
import threading
import socket

SERVER_A = '34.171.194.225'
SERVER_B = '34.174.196.10'

avg_rtt_regex = r'round-trip min/avg/max/stddev = [\d.]+/([\d.]+)/'

latency_dict = {'A':0.0, 'B':0.0} 
latency_lock = threading.Lock()


def ping():
    a_ping = subprocess.run(['ping','-c','1',SERVER_A],capture_output=True)
    b_ping = subprocess.run(['ping','-c','1',SERVER_B],capture_output=True)
    a_match = re.search(avg_rtt_regex,str(a_ping.stdout))
    b_match = re.search(avg_rtt_regex,str(b_ping.stdout))
    if a_match and b_match:
        a_avg = float(a_match.group(1))
        b_avg = float(b_match.group(1))
        latency_lock.acquire()
        latency_dict['A'] = a_avg
        latency_dict['B'] = b_avg
        latency_lock.release()

def initialize_latency_dict():
    ping()
    
    
def ping_scheduler():
    schedule.every(10).seconds.do(ping)
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_server():
    initialize_latency_dict()
    ping_thread = threading.Thread(target=ping_scheduler)
    ping_thread.start()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('0.0.0.0', 53))
    
    while True:
        latency_lock.acquire()
        print(latency_dict['A']+latency_dict['B'])
        latency_lock.release()
        time.sleep(1)

run_server()


    


