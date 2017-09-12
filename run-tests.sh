#!/bin/sh
make

export LD_PRELOAD="$(pwd)/libkafel.so"

python kafel.py

rm *.class 2>/dev/null
javac -cp jna-4.4.0.jar:. KafelTest.java
java -cp jna-4.4.0.jar:. KafelTest
