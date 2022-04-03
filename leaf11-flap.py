import pexpect
import threading
import subprocess
import time
import sys
import re

apic_ip = "172.25.74.191"
#ports = {'102': [['1/4/1','1/4/2','1/4/3','1/4/4','1/7/1','1/7/2','1/7/3'], ['172.31.209.179']]} 

#, '201': [['1/53', '1/55', '1/13', '1/17'], ['172.25.74.199']]}

#ports = {'102': [['1/1','1/2','1/3','1/5','1/6','1/8','1/9','1/12','1/13','1/15','1/18','1/20','1/21','1/22','1/23','1/27','1/28','1/29','1/30'], ['172.25.74.197']]}

ports = {'111': [['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96'], ['10.195.225.75']]}
#ports = {'106': [['1/106'], ['10.28.120.85']]}

#ports = {'118': [['1/1','1/9'], ['10.23.233.202']]}

#ports = {'106': [['1/25', '1/45','1/46','1/98','1/104'], ['10.28.120.85']]}
def login(ip):
    pwd = 'ins3965!'
    ssh  = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@' + ip)
    ssh.expect([".ssword:*"], timeout=120)
    ssh.sendline(pwd)
    ssh.expect(['# '], timeout=120)
    if ssh:
        return ssh
    else:
        print "login to ip failed"
        sys.exit()

def up_resets():
    for node in ports:
        ip = ports[node][1][0]
        session = login(ip)
        #ethernet = 'eth'
        for eth in ports[node][0]:
            ethernet = 'eth' + eth
            cmd = 'show int %s | grep -Ei "Flap|Reset"' %(ethernet)
            session.sendline(cmd)        
            session.expect(['# '], timeout=120)
            resets = session.before
            resets = resets.split('\r\n')[2]
            number = re.match('\d{1,2}', resets.strip())
            print "Number of resets %s for %s on node %s" %(number.group(0), eth, node) 
        

def flap():
    ssh = login(apic_ip)
    ethernet = 'interface ethernet'
    for node in ports:
        #import pdb; pdb.set_trace()
        lea = login(ports[node][1][0])
        lea.sendline("show lldp neighbors | grep Total")
        lea.expect(['# '], timeout=120)
        lldp_before = re.search("\d{1,3}", lea.before.split("\r\n")[1]).group(0)
        print "lldp neighbors found %s, for %s" %(lldp_before, node)
        for port in ports[node][0]:
            ethernet +=  ' ' + port + ','
        #import pdb; pdb.set_trace()
        ethernet = ethernet[:len(ethernet)-1] 
        cmd = 'configure; ' + 'leaf ' + node + '; ' + ethernet + '; '+ 'shutdown; ' + 'end'
        ssh.sendline(cmd)
        ssh.expect(['# '], timeout=120)
        time.sleep(30)
        cmd = 'configure; ' + 'leaf ' + node + '; ' + ethernet + '; '+ 'no shutdown; ' + 'end' 
        ssh.sendline(cmd)
        ssh.expect(['# '], timeout=120)
        ethernet = 'interface ethernet'
        time.sleep(20)
        lea.sendline("show lldp neighbors | grep Total")
        lea.expect(['# '], timeout=120)
        lldp_after = re.search("\d{1,3}", lea.before.split("\r\n")[1]).group(0)
        if lldp_before == lldp_after:
            print "LLDPs match"
        else:
            print "lldps dont match for %s, waiting for 90 more seconds" %(node)
            time.sleep(90)
            lea.sendline("show lldp neighbors | grep Total")
            lea.expect(['# '], timeout=120)
            lldp_after = re.search("\d{1,3}", lea.before.split("\r\n")[1]).group(0)
            if lldp_before == lldp_after:
                print "LLDPs match"
            else:
                print "lldps dont match"
                print "lldps before %s" %(lldp_before)
                print "lldps after %s" %(lldp_after) 
                sys.exit()
def main():
    for i in range(5000):   
        print "Flap number: %d" %(i)
        flap()

main()
         
         
             
    
    
