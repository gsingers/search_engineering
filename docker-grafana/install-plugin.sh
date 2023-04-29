#!/bin/bash
set -euo pipefail

# For each running opensearch container:
# - Install opensearch-prometheus-exporter plugin
# - restart container for plugin install to take effect
# - list plugins to verify the installation worked

docker ps --filter "name=opensearch-node*" --filter "status=running" --format "{{.Names}}" | while read -r container_name; do

  echo "$container_name: Installing prometheus-exporter plugin ..."
  docker exec -t $container_name ./bin/opensearch-plugin install "https://github.com/aiven/prometheus-exporter-plugin-for-opensearch/releases/download/2.6.0.0/prometheus-exporter-2.6.0.0.zip"

  echo "$container_name: Restarting ..."
  docker restart $container_name

  # need to give opensearch some time before querying for plugins
  sleep 3

  output=$(docker exec -t $container_name ./bin/opensearch-plugin list)
  if echo "$output" | grep -q "prometheus"; then
    echo "$container_name: Confirmed - prometheus-exporter sucessfully installed"
  else
    echo "$container_name: Uh oh - prometheus-exporter is not in the plugin list"
  fi

done
