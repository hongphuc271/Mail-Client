from socket import *
from mail_client_smtp_func import *
from mail_client_pop3_func import *
from mail_client_gui_functions import *
import time
import os
import subprocess
#run server


run_command = "java -jar test-mail-server-1.0.jar -s 2225 -p 3335 -m .test-mail-server/"
process = subprocess.Popen(run_command, shell=True)
time.sleep(2.0)

if not has_config("./.mails"):
    save_default_config("./.mails")
    #print("Write new config")

cfg = load_config("./.mails")    

login_window(cfg)
app(cfg)

