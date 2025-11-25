#!/bin/bash 

while IFS= read -r line; do 

    [ -z "$line" ] && continue 

    echo "Creating file: $line" 

    mkdir -p "$(dirname "$line")" 

    touch "$line" 

done < files.txt 