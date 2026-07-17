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
from datetime import datetime, timezone

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
    uploaded_at: "datetime | None" = None


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
        return DatasetVersion(
            dataset=dataset,
            version=version,
            sha256=sha256,
            key=key,
            uploaded_at=datetime.now(timezone.utc),
        )

    def download(self, version_info: DatasetVersion) -> bytes:
        """Downloads a dataset version's payload.

        Args:
            version_info: Version descriptor from upload() or manifest().

        Returns:
            payload: Raw dataset bytes.
        """
        response = self.client.get_object(Bucket=self.bucket, Key=version_info.key)
        return response["Body"].read()

    def verify(self, version_info: DatasetVersion) -> bool:
        """Re-hashes the stored payload against the version descriptor.

        Args:
            version_info: Version descriptor to verify.

        Returns:
            intact: True when the stored payload matches its recorded hash.
        """
        return content_hash(self.download(version_info)).startswith(version_info.sha256[:12])

    def read_jsonl(self, version_info: DatasetVersion) -> list[dict]:
        """Downloads a version and parses it as JSONL records.

        Args:
            version_info: Version descriptor from upload() or manifest().

        Returns:
            records: Parsed dataset rows.
        """
        payload = self.download(version_info).decode()
        return [json.loads(line) for line in payload.splitlines() if line.strip()]

    def upload_jsonl(self, dataset: str, records: list[dict]) -> DatasetVersion:
        """Serializes records as JSONL and uploads them as the next version.

        Args:
            dataset: Dataset identifier.
            records: Dataset rows to serialize.

        Returns:
            version_info: DatasetVersion describing the stored object.
        """
        payload = "\n".join(json.dumps(record) for record in records).encode()
        version = next_version(self.manifest(dataset))
        return self.upload(dataset, version, payload)

    def latest(self, dataset: str) -> DatasetVersion | None:
        """Resolves the newest stored version of a dataset.

        Args:
            dataset: Dataset identifier.

        Returns:
            version_info: Newest version, or None when the dataset is empty.
        """
        versions = self.manifest(dataset)
        return versions[-1] if versions else None

    def _version_from_key(self, dataset: str, key: str) -> DatasetVersion:
        """Parses a version descriptor back out of an object key.

        Args:
            dataset: Dataset identifier.
            key: S3 object key produced by object_key().

        Returns:
            version_info: Parsed DatasetVersion with a placeholder hash.
        """
        stem = key.rsplit("/", 1)[-1].removesuffix(".jsonl")
        version_part, hash_part = stem.split("-", 1)
        return DatasetVersion(
            dataset=dataset, version=int(version_part.lstrip("v")), sha256=hash_part, key=key
        )

    def manifest(self, dataset: str) -> list[DatasetVersion]:
        """Lists every stored version of a dataset.

        Args:
            dataset: Dataset identifier.

        Returns:
            versions: Stored versions in ascending version order.
        """
        prefix = f"{self.prefix}/{dataset}/"
        response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        versions = []
        for entry in response.get("Contents", []):
            versions.append(self._version_from_key(dataset, entry["Key"]))
        return sorted(versions, key=lambda version: version.version)

def next_version(versions: list[DatasetVersion]) -> int:
    """Computes the next version number for a dataset.

    Args:
        versions: Existing versions from manifest().

    Returns:
        version: One past the highest existing version; 1 when empty.
    """
    if not versions:
        return 1
    return max(version.version for version in versions) + 1
