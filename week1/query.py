# A simple client for querying driven by user input on the command line.  Has hooks for the various
# weeks (e.g. query understanding).  See the main section at the bottom of the file
from opensearchpy import OpenSearch
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
        logger.debug(json.dumps(response, indent=2))

        return hits


@click.command()
@click.option('--query_file', '-q', default="/workspace/datasets/train.csv", help='Path to train.csv or test.csv or similar file containing queries')
@click.option('--index_name', '-i', default="bbuy_products", help="The name of the index to write to")
@click.option('--host', '-o', default="localhost", help="The name of the host running OpenSearch")
@click.option('--max_queries', '-m', default=500, help="The maximum number of queries to run.  Set to -1 to run all.")
def main(query_file: str, index_name: str, host: str, max_queries: int):
    logger.info(f"Loading query file from {query_file}")
    query_df = pd.read_csv(query_file, parse_dates=['click_time', 'query_time'])
    queries = query_df["query"][0:max_queries]
    client = get_opensearch(host)
    start = perf_counter()
    i = 0
    modulo = 1000
    logger.info(f"Running queries, checking in every {modulo} queries:")
    for query in queries:
        i+= 1
        hits = search(client, query, index_name)
        if i % modulo == 0 and hits is not None:
            logger.info(f"Query: {query} has {len(hits)} hits.")


    end = perf_counter()
    logger.info(f"Finished running {len(queries)} queries in {(end - start)/60} minutes")
    
    

if __name__ == "__main__":
    main()

