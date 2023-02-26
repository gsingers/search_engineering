import os
import click
import glob
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging

from time import perf_counter
import concurrent.futures
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')


# NOTE: this is not a complete list of fields.  If you wish to add more, put in the appropriate XPath expression.
# TODO: is there a way to do this using XPath/XSL Functions so that we don't have to maintain a big list?

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


def index_file(file, index_name):
    docs_indexed = 0
    client = get_opensearch()
    logger.info(f'Processing file : {file}')
    tree = etree.parse(file)
    root = tree.getroot()
    children = root.findall("./product")
    docs = []
    for child in children:
        doc = {}
        for idx in range(0, len(mappings), 2):
            xpath_expr = mappings[idx]
            key = mappings[idx + 1]
            doc[key] = child.xpath(xpath_expr)
        #print(doc)
        if 'productId' not in doc or len(doc['productId']) == 0:
            continue

        docs.append({'_index': index_name, '_id':doc['sku'][0], '_source' : doc})
        #docs.append({'_index': index_name, '_source': doc})
        docs_indexed += 1
        if docs_indexed % 200 == 0:
            bulk(client, docs, request_timeout=60)
            #logger.info(f'{docs_indexed} documents indexed')
            docs = []
    if len(docs) > 0:
        bulk(client, docs, request_timeout=60)
        logger.info(f'{docs_indexed} documents indexed')
    return docs_indexed

@click.command()
@click.option('--source_dir', '-s', help='ESCI split JSON-Lines directory', default="/workspace/datasets/esci")
@click.option('--index_name', '-i', default="esci", help="The name of the index to write to")
@click.option('--max_docs', '-m', default="2000000",
              help="The maximum number of documents to index per worker")
@click.option('--workers', '-w', default=8, help="The number of workers to use to process files")
def main(source_file: str, index_name: str, max_docs: int):
    files = glob.glob(source_dir + "/*.xml")
    docs_indexed = 0
    start = perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(index_file, file, index_name) for file in files]
        for future in concurrent.futures.as_completed(futures):
            docs_indexed += future.result()

    finish = perf_counter()
    logger.info(f'Done. Total docs: {docs_indexed} in {(finish - start)/60} minutes')


if __name__ == "__main__":
    main()
