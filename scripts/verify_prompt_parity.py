#!/usr/bin/env python3
"""Verify tenant prompts file is exact copy of original."""
import hashlib
import sys
import os

def file_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

original = os.path.join(project_root, 'api/visualizer/prompts.py')
tenant = os.path.join(project_root, 'api/tenants/boss/prompts.py')

try:
    original_hash = file_hash(original)
    tenant_hash = file_hash(tenant)
except FileNotFoundError as e:
    print(f"ERROR: File not found: {e}")
    sys.exit(1)

if original_hash == tenant_hash:
    print(f"PASS: Files are identical")
    print(f"   SHA256: {original_hash}")
    sys.exit(0)
else:
    print(f"FAIL: Files differ!")
    print(f"   Original: {original_hash}")
    print(f"   Tenant:   {tenant_hash}")
    sys.exit(1)
