from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from boto3.s3.transfer import TransferConfig
from boto3.s3 import transfer

def create_transfer_manager(*arg, **kwargs):
    return transfer.TransferManager(
        *arg, **kwargs, executor_cls=transfer.NonThreadedExecutor
    )

class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

class PublicMediaStorage(S3Boto3Storage):
    transfer.create_transfer_manager = create_transfer_manager
    location = 'public'
    default_acl = 'public-read'
    file_overwrite = False

class PrivateMediaStorage(S3Boto3Storage):
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False