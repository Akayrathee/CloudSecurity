import boto3
import datetime
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
from itertools import zip_longest


# All of the active regions
regions = ['us-east-1','us-west-1','us-east-2','us-west-2','ap-south-1']

for region in regions:

    print("The Current Region is : ", region)
    # Create EC2 client
    ec2 = boto3.client('ec2',region_name=region)

    # Get all instances
    instances = ec2.describe_instances()

    # Get all AMIs in use
    ami_ids = set()
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            ami_ids.add(instance['ImageId'])

    # Check if AMIs are supported by AWS
    unsupported_amis = []
    amis_over_90days = []
    amis_expiring_in_120days =[]
    for ami_id in ami_ids:
            # Get a list of all instances with the specified AMI ID
            response = ec2.describe_instances(Filters=[{'Name': 'image-id', 'Values': [ami_id]}])
            # Count the number of instances
            count = sum([len(reservation['Instances']) for reservation in response['Reservations']])   
            response = ec2.describe_images(ImageIds=[ami_id])

            try:
                image = response['Images'][0]
            except:
                print("Image dont't have anything!!")

            try: 
                depreciation_date_str = image["DeprecationTime"]
                creation_date_str = image["CreationDate"]
            except:
                pass
            if depreciation_date_str is not None:
                depreciation_date = datetime.fromisoformat(depreciation_date_str.replace('Z', '+00:00'))
                if depreciation_date <= datetime.now(timezone.utc):
                    inside_array = [ami_id,depreciation_date, region, count]
                    unsupported_amis.append(inside_array)

            if creation_date_str is not None:
                creation_date = datetime.fromisoformat(creation_date_str.replace('Z', '+00:00'))
                current_date = datetime.now(timezone.utc)
                ninety_days_from_creation = creation_date + relativedelta(days=+90)
                # Check if the 90-day mark has passed
                if ninety_days_from_creation > current_date:
                    pass
                else:
                    inside_array = [ami_id,creation_date, region, count]
                    amis_over_90days.append(inside_array)

            if depreciation_date_str is not None:
                depreciation_date = datetime.fromisoformat(depreciation_date_str.replace('Z', '+00:00'))
                current_date = datetime.now(timezone.utc)
                one20_days_from_today = current_date + relativedelta(days=+120)
                if one20_days_from_today > depreciation_date and depreciation_date>current_date:
                    inside_array = [ami_id,depreciation_date, region, count]
                    amis_expiring_in_120days.append(inside_array)

    if unsupported_amis:
        for ami_id in unsupported_amis:
            pass
    print("The total number of Unsupported AMIs are : ", len(unsupported_amis))
    if amis_over_90days:
        for ami_id in amis_over_90days:
            pass
    print("The total number of AMIs over 90 days are : ", len(amis_over_90days))




    ## Table code

    depreciation_headers = ["AMI ID", "Depreciation Date", "Region", "No of EC2 instances"]
    creation_headers = ["AMI ID", "Creation Date", "Region", "No of EC2 instances"]


    # Printing Unsupported AMIs
    print("\nUnsupported AMIs:")
    print(tabulate(unsupported_amis, headers=depreciation_headers, tablefmt="fancy_grid", numalign="center", stralign="left"))

    print("\nAMIs over 90 days")
    print(tabulate(amis_over_90days, headers=creation_headers, tablefmt="fancy_grid", numalign="center", stralign="left"))

    print("\nAMIs expiring in 120 days")
    print(tabulate(amis_expiring_in_120days, headers=depreciation_headers, tablefmt="fancy_grid", numalign="center", stralign="left"))
