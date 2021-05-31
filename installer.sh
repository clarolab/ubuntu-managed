
sudo echo "
[Unit]
Description=claro lab security check
After=syslog.target network.target clamav-freshclam.service
[Service]
Type=simple
WorkingDirectory = $(pwd)
ExecStart=/usr/bin/python3 $(pwd)/securitycheck.py
StandardOutput=syslog
StandardError=syslog
[Install]
WantedBy=multi-user.target " > /lib/systemd/system/securitycheck-py.service


sudo systemctl daemon-reload
sudo systemctl enable securitycheck-py.service
sudo systemctl start securitycheck-py.service

echo 'securitycheck successfully installed'