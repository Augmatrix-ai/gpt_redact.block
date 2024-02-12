#!/bin/bash
pushd /app 
python3 main.py
popd
exec "$@"
