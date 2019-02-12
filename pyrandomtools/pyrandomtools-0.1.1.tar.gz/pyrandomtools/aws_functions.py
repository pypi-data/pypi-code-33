# It's ok if we do not have boto3
#
try:
    import boto3
except:
    pass

amazon_regions = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'ca-central-1',
    'eu-central-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'eu-north-1',
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-northeast-3',
    'ap-southeast-1',
    'ap-southeast-2',
    'ap-south-1',
    'sa-east-1',
]

def validate_region(region, service='ec2'):   
    # First try static list
    #
    if region in amazon_regions:
        return True
    
    # Then try boto, but we need permissions so it may fail 
    # which is why we try the static list first
    #
    try: 
        if any(item['RegionName'] == region for item in boto3.client(service).describe_regions().get('Regions',[])):
            return True
    except:
        return False
      
    # Otherwise its not a valid region
    #  
    return False
    
def parse_arn(arn):
    import re

    defaultReply = {
        'Arn': None,
        'Partition': None,
        'Service': None,
        'Region': None,
        'Account': None,
        'RawResource': None,
        'ResourceType': None,
        'Resource': None,
        'Qualifier': None,
    }

    # Undecided if I'm confortable with this, but lets discuss
    #
    if arn is None or not arn.startswith('arn:'):
        return defaultReply

    # Make sure the returned arrar is 6 elements
    parsed = arn.split(':',5)
    while len(parsed) < 6:
        parsed.append('')
            
    reply = {
        'Arn': parsed[0],
        'Partition': parsed[1],
        'Service': parsed[2],
        'Region': parsed[3],
        'Account': parsed[4],
        'RawResource': parsed[5],
        'Resourcetype': None,
        'Resource': None,
        'Qualifier': None,
    }

    # If this is a fake serverless ARN, treat as invalid
    #
    if reply['Region'] == 'serverless':
        return defaultReply
        
    # Sometimes resource needs to be split into further components
    #
    resource = re.split('[:/]',parsed[5])
    
    if len(resource) == 3:
        reply['ResourceType'], reply['Resource'], reply['Qualifier'] = resource
        
    elif len(resource) == 2:
        reply['ResourceType'], reply['Resource'] = resource
        
    else:
        reply['Resource'] = resource[0]

    return reply
