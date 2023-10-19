import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def copy_file_between_s3_buckets(source_bucket, source_key, target_bucket, target_key, access_key, secret_key, source_account_id):
    """
    Copy an object from one S3 bucket to another, potentially across different accounts.

    :param source_bucket: The name of the source bucket
    :param source_key: The key of the source object
    :param target_bucket: The name of the target bucket
    :param target_key: The key for the target object
    :param access_key: AWS access key
    :param secret_key: AWS secret access key
    :param source_account_id: The AWS account ID of the source bucket
    """
    # Create a session using your current creds
    boto_session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    s3 = boto_session.resource('s3')

    try:
        copy_source = {
            'Bucket': source_bucket,
            'Key': source_key
        }

        # Using the session, construct an S3 resource
        s3 = boto_session.resource('s3')

        # Ensure the target bucket allows for the copy (bucket policy may need to be adjusted accordingly)
        s3.meta.client.put_bucket_policy(
            Bucket=target_bucket,
            Policy='''
            {{
                "Version": "2012-10-17",
                "Statement": [
                    {{
                        "Sid": "DelegateS3Access",
                        "Effect": "Allow",
                        "Principal": {{"AWS": "arn:aws:iam::{}:root"}},
                        "Action": ["s3:ListBucket", "s3:GetObject", "s3:PutObject", "s3:PutObjectAcl"],
                        "Resource": [
                            "arn:aws:s3:::{}/*",
                            "arn:aws:s3:::{}"
                        ]
                    }}
                ]
            }}
            '''.format(source_account_id, target_bucket, target_bucket)
        )

        # Now, we can copy the file
        bucket = s3.Bucket(target_bucket)
        bucket.copy(copy_source, target_key)

        print(f'File {source_key} copied from s3://{source_bucket} to s3://{target_bucket}/{target_key}')

    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print('Access denied - do you have the correct permissions?')
        else:
            # Something else has gone wrong.
            raise
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(e)

# Replace these variables with appropriate values for your use case
source_bucket_name = 'my-source-bucket'
source_file_key = 'source_file.txt'
target_bucket_name = 'my-target-bucket'
target_file_key = 'target_file.txt'
aws_access_key = 'your_access_key_here'
aws_secret_key = 'your_secret_key_here'
aws_source_account_id = 'source_account_id'

copy_file_between_s3_buckets(source_bucket_name, source_file_key, target_bucket_name, target_file_key, aws_access_key, aws_secret_key, aws_source_account_id)
