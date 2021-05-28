#!/bin/bash
clear
touch config
>config
echo ""
echo "security check"
echo ""
echo 'please enter your full name: ' 
read name
echo "name=$name" >> config
clear
echo 'please enter your email: ' 
read email
echo "personalEmail=$email" >> config
clear
echo 'do you want to get the report on your email: (y/n) '  
read notifemail
if [ $notifemail = "y" ] 
then
    echo "localEmail=true" >> config
else
    echo "localEmail=false" >> config
fi
clear
echo 'notify if all security checks pass (y/n) '  
read notifyOnSucceded
if [ $notifyOnSucceded = "y" ] 
then
    echo "notifyOnSucceded=true" >> config
else
    echo "notifyOnSucceded=false" >> config
fi
clear
echo 'please enter your manager email: ' 
read manageremail
echo "managerEmail=$manageremail" >> config
clear

echo 'please select your company:'
echo 'clarolab (1)'
echo 'khoros   (2)'
echo 'act-on   (3)' 
read op;
case $op in
    1) echo 'companyName=clarolab' >> config;;
    2) echo 'companyName=khoros' >> config;;
    3) echo 'companyName=act-on' >> config;;
esac 
clear

echo 'please enter your smtp server: ' 
read smtpServer
echo "smtpServer=$smtpServer" >> config
echo 'please enter your sender email: ' 
read senderEmail
echo "senderEmail=$senderEmail" >> config
echo 'please enter your sender email password: ' 
read password
echo "password=$password" >> config
echo 'verbose=false' >>  config

# sudo echo "
# [Unit]
# Description=claro lab security check
# After=syslog.target network.target clamav-freshclam.service
# [Service]
# Type=simple
# WorkingDirectory = $(pwd)
# ExecStart=/usr/bin/python3 $(pwd)/securitycheck.py
# StandardOutput=syslog
# StandardError=syslog

# [Install]
# WantedBy=multi-user.target " > /lib/systemd/system/securitycheck-py.service


# sudo systemctl daemon-reload
# sudo systemctl enable securitycheck-py.service
# sudo systemctl start securitycheck-py.service

# echo 'successfully installed'