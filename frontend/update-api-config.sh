#!/bin/bash
# Script to update Vue files to import and use API_BASE_URL from config

cd "$(dirname "$0")"

# For each .vue file in src/views
for file in src/views/*.vue; do
  # Check if file contains import.meta.env.VITE_API_URL
  if grep -q "import.meta.env.VITE_API_URL" "$file"; then
    echo "Updating $file..."
    
    # Add import statement after <script> tag if not already present
    if ! grep -q "import API_BASE_URL from" "$file"; then
      sed -i '/<script>/a import API_BASE_URL from '\''@/config/api.js'\'';' "$file"
    fi
    
    # Replace import.meta.env.VITE_API_URL + ' with API_BASE_URL + '
    sed -i "s|import.meta.env.VITE_API_URL + '|API_BASE_URL + '|g" "$file"
    
    # Replace ${import.meta.env.VITE_API_URL} with ${API_BASE_URL}
    sed -i 's|${import.meta.env.VITE_API_URL}|${API_BASE_URL}|g' "$file"
  fi
done

echo "All Vue files updated to use API_BASE_URL from config"
