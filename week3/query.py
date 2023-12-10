# A simple client for querying driven by user input on the command line.  Has hooks for the various
# weeks (e.g. query understanding).  See the main section at the bottom of the file
from opensearchpy import OpenSearch
import signal
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import argparse
import json
import os
from getpass import getpass
from urllib.parse import urljoin
import pandas as pd
import fileinput
import logging
import click

from time import perf_counter
import concurrent.futures
from multiprocessing import Event
from multiprocessing import Manager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

def get_opensearch(the_host="localhost"):
    host = the_host
    port = 9200
    auth = ('admin', 'admin')
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=False,  # enables gzip compression for request bodies
        http_auth=auth,
        # client_cert = client_cert_path,
        # client_key = client_key_path,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        # ca_certs=ca_certs_path
    )
    return client


# Hardcoded query here.  Better to use search templates or other query config.
def create_query(user_query, filters=None, sort="_score", sortDir="desc", size=10, source=None):
    query_obj = {
        'size': size,
        "sort": [
            {sort: {"order": sortDir}}
        ],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [

                        ],
                        "should": [  #
                            {
                                "match": {
                                    "name": {
                                        "query": user_query,
                                        "fuzziness": "1",
                                        "prefix_length": 2,
                                        # short words are often acronyms or usually not misspelled, so don't edit
                                        "boost": 0.01
                                    }
                                }
                            },
                            {
                                "match_phrase": {  # near exact phrase match
                                    "name.hyphens": {
                                        "query": user_query,
                                        "slop": 1,
                                        "boost": 50
                                    }
                                }
                            },
                            {
                                "multi_match": {
                                    "query": user_query,
                                    "type": "phrase",
                                    "slop": "6",
                                    "minimum_should_match": "2<75%",
                                    "fields": ["name^10", "name.hyphens^10", "shortDescription^5",
                                               "longDescription^5", "department^0.5", "sku", "manufacturer", "features",
                                               "categoryPath"]
                                }
                            },
                            {
                                "terms": {
                                    # Lots of SKUs in the query logs, boost by it, split on whitespace so we get a list
                                    "sku": user_query.split(),
                                    "boost": 50.0
                                }
                            },
                            {  # lots of products have hyphens in them or other weird casing things like iPad
                                "match": {
                                    "name.hyphens": {
                                        "query": user_query,
                                        "operator": "OR",
                                        "minimum_should_match": "2<75%"
                                    }
                                }
                            }
                        ],
                        "minimum_should_match": 1,
                        "filter": filters  #
                    }
                },
                "boost_mode": "multiply",  # how _score and functions are combined
                "score_mode": "sum",  # how functions are combined
                "functions": [
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankShortTerm"
                            }
                        },
                        "gauss": {
                            "salesRankShortTerm": {
                                "origin": "1.0",
                                "scale": "100"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankMediumTerm"
                            }
                        },
                        "gauss": {
                            "salesRankMediumTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankLongTerm"
                            }
                        },
                        "gauss": {
                            "salesRankLongTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "script_score": {
                            "script": "0.0001"
                        }
                    }
                ]

            }
        },
        "aggs": {
            "department": {
                "terms": {
                    "field": "department.keyword",
                    "min_doc_count": 1
                }
            },
            "missing_images": {
                "missing": {
                    "field": "image"
                }
            },
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    "ranges": [
                        {"key": "$", "to": 100},
                        {"key": "$$", "from": 100, "to": 200},
                        {"key": "$$$", "from": 200, "to": 300},
                        {"key": "$$$$", "from": 300, "to": 400},
                        {"key": "$$$$$", "from": 400, "to": 500},
                        {"key": "$$$$$$", "from": 500},
                    ]
                },
                "aggs": {
                    "price_stats": {
                        "stats": {"field": "regularPrice"}
                    }
                }
            }
        }
    }
    if user_query == "*" or user_query == "#":
        # replace the bool
        try:
            query_obj["query"] = {"match_all": {}}
        except:
            print("Couldn't replace query for *")
    if source is not None:  # otherwise use the default and retrieve all source
        query_obj["_source"] = source
    return query_obj


def search(client, user_query, index="bbuy_products"):
    query_obj = create_query(user_query)
    logging.info(query_obj)
    start = perf_counter()
    response = client.search(query_obj, index=index)
    end = perf_counter()
    if response and response['hits']['hits'] and len(response['hits']['hits']) > 0:
        hits = response['hits']['hits']
        aggregations = response["aggregations"]
        #logger.info(json.dumps(aggregations, indent=2))

        return hits, aggregations
    else:
        logger.debug(f'No results for query: {user_query}')
        return None, None

def query_opensearch(worker_num, query_file: str, host: str, index_name: str, max_queries: int, seed: int, stop_event):
    logger.info(f"Loading query file from {query_file} and using seed {seed} for worker: {worker_num}")
    query_df = pd.read_csv(query_file, parse_dates=['click_time', 'query_time'])
    queries = query_df["query"].sample(n=max_queries, random_state=seed)
    #logger.info(f'query len: {len(queries)}')
    client = get_opensearch(host)
    start = perf_counter()
    i = 0
    modulo = 1000
    logger.info(f"WN: {worker_num}: Running queries, checking in every {modulo} queries:")
    for query in queries:
        try:
            hits, aggregations = search(client, query, index_name)
            if i % modulo == 0 and hits is not None:
                logger.info(f"WN: {worker_num}: Query: {query} has {len(hits)} hits.")
                if len(hits) > 0:
                    logger.info(f"WN: {worker_num}: First result: {hits[0]}")
                if aggregations is not None:
                    logger.info(f'WN: {worker_num}: Aggs: {aggregations}')
        except:
            logger.warn(f'WN: {worker_num}: Failed to process query: {query}')
        i+= 1
        if stop_event.is_set():
            logger.info(f"WN: {worker_num}: Stopped early.")
            end = perf_counter()
            return (end-start)

    end = perf_counter()
    logger.info(f"WN: {worker_num}: Finished running {len(queries)} queries in {(end - start)/60} minutes")
    return (end-start)


@click.command()
@click.option('--query_file', '-q', default="/workspace/datasets/train.csv", help='Path to train.csv or test.csv or similar file containing queries')
@click.option('--index_name', '-i', default="bbuy_products", help="The name of the index to write to")
@click.option('--host', '-o', default="localhost", help="The name of the host running OpenSearch")
@click.option('--max_queries', '-m', default=500, help="The maximum number of queries to run.  Set to -1 to run all.")
@click.option('--seed', '-s', default=42, help="The seed to use for random sampling.  If multiple workers are used, a different seed will be given to each worker as a multiple of this seed.")
@click.option('--workers', '-w', default=1, help="The number of workers/processes to use")
def main(query_file: str, index_name: str, host: str, max_queries: int, seed: int, workers: int):

    start = perf_counter()
    time_querying = 0

    with Manager() as manager:
        stop_event = manager.Event()

        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(query_opensearch, i, query_file, host, index_name, max_queries, seed*(i+1), stop_event) for i in range(workers)]

            # Define a signal handler to shut down the process pool when Ctrl+C is pressed
            def signal_handler(sig, frame):
                print()
                print("Caught SIGINT. Shutting down workers...")
                print()
                for future in futures:
                    # cancel any tasks not yet running
                    future.cancel()
                    # signal running tasks in the process pool to stop
                    stop_event.set()

            # Register the signal handler for SIGINT 
            signal.signal(signal.SIGINT, signal_handler)

            for future in concurrent.futures.as_completed(futures):
                time = future.result()
                logger.info(f"Query worker finished in time: {time/60}")

    end = perf_counter()
    
if __name__ == "__main__":
    main()
