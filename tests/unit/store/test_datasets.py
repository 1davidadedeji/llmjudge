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

def test_version_from_key_roundtrip() -> None:
    """Keys produced by object_key parse back to their version."""
    store = make_store()
    key = store.object_key("gold", 7, "deadbeefcafe")
    parsed = store._version_from_key("gold", key)
    assert parsed.version == 7

def test_next_version() -> None:
    """next_version increments past the highest existing version."""
    from store.datasets import DatasetVersion, next_version

    assert next_version([]) == 1
    versions = [DatasetVersion("gold", 2, "x", "k")]
    assert next_version(versions) == 3

def test_upload_jsonl_uses_next_version() -> None:
    """upload_jsonl picks the next version automatically."""
    store = make_store()
    store.upload("gold", 1, b"old")
    store.client.list_objects_v2 = lambda Bucket, Prefix: {
        "Contents": [{"Key": store.object_key("gold", 1, "x")}]
    }
    info = store.upload_jsonl("gold", [{"q": 1}])
    assert info.version == 2

def test_hash_length() -> None:
    """Content hash is a full sha256 hex digest."""
    assert len(content_hash(b"x")) == 64

def test_read_jsonl_roundtrip() -> None:
    """read_jsonl parses back what upload_jsonl wrote."""
    store = make_store()
    store.client.list_objects_v2 = lambda Bucket, Prefix: {"Contents": []}
    info = store.upload_jsonl("gold", [{"q": 1}, {"q": 2}])
    assert store.read_jsonl(info) == [{"q": 1}, {"q": 2}]

def test_upload_returns_version_descriptor() -> None:
    """upload returns the version it stored."""
    store = make_store()
    info = store.upload("gold", 4, b"data")
    assert info.version == 4 and info.dataset == "gold"

def test_upload_records_aware_timestamp() -> None:
    """Uploaded versions carry a timezone-aware upload time."""
    from datetime import timezone

    store = make_store()
    info = store.upload("gold", 1, b"data")
    assert info.uploaded_at is not None
    assert info.uploaded_at.tzinfo == timezone.utc

def test_verify_intact() -> None:
    """verify accepts an untampered payload."""
    store = make_store()
    info = store.upload("gold", 1, b"data")
    assert store.verify(info)
