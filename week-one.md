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

Time | -1 | 1s | 60s
--- | --- | --- | ---
Indexing time (minutes) | 2.13 | 2.27 | 2.10
Total accumulated time (minutes) | 8.24 | 9.28 | 8.06


## Level 1, Batch Size

The best results were at the batch size of 800. At 1600 and 3200 it gets worse. And at 5000 it gets better again, but not as good as 800.
All of the runs were done with the following defaults:
```
Max Docs: 2M
Workers: 8
Refresh Interval: 60s
Full field set, with `bbuy_products` mappings
```

Time | 200 | 400 | 800 | 1600 | 3200 | 5000
--- | --- | --- | --- | --- | --- | ---
Indexing time (minutes) | 2.03 | 2.02 | 2.01 | 2.09 | 2.09 | 2.07
Total accumulated time (minutes) | 7.60 | 7.46 | 7.35 | 7.81 | 7.49 | 7.46


## Level 1, Workers

Here it seems that 8 workers are enough. The gains of 16 workers are negligible.
All of the runs were done with the following defaults:
```
Max Docs: 2M
Batch Size: **3200**
Refresh Interval: -1
Full field set, with `bbuy_products` mappings
```

Time | 8 | 16 | 32 | 64
--- | --- | --- | --- | ---
Indexing time (minutes) | 2.07 | 2.06 | 2.76 | 3.14
Total accumulated time (minutes) | 7.50 | 22.34 | 65.16 | 156.13


