import boto3

client = boto3.client('cloudfront')


response = client.create_distribution(
    DistributionConfig={
        'CallerReference': "initialAttempt",
        'DefaultRootObject': 'Flames.html',
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': '1',
                    'DomainName': 'flamegame.s3.amazonaws.com',
                    'OriginPath': '/Flamer',
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
        
        'Comment': 'This is a minimal cloudfront configuration',
        'PriceClass': 'PriceClass_All',
        'Enabled': True,
        'HttpVersion': 'http2',
        'IsIPV6Enabled': True
    }
)