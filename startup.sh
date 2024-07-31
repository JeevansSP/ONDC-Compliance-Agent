#!/bin/bash
sudo fuser -k 443/tcp
sudo fuser -k 5000/tcp

cd /home/app/hackathon
source env/bin/activate
sudo python3 main.py
  
sudo systemctl restart nginx
