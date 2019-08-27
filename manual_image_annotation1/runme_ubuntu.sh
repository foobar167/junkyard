#!/usr/bin/env bash
conda info --envs
conda activate DL3
python runme.py
conda deactivate
