from contextlib import asynccontextmanager

from s3fs import S3FileSystem


@asynccontextmanager
async def managed_s3_file_system():
    """
    Managed s3 file system with sets session.

    To be used as context manager. Need to ensure that following environment variables
    are set:
        `AWS_ACCESS_KEY_ID`
        `AWS_SECRET_ACCESS_KEY`
        `AWS_ENDPOINT_URL`
    """
    s3 = S3FileSystem(asynchronous=True)

    session = await s3.set_session()

    yield s3

    await session.close()
