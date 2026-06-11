#!/usr/bin/env python3
"""
test_datasets.py --- unit tests for versioned dataset storage

Contains:
    FakeS3Client: in-memory S3 stand-in
    test_content_hash_stable: same payload hashes the same
    test_upload_download_roundtrip: uploaded payload downloads identically
"""

import io

from store.datasets import DatasetStore, content_hash


class FakeS3Client:
    """In-memory S3 stand-in.

    Attributes:
        objects: Stored objects keyed by (bucket, key).
    """

    def __init__(self) -> None:
        """Initializes the empty object map."""
        self.objects: dict[tuple[str, str], bytes] = {}

    def put_object(self, Bucket: str, Key: str, Body: bytes) -> None:
        """Stores the object in memory."""
        self.objects[(Bucket, Key)] = Body

    def get_object(self, Bucket: str, Key: str) -> dict:
        """Returns the stored object as an S3-shaped response."""
        return {"Body": io.BytesIO(self.objects[(Bucket, Key)])}


def make_store() -> DatasetStore:
    """Builds a DatasetStore backed by the fake client.

    Returns:
        store: DatasetStore with an in-memory backend.
    """
    return DatasetStore("test-bucket", client=FakeS3Client())


def test_content_hash_stable() -> None:
    """Same payload hashes identically; different payloads differ."""
    assert content_hash(b"abc") == content_hash(b"abc")
    assert content_hash(b"abc") != content_hash(b"abd")


def test_upload_download_roundtrip() -> None:
    """Uploaded payload downloads byte-identically."""
    store = make_store()
    info = store.upload("gold", 1, b'{"q": 1}\n')
    assert store.download(info) == b'{"q": 1}\n'

def test_object_key_layout() -> None:
    """Object keys follow the prefix/dataset/version-hash layout."""
    store = make_store()
    info = store.upload("gold", 3, b"payload")
    assert info.key.startswith("datasets/gold/v0003-")
    assert info.key.endswith(".jsonl")

def test_upload_versions_independent() -> None:
    """Two versions of one dataset coexist under different keys."""
    store = make_store()
    first = store.upload("gold", 1, b"v1")
    second = store.upload("gold", 2, b"v2")
    assert first.key != second.key
    assert store.download(first) == b"v1"
    assert store.download(second) == b"v2"
