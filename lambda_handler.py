
import boto3
from json import loads
from botocore.exceptions import ClientError


table_name="cpdtables"
def sms_notification(phone_number,message):
    """
    Publishes a text message directly to a phone number without need for a subscription.
    :param message: The message to publish.
    :param phone_number:The phone number that receives the message.This must be
    in E.164 format. For example , a US phone number might be +12065550101
    :return: The ID of the message.
    """
    try:
        sns_client=boto3.client('sns',region_name="us-west-2")
        response= sns_client.publish(
        PhoneNumber=phone_number,
        Message=message)
        #print("Message sent to mobile number")
        print(response)
         
    except ClientError as e:
      print(e)
     
def lambda_handler(event,context):
  phone_number="ZZ-ZZZZZZZZZZ" 
  dynamo_resource=boto3.resource("dynamodb",region_name="us-west-2")
  table=dynamo_resource.Table(table_name)
  message=event["Records"][0]["Sns"]["Message"] # returns a JSON string
  message=loads(message)# converts the string into a Pyhton dictionary
  bucket=message["Records"][0]["s3"]["bucket"]["name"]
  
  key=message["Records"][0]["s3"]["object"]["key"]
  rekognition_client=boto3.client('rekognition',region_name="us-west-2") 
  response=rekognition_client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':key}})
  for detection in response['TextDetections']:
    text=detection['DetectedText']
    confidence=round(detection['Confidence'],3)
    id=detection['Id']
    type=detection['Type']
    data={"Id":text+str(id),"ImageName":key,"Text":text,"ConfidenceLevel":str(confidence),"Type":type}
    table.put_item(Item=data)
    if(text.capitalize().__contains__("Hazard") or text.capitalize().__contains__("Danger")):
        sms_notification(phone_number,"hello something bad happened")
        
     
  
     

