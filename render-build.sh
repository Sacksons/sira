#!/usr/bin/env bash
# Render build script for SIRA Backend
set -e

echo "=== SIRA Platform - Render Build ==="

cd backend

echo "[1/3] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[2/3] Setting up database..."
python setup_dev.py

echo "[3/3] Build complete!"
