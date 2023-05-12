# Week 3 Results

## Level 1

### Q1: Which node was elected as cluster manager?

**Answer:**

Opensearch-node1 was elected as cluster manager.

`GET _cat/nodes?v`

| ip                  |heap.percent |ram.percent |cpu | load_1m | load_5m | load_15m | node.role | node.roles                                          |  cluster_manager | name                  |
|---------------------|-------------|------------|----|---------|---------|----------|-----------|-----------------------------------------------------|------------------|-----------------------|
| 172.18.0.7          | 20          |98          | 2  |   0.35  |   0.27  |   0.28   |   dimr    |   cluster_manager,data,ingest,remote_cluster_client | *                |    opensearch-node1   |
| 172.18.0.6          | 45          |98          | 3  |   0.35  |   0.27  |   0.28   |   dimr    |   cluster_manager,data,ingest,remote_cluster_client | -                |    opensearch-node2   |
| 172.18.0.5          | 52          |98          | 3  |   0.35  |   0.27  |   0.28   |   dimr    |   cluster_manager,data,ingest,remote_cluster_client | -                |    opensearch-node3   |


### Q2: After stopping the previous cluster manager, which node was elected the new cluster manager?

**Answer:**

Opensearch-node3 was elected as cluster manager.

```sh
docker stop opensearch-node1
```

| ip                  |heap.percent |ram.percent |cpu | load_1m | load_5m | load_15m | node.role | node.roles                                          |  cluster_manager | name                  |
|---------------------|-------------|------------|----|---------|---------|----------|-----------|-----------------------------------------------------|------------------|-----------------------|
| 172.18.0.5          | 29          |91          | 2  |   0.07  |   0.16  |   0.23   |   dimr    |   cluster_manager,data,ingest,remote_cluster_client | *                |    opensearch-node3   |
| 172.18.0.6          | 29          |91          | 2  |   0.07  |   0.16  |   0.23   |   dimr    |   cluster_manager,data,ingest,remote_cluster_client | -                |    opensearch-node2   |

[INFO ][o.o.c.c.FollowersChecker ] [opensearch-node3] FollowerChecker{discoveryNode={opensearch-node1}, failureCountSinceLastSuccess=1, [cluster.fault_detection.follower_check.retry_count]=3} marking node as faulty
[INFO ][o.o.c.c.Coordinator      ] [opensearch-node3] cluster-manager node [{opensearch-node1}] failed, restarting discovery
[INFO ][o.o.c.s.ClusterApplierService] [opensearch-node3] cluster-manager node changed {previous [{opensearch-node1}], current []}, term: 2, version: 66, reason: becoming candidate: onLeaderFailure
[INFO ][o.o.c.s.MasterService    ] [opensearch-node3] elected-as-cluster-manager ([2] nodes joined)[{opensearch-node3} elect leader, {opensearch-node2} elect leader, _BECOME_CLUSTER_MANAGER_TASK_, _FINISH_ELECTION_], term: 4, version: 67, delta: cluster-manager node changed {previous [], current [{opensearch-node3}]}


### Q3: Did the cluster manager node change again? (was a different node elected as cluster manager when you started the node back up?)

**Answer:**

Opensearch-node3 stays the cluster manager.

```sh
docker start opensearch-node1
```

| ip                  |heap.percent |ram.percent |cpu | load_1m | load_5m | load_15m | node.role | node.roles                                          |  cluster_manager | name                  |
|---------------------|-------------|------------|----|---------|---------|----------|-----------|-----------------------------------------------------|------------------|-----------------------|
| 172.18.0.7          | 21          |98          | 47 |   0.50  |   0.23  |   0.20   |   dimr    |   cluster_manager,data,ingest,remote_cluster_client | -                |    opensearch-node1   |
| 172.18.0.5          | 40          |98          | 48 |   0.50  |   0.23  |   0.20   |   dimr    |   cluster_manager,data,ingest,remote_cluster_client | *                |    opensearch-node3   |
| 172.18.0.6          | 36          |98          | 47 |   0.50  |   0.23  |   0.20   |   dimr    |   cluster_manager,data,ingest,remote_cluster_client | -                |    opensearch-node2   |


## Level 2: Creating a sharded Index


```
PUT /sensor
{
    "settings" : {
        "index" : {
            "number_of_shards" : 3, 
            "number_of_replicas" : 2 
        }
    }
}
```

```
curl -k -X PUT -u admin:admin https://localhost:9200/bbuy_products -H 'Content-Type: application/json' -d @week3/bbuy_products.json
cd week3
export BBUY_DATA=../datasets/product_data/products
python index.py -s $BBUY_DATA -w 8 -b 500
```

INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 200000 and 500 per batch.
INFO:Done. 1275077 were indexed in 5.702952890283333 minutes.  Total accumulated time spent in `bulk` indexing: 18.04553139530001 minutes

`GET /_cat/shards/bbuy_products?v&s=shard,prirep`

| index         | shard | prirep | state   |   docs |   store | ip         | node             |
|---------------|-------|--------|---------|--------|---------|------------|------------------|
| bbuy_products | 0     | p      | STARTED | 423938 | 417.6mb | 172.18.0.7 | opensearch-node1 |
| bbuy_products | 0     | r      | STARTED | 423938 | 418.6mb | 172.18.0.6 | opensearch-node2 |
| bbuy_products | 0     | r      | STARTED | 423938 | 418.9mb | 172.18.0.5 | opensearch-node3 |
| bbuy_products | 1     | p      | STARTED | 425833 | 420.8mb | 172.18.0.6 | opensearch-node2 |
| bbuy_products | 1     | r      | STARTED | 425833 | 417.4mb | 172.18.0.5 | opensearch-node3 |
| bbuy_products | 1     | r      | STARTED | 425833 | 419.8mb | 172.18.0.7 | opensearch-node1 |
| bbuy_products | 2     | p      | STARTED | 425306 | 424.9mb | 172.18.0.5 | opensearch-node3 |
| bbuy_products | 2     | r      | STARTED | 425306 | 431.7mb | 172.18.0.6 | opensearch-node2 |
| bbuy_products | 2     | r      | STARTED | 425306 | 433.9mb | 172.18.0.7 | opensearch-node1 |


```
{
  "settings": {
    "index": {
      "number_of_shards": 3,
      "number_of_replicas": 2
    },
    ...
    }
}
```

### Q4: How much faster was it to index the dataset with 0 replicas versus the previous time with 2 replica shards?

INFO:Done. 1275077 were indexed in 2.8425195375000003 minutes.  Total accumulated time spent in `bulk` indexing: 4.234756157766661 minutes

**Answer:**

5.70 - 2.84 = 2.86 minutes faster

### Q5: Why was it faster?

Because there is no replica shards, so the data is only written to the primary shard.

Update the existing index to add 2 replica shards.

```
PUT /bbuy_products/_settings
{
  "index": {
    "number_of_replicas": 2
  }
}
```


### Q6: How long did it take to create the new replica shards?  This will be the difference in time between those two log messages.


[2023-05-12T22:59:52,188][INFO ][o.o.c.m.MetadataUpdateSettingsService] [opensearch-node3] updating number_of_replicas to [2] for indices [bbuy_products]
[2023-05-12T23:00:35,129][INFO ][o.o.c.r.a.AllocationService] [opensearch-node3] Cluster health status changed from [YELLOW] to [GREEN] (reason: [shards started [[bbuy_products][0]]]).

2023-05-12T23:00:35,129 - 2023-05-12T22:59:52,188 = 43.941 seconds

### Q7: Those two messages were both logged by the cluster_manager.  Why do you think the cluster manager is the node that logs these actions (versus non-manager nodes)?

The cluster manager handles the cluster state, so it is responsible for managing the number of replicas shards and where they are located.

`GET /_cat/shards/bbuy_products?v&s=shard,prirep`

| index         | shard | prirep | state   |   docs |   store      | ip         | node             |
|---------------|-------|--------|---------|--------|--------------|------------|------------------|
| bbuy_products | 0     | p      | STARTED | 423938 | **440.8mbb** | 172.18.0.7 | opensearch-node1 |
| bbuy_products | 0     | r      | STARTED | 423938 | **440.8mb**  | 172.18.0.6 | opensearch-node2 |
| bbuy_products | 0     | r      | STARTED | 423938 | **440.8mb**  | 172.18.0.5 | opensearch-node3 |
| bbuy_products | 1     | p      | STARTED | 425833 | **413.5mbb** | 172.18.0.6 | opensearch-node2 |
| bbuy_products | 1     | r      | STARTED | 425833 | **413.5mbb** | 172.18.0.5 | opensearch-node3 |
| bbuy_products | 1     | r      | STARTED | 425833 | **413.5mb**  | 172.18.0.7 | opensearch-node1 |
| bbuy_products | 2     | p      | STARTED | 425306 | **412.4mbb** | 172.18.0.5 | opensearch-node3 |
| bbuy_products | 2     | r      | STARTED | 425306 | **412.4mbb** | 172.18.0.6 | opensearch-node2 |
| bbuy_products | 2     | r      | STARTED | 425306 | **412.4mbb** | 172.18.0.7 | opensearch-node1 |


> *Note that the replicas are now the same storage size as their primaries, since they are now exact copies of (not re-indexed versions of) the primary shard content.*

## Level 3: Query Performance with Replica Shards

``sh
export BBUY_QUERIES=/Users/jessica-g/Documents/search/corise/search_engineering/search_engineering/datasets           
python ./query.py -q $BBUY_QUERIES/train.csv -w 4 -m 25000
```

Q: Looking at the metrics dashboard, what queries/sec rate are you getting?

**Answer:**

360 queries/sec


Q: How does that compare to the max queries/sec rate you saw in week 2?

**Answer:**

Max queries/sec rate in week 2:  462 queries/sec (4CPU with 2GB)

My week 2 max is around 100 more queries/sec than week. This doesn't seem to match the suggested 2x improvement in the project instructions.


## Level 4: Re-sharding

> The shrink index API operation moves all of your data in an existing index into a new index with fewer primary shards.

```
PUT bbuy_products/_settings
{
  "index.blocks.write": true
}
```

```
POST /bbuy_products/_shrink/bbuy_products
{
  "settings": {
    "index.number_of_replicas": 2,
    "index.number_of_shards": 1
  }
}
```