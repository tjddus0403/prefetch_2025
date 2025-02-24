#!/bin/sh

ROOT="./paddr"
DIRS=("astar" "bc" "bfs" "cc" "mcf" "pr" "sssp")

for dir in "${DIRS[@]}"; do
    INPUT="$ROOT/$dir/${dir}_5m.paddr"

    if [ -f "$INPUT" ]; then
        echo "Processing $INPUT"

        head -4000000 "$INPUT" > "$ROOT/$dir/${dir}_4m.paddr"
        head -3000000 "$INPUT" > "$ROOT/$dir/${dir}_3m.paddr"
        tail -1000000 "$INPUT" > "$ROOT/$dir/${dir}_1m_tail.paddr"

        echo "Created ${dir}_4m.paddr, ${dir}_3m.paddr, and ${dir}_1m_tail.paddr in $dir"
    else
        echo "File $INPUT not found, skipping..."
    fi
done
