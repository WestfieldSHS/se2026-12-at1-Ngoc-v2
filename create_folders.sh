#!/bin/bash 

while IFS= read -r line; do 
    [ -z "$line" ] && continue 
    echo "Creating folder: $line" 
    mkdir -p "$line" 
done < folders.txt  