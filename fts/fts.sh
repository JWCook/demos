#!/bin/bash
read -p "Search query: " query
sqlite3 demo.db <<EOF
.mode list
.separator " - "
SELECT name, desc FROM pkg_fts WHERE name MATCH '$query';
EOF
