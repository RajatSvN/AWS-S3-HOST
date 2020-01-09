import logging
import boto3
from botocore.exceptions import ClientError
import pyfiglet
import json
import time
import os

def prRed(skk): print("\033[91m {}\033[00m" .format(skk)) 
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))

def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError:
        #logging.error(e)
        return False
    return True

def config_as_WebHost(bucket_name,index,error):

    try:
        # Define the website configuration
        website_configuration = {
            'ErrorDocument': {'Key': error},
            'IndexDocument': {'Suffix': index},
            }
            # Set the website configuration
        s3 = boto3.client('s3')
        s3.put_bucket_website(Bucket=bucket_name,WebsiteConfiguration=website_configuration)
        return True
    except:
        return False

def create_bucket_policy(bucket_name):
    try:
        bucket_policy = {
            "Version":"2012-10-17",
            "Statement":[{
 	        "Sid":"PublicReadForGetBucketObjects",
                "Effect":"Allow",
 	        "Principal": "*",
            "Action":["s3:GetObject"],
            "Resource":["arn:aws:s3:::"+bucket_name+"/*"
            ]
            }
        ]
        }

        # convert policy from JSON to String
        bucket_policy = json.dumps(bucket_policy)

        # attach New Policy
        s3 = boto3.client('s3')
        s3.put_bucket_policy(Bucket=bucket_name,Policy=bucket_policy)
        return True
    except:
        return False

def upload(bucket_name,source_path):
    try:
        sync_command = f"aws s3 sync "+source_path+" s3://"+bucket_name+"/"
        os.system(sync_command)
        return True
    except:
        return False


def createCDN(bucket_name,index,directory_location):
    try:
        client = boto3.client('cloudfront')
        response = client.create_distribution(
            DistributionConfig={
                'CallerReference': "initialAttempt",
                'DefaultRootObject': index,
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': '1',
                            'DomainName': bucket_name+'.s3.amazonaws.com',
                            'OriginPath': directory_location,
                            'S3OriginConfig': {
                                'OriginAccessIdentity': ''
                            }
                        }
                    
                    ]
                
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': '1',
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {
                            'Forward': 'none'
                        }
                    
                    },
                    'ViewerProtocolPolicy': 'allow-all',
                    'MinTTL': 0,
                    'AllowedMethods': {
                        'Quantity': 2,
                        'Items': [
                            'GET','HEAD'
                        ],
                        'CachedMethods': {
                            'Quantity': 2,
                            'Items': [
                                'GET','HEAD'
                            ]
                        }
                    },
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0,
                        'Items': []
                    },
                    'SmoothStreaming': False,
                    'DefaultTTL': 86400,
                    'MaxTTL': 31536000,
                    'Compress': False
                
                },
            
                'Comment': 'This is a minimal cloudfront configuration to improve the load time of a Website!',
                'PriceClass': 'PriceClass_All',
                'Enabled': True,
                'HttpVersion': 'http2',
                'IsIPV6Enabled': True
            }
        )
        return True
    except:
        return False


art = pyfiglet.figlet_format("AWS S3 WEB HOST",font="slant")
print(art)

bucket_name = input("Enter a bucket name: ")
region = input("Enter an aws region you want to deploy (eg. ap-south-1(Mumbai) ): ")

while(not create_bucket(bucket_name,region)):
    prRed("An error occured while creating your S3 bucket :( , Try changing the name of bucket and type in a valid region !\n")
    prRed("All Valid regions can be found here : https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html")
    bucket_name = input("Enter a bucket name: ")
    region = input("Enter an aws region you want to deploy (eg. ap-south-1): ")

prGreen("S3 Bucket created successfully in region "+region)

index=input("Enter only the name of the index document of your website (like index.html ): ")
error=input("Enter only the name of the error document of your website (like error.html ): ")

    
while(not config_as_WebHost(bucket_name,index,error)):
    prRed("Bucket Configuration failed :( , Please try again! \n Add only the file name not the full path if you were doing so :) ")
    index=input("Enter only the name of the index document of your website (like index.html ): ")
    error=input("Enter only the name of the error document of your website (like error.html ): ")
    config_as_WebHost(bucket_name,index,error)

prGreen("Bucket Configured as a Web Host successfully!")

prGreen("Adding Bucket Policy.......")


while(not create_bucket_policy(bucket_name)):
    prRed("Facing problems adding policy, Retrying in 2 secs........")
    t =2 
    time.sleep(t)
    create_bucket_policy(bucket_name)

prGreen("Bucket Policy Added Successfully!")

source_path = input("Enter the path of the Folder you want to upload in Linux Format (eg:- ../<folder-to-upload>): ")

while(not upload(bucket_name,source_path)):
    prRed("Error uploading Folder :( , Please Try again")
    source_path = input("Enter the path of the Folder you want to upload in Linux Format (eg. ../<folder-to-upload>): ")

prGreen("Folder Upload Successful, Your Static Website is now Live!\n")

prGreen("Website URL: http://"+bucket_name+".s3-website."+region+".amazonaws.com/<Location-of-your-index-file-in-Local-Directory>\n")



print("Would you like your website to load superfast all around the globe?")
response = input("[y/n] Press y to continue, n to exit. : ")
if response=='y' or response=='Y':
    directory_location = input("Enter the File Path where Index file is located(Don't put a slash at the end): ")
    flag = False
    while(not createCDN(bucket_name,index,directory_location)):
        prRed("There was some error configuring your CDN :( ,trying again in 2 seconds...")
        t=2
        time.sleep(t)
        directory_location = input("Enter the File Path where Index file is located(Don't put a slash at the end): ")
    prGreen("CDN Configured Properly, Effect may be seen in 20-30 minutes.")
    prGreen("Process Complete.")    
elif response=='n' or response=='N':
    prGreen("Process Complete.")
else:
    prRed("Invalid key Pressed! Dumping Process.")










    

    
