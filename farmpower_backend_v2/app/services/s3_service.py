import uuid
from typing import Optional, Union, BinaryIO # BinaryIO for file-like objects
from ..core.config import settings # Assuming settings are in app.core.config

# Conditional import for aiobotocore, only if actually using S3
if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.AWS_S3_BUCKET_NAME:
    try:
        from aiobotocore.session import get_session
    except ImportError:
        # This allows the app to run if aiobotocore couldn't be installed (e.g. in timeout scenarios)
        # but S3 features will be strictly mocked.
        print("WARNING: aiobotocore not installed. S3 functionality will be fully mocked.")
        get_session = None
else:
    get_session = None # Not using S3, so no need for the session object

async def upload_file_to_s3(file_object: Union[bytes, BinaryIO], original_filename: str) -> Optional[str]:
    """
    Uploads a file object (bytes or binary file-like object) to S3.
    If AWS credentials are not set in settings or aiobotocore is missing, it runs in mocking mode.
    Returns the S3 URL of the uploaded file or a mock URL.
    """
    file_extension = ""
    if "." in original_filename:
        file_extension = original_filename.rsplit(".", 1)[1].lower()
        name_part = original_filename.rsplit(".",1)[0]
        safe_name_part = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in name_part)
        unique_filename_base = f"{uuid.uuid4()}-{safe_name_part[:50]}"
    else:
        unique_filename_base = str(uuid.uuid4())

    unique_filename = f"{unique_filename_base}.{file_extension}" if file_extension else unique_filename_base

    # Mocking mode if AWS not fully configured or aiobotocore not available
    if not get_session or not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_S3_BUCKET_NAME, settings.AWS_S3_REGION]):
        print(f"S3 Service (Mock Mode): Simulating upload for {unique_filename}.")
        if hasattr(file_object, 'read'):
            try:
                # If it's a file-like object from UploadFile, it might have been read already.
                # If it's SpooledTemporaryFile, reading it consumes it.
                # For mock, just acknowledge. In real, ensure it's seek(0) or pass bytes.
                print(f"Mock S3: File object received for {unique_filename}. Assuming it can be read.")
            except Exception as e:
                print(f"Mock S3: Error with file object for {unique_filename}. Error: {e}")
        else: # Assuming it's bytes
             print(f"Mock S3: Received bytes directly for {unique_filename}.")

        mock_bucket = settings.AWS_S3_BUCKET_NAME or 'mock-farmpower-bucket'
        mock_region = settings.AWS_S3_REGION or 'mock-region-1'
        return f"https://s3.{mock_region}.amazonaws.com/{mock_bucket}/{unique_filename}"

    # Actual S3 upload logic
    session = get_session()
    try:
        async with session.create_client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ) as client:

            body_content: bytes
            if isinstance(file_object, bytes):
                body_content = file_object
            elif hasattr(file_object, 'read'): # Should be a file-like object
                if hasattr(file_object, 'seek'):
                    file_object.seek(0) # Ensure reading from the start
                content_read = file_object.read()
                if isinstance(content_read, str): # If read as text, encode to bytes
                    body_content = content_read.encode('utf-8')
                elif isinstance(content_read, bytes):
                    body_content = content_read
                else:
                    raise TypeError("File object read method did not return bytes or string.")
            else:
                raise TypeError("file_object must be bytes or a file-like object supporting read().")

            await client.put_object(
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=unique_filename,
                Body=body_content
                # TODO: Consider adding ContentType=file.content_type if available from UploadFile
            )
            return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{unique_filename}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
