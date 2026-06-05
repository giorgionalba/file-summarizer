import os
import time
import boto3
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
CARPETA = "documentos"
archivos_procesados = set()

# Genera un resumen del texto en 3 puntos clave usando la IA de Groq.
def resumir(texto):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"Resumí este texto en 3 puntos clave:\n\n{texto}"
            }
        ]
    )
    return response.choices[0].message.content

# Guarda el resumen generado en un bucket de Amazon S3.
def subir_a_s3(nombre_archivo, contenido):
    nombre_resumen = f"resumen_{nombre_archivo}"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=nombre_resumen,
        Body=contenido.encode('utf-8')
    )
    print(f"Subido a S3: {nombre_resumen}")

# Revisa continuamente la carpeta buscando archivos nuevos para resumirlos y subirlos.
def monitorear():
    print(f"Monitoreando carpeta '{CARPETA}'...")
    while True:
        for archivo in os.listdir(CARPETA):
            if archivo.endswith('.txt') and archivo not in archivos_procesados:
                print(f"Archivo nuevo detectado: {archivo}")
                path = os.path.join(CARPETA, archivo)
                with open(path, 'r', encoding='utf-8') as f:
                    texto = f.read()
                print("Generando resumen con IA...")
                resumen = resumir(texto)
                print("Subiendo a S3...")
                subir_a_s3(archivo, resumen)
                archivos_procesados.add(archivo)
                print(f"Listo! {archivo} procesado.\n")
        time.sleep(5)

if __name__ == "__main__":
    monitorear()
