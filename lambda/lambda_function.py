import json
import boto3
from OpenSSL import crypto
region = "us-east-1"
topicName = "jitr/demo"
dynamodb_table = 'jitr'

iot = boto3.client('iot', region_name=region)
dynamodb = boto3.client('dynamodb')

def delete_cert_and_policy(deviceId, principals):
    for principal in principals:
        certificateId = principal.split('/')[-1]
        policies = iot.list_attached_policies(target=principal)
        for policy in policies['policies']:
            try:
                #update certificate status to INACTIVE
                iot.update_certificate(
                    certificateId=certificateId, newStatus='INACTIVE'
                )
                #deatch thing's principle
                #Asynchronous call. How to make sure it done or not?
                iot.detach_thing_principal(
                    thingName=deviceId,
                    principal=principal
                )
                #deatch thing's policy
                iot.detach_policy(
                    policyName=policy['policyName'], target=principal
                )
                #delete policy
                iot.delete_policy(policyName=policy['policyName'])
                #delete thing's certificate
                iot.delete_certificate(
                    certificateId=certificateId, forceDelete=True
                )
            except Exception as e:
                print(e)

def lambda_handler(event, context):

    print("event:  ", event)

    certId = event['certificateId']
    accountId = context.invoked_function_arn.split(":")[4]

    #get dsn (device serial number )
    response = iot.describe_certificate(certificateId=certId)
    certificatePem = response['certificateDescription']['certificatePem']
    print(certificatePem)
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, certificatePem)
    serial_number = hex(int(cert.get_serial_number()))[2:]
    print("serial:",str(serial_number))
    deviceId = 'dsn_xx' + '_' + str(serial_number)


    #####template policy, users should revise it according to the uses case
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "iot:Connect"
                ],
                "Resource": "arn:aws:iot:" + region + ":" + str(accountId) + ":client/" + deviceId
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iot:Publish",
                    "iot:Receive"
                ],
                "Resource": "arn:aws:iot:" + region + ":" + str(accountId) + ":topic/" + topicName + "/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iot:Subscribe",
                ],
                "Resource": "arn:aws:iot:" + region + ":" + str(accountId) + ":topicfilter/" + topicName + "/#"
            }
        ]
    }

    #check dsn exists in DynamoDB
    deviceItem = dynamodb.get_item(TableName=dynamodb_table, Key={'dsn': {'S': str(serial_number)}})
    if not deviceItem.get('Item'):
       ######exception handler
       print("dsn not found")
    else:
        # create thing if it does not exist
        try:
            iot.describe_thing(
                thingName=deviceId
            )
        except iot.exceptions.ResourceNotFoundException:
            response = iot.create_thing(
                thingName=deviceId
            )

        # delete certificates which are attached to this thing
        response = iot.list_thing_principals(
            thingName=deviceId
        )
        if response['principals']:
            delete_cert_and_policy(deviceId, response['principals'])

        # get certificate arn and pem
        response = iot.describe_certificate(
            certificateId=certId)
        certificatePem = response['certificateDescription']['certificatePem']
        certificateArn = response['certificateDescription']['certificateArn']


        # attach certificate to thing
        iot.attach_thing_principal(
            thingName=deviceId,
            principal=certificateArn
        )

        # create a policy for thing
        policyDocument = json.dumps(policy)
        policyName = 'Policy_' + deviceId
        iot.create_policy(
            policyName=policyName,
            policyDocument=policyDocument
        )

        # attach policy to certificate
        iot.attach_policy(
            policyName=policyName,
            target=certificateArn
        )
        iot.update_certificate(
            certificateId=certId,                
            newStatus='ACTIVE'
        )
