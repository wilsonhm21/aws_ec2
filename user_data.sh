#!/bin/bash
sudo apt update -y
sudo apt install -y python3-pip git

# Clonar el repo
cd /home/ubuntu
git clone https://github.com/wilsonhm21/aws_ec2.git app
cd app

# Instalar dependencias
pip3 install -r requirements.txt

# Configurar variables de entorno para que *todos* los procesos las hereden
echo "OUTPUT_BUCKET=${bucket_name}" | sudo tee -a /etc/environment
echo "RDS_HOST=${rds_host}" | sudo tee -a /etc/environment
echo "RDS_USER=${rds_user}" | sudo tee -a /etc/environment
echo "RDS_PASS=${rds_pass}" | sudo tee -a /etc/environment
echo "RDS_DB=${rds_db}" | sudo tee -a /etc/environment

# Recargar variables
source /etc/environment

# Ejecutar Flask
export FLASK_APP=app
nohup flask run --host=0.0.0.0 --port=80 &
