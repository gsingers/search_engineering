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

## Level 1, Batch Size

The best results were at the batch size of 800. At 1600 and 3200 it gets worse. And at 5000 it gets better again, but not as good as 800.
All of the runs were done with the following defaults:
```
Max Docs: 2M
Workers: 8
Refresh Interval: 60s
Full field set, with `bbuy_products` mappings
```

### 200
```
Indexing time: 2.03 minutes
Total accumulated time: 7.60 minutes
```

### 400
```
Indexing time: 2.02 minutes
Total accumulated time: 7.46 minutes
```

### 800
```
Indexing time: 2.01 minutes
Total accumulated time: 7.35 minutes
```

### 1600
```
Indexing time: 2.09 minutes
Total accumulated time: 7.81 minutes
```

### 3200
```
Indexing time: 2.09 minutes
Total accumulated time: 7.49 minutes
```

### 5000
```
Indexing time: 2.07 minutes
Total accumulated time: 7.46 minutes
```

## Level 1, Workers

Here it seems that 8 workers are enough. The gains of 16 workers are negligible.
All of the runs were done with the following defaults:
```
Max Docs: 2M
Batch Size: **3200**
Refresh Interval: -1
Full field set, with `bbuy_products` mappings
```

### 8
```
Indexing time: 2.07 minutes
Total accumulated time: 7.50 minutes
```

### 16
```
Indexing time: 2.06 minutes
Total accumulated time: 22.34 minutes
```

### 32
```
Indexing time: 2.76 minutes
Total accumulated time: 65.16 minutes
```

### 64
```
Indexing time: 3.14 minutes
Total accumulated time: 156.13 minutes
```

