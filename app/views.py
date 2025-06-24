from app import app
from flask import render_template
import boto3
import pymysql
import os
import json

s3 = boto3.client('s3')
bucket_name = os.getenv('OUTPUT_BUCKET')

rds_host = os.getenv('RDS_HOST')
rds_user = os.getenv('RDS_USER')
rds_pass = os.getenv('RDS_PASS')
rds_db   = os.getenv('RDS_DB')

@app.route('/')
def index():
    # Leer archivos del bucket S3
    files = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
    json_files = [f['Key'] for f in files if f['Key'].endswith('.json')]

    # Conexión a RDS
    conn = pymysql.connect(host=rds_host, user=rds_user, password=rds_pass, db=rds_db)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM reportes")
        total = cur.fetchone()[0]
    conn.close()

    return render_template("index.html", files=json_files, total=total)
