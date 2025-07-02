#!/bin/bash
sudo apt update -y
sudo apt install -y python3-pip git


# Clonar el repo
cd /home/ubuntu
git clone https://github.com/wilsonhm21/aws_ec2.git app
cd app

# Instalar dependencias
pip3 install -r requirements.txt

# --- CAMBIO SUGERIDO AQUÍ ---
# Configurar variables de entorno directamente en el shell actual,
# para que el proceso de Flask las herede.
export OUTPUT_BUCKET="${bucket_name}"
export RDS_HOST="${rds_host}"
export RDS_USER="${rds_user}"
export RDS_PASS="${rds_pass}"
export RDS_DB="${rds_db}"
# --- FIN DEL CAMBIO SUGERIDO ---
export FLASK_SECRET_KEY="clave-super-segura-4567" 
# Ejecutar Flask
export FLASK_APP=app
nohup python3 -m flask run --host=0.0.0.0 --port=5000 > flask.log 2>&1 &
