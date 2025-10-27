#! /bin/bash

# Install script for the project
echo "Starting installation..."
source ./scripts/env.sh
for url in ${MOD_CURL_URLS}; do
    echo "Fetching mod from ${url}"
    echo "-> $(basename ${url})"
    curl -L -o ./raw_mods/$(basename ${url}) ${url}
done