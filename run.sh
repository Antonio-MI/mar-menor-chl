#!/bin/bash

mkdir -p logs
rm -f logs/*.txt

source .venv/bin/activate

python main.py > logs/output.txt & 
