import boto3
import json
import logging

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
product = "/product"
products = "/products"


def lambda_handler (event, context)
    logger.info(event)                 # Log request event to see how request looks like
    httpMethod = event['httpMethod']   # extract http method from event object
    path = event['path']               # extract path from event object