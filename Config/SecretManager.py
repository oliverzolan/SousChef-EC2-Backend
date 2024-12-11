import boto3
import json

def get_secret(secret_name, region_name):
    """
    Retrieve a secret from AWS Secrets Manager.
    """
    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            return json.loads(response['SecretString'])
        else:
            raise Exception("SecretBinary is not supported")
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        raise e

