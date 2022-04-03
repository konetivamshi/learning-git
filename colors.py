import pexpect
import threading
import subprocess
import time
import sys
import re

#leaf_ip = "10.28.120.62"
leaf_ip = "10.23.233.114"
ports=54
#port,status,vlan=0,'',''
leds={'out-of-ser':'green','connected':'green','sfpabsent':'yellow','notconnect':'no-color'}

def login():
    pwd = 'ins3965!'
    ssh  = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@' + leaf_ip)
    ssh.expect([".ssword:*"], timeout=60)
    ssh.sendline(pwd)
    ssh.expect(['# '], timeout=60)
    if not ssh:
        print("login to ip failed")
        sys.exit()

    # s=login()
    for port in range(1,ports+1):
        #cmd = 'show int ethernet 1/{} status | sed -n "4p" | awk "{{print $1}}"'.format(port)
        cmd = "show int ethernet 1/" + str(port) + " status | sed -n '4p' | awk '{print $3}'"
	ssh.sendline(cmd)
        time.sleep(2)
        ssh.expect('#')
        status = ssh.before
	status = status.splitlines()[-2]
	#status = status.split('\n')[1:-1]
	#for i in status:
		#status = i.strip('\r')
       	#print(status)

	cmd = "show int ethernet 1/" + str(port) + " status | sed -n '4p' | awk '{print $4}'"
        ssh.sendline(cmd)
        time.sleep(2)
        ssh.expect('#')
        vlan = ssh.before
	vlan = vlan.splitlines()[-2]
      	checkLed(ssh, port, status, vlan)


def checkLed(ssh,port,status,vlan):

	if vlan == 'trunk':
		cmd = "cat /mit/sys/ch/lcslot-1/lc/leafport-"+ str(port) +"/indled-1/summary | sed -n '5p' | awk '{print $3}'"
        	ssh.sendline(cmd)
        	time.sleep(2)
        	ssh.expect('#')
        	led = ssh.before
        	led = led.splitlines()[-2]
		try:
			if led == leds[status]:
				print("Port" + str(port) + " has correct led")
		        else:
				print("Port" + str(port) + " not has correct led")
			        print("-------------------Please check this port------------------------")
		        print (port, status, vlan,led)
              	except KeyError:
                	print(status + " is not present in led-status. Please check Manually for port " + str(port))
	else:
		cmd = "cat /mit/sys/ch/lcslot-1/lc/fabport-"+ str(port) +"/indled-1/summary | sed -n '5p' | awk '{print $3}'"
                ssh.sendline(cmd)
                time.sleep(2)
                ssh.expect('#')
                led = ssh.before
                led = led.splitlines()[-2]
		try:
                	if led == leds[status]:
                        	print("Port" + str(port) + " has correct led")
                  	else:
                        	print("Port" + str(port) + " not has correct led")
                           	print("-------------------Please check this port------------------------")
              		print (port, status, vlan,led)
          	except KeyError:
                	print(status + " is not present in led-status. Please check Manually for port " + str(port))

print(login())
