import json
import boto3

# Nome do seu Glue Job
GLUE_JOB_NAME = "etl-bovespa-job"

# Cliente do Glue
glue_client = boto3.client('glue')

def lambda_handler(event, context):
    try:
        # Extrai informações do evento S3
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            
            print(f"Novo arquivo detectado: s3://{bucket_name}/{object_key}")
            
            # Aciona o Glue Job
            response = glue_client.start_job_run(JobName=GLUE_JOB_NAME)
            
            print(f"Job {GLUE_JOB_NAME} iniciado com sucesso!")
            return {
                'statusCode': 200,
                'body': json.dumps(f"Glue Job {GLUE_JOB_NAME} iniciado!")
            }
    
    except Exception as e:
        print(f"Erro ao iniciar Glue Job: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro ao iniciar Glue Job: {str(e)}")
        }
