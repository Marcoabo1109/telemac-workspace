#!/usr/bin/env python3
"""Restore large original files and verify SHA-256, retaining published archives."""
from pathlib import Path
import gzip, hashlib, json, shutil, tempfile
root = Path(__file__).resolve().parents[1]
records = json.loads((root / 'consolidation/manifest.json').read_text())
for item in records:
    if not item['gzip']:
        continue
    dest = root / item['source']
    if dest.exists():
        with dest.open('rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        if digest != item['sha256']:
            raise SystemExit(f'Refusing to overwrite a different file: {dest}')
        print(f'Already verified: {item["source"]}')
        continue
    with tempfile.TemporaryFile() as joined:
        for part in item.get('parts', [item['published']]):
            with (root / part).open('rb') as src:
                shutil.copyfileobj(src, joined)
        joined.seek(0)
        with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as tmp:
            temp_path = Path(tmp.name)
            digest = hashlib.sha256()
            try:
                with gzip.GzipFile(fileobj=joined, mode='rb') as src:
                    while block := src.read(1024 * 1024):
                        tmp.write(block)
                        digest.update(block)
                if digest.hexdigest() != item['sha256']:
                    raise ValueError(f'Checksum mismatch: {item["source"]}')
            except BaseException:
                temp_path.unlink(missing_ok=True)
                raise
        temp_path.replace(dest)
    print(f'Restored and verified: {item["source"]}')
