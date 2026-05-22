"""Taint-analysis fixture -- explicit source-to-sink dataflow.

Target for Opengrep in TAINT MODE specifically. Where ``sast_fixture.py``
plants single-expression weaknesses that pattern rules catch, this file plants
multi-hop flows that only interprocedural taint tracking should follow.

The sources here are deliberately library-shaped, and that is the hardest
case of the four project types in this family. **A library does not control
its callers.** Every parameter of every public function is attacker-controlled
from the library's point of view: there is no argv to parse, no request to
authenticate, no broker to trust. Whatever a downstream application passes in
is the taint source, which is exactly why supply-chain analysis of
dependencies matters.

That makes these flows a good discriminator: an engine that only recognises
``sys.argv``, ``request.args`` or ``os.environ`` as sources will miss every
one of FLOWS 1, 2 and 4, because the source is simply a function parameter.

FLOW 1  source: public API parameter  -> 2 hops -> sink: os.system        (CWE-78)
FLOW 2  source: caller-supplied dict  -> 3 hops -> sink: sqlite3 execute  (CWE-89)
FLOW 3  source: env var               -> 1 hop  -> sink: eval             (CWE-94)
FLOW 4  source: public API parameter  -> 2 hops -> sink: subprocess shell (CWE-78)
FLOW 5  sanitized flow -- the source reaches the sink through shlex.quote and
        must NOT be reported. This is the false-positive control.

Nothing in this module is exported from ``orderkit.api`` or reachable from the
public surface.
"""

# ruff: noqa
# pylint: disable=all

import os
import shlex
import sqlite3
import subprocess

import requests

# ---------------------------------------------------------------- FLOW 1
# A plain function parameter is the taint source. Expect a finding.


def _flow1_relay(value: str) -> str:
    return "/data/exports/" + value


def export_report(report_name: str) -> None:
    """Public-shaped entry point. ``report_name`` comes from the caller."""
    relayed = _flow1_relay(report_name)
    os.system("tar -czf archive.tgz " + relayed)  # SINK: CWE-78


# ---------------------------------------------------------------- FLOW 2
# Remote content reaches a SQL sink across three hops. Expect a finding.


def _flow2_source(url: str) -> str:
    return requests.get(url, timeout=30).text


def _flow2_parse(body: str) -> str:
    return body.strip().splitlines()[0]


def _flow2_build(fragment: str) -> str:
    return "SELECT * FROM orders WHERE channel = '" + fragment + "'"


def lookup_by_feed(conn: sqlite3.Connection, url: str):
    body = _flow2_source(url)
    fragment = _flow2_parse(body)
    query = _flow2_build(fragment)
    return conn.execute(query).fetchall()  # SINK: CWE-89


# ---------------------------------------------------------------- FLOW 3
# Environment variable straight into eval. Expect a finding.


def evaluate_pricing_rule() -> object:
    rule = os.environ.get("ORDERKIT_PRICING_RULE", "1 + 1")
    return eval(rule)  # SINK: CWE-94


# ---------------------------------------------------------------- FLOW 4
# A caller-supplied mapping value reaches a shell sink.


def _flow4_source(options: dict) -> str:
    return options["destination"]


def _flow4_relay(target: str) -> str:
    return f"scp {target} backup:/archive/"


def sync_archive(options: dict) -> None:
    target = _flow4_source(options)
    command = _flow4_relay(target)
    subprocess.run(command, shell=True, check=False)  # SINK: CWE-78


# ---------------------------------------------------------------- FLOW 5
# SANITIZED CONTROL -- shlex.quote neutralises the taint before the sink.
# A taint engine that reports this flow has produced a false positive.


def export_report_safely(report_name: str) -> None:
    safe = shlex.quote(report_name)
    subprocess.run(f"tar -czf archive.tgz {safe}", shell=True, check=False)
