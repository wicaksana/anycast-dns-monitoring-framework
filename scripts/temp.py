import subprocess

cmd = 'netcat whois.cymru.com 43 < list.txt | sort -n > list2.txt'
p = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()

# Bulk mode; whois.cymru.com

