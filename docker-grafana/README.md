# Metrics stack for observing OpenSearch

Observing metrics, both about OpenSearch internals and host resource usage, can help you gain intuition for how OpenSearch works.  Here we provision a metrics system (Prometheus) to gather and store time-series metrics, Grafana to visualize them, and a pre-built dashboard for OpenSearch.

## The Pieces
1. The [Prometheus Exporter Plugin](https://github.com/aiven/prometheus-exporter-plugin-for-opensearch)
 adds the `/_prometheus/metrics` URI to the OpenSearch HTTP endpoint, and exposes metrics about OpenSearch internals in a Prometheus compatible format.
2. The [cadvisor](https://github.com/google/cadvisor) container exposes container metrics (CPU, Mem, Network I/O)
3. The Prometheus container scrapes those metrics (configs are in `./prometheus/prometheus.yml`) and stores in Prometheus DB.
4. The Grafana container exposes Grafana on http://localhost:3000 to visualize the metrics.  We provide a pre-built dashboard which is defined in `grafana/provisioning/dashboards/opensearch-prometheus.yml`.

## Setup

### First Time Setup
The first time you spin up an OpenSearch container (for W1, W2, etc), you'll need to install the Prometheus Exporter Plugin into that OpenSearch instance(s).

1. Make sure your opensearch containers are running.

2. Run the `install-plugin.sh` script in this directory.

Proceed to Start the Metrics Stack below.

### Careful How You Stop the OpenSearch Containers
When you want to stop/restart your opensearch containers (the docker-compose-wX.yml stack), use the docker `stop` or `restart` commands instead of `Ctrl-c`.  Using `Ctrl-c` will cause the prometheus-exporter plugin to get lost and you'll have to re-run the `install-plugin.sh` script to re-install it.  Instead, use the docker `stop` or `restart` commands to stop/restart the opensearch containers.

This is due to be a difference in signal handling:
- `Ctrl-c` will send a SIGINT to the process
- `docker stop` will send a SIGTERM allowing for a more graceful cleanup

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
If you're not seeing metrics in the dashboard, here are a few things to check:

1. Check the Time Picker

Top right of the Grafana dashboard - make sure the time range is recent (like Last 15 Minutes), and that auto-refresh is on.

2. Is the OpenSearch plugin listed?  You should see `prometheus-exporter` in the OpenSearch plugin list.  You can list installed plugins by either:
```
docker exec -t opensearch-nodeX ./bin/opensearch-plugin list
```
 ... or via the OpenSearch API ...
```
GET _cat/plugins?v
```
If not, try the `install-plugin.sh` script again.

3. Are the Prometheus targets showing a State of "Up"?
```
http://localhost:9090/targets
```
This shows each "target" - each job that Prometheus is running to scrape metrics data from the targets.  If they aren't in a green "Up" state, there will be a red error message indicating why.  **NOTE** that for W1 and W2 we only have a single OpenSearch node, so it's expected that the targets for node2 and node3 will be red.

4. Are the Dashboard Parameters Set Correctly?
At the top of the dashboard are two parameters selectable in drop-down lists.  Make sure datasource is set to `Prometheus` and index is set to the index for which you want to see metrics (usually `bbuy_products`)

## References
- cadvisor [Container metrics reference](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)
- [Prometheus query example](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- [Grafana dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
