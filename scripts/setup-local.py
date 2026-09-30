#!/usr/bin/env python3
"""Create local credentials without printing or overwriting existing values."""
import os
from pathlib import Path
import secrets
import shutil

root = Path(__file__).resolve().parents[1]
directory = root / '.secrets'
directory.mkdir(mode=0o700, exist_ok=True)
directory.chmod(0o700)
for name in ('mongo_root_password', 'mongo_app_password', 'redis_password', 'jwt_secret'):
    path = directory / name
    if not path.exists():
        # The private parent directory restricts host access. Read-only mounts
        # must be readable by different non-root container user IDs.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as handle:
            handle.write(secrets.token_hex(32) + '\n')
        path.chmod(0o444)
        print(f'Created .secrets/{name} (value hidden)')
if not (root / '.env').exists():
    shutil.copyfile(root / '.env.example', root / '.env')
    print('Created .env with non-secret settings')
print('Local setup ready. Existing credentials were preserved.')
