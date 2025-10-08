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

def initialize_latency_dict():
    a_ping = subprocess.run(['ping','-c','1',SERVER_A],capture_output=True)
    b_ping = subprocess.run(['ping','-c','1',SERVER_B],capture_output=True)
    a_match = re.search(avg_rtt_regex,str(a_ping.stdout))
    b_match = re.search(avg_rtt_regex,str(b_ping.stdout))
    if a_match and b_match:
        a_avg = float(a_match.group(1))
        b_avg = float(b_match.group(1))
        latency_dict['A'] = a_avg
        latency_dict['B'] = b_avg


def ping():
    a_ping = subprocess.run(['ping','-c','1',SERVER_A],capture_output=True)
    b_ping = subprocess.run(['ping','-c','1',SERVER_B],capture_output=True)
    a_avg = re.search(avg_rtt_regex,str(a_ping.stdout))
    b_avg = re.search(avg_rtt_regex,str(b_ping.stdout))
    if a_avg and b_avg:
        print(float(a_avg.group(1)))
        print(float(b_avg.group(1)))
        
def ping_scheduler():
    schedule.every(10).seconds.do(ping)
    while True:
        schedule.run_pending()
        time.sleep(1)

initialize_latency_dict()

ping_thread = threading.Thread(target=ping_scheduler)
ping_thread.start()
    


