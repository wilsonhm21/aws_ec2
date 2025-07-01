from app import app
from flask import render_template, request, redirect, url_for, flash
import boto3
import pymysql
import os
import json
from datetime import datetime
import pandas as pd

s3 = boto3.client('s3')

# Configuración de entorno
bucket_name = os.getenv('OUTPUT_BUCKET')
rds_host = os.getenv('RDS_HOST')
rds_user = os.getenv('RDS_USER')
rds_pass = os.getenv('RDS_PASS')
rds_db = os.getenv('RDS_DB')

@app.route('/')
def dashboard():
    try:
        # Obtener archivos JSON del bucket S3
        files = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
        json_files = []
        valid_records = 0
        invalid_records = 0
        
        for f in files:
            if f['Key'].endswith('.json'):
                # Obtener metadata adicional
                response = s3.get_object(Bucket=bucket_name, Key=f['Key'])
                data = json.loads(response['Body'].read().decode('utf-8'))
                
                json_files.append({
                    'filename': f['Key'],
                    'date_processed': f['LastModified'].strftime("%Y-%m-%d %H:%M:%S"),
                    'size': f'{f["Size"]/1024:.1f} KB',
                    'records': len(data)
                })
                
                valid_records += len(data)
                # Aquí podrías agregar lógica para contar inválidos si los tienes
        
        # Estadísticas para el dashboard
        stats = {
            'total_files': len(json_files),
            'valid_records': valid_records,
            'invalid_records': invalid_records,
            'storage_used': sum(f['Size'] for f in files if f['Key'].endswith('.json'))/1024/1024
        }
        
        return render_template("dashboard.html", 
                            files=json_files, 
                            stats=stats,
                            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    except Exception as e:
        flash(f'Error al cargar los archivos: {str(e)}', 'danger')
        return render_template("dashboard.html", 
                            files=[], 
                            stats={},
                            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/preview/<filename>')
def preview(filename):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=filename)
        data = json.loads(response['Body'].read().decode('utf-8'))
        
        # Convertir a DataFrame para análisis rápido
        df = pd.DataFrame(data)
        summary = {
            'total_records': len(df),
            'marcas': df['marca'].value_counts().to_dict(),
            'stock_promedio': df['stock'].mean(),
            'precio_promedio': df['precio'].mean()
        }
        
        return render_template("preview.html", 
                            filename=filename,
                            data=data[:10],  # Solo mostramos 10 registros para la vista previa
                            summary=summary)
    
    except Exception as e:
        flash(f'Error al cargar la vista previa: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/guardar', methods=['POST'])
def guardar():
    try:
        filename = request.form['file']
        
        # Descargar JSON
        response = s3.get_object(Bucket=bucket_name, Key=filename)
        data = json.loads(response['Body'].read().decode('utf-8'))
        
        # Conexión a la base de datos
        conn = pymysql.connect(
            host=rds_host, 
            user=rds_user, 
            password=rds_pass, 
            db=rds_db,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cur:
            # Verificar si la tabla existe
            cur.execute("""
                CREATE TABLE IF NOT EXISTS repuestos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo VARCHAR(20) NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    marca VARCHAR(50) NOT NULL,
                    stock INT NOT NULL,
                    precio DECIMAL(10,2) NOT NULL,
                    fecha_procesado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY (codigo)
                )
            """)
            
            # Insertar datos (versión moderna con manejo de duplicados)
            sql = """
            INSERT INTO repuestos (codigo, nombre, descripcion, marca, stock, precio)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                nombre = VALUES(nombre),
                descripcion = VALUES(descripcion),
                marca = VALUES(marca),
                stock = VALUES(stock),
                precio = VALUES(precio)
            """
            
            for row in data:
                valores = (
                    row.get("codigo"),
                    row.get("nombre"),
                    row.get("descripcion"),
                    row.get("marca"),
                    int(row.get("stock", 0)),
                    float(row.get("precio", 0))
                )
                cur.execute(sql, valores)
            
            conn.commit()
            flash(f'Datos de {filename} guardados correctamente en la base de datos!', 'success')
            
    except pymysql.MySQLError as e:
        conn.rollback()
        flash(f'Error de base de datos: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error al procesar el archivo: {str(e)}', 'danger')
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/estadisticas')
def estadisticas():
    try:
        conn = pymysql.connect(
            host=rds_host, 
            user=rds_user, 
            password=rds_pass, 
            db=rds_db,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cur:
            # Estadísticas de la base de datos
            cur.execute("""
                SELECT 
                    COUNT(*) as total_repuestos,
                    SUM(stock) as total_stock,
                    AVG(precio) as precio_promedio,
                    marca,
                    COUNT(*) as cantidad
                FROM repuestos
                GROUP BY marca
                ORDER BY cantidad DESC
            """)
            stats = cur.fetchall()
            
            # Top 10 repuestos con mayor stock
            cur.execute("""
                SELECT nombre, marca, stock, precio
                FROM repuestos
                ORDER BY stock DESC
                LIMIT 10
            """)
            top_stock = cur.fetchall()
            
        return render_template("estadisticas.html",
                            stats=stats,
                            top_stock=top_stock)
        
    except Exception as e:
        flash(f'Error al obtener estadísticas: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()