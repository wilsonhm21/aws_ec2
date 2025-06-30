from app import app
from flask import render_template, request, redirect
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
    files = s3.list_objects_v2(Bucket=bucket_name).get('Contents',[])
    json_files = [f['Key'] for f in files if f['Key'].endswith('.json')]
    return render_template("index.html", files=json_files)

@app.route('/guardar', methods=['POST'])
def guardar():
    file = request.form['file']
    # descarga JSON
    response = s3.get_object(Bucket=bucket_name, Key=file)
    data = json.loads(response['Body'].read().decode('utf-8'))

    conn = pymysql.connect(
        host=rds_host, user=rds_user, password=rds_pass, db=rds_db
    )
    with conn.cursor() as cur:
        sql = """
        INSERT INTO reportes (CODIGO, `CODIGO OEM`, `MARCA AUTOMOVIL`, MODELO, DESCRIPCION,
                              STOCK, DIAMETRO, MEDIDA, AÑO, MOTOR)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        for row in data:
            valores = [
                row.get("CODIGO",""),
                row.get("CODIGO OEM",""),
                row.get("MARCA AUTOMOVIL",""),
                row.get("MODELO",""),
                row.get("DESCRIPCION",""),
                row.get("STOCK",""),
                row.get("DIAMETRO",""),
                row.get("MEDIDA",""),
                row.get("AÑO",""),
                row.get("MOTOR","")
            ]
            cur.execute(sql, valores)
        conn.commit()
    conn.close()
    return redirect("/")
