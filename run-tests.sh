#!/bin/sh
make

export LD_PRELOAD="$(pwd)/libkafel.so"

python kafel.py
