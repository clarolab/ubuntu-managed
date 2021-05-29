import subprocess as sub
from datetime import datetime, timedelta
import re
import sys
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

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
        body += 'firewall is not active'

    #antivirus
    hasAntiviurs = False
    try:
        hasAntiviurs = sub.check_output(('pgrep','freshclam')).decode('utf-8') != ''
    except:pass
    if(not hasAntiviurs):
        body += 'antivirus is not enabled'

    # Encryption
    devices_staus = sub.check_output(('sudo', 'dmsetup', 'status')).decode('utf-8')
    if(devices_staus.find('crypt') != -1):
        body += 'device is unencripted'


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
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, message)


def parse_config_file():
    #user info
    config_data={}
    try:
        config_file = open("config", "r")
    except :
        print('securityCheck: error could not open config file')
        return None
    try:
        for l in config_file.readlines():
            var, val = l.split('=')
            var=var.strip()
            val=val.strip()
            if (val.lower() == 'false'):
                val=False
            elif (val.lower() == 'true'):
                val=True
            config_data[var]=val
    except :
        print('securityCheck: error parsing config file')
        return None

    if (set(config_data.keys()) != {'notifyOnSucceded', 'smtpServer', 'personalEmail', 'password', 'name', 'localEmail', 'managerEmail', 'companyName', 'senderEmail','verbose'} or '' in config_data.values()):
       print('securityCheck: invalid config file')
       return None
    

    return config_data



config_data = parse_config_file()

if(config_data):
    for arg in sys.argv:
        if (arg == 'v' or arg == 'verbose'):
            config_data['verbose'] = True

    body = get_body()
    if(config_data['notifyOnSucceded'] and not body):
        body = 'success on all security checks'
    if(body):
        send_email(smtp_server=config_data['smtpServer'],
        sender_email=config_data['senderEmail'],
        password=config_data['password'],
        recipient_email=[config_data['managerEmail'], config_data['personalEmail']],
        body=body,
        subject=f"security report for {config_data['name']}")


