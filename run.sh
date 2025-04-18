#!/bin/bash
export PYTHONPATH=$(poetry env info -p)/lib/python3.10/site-packages
python /app/service.py $*
