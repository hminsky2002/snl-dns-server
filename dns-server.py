import subprocess


SERVER_A = '34.171.194.225'
SERVER_B = '34.174.196.10'


a_ping = subprocess.run(['ping','-c','1',SERVER_A],capture_output=True)
b_ping = subprocess.run(['ping','-c','1',SERVER_B],capture_output=True)

print(a_ping.stdout)
print(b_ping.stdout)
