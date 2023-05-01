# Week one results

## Level 1, Mappings

Here all as expected:
- Default mappings are analyzed faster than custom ones
- More fields require more processing time

All of the runs were done with the following defaults:

```
Max Docs: 2M
Batch Size: 200
Workers: 8
Refresh Interval: -1
```

### `bbuy_products_no_map` - shorter field set, without user-defined mapping
```
Indexing time: 2.08 minutes
Total accumulated time: 7.78 minutes
```

### `bbuy_products` - shorter field set, instructor mapping
```
Indexing time: 2.24 minutes
Total accumulated time: 8.99 minutes
```

### `bbuy_products_no_map` - full field set, without user-defined mapping
```
Indexing time: 2.13 minutes
Total accumulated time: 8.04 minutes
```

### `bbuy_products` - full field set, instructor mapping
```
Indexing time: 2.27 minutes
Total accumulated time: 9.20 minutes
```

## Level 1, Refresh Interval

Here, surprisingly `60s` interval performed better than switching it off with `-1`.
`1s` is the worst, as expected.
All of the runs were done with the following defaults:

```
Max Docs: 2M
Batch Size: 200
Workers: 8
Full field set, with `bbuy_products` mappings
```

### Refresh interval switched off
```
Indexing time: 2.13 minutes
Total accumulated time: 8.24 minutes
```

### Default refresh interval, 1s
```
Indexing time: 2.27 minutes
Total accumulated time: 9.28 minutes
```

### 60s
```
Indexing time: 2.10 minutes
Total accumulated time: 8.06 minutes
```

## Level 1, Batch Size, Refresh Interval 60s

All of the runs were done with the following defaults:
```
Max Docs: 2M
Batch Size: 200
Workers: 8
Refresh Interval: 60s
Full field set, with `bbuy_products` mappings
```

### 200
INFO:Indexing to bbuy_products with 8 workers, refresh_interval of 60s to host localhost with a maximum number of docs sent per file per worker of 2000000 and 200 per batch.
INFO:Done. 1275077 were indexed in 2.0352100041656134 minutes. total accumulated time spent in `bulk` indexing: 7.603266260070571 minutes

### 400
INFO:Indexing to bbuy_products with 8 workers, refresh_interval of 60s to host localhost with a maximum number of docs sent per file per worker of 2000000 and 400 per batch.
INFO:Done. 1275077 were indexed in 2.022885565966135 minutes. total accumulated time spent in `bulk` indexing: 7.4555092402093575 minutes

### 800
INFO:Indexing to bbuy_products with 8 workers, refresh_interval of 60s to host localhost with a maximum number of docs sent per file per worker of 2000000 and 800 per batch.
INFO:Done. 1275077 were indexed in 2.013187640267036 minutes. total accumulated time spent in `bulk` indexing: 7.35212853756966 minutes

### 1600
INFO:Indexing to bbuy_products with 8 workers, refresh_interval of 60s to host localhost with a maximum number of docs sent per file per worker of 2000000 and 1600 per batch.
INFO:Done. 1275077 were indexed in 2.08874557223365 minutes. total accumulated time spent in `bulk` indexing: 7.81045693566557 minutes

### 3200
INFO:Indexing to bbuy_products with 8 workers, refresh_interval of 60s to host localhost with a maximum number of docs sent per file per worker of 2000000 and 3200 per batch.
INFO:Done. 1275077 were indexed in 2.0867465250000046 minutes. total accumulated time spent in `bulk` indexing: 7.486287612695014 minutes

### 5000
INFO:Indexing to bbuy_products with 8 workers, refresh_interval of 60s to host localhost with a maximum number of docs sent per file per worker of 2000000 and 5000 per batch.
INFO:Done. 1275077 were indexed in 2.0712099798663983 minutes. total accumulated time spent in `bulk` indexing: 7.462551590200746 minutes

## Level 1, Workes, Refresh Interval -1

### 8
INFO:Indexing to bbuy_products with 8 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 2000000 and 3200 per batch.
INFO:Done. 1275077 were indexed in 2.065828593748544 minutes. total accumulated time spent in `bulk` indexing: 7.498947101092199 minutes

### 16
INFO:Indexing to bbuy_products with 16 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 2000000 and 3200 per batch.
INFO:Done. 1275077 were indexed in 2.055382668750826 minutes. total accumulated time spent in `bulk` indexing: 22.339362691701776 minutes

### 32
INFO:Indexing to bbuy_products with 32 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 2000000 and 3200 per batch.
INFO:Done. 1275077 were indexed in 2.7611230756990457 minutes. total accumulated time spent in `bulk` indexing: 65.16197838865531 minutes

### 64
INFO:Indexing to bbuy_products with 64 workers, refresh_interval of -1 to host localhost with a maximum number of docs sent per file per worker of 2000000 and 3200 per batch.
INFO:Done. 1275077 were indexed in 3.1376471444498746 minutes. total accumulated time spent in `bulk` indexing: 156.12936868037988 minutes

