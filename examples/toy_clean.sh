#!/bin/bash
# toy_clean.sh — DESTRUCTIVE DEMO: recursively delete a scratch directory.
#
# Usage:
#   toy_clean.sh <target-dir>
#
# This is intentionally destructive (rm -rf) so fleet classifies it as
# destructive and refuses to run it without an ALLOW_DESTRUCTIVE marker.
# Only ever point it at disposable scratch dirs under /tmp.
set -u

TARGET="${1:?usage: toy_clean.sh <target-dir>}"
echo "toy_clean: removing $TARGET"
rm -rf "$TARGET"
echo "toy_clean: done (exit $?)"
