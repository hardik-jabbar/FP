import uuid
from typing import Optional, Union, BinaryIO
from aiobotocore.session import get_session # For async S3 client
from ..core.config import settings

async def upload_file_to_s3(file_object: Union[bytes, BinaryIO], filename: str) -> Optional[str]:
    """
    Uploads a file object (bytes or binary file-like object) to S3.
    If AWS credentials are not set in settings, it runs in mocking mode.
    Returns the S3 URL of the uploaded file or a mock URL.
    """
    # Sanitize filename or generate a completely unique one to avoid issues
    # Using original filename extension with a UUID prefix for uniqueness and recognizability.
    file_extension = ""
    if "." in filename:
        file_extension = filename.rsplit(".", 1)[1]
        original_name_part = filename.rsplit(".",1)[0]
        # Basic sanitization for filename part
        original_name_part = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in original_name_part)
        safe_filename_base = f"{uuid.uuid4()}-{original_name_part[:50]}" # Limit length of original name part
    else:
        safe_filename_base = str(uuid.uuid4()) # No extension, just UUID

    unique_filename = f"{safe_filename_base}.{file_extension}" if file_extension else safe_filename_base


    # Mocking mode if AWS credentials are not fully configured
    if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_S3_BUCKET_NAME, settings.AWS_S3_REGION]):
        print(f"Mock S3: Credentials not fully configured. Simulating upload for {unique_filename}")
        # Ensure file_object is read if it's a SpooledTemporaryFile (like FastAPI's UploadFile.file)
        if hasattr(file_object, 'read'):
            try:
                contents = file_object.read() # Read the content
                print(f"Mock S3: Read {len(contents)} bytes from file object for {unique_filename}.")
                # In a real scenario with SpooledTemporaryFile, you might need to file_object.seek(0) after this if reading again.
            except Exception as e:
                print(f"Mock S3: Could not read file object for {unique_filename}. Error: {e}")
        else: # Assuming it's bytes
             print(f"Mock S3: Received {len(file_object)} bytes directly for {unique_filename}.")

        return f"https://s3.{settings.AWS_S3_REGION or 'mock-region'}.amazonaws.com/{settings.AWS_S3_BUCKET_NAME or 'mock-bucket'}/{unique_filename}"

    session = get_session()
    try:
        async with session.create_client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ) as client:
            # If file_object is UploadFile.file (SpooledTemporaryFile), it needs to be read.
            # If it's already bytes, it can be passed directly.
            # aiobotocore's put_object Body expects bytes or a file-like object that supports read().
            # For FastAPI's UploadFile, file.file is a SpooledTemporaryFile.
            # Ensure it's in a state to be read (e.g., after file.read(), do file.seek(0)).

            # If file_object is a SpooledTemporaryFile, ensure it's read from the beginning
            if hasattr(file_object, 'seek') and hasattr(file_object, 'read'):
                file_object.seek(0)
                body_content = file_object.read()
            elif isinstance(file_object, bytes):
                body_content = file_object
            else:
                # This case should ideally not happen if input is controlled
                raise TypeError("file_object must be bytes or a file-like object supporting read() and seek()")

            await client.put_object(
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=unique_filename,
                Body=body_content
            )
            return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{unique_filename}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        # Consider raising a custom exception or returning None to indicate failure
        return None
