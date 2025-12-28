#!/bin/bash
# Script to replace hardcoded localhost URLs with API config import

cd "$(dirname "$0")"

# Find all .vue files and replace localhost URLs
find src/views -name "*.vue" -type f -exec sed -i "s|'http://localhost:5000|import.meta.env.VITE_API_URL + '|g" {} \;
find src/views -name "*.vue" -type f -exec sed -i 's|`http://localhost:5000|`${import.meta.env.VITE_API_URL}|g' {} \;

echo "Updated all Vue files to use VITE_API_URL environment variable"
