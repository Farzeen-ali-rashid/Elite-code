import boto3
import json
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


dynamodbTableName = "product-inventory"
dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(dynamodbTableName)

getMethod = "GET"
postMethod = "POST"
patchMethod = "PATCH"
deleteMethod = "DELETE"
healthPath = "/health"
productPath = "/product"
productsPath = "/products"


def lambda_handler (event, context):
    logger.info(event)                 # Log request event to see how request looks like
    httpMethod = event['httpMethod']   # extract http method from event object
    path = event['path']               # extract path from event object

    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)

    elif httpMethod == getMethod and path == productPath:
        response = getProduct(event['queryStringParameters']['productId'])
    
    elif httpMethod == getMethod and path == productsPath:
        response = getProducts()

    elif httpMethod == postMethod and path == productsPath:
        response = saveProduct(json.loads(event['body']))  # Extract request body from event object

    elif httpMethod == patchMethod and path == productsPath:
        requestBody = json.loads(event['body']) 
        response = modifyProduct(requestBody['productId'], requestBody['updateKey'], requestBody['updateValue'])

    elif httpMethod == deleteMethod and path == productsPath:
         requestBody = json.loads(event['body'])
         response = deleteProduct(requestBody['productId'])

    else:
        response = buildResponse(404, 'Not Found')

    return response


def getProduct(productId):
    try:
        response = table.get_item(
            Key = {
                 'productId' : productId
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message' : 'ProductId: %s not found' %productId})
    except:
        logger.exception('Do your custom error handling here. I am just logging out here!')
        

def getProducts():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey = response['LastEvaluatedKey'])
            result.extend(response['Items'])

        body =  {
            'products' : result
        }

        return buildResponse(200, body)
    except:
     logger.exception('Do your custom error handling here. I am just logging out here!')


def saveProduct(requestBody):
    try:
        table.put_item(Item = requestBody)
        body ={
            'Operation' : 'SAVE',
            'Message': 'SUCCESS',
            'Item' :  requestBody
        }
        return buildResponse(200, body)
    except:
        logger.exception('Do your custom error handling here. I am just logging out here!')

def modifyProduct(productId, updateKey, updateValue):
    try:
        response = table.update_Item(Key = {
            'productId' : productId
        },
         UpdateExpression = 'set %s =  :value' % updateKey,
         ExpressionAttributeValues = {
             ':value' : updateValue
         },
         ReturnValues = 'UPDATED_NEW'
        )

        body ={
            'Operation' : 'UPDATE',
            'Message': 'SUCCESS',
            'UpdateAttributes' : response
        }

        return buildResponse(200, body)
    except:
        logger.exception('Do your custom error handling here. I am just logging out here!')

def deleteProduct(productId):
    try:
        repsonse = table.delete_item(
            Key = {
                'productId' : productId
            },
            ReturnValues = 'ALL_OLD'
        )

        body ={
            'Operation' : 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem' : repsonse
        }

        return buildResponse(200, body)
    
    except:
        logger.exception('Do your custom error handling here. I am just logging out here!')





def buildResponse(statuscode, body = None):
    response = {
        'statuscode' : statuscode,
        'headers' : {
            'Content-Type' : 'application/json',
            'Access-Control-Allow-Origin' : '*'      # This is important if we need to integrate with FE with differenet hostname. Allows cross region access
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls= CustomEncoder)
    return response


    