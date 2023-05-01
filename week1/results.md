# Results

## Commands

```
export HOST=localhost
export BBUY_DATA=../datasets/product_data/products

curl -k -X DELETE -u admin:admin https://localhost:9200/bbuy_products

curl -k -X PUT -u admin:admin  "https://$HOST:9200/bbuy_products" -H 'Content-Type: application/json' -d @bbuy_products_no_map.json

python index.py -s $BBUY_DATA
```

## Level 1

### Indexing with more fields mapped

#### Index using the class field mappings

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.5614970270833335 minutes.  Total accumulated time spent in `bulk` indexing: 8.294717284033334 minutes
```

#### Index using the default field mappings

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.399084845133333 minutes.  Total accumulated time spent in `bulk` indexing: 7.426271914566667 minutes
```

*"We added more fields, which both increased our extraction time (as seen by the overall time increasing) and our indexing time increased as well because we sent a bigger payload and had more indexing to do."*

### Indexing with different refresh intervals

#### Index with refresh_interval of 5s

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of 5 to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.4566616111166666 minutes.  Total accumulated time spent in `bulk` indexing: 7.4569628405333255 minutes
```

#### Index with refresh_interval of -1

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.2866771340333334 minutes.  Total accumulated time spent in `bulk` indexing: 6.842631512999996 minutes
```

#### Index with refresh_interval of 1s

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of 1s to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.39362734445 minutes.  Total accumulated time spent in `bulk` indexing: 7.131289079816664 minutes
```

#### Index with refresh_interval of 60s

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of 60s to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.32450584235 minutes.  Total accumulated time spent in `bulk` indexing: 6.764026175166666 minutes
```


### Indexing with different batch sizes

#### Index with batch size of 400

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 200000 and 400 per batch.
INFO:Done. 1275077 were indexed in 2.220876511116667 minutes.  Total accumulated time spent in `bulk` indexing: 5.979449398966679 minutes
```

#### Index with batch size of 800

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 200000 and 800 per batch.
INFO:Done. 1275077 were indexed in 2.2385063291666665 minutes.  Total accumulated time spent in `bulk` indexing: 5.981635271383334 minutes
```

#### Index with batch size of 1600

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 200000 and 1600 per batch.
INFO:Done. 1275077 were indexed in 2.3413532215333333 minutes.  Total accumulated time spent in `bulk` indexing: 6.499164863516671 minutes
```

#### Index with batch size of 3200

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 200000 and 3200 per batch.
INFO:Done. 1275077 were indexed in 2.4178878458333335 minutes.  Total accumulated time spent in `bulk` indexing: 6.513337936033336 minutes
```

#### Index with batch size of 5000

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 200000 and 5000 per batch.
INFO:Done. 1275077 were indexed in 2.4020838416666668 minutes.  Total accumulated time spent in `bulk` indexing: 6.352190013016671 minutes
```

*"It isn’t all that uncommon to see performance improve and then degrade again as batch size increases. The likely cause of this is more time spent accumulating the docs in bulk versus time spent in network, swap or other activities like garbage collection, disk I/O, etc."*

### Indexing with different number of workers

#### Index with 8 workers

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 8 workers, refresh_interval of 5s to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.377778297916666 minutes.  Total accumulated time spent in `bulk` indexing: 7.121490175066674 minutes
```

#### Index with 16 workers

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 16 workers, refresh_interval of 5s to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.3111792382 minutes.  Total accumulated time spent in `bulk` indexing: 16.574846963633323 minutes
```

#### Index with 32 workers

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 32 workers, refresh_interval of 5s to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.6759482340166665 minutes.  Total accumulated time spent in `bulk` indexing: 40.13966463111671 minutes
```

#### Index with 64 workers

```
INFO:Indexing ../datasets/product_data/products to bbuy_products with 64 workers, refresh_interval of 5s to host localhost with a maximum number of docs sent per file per worker of 200000 and 200 per batch.
INFO:Done. 1275077 were indexed in 3.0282032159666668 minutes.  Total accumulated time spent in `bulk` indexing: 88.13670687255002 minutes
```

*"Here again, there are diminishing returns, as predicted by things like CPU cores, disk I/O, memory, etc."*

## Table of results

| Indexing Parameters | Time to index (minutes) | Time to extract (minutes) |
|---------------------|-------------------------|---------------------------|
| Default             | 2.5614970270833335      | 8.294717284033334         |
| More fields         | 2.399084845133333       | 7.426271914566667         |
| Refresh 5s          | 2.4566616111166666      | 7.4569628405333255        |
| Refresh -1          | 2.2866771340333334      | 6.842631512999996         |
| Refresh 1s          | 2.39362734445           | 7.131289079816664         |
| Refresh 60s         | 2.32450584235           | 6.764026175166666         |
| Batch 400           | 2.220876511116667       | 5.979449398966679         |
| Batch 800           | 2.2385063291666665      | 5.981635271383334         |
| Batch 1600          | 2.3413532215333333      | 6.499164863516671         |
| Batch 3200          | 2.4178878458333335      | 6.513337936033336         |
| Batch 5000          | 2.4020838416666668      | 6.352190013016671         |
| Workers 8           | 2.377778297916666       | 7.121490175066674         |
| Workers 16          | 2.3111792382            | 16.574846963633323        |
| Workers 32          | 2.6759482340166665      | 40.13966463111671         |
| Workers 64          | 3.0282032159666668      | 88.13670687255002         |


