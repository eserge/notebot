#!/usr/bin/env bash

`poetry run printenv VIRTUAL_ENV`/bin/python webhook.py reinstall
exec `poetry run printenv VIRTUAL_ENV`/bin/uvicorn \
    app:app \
    --host 0.0.0.0 \
    --port 80 \
    --proxy-headers
