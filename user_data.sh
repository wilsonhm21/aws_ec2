#!/bin/bash
sudo apt update -y
sudo apt install -y python3-pip git

# Clonar el repo
cd /home/ubuntu
git clone https://github.com/wilsonhm21/aws_ec2.git app
cd app

# Instalar dependencias
pip3 install -r requirements.txt

# Exportar variables de entorno
echo "export OUTPUT_BUCKET='${bucket_name}'" >> ~/.bashrc
echo "export RDS_HOST='${rds_host}'" >> ~/.bashrc
echo "export RDS_USER='${rds_user}'" >> ~/.bashrc
echo "export RDS_PASS='${rds_pass}'" >> ~/.bashrc
echo "export RDS_DB='${rds_db}'" >> ~/.bashrc
source ~/.bashrc

# Ejecutar Flask
export FLASK_APP=app
nohup flask run --host=0.0.0.0 --port=80 &
