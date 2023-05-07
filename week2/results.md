# Week 2 Results

## Level 1

### Q: How long did it take to index the 1.2M product data set?  What docs/sec indexing rate did you see?

4.30 minutes
5.74K docs/sec

### Q: Notice that the Index size rose (roughly doubled) while the content was being indexed, peaked, then ~ 5 minutes after indexing stopped, the index size dropped down substantially.  Why did it drop back down?  (What did OpenSearch do here?)

The on-disk size of the index roughly doubled because we were indexing the exact same content. When indexing content, even if it's previously indexed content, OpenSearch is creating new Lucene segments on disk to store those documents, this is due to the append-only structure of Lucene segments meaning documents are not updated in-place. The index size dropped down again because OpenSearch merges these segments as part of the process and then removes the older copies of documents.

Takeaway: This is a good example of how disk usage can burst substantially when you’re re-indexing (i.e. updating) a large percentage of the docs in your index.  This is why it’s important to have enough disk space to handle these bursts.

### Q: Looking at the metrics dashboard, what queries/sec rate are you getting?

137 queries/sec

### Q: What resource(s) appear to be the constraining factor?

The OpenSearch Process CPU is at 100%. We also see a maximum of 2 Threads in the thread pool for search. This is because the search [thread pool](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/modules-threadpool.html) will only increase to two threads on a system with 1 CPU. 

## Level 2

#### CPUs 2, Memory 2GB

Some spikes up to 4 threads for search, however in parts it only used 3. The Queue depth was also 0 throughout. I noticed that the CPU usage relative to the request was doubled from 20% to 40%.

I created a new panel for this using the following promql query:

`sum(irate(container_cpu_user_seconds_total{}[5m])) by (namespace,container) / sum(container_spec_cpu_shares{} / 1024) by (namespace,container)`

and memory is almost at 100% relative to the limit.

`sum(container_memory_usage_bytes{}) by (namespace,container) / sum(container_spec_memory_limit_bytes{}) by (namespace,container)`

I noticed CPU usage is peaking far beyond the limit set (a max of 300%!!) I used the following query for this:

`sum(irate(container_cpu_usage_seconds_total{}[5m])) by (namespace,container) / sum(container_spec_cpu_quota{} / container_spec_cpu_period{}) by (namespace,container)`

Also noticeable is the search query rate jumped to 289 queries/sec.


#### Index query rate in relation to resources


| CPU count | Memory | CPU peak relative to request  |  CPU mean relative to request  | CPU peak relative to limit  | Memory peak relative to limit  |  Index query rate max  | Thread pool | Queue depth | GC |
| --------- | ------ | ----------------------------- |  ----------------------------- | --------------------------- | ------------------------------ |  --------------------- | ----------- | ----------- | -- |
| 1         | 2GB    | 20%                           |  17%                           | 216%                        | 98%                            |  5.11k                 | 1           | 14          | 3  |
| 2         | 2GB    | 38%                           |  28%                           | 214%                        | 108%                           |  7.65k                 | 2           | 10          | 1  |
| 2         | 4GB    | 40%                           |  34%                           | 210%                        | 90%                            |  7.63k                 | 2           | 10          | 1  |
| 2         | 8GB    | 40%                           |  27%                           | 218%                        | 105%                           |  7.14k                 | 2           | 13          | 3  |
| 4         | 2GB    | 72%                           |  60%                           | 189%                        | 109%                           |  7.60k                 | 5           | 2           | 1  |
| 4         | 4GB    | 38%                           |  37%                           | 206%                        | 92%                            |  8.36k                 | 4           | 8           | 1  |
| 4         | 8GB    | 70%                           |  40%                           | 196%                        | 103%                           |  8.36k                 | 5           | 11          | 1  |

#### Search query rate in relation to resources

| CPU count | Memory | CPU peak relative to request  |  CPU mean relative to request  | CPU peak relative to limit  | Memory mean relative to limit  | Search query rate max | Thread pool | Queue depth | GC |
| --------- | ------ | ----------------------------- |  ----------------------------- | --------------------------- | ------------------------------ | --------------------- | ----------- | ----------- | -- |
| 1         | 2GB    | 20%                           |  18%                           | 102%                        | 97%                            | 144                   | 2           | 2           | 2  |
| 2         | 2GB    | 40%                           |  30%                           | 300%                        | 100%                           | 289                   | 3-4         | 0           | 2  |
| 2         | 4GB    | 40%                           |  34%                           | 210%                        | 90%                            | 265                   | 3-4         | 0           | 1  |
| 2         | 8GB    | 40%                           |  30%                           | 212%                        | 209%                           | 286                   | 3-4         | 0           | 2  |
| 4         | 2GB    | 70%                           |  65%                           | 177%                        | 80%                            | 419                   | 3-4         | 0           | 1  |
| 4         | 4GB    | 67%                           |  57%                           | 179%                        | 95%                            | 377                   | 3-4         | 0           | 0  |
| 4         | 8GB    | 68%                           |  61%                           | 180%                        | 84%                            | 388                   | 3-4         | 0           | 0  |

### Q: As you increased CPU and memory in your L2 tests, what seemed to be the constraining factor limiting indexing rate?

It appears that the increase of both CPUs and memory had a positive impact on the indexing rate.

### Q: As you increased CPU and memory in your L2 tests, what was the constraining factor for querying rate?

As the CPU increased it was noticeably how the query rate increased. Memory seemed to make little difference.

## Level 3

### Q: What is the impact on your query throughput (QPS) and indexing throughput (docs/sec)?

## Level 4 (Optional)

Can you break the system? Can you move the needle on a given metric? Given what you’ve learned about the various system metrics, the way Lucene and OpenSearch works as well as your general knowledge of CPU, Memory and I/O, go through the metrics in our class dashboard and see if you can purposefully move the needle on that metric via indexing or querying changes and not via resource constraints on the container.


Ideas to try:
- Aggressively try different aggregations to induce field data changes
- Try span, regex and other really expensive queries
- Write your own indexer and query client that generates way more load
- Call your search engine from other machines to generate more load?
- Try restricting some of the lower level settings related to threads, memory, etc.
- Try a different garbage collector