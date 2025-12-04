#!/bin/bash
# Upload files to HDFS from within Docker network
# This script runs the upload command from inside a container that has access to HDFS hostnames

set -e

echo "Uploading files to HDFS from within Docker network..."
echo

# Run upload command from inside a container on the same Docker network
docker run --rm \
  --network ddbs-group-project_default \
  -v "$(pwd):/workspace" \
  -w /workspace \
  python:3.11-slim \
  bash -c "
    pip install -q hdfs &&
    python -c \"
import sys
sys.path.insert(0, '/workspace')
from pathlib import Path
from src.domains.storage.hdfs_manager import HDFSManager

print('Connecting to HDFS...')
# Use 'namenode' hostname from inside Docker network
import src.config as config
config.HDFS_CONFIG['namenode'] = 'namenode'

hdfs = HDFSManager()
info = hdfs.get_storage_info()

if not info.get('available'):
    print(f'✗ HDFS not available: {info.get(\\\"error\\\")}')
    sys.exit(1)

print(f'✓ HDFS available at {info[\\\"base_path\\\"]}')
print(f'  Replication factor: {info[\\\"replication\\\"]}\\n')

uploaded = 0
failed = 0

mock_dir = Path('mock_articles')
for article_dir in sorted(mock_dir.iterdir()):
    if not article_dir.is_dir():
        continue

    article_name = article_dir.name
    print(f'Uploading {article_name}...')

    for file_path in article_dir.iterdir():
        hdfs_path = f'{article_name}/{file_path.name}'

        if hdfs.upload_file(str(file_path), hdfs_path):
            uploaded += 1
        else:
            failed += 1

print(f'\\n✓ Upload complete: {uploaded} files uploaded, {failed} failed')
\"
  "

echo
echo "Done!"
