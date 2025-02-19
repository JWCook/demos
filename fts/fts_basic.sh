#!/bin/bash
# Example FTS search using sqlite3 shell features
while :
do
read -rp "Search query: " query
sqlite3 demo.db <<EOF
.mode list
.separator " - "
SELECT name, desc FROM pkg_fts WHERE name MATCH '$query';
EOF
done
