#!/bin/bash
# Simple deployment wrapper
# Usage: ./deploy.sh

cd "$(dirname "$0")"
python3 auto_deploy.py
