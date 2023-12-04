from socket import *
from mail_client_smtp_func import *
from mail_client_pop3_func import *
from mail_client_gui_functions import *
import time
import os
import subprocess
#run server

os.chdir("D:/")
run_command = "java -jar test-mail-server-1.0.jar -s 2225 -p 3335 -m .test-mail-server/"
process = subprocess.Popen(run_command, shell=True)
time.sleep(2.0)
# Choose a mail server (e.g. Google mail server) and call it mailserver
smtpMailserver : tuple = ("127.0.0.1", 2225)
pop3Mailserver : tuple = ("127.0.0.1", 3335)


app(smtpMailserver, pop3Mailserver)

