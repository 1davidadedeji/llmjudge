#!/usr/bin/env python3
"""
datasets.py --- versioned dataset storage on S3

Contains:
    DatasetVersion: one immutable dataset version
    DatasetStore: uploads, downloads, and lists dataset versions
    content_hash(): stable content hash for a dataset payload
"""

import hashlib
import json
from dataclasses import dataclass

import boto3


@dataclass(frozen=True)
class DatasetVersion:
    """One immutable dataset version.

    Attributes:
        dataset: Dataset identifier.
        version: Monotonic version number.
        sha256: Content hash of the payload.
        key: S3 object key the payload is stored under.
    """

    dataset: str
    version: int
    sha256: str
    key: str


def content_hash(payload: bytes) -> str:
    """Computes the stable content hash of a dataset payload.

    Args:
        payload: Raw dataset bytes.

    Returns:
        sha256: Hex digest of the payload.
    """
    return hashlib.sha256(payload).hexdigest()


class DatasetStore:
    """Uploads, downloads, and lists versioned datasets on S3.

    Attributes:
        bucket: S3 bucket datasets live in.
        prefix: Key prefix inside the bucket.
    """

    def __init__(self, bucket: str, prefix: str = "datasets", client: object = None) -> None:
        """Stores the bucket layout and S3 client."""
        self.bucket = bucket
        self.prefix = prefix
        self.client = client or boto3.client("s3")

    def object_key(self, dataset: str, version: int, sha256: str) -> str:
        """Builds the object key for a dataset version.

        Args:
            dataset: Dataset identifier.
            version: Version number.
            sha256: Content hash of the payload.

        Returns:
            key: S3 object key.
        """
        return f"{self.prefix}/{dataset}/v{version:04d}-{sha256[:12]}.jsonl"

    def upload(self, dataset: str, version: int, payload: bytes) -> DatasetVersion:
        """Uploads a new dataset version.

        Args:
            dataset: Dataset identifier.
            version: Version number for the payload.
            payload: Raw JSONL dataset bytes.

        Returns:
            version_info: DatasetVersion describing the stored object.
        """
        sha256 = content_hash(payload)
        key = self.object_key(dataset, version, sha256)
        self.client.put_object(Bucket=self.bucket, Key=key, Body=payload)
        return DatasetVersion(dataset=dataset, version=version, sha256=sha256, key=key)

    def download(self, version_info: DatasetVersion) -> bytes:
        """Downloads a dataset version's payload.

        Args:
            version_info: Version descriptor from upload() or manifest().

        Returns:
            payload: Raw dataset bytes.
        """
        response = self.client.get_object(Bucket=self.bucket, Key=version_info.key)
        return response["Body"].read()
