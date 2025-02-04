#!/bin/sh

ROOT="./paddr/"
INPUT="$ROOT$1/$1_5m.paddr"
echo "$INPUT"
echo `head -4000000 $INPUT > $ROOT$1/$1_4m.paddr`
echo `head -3000000 $INPUT > $ROOT$1/$1_3m.paddr`
echo `tail -1000000 $INPUT > $ROOT$1/$1_1m_tail.paddr`