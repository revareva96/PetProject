#!/bin/sh
echo "upgrade DB"
alembic upgrade head;
echo "starting backend..."
python3 main.py