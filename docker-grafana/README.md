# Metrics stack for observing OpenSearch

Observing metrics, both OpenSearch internal and external host metrics, can help you gain intuition for how OpenSearch works.  Here we provision a metrics system (Prometheus) to gather metrics and store time-series metrics, Grafana to visualize them, and a pre-built dashboard for OpenSearch.

## The Pieces
1. The [Prometheus Exporter Plugin](https://github.com/aiven/prometheus-exporter-plugin-for-opensearch)
 adds the `/_prometheus/metrics` URI to the OpenSearch HTTP endpoint, and exposes metrics about OpenSearch internals in a Prometheus compatible format.
2. The [cadvisor](https://github.com/google/cadvisor) container exposes container metrics (CPU, Mem, Network I/O)
3. The Prometheus container scrapes those metrics (configs are in `./prometheus/prometheus.yml`) and stores in Prometheus DB.
4. The Grafana container exposes Grafana on http://localhost:3000 to visualize the metrics.  We provide a pre-built dashboard.

## Setup

### First Time Setup
The first time you spin up an OpenSearch container (for W1, W2, etc), you'll need to install the Prometheus Exporter Plugin into that OpenSearch instance(s).  Run this against *EVERY* OpenSearch node that you are running (adjust the container name as needed):
```
docker exec -t opensearch-node1 ./bin/opensearch-plugin install https://github.com/aiven/prometheus-exporter-plugin-for-opensearch/releases/download/2.6.0.0/prometheus-exporter-2.6.0.0.zip
```
Restart each of the OpenSearch node(s) for the plugin install to take effect (adjusting the filename and container name as needed).  Note that just Ctrl-C stopping the containers seems to interfere with the plugin install.  So we're doing a `restart` here instead:
```
docker compose -f docker-compose-w2.yml restart opensearch-node1
```
Make sure the plugin shows in the list of installed plugins:
```
docker exec -t opensearch-node1 ./bin/opensearch-plugin list
```
  ... or by querying the CAT API:
```
GET /_cat/plugins?v
```

### Start the Metrics Stack
Whenever you want to gather or look at metrics, just compose up:

```
docker compose -f monitoring.yml up
```
Open the pre-built OpenSearch Grafana dashboard (note HTTP not HTTPS):
```
http://localhost:3000/d/opensearch/opensearch-prometheus
```
and login using admin/admin.

Note that we're running this **in addition to** (along side of) the weekly docker-compose-wX files that run the OpenSearch instances.  In other words, you'll `docker compose up` two things concurrently.

You might want to stop (`docker compose down`) the stack when you don't need it.  It only consumes ~ 300 MB memory, but does incur a bit of CPU since it polls and stores the metrics every 15 seconds.

## Troubleshooting

1. Did you restart the OpenSearch node after installing the plugin?
```
docker compose -f <docker-compose-file> restart opensearch-nodeX
```

2. Is the OpenSearch plugin listed?  You should see `prometheus-exporter` in the plugin list.  You can list installed plugins by either:
```
docker exec -t opensearch-nodeX ./bin/opensearch-plugin list
```
 ... or via the OpenSearch API ...
```
GET _cat/plugins?v
```
If not, try the install command again and restart the container (step #1).

3. Are the Prometheus targets showing a State of "Up"?
```
http://localhost:9090/targets
```
This shows each "target" - each job that Prometheus is running to scrape metrics data from the targets.  If they aren't in a green "Up" state, there will be a red error message indicating why.  **NOTE** that for W1 and W2 we only have a single OpenSearch node, so it's expected that the targets for node2 and node3 will be red.

## References
- cadvisor [Container metrics reference](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)
- [Prometheus query example](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- [Grafana dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
