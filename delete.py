import boto3
import json

def lambda_handler(input, context):
    """
    API Endpoint for creating Recipes.
    """
    client = boto3.client('lambda')

    key = {"id" : int(input['params']['path']['id'])}

    # Create the create object we'll pass to the lambda endpoint
    create = {
        "table_name": "Recipes",
        "key": key
    }

    response = client.invoke(
        FunctionName='DALDelete',
        InvocationType='RequestResponse',
        Payload=json.dumps(create)
    )

    return "deleted"
