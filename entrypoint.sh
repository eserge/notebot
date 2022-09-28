#!/usr/bin/env bash

exec `poetry run printenv VIRTUAL_ENV`/bin/uvicorn \
    app:app \
    --host 0.0.0.0 \
    --port 80
