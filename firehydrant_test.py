import json
import boto3
import os
import base64
import urllib3
import ssl

ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL


secret_name = os.getenv('FIREHYDRANT_SECRET_NAME')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_session_token = os.getenv('AWS_SESSION_TOKEN')

session = boto3.session.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token,
    region_name='eu-west-1'
)

secret_client = session.client(
    service_name="secretsmanager"
)

url = "https://api.firehydrant.io/v1/incidents"


def get_data(token, query_string):
    
    print("Constructing request")
    headers = {
        "Content-Type": "application/json", 
        "Authorization": token,
    }
    http = urllib3.PoolManager()
    response = http.request("GET", f"{url}?{query_string}", headers=headers)
    data = response.json()

    if not data["pagination"]["next"]:
        # publish_data(data["data"])
        return response.status

    while data["pagination"]["next"]:
        # publish_data(data["data"])
        next = data["pagination"]["next"]
        next_url = url + f'?page={next}&{query_string}'
        print(f'Next page: {next_url}')
        response = http.request("GET", next_url, headers=headers)
        data = json.loads(response.data.decode("utf-8"))
        
    # publish_data(data["data"])
    return response.status 

def get_secret():
    
    print("Retrieving secret")

    try:
        get_secret_value_response = secret_client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        print("Error: {}".format(e))
        raise e

    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)['token']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret

if __name__ == "__main__":

    print("getting secret")
    token = get_secret()
    print("getting data")
    get_data(token, query_string="per_page=20000")
    response = {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Successfully called Firehydrant API"
            }
        )
    }
    print("finished getting data")
