"""SAST fixture -- deliberate security vulnerabilities.

Target for Opengrep (default rule mode). Mirrors ``Analysis/SastFixture.cs``
in the C# reference repository, which planted a SQL injection and a hardcoded
credential for Semgrep / roslyn-sast.

Every weakness below is intentional and unreachable from the worker.
DO NOT DEPLOY. DO NOT COPY.

Planted weaknesses, by CWE:
  CWE-89   SQL injection via string concatenation
  CWE-78   OS command injection via shell=True and os.system
  CWE-94   Code injection via eval / exec
  CWE-502  Unsafe deserialization via pickle.loads and yaml.load
  CWE-798  Hardcoded credentials
  CWE-327  Weak hashing algorithm (MD5)
  CWE-295  TLS certificate verification disabled
  CWE-377  Insecure temporary file creation
"""

# ruff: noqa
# pylint: disable=all

import hashlib
import os
import pickle
import sqlite3
import subprocess
import tempfile

import requests
import yaml

# CWE-798: hardcoded credentials
ADMIN_PASSWORD = "admin123"
API_TOKEN = "sk_live_51H8xQ2eZvKYlo2C0000000000"
DB_CONNECTION = "postgresql://etl_user:Sup3rS3cret@warehouse.internal:5432/orders"


def get_order(conn: sqlite3.Connection, order_id: str):
    """CWE-89: SQL injection -- user input concatenated into the query."""
    query = "SELECT * FROM orders WHERE order_id = '" + order_id + "'"
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def get_orders_by_channel(conn: sqlite3.Connection, channel: str):
    """CWE-89: SQL injection via f-string interpolation."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM orders WHERE channel = '{channel}'")
    return cursor.fetchall()


def export_partition(partition: str):
    """CWE-78: OS command injection -- shell=True with interpolated input."""
    subprocess.call("aws s3 cp /tmp/" + partition + " s3://warehouse/", shell=True)
    os.system("gzip /tmp/" + partition)
    subprocess.Popen(f"rsync -a /tmp/{partition} backup:/data", shell=True)


def evaluate_rule(expression: str):
    """CWE-94: code injection via eval / exec."""
    result = eval(expression)
    exec("computed = " + expression)
    return result


def load_state(blob: bytes):
    """CWE-502: unsafe deserialization."""
    return pickle.loads(blob)


def load_manifest(raw: str):
    """CWE-502: yaml.load without a safe loader."""
    return yaml.load(raw, Loader=yaml.Loader)


def checksum(payload: bytes) -> str:
    """CWE-327: MD5 is not collision resistant."""
    return hashlib.md5(payload).hexdigest()


def fetch_feed(url: str):
    """CWE-295: TLS verification disabled."""
    return requests.get(url, verify=False, timeout=30)


def stage_file(contents: str) -> str:
    """CWE-377: insecure temporary file with a predictable name."""
    path = "/tmp/etl_staging_file.csv"
    with open(path, "w") as handle:
        handle.write(contents)
    os.chmod(path, 0o777)
    legacy = tempfile.mktemp(suffix=".csv")
    return legacy
