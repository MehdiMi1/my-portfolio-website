#!/bin/bash

echo "==> 1. Installing packages..."
pip install -r requirements.txt

echo "==> 2. Removing old database..."
rm -f blog.db

echo "==> 3. Initializing new database..."
flask init-db

echo "
==> SETUP COMPLETE! Please go to Web tab and RELOAD your app. <=="