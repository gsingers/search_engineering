import os
import click
import glob
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging

from time import perf_counter
import concurrent.futures
import pandas as pd
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

def get_opensearch():
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
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

# Input is JSON Lines file, so each line is a complete JSON document
def index_file(file, index_name, max_docs, batch_size=500):
    docs_indexed = 0
    client = get_opensearch()
    logger.info(f'Processing file : {file}')
    json_lines = pd.read_json(file, lines=True)
    docs = []
    for line in json_lines:
        if docs_indexed < max_docs:
            doc = json.loads(line)

            docs.append({'_index': index_name, '_id':doc.product_id, '_source' : doc._asdict()})
            docs_indexed += 1
            if docs_indexed % batch_size == 0:
                bulk(client, docs, request_timeout=60)
                docs = []
            else:
                break
    if len(docs) > 0:
        bulk(client, docs, request_timeout=60)
        logger.info(f'{docs_indexed} documents indexed')
    return docs_indexed

@click.command()
@click.option('--source_dir', '-s', help='ESCI split JSON-Lines directory', default="/workspace/datasets/esci")
@click.option('--index_name', '-i', default="esci", help="The name of the index to write to")
@click.option('--max_docs', '-m', default="2000000",
              help="The maximum number of documents to index per worker")
@click.option('--batch_size', '-b', default="500",
              help="The maximum number of documents to send in bulk to OpenSearch at a time")
@click.option('--workers', '-w', default=8, help="The number of workers to use to process files")
def main(source_dir: str, index_name: str, max_docs: int, batch_size: int, workers: int):
    files = glob.glob(source_dir + "/esci.json.split.*") #this should work on the split files, not the main file, which allows us to index in parallel
    docs_indexed = 0
    start = perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(index_file, file, index_name, max_docs, batch_size) for file in files]
        for future in concurrent.futures.as_completed(futures):
            docs_indexed += future.result()

    finish = perf_counter()
    logger.info(f'Done. Total docs: {docs_indexed} in {(finish - start)/60} minutes')


if __name__ == "__main__":
    main()
