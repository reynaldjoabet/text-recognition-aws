
from credentials import *  # imports region,access_key_id and other environment variables 
import boto3 
from botocore.exceptions import ClientError
from json import dumps
from glob import glob
import os
import time

s3_resource=boto3.resource('s3',region_name=region,aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)  

lambda_client=boto3.client('lambda',region_name=region,aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)  

bucket="cpdbuckets"
lambda_name="cpdlambda"
statement_id="cpdstatements"
topic_name="cpdtopics"

def create_s3_bucket(bucket_name, region=None):
  """
  function to create s3 bucket in a specified region
  Defaults to us-east1 if not specified
  takes bucket name and region in which bucket is to be created
  it can be either us-east-1 or us-west-2. Default region is us-east-1

  :param bucket_name: Bucket to create 
  :param region: String region to create bucket in, eg 'us-east-1'
  :return None

  """

# Create bucket
  global s3_bucket_name
  global s3_client
  try:
    if region is None:
     s3_bucket_name=bucket_name
     default_region="us-east-1"
     s3_client=boto3.client('s3',region_name=region,aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
     s3_client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration ={
     'LocationConstraint':default_region
     })
     print("s3 bucket successfully created in the default region\n") 
    else:
      s3_bucket_name=bucket_name
      s3_client=boto3.client('s3',region_name=region,aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
      s3_client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration ={
     'LocationConstraint':region
      })
      
      print("s3 bucket successfully created in the specified region\n") 
  except ClientError as e:
      print(e)




def create_sns_instance(topic_name,region=None):
  """
  function to create s3 bucket in a specified region
  Defaults to us-east-1 if not specified
  takes bucket name and region in which bucket is to be created
  it can be either us-east-1 or us-west-2. Default region is us-east-1

  :param topic_name: name of topic  to create 
  :param region: String region to create bucket in, eg 'us-east-1'
  :return: None

  """
  global sns_client
  global topic_arn
# Create sns instance
  try:
    if region is None:
    
     default_region="us-east-1"
     # Get the service client
     sns_client = boto3.client('sns',aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token, region_name=default_region) 
     # Create the topic
     topic_arn = sns_client.create_topic(Name=topic_name)["TopicArn"]
     print(f" SNS topic  created in the defualt region")

    else:
      # Get the service client
     sns_client = boto3.client('sns',region_name=region,aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
     # Create the topic
     topic_arn = sns_client.create_topic(Name=topic_name)["TopicArn"]
     print(f" SNS topic created in the specified region ")

  except   ClientError as e:
      print(e)




def set_sns_access_policy(topicarn,policy):
  """
  S3 just needs to publish messages to SNS topic

  In this case, we want to set a Policy attribute,which helps us define who can access the topic
  By default, only the topic owner can publish or subscribe to the topic.
  """
  try:
   sns_client.set_topic_attributes(
    TopicArn=topicarn,
  AttributeValue= dumps(policy),
  AttributeName="Policy"

)
  except ClientError as e:
      print(e)   
    
  



def upload_files(file_name,bucket_name,object_name=None,args=None):
  
   """
   :param file_name : name of file to upload
   :param bucket_name: bucket name
   :param object_name : name of file on s3
   :param agrs: custom args
   """

   if object_name is None:
     object_name=os.path.basename(file_name).replace(" ","")
     s3_client.upload_file(file_name,bucket_name,object_name,ExtraArgs=args)   



def attach_s3_policy(bucket_name,bucket_policy):
  """
  """
  s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
  print("Policy attached to specified bucket\n")



create_s3_bucket(bucket,region)# call function to create bucket


       
create_sns_instance(topic_name,region)# call function to create sns topic

sns_access_policy={
	"Version": "2012-10-17",
	"Statement": [
		{
			"Principal":{
        "Service": [
          "s3.amazonaws.com",
          
        ]
      },
			"Effect":"Allow",
			"Action":[
				"SNS:Publish"
			],
			"Resource":f"{topic_arn}",

            
		}
        
	]
}



#adds permission  for sns to invoke a Lambda function

def subscribe_sns_topic(topic_arn,protocol,endpoint):
  """
  subscribe to sns topic
  Subscribes an endpoint to the topic. Some endpoint types, such as email,
    must be confirmed before their subscriptions are active. When a subscription
    is not confirmed, its Amazon Resource Number (ARN) is set to
    'PendingConfirmation'.

    :param topic: The topic to subscribe to.
    :param protocol: The protocol of the endpoint, such as 'sms' ,'sqs','http','lambda' or 'email'.
    :param endpoint: The endpoint that receives messages, such as a phone number
    or an email address.For the lambda protocol, the endpoint is the ARN of a Lambda function.
    :return: None
  """
  global subscription_arn
  try:
   subscription_arn=sns_client.subscribe(
  TopicArn=topic_arn,
  Protocol=protocol,
  Endpoint=endpoint,
  ReturnSubscriptionArn=True
   )
   print("Lambda successfully subscribes to SNS topic\n")
  except ClientError as e:
    print(e)  


def lambda_add_permission(lambda_name):

     """
     Grants an Amazon Web Services service  permission to use a function
     Principal for Amazon Web Services services is a domain-style identifier defined by the service, like s3.amazonaws.com or sns.amazonaws.com .
     For Amazon Web Services services, you can also specify the ARN of the associated resource as the SourceArn 
     :param lambda_name: name of existed lambda function to add permission to
     :return : None
     """
     try:
      lambda_client.add_permission(
    Action='lambda:InvokeFunction',
    FunctionName=lambda_name,
    Principal='sns.amazonaws.com',
    SourceArn=f'{topic_arn}',
    StatementId=statement_id,
)
     except ClientError as e:
      print(e)     



# adds permission  to allow sns to trigger it or call function
lambda_add_permission(lambda_name)
 
# set sns policy to allow S3 to publish notifications to it
set_sns_access_policy(topic_arn,sns_access_policy)


images=glob("./images/*") # read all images



"""
Resource-based policies grant permissions to the principal that is specified in the policy. 
"""
bucket_policy={
	"Version": "2012-10-17",
	"Statement": [
		{
			"Principal":{
        "Service": [
           "rekognition.amazonaws.com"
          
        ]
      },
			"Effect":"Allow",
			"Action":[
					"s3:GetObject"
			],
			"Resource":f'arn:aws:s3:::{s3_bucket_name}/*'
		}
	]
}



# lambda subcribes to sns topic
subscribe_sns_topic(topic_arn,"lambda",endpoint)

# Convert the policy from JSON dict to string
bucket_policy= dumps(bucket_policy)

#call function


#Set the new policy
attach_s3_policy(s3_bucket_name,bucket_policy)




bucket_notification = s3_resource.BucketNotification(bucket)


# update the attributes of the BucketNotification resource
bucket_notification.put(
    NotificationConfiguration={
        'TopicConfigurations': [
            {
                'Id':'cpduploadevent',
                'TopicArn': topic_arn,
                'Events': [
                    's3:ObjectCreated:Put'
                ]
            }
        ]
        })
 



for image_name in images: 
  upload_files(image_name,s3_bucket_name)
  time.sleep(int(time_interval))
  print("image uploaded successfully\n")