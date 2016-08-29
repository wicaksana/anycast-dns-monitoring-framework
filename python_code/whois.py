import subprocess

p = subprocess.Popen(['whois', '-h', 'whois.cymru.com', 'as7500'], stdout=subprocess.PIPE)
out, err = p.communicate()
result = out.decode("utf-8").split('\n')[1]

print(result)