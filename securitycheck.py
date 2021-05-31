import subprocess as sub
from datetime import datetime, timedelta
import re
import sys
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser
from time import sleep 

#from email.mime.base import MIMEBase



def get_body():
    body=''
    #  unique normal user. UID must be between 1000 y 60000 
    users = sub.check_output(('cat', '/etc/passwd')).decode('utf-8').split('\n')[:-1]
    normal_users=[]
    for u in users:
        u=u.split(':')
        if int(u[2])>=1000 and int(u[2])<=60000:
            normal_users.append(u[0])

    if(len(normal_users) > 1):
        body += 'more than one normal user found \n' 

    # Password updated 
    all_user_status = sub.check_output(('sudo', 'passwd', '-S', '-a' )).decode('utf-8').split('\n')[:-1]
    current_user = ''
    if(len(normal_users)>0):
        current_user=normal_users[0]
    user_info=[]
    for u in all_user_status:
        u=u.split()
        if u[0] == current_user:
            user_info = u
            break
    if(datetime.strptime(user_info[2], "%m/%d/%Y") < datetime.now() - timedelta(days=180)):
        body += 'the password has not been updated in the last 180 days \n'

    #firewall
    ufw = sub.check_output(('sudo', 'ufw', 'status', 'VERBOSE')).decode('utf-8')
    firewall_status = re.findall('Status: (active|inactive)', ufw)
    if(firewall_status != ['active']):
        body += 'firewall is not active\n'

    #antivirus
    hasAntiviurs = False
    try:
        hasAntiviurs = sub.check_output(('pgrep','freshclam')).decode('utf-8') != ''
    except:pass
    if(not hasAntiviurs):
        body += 'antivirus is not enabled\n'

    # Encryption
    devices_status = sub.check_output(('sudo', 'dmsetup', 'status')).decode('utf-8')
    if(devices_status.find('crypt') == -1):
        body += 'device is unencripted\n'

    #crypt_status = sub.check_output(('sudo', 'cryptsetup', 'status', '/dev/mapper/sda5_crypt')).decode('utf-8')[:-1]
    #list_devices = sub.check_output(('sudo', 'blkid' )).decode('utf-8')[:-1]

    #macaddress
    # ifconfig = sub.check_output('ifconfig').decode('utf-8')
    # macaddress = re.findall('(enp|eno|wlp|wlo).{0,10}:[\s\S]*?ether ((?:[0-9a-fA-F]:?){12})', ifconfig)
    # mac_str=''
    # for m in macaddress:mac_str += m[1] + ','

    return body
 

def send_email(smtp_server, sender_email , password, recipient_email, body, subject):
    port = 465  # For SSL
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] =", ".join(recipient_email)
    msg['Subject'] = subject
    msg.attach(MIMEText(body,'plain'))
    message = msg.as_string()
    context = ssl.create_default_context()
    
    back_off = 4 
    server=None
    while(True):
    
        try:
            server = smtplib.SMTP_SSL(smtp_server, port, context=context)
            server.login(sender_email, password)
        except:
            if(back_off < 1024):back_off += back_off
            print(f'securityCheck: server conection failed: trying again in {back_off} seconds')
            sleep(back_off)
        if(server):
            print('sending email..')
            server.sendmail(sender_email, recipient_email, message)
            server.close()
            break

def parse_config_file():
    config = configparser.ConfigParser()
    try:
        config.read('config')
    except:
        print('securityCheck: config file could not be opened')
        return None

    if (set({k for k in config['global'].keys()}) != set({'name','notifyonsucceded','companyname','verbose'})
    or 
    set({k for k in config['email'].keys()}) != set({'personalemail', 'smtpserver', 'localemail', 'senderemail', 'manageremail', 'password'})):
       print('securityCheck: invalid config file')
       return None
    return config
    

config = parse_config_file()

if(config):
    # read arguments pased
    for arg in sys.argv:
        if (arg == 'v' or arg == 'verbose'):
            config['global']['verbose'] = True

    body = get_body()
    if(config.getboolean('global','notifyOnSucceded',fallback=False) and not body):
        body = 'success on all security checks'
    if(body):
        send_email(smtp_server=config['email']['smtpServer'],
        sender_email=config['email']['senderEmail'],
        password=config['email']['password'],
        recipient_email=[config['email']['managerEmail'], config['email']['personalEmail']],
        body=body,
        subject=f"security report for {config['global']['name']}")


print('done')