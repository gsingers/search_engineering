# From https://github.com/dshvadskiy/search_with_machine_learning_course/blob/main/index_products.py
import opensearchpy
import requests
from lxml import etree

import os
import click
import glob
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging
from pathlib import Path
import requests
import json

from time import perf_counter
import signal
import concurrent.futures
from multiprocessing import Event
from multiprocessing import Manager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

# NOTE: this is not a complete list of fields.  If you wish to add more, put in the appropriate XPath expression.
# TODO: is there a way to do this using XPath/XSL Functions so that we don't have to maintain a big list?
mappings = {
    "sku":"sku/text()",
    "productId": "productId/text()",
    "name": "name/text()",
    "type":"type/text()",
    "shortDescription": "shortDescription/text()",
    "startDate": "startDate/text()",
"active": "active/text()",
"regularPrice": "regularPrice/text()",
"salePrice": "salePrice/text()",
"shortDescription": "shortDescription/text()",
"shortDescriptionHtml": "shortDescriptionHtml/text()",
"longDescription": "longDescription/text()",
"longDescriptionHtml": "longDescriptionHtml/text()",
"artistName": "artistName/text()",
"onSale": "onSale/text()",
"digital": "digital/text()",
"frequentlyPurchasedWith": "frequentlyPurchasedWith/*/text()",  # Note the match all here to get the subfields
"accessories": "accessories/*/text()" ,  # Note the match all here to get the subfields
"relatedProducts": "relatedProducts/*/text()",  # Note the match all here to get the subfields
"crossSell": "crossSell/text()",
"salesRankShortTerm": "salesRankShortTerm/text()",
"salesRankMediumTerm": "salesRankMediumTerm/text()",
"salesRankLongTerm": "salesRankLongTerm/text()",
"bestSellingRank": "bestSellingRank/text()",
"url": "url/text()",
"categoryPath": "categoryPath/*/name/text()",  # Note the match all here to get the subfields
"categoryPathIds": "categoryPath/*/id/text()",  # Note the match all here to get the subfields
"categoryLeaf": "categoryPath/category[last()]/id/text()",
"categoryPathCount": "count(categoryPath/*/name)",
"customerReviewCount": "customerReviewCount/text()",
"customerReviewAverage": "customerReviewAverage/text()",
"inStoreAvailability": "inStoreAvailability/text()",
"onlineAvailability": "onlineAvailability/text()",
"releaseDate": "releaseDate/text()",
"shippingCost": "shippingCost/text()",
"class": "class/text()",
"classId": "classId/text()",
"subclass": "subclass/text()",
"subclassId": "subclassId/text()",
"department": "department/text()",
"departmentId": "departmentId/text()",
"bestBuyItemId": "bestBuyItemId/text()",
"description": "description/text()",
"manufacturer": "manufacturer/text()",
"modelNumber": "modelNumber/text()",
"image": "image/text()",
"condition": "condition/text()",
"inStorePickup": "inStorePickup/text()",
"homeDelivery": "homeDelivery/text()",
"quantityLimit": "quantityLimit/text()",
"color": "color/text()",
"depth": "depth/text()",
"height": "height/text()",
"weight": "weight/text()",
"shippingWeight": "shippingWeight/text()",
"width": "width/text()",
"features": "features/*/text()"  # Note the match all here to get the subfields

}
'''
"startDate": "startDate/text()",
"active": "active/text()",
"regularPrice": "regularPrice/text()",
"salePrice": "salePrice/text()",
"shortDescription": "shortDescription/text()",
"shortDescriptionHtml": "shortDescriptionHtml/text()",
"longDescription": "longDescription/text()",
"longDescriptionHtml": "longDescriptionHtml/text()",
"artistName": "artistName/text()",
"onSale": "onSale/text()",
"digital": "digital/text()",
"frequentlyPurchasedWith": "frequentlyPurchasedWith/*/text()",  # Note the match all here to get the subfields
"accessories": "accessories/*/text()" ,  # Note the match all here to get the subfields
"relatedProducts": "relatedProducts/*/text()",  # Note the match all here to get the subfields
"crossSell": "crossSell/text()",
"salesRankShortTerm": "salesRankShortTerm/text()",
"salesRankMediumTerm": "salesRankMediumTerm/text()",
"salesRankLongTerm": "salesRankLongTerm/text()",
"bestSellingRank": "bestSellingRank/text()",
"url": "url/text()",
"categoryPath": "categoryPath/*/name/text()",  # Note the match all here to get the subfields
"categoryPathIds": "categoryPath/*/id/text()",  # Note the match all here to get the subfields
"categoryLeaf": "categoryPath/category[last()]/id/text()",
"categoryPathCount": "count(categoryPath/*/name)",
"customerReviewCount": "customerReviewCount/text()",
"customerReviewAverage": "customerReviewAverage/text()",
"inStoreAvailability": "inStoreAvailability/text()",
"onlineAvailability": "onlineAvailability/text()",
"releaseDate": "releaseDate/text()",
"shippingCost": "shippingCost/text()",
"class": "class/text()",
"classId": "classId/text()",
"subclass": "subclass/text()",
"subclassId": "subclassId/text()",
"department": "department/text()",
"departmentId": "departmentId/text()",
"bestBuyItemId": "bestBuyItemId/text()",
"description": "description/text()",
"manufacturer": "manufacturer/text()",
"modelNumber": "modelNumber/text()",
"image": "image/text()",
"condition": "condition/text()",
"inStorePickup": "inStorePickup/text()",
"homeDelivery": "homeDelivery/text()",
"quantityLimit": "quantityLimit/text()",
"color": "color/text()",
"depth": "depth/text()",
"height": "height/text()",
"weight": "weight/text()",
"shippingWeight": "shippingWeight/text()",
"width": "width/text()",
"features": "features/*/text()"  # Note the match all here to get the subfields

'''

def get_opensearch(the_host="localhost"):
    host = the_host
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


def index_file(file, index_name, stop_event, host="localhost", max_docs=2000000, batch_size=200):
    docs_indexed = 0
    ### W4: S1: Load the model.  # We do this here to avoid threading issues
    client = get_opensearch(host)
    logger.debug(f'Processing file : {file}')
    tree = etree.parse(file)
    root = tree.getroot()
    children = root.findall("./product")
    batch_size = min(max_docs, batch_size) # make sure our batch size isn't bigger than our max_docs, else we will never transmit
    docs = []
    time_indexing = 0

    for child in children:
        if docs_indexed >= max_docs or stop_event.is_set():
            break
        doc = {}
        for name, xpath in mappings.items():
            doc[name] = child.xpath(xpath)
        # print(doc)
        if 'productId' not in doc or len(doc['productId']) == 0:
            continue
        docs.append({'_index': index_name, '_id': doc['sku'][0], '_source': doc})
        docs_indexed += 1
        if docs_indexed % batch_size == 0:
            start = perf_counter()
            bulk(client, docs, request_timeout=120)
            stop = perf_counter()
            time_indexing += (stop - start)
            docs = []
    if len(docs) > 0:
        logger.debug("Sending final batch of docs")
        start = perf_counter()
        bulk(client, docs, request_timeout=120)
        stop = perf_counter()
        time_indexing += (stop - start)
    logger.debug(f'{docs_indexed} documents indexed in {time_indexing}')
    return docs_indexed, time_indexing


@click.command()
@click.option('--source_dir', '-s', help='XML files source directory')
@click.option('--file_glob', '-g', help='The file glob to use to get the files to index in the source dir.', default="*.xml")
@click.option('--index_name', '-i', default="bbuy_products", help="The name of the index to write to")
@click.option('--workers', '-w', default=8, help="The number of workers/processes to use")
@click.option('--host', '-o', default="localhost", help="The name of the host running OpenSearch")
@click.option('--max_docs', '-m', default=200000, help="The maximum number of docs to be indexed PER WORKER PER FILE.")
@click.option('--batch_size', '-b', default=200, help="The number of docs to send per request. Max of 5000")
@click.option('--refresh_interval', '-r', default="-1", help="The number of docs to send per request. Max of 5000")
def main(source_dir: str, file_glob: str, index_name: str, workers: int, host: str, max_docs: int, batch_size: int, refresh_interval: str):
    batch_size = min(batch_size, 5000)  # I believe this is the default max batch size, but need to find docs on that
    logger.info(
        f"Indexing {source_dir} to {index_name} with {workers} workers, refresh_interval of {refresh_interval} to host {host} with a maximum number of docs sent per file per worker of {max_docs} and {batch_size} per batch.")
    files = glob.glob(source_dir + "/" + file_glob)
    docs_indexed = 0

    client = get_opensearch(host)

    #TODO: set the refresh interval
    logger.debug(client.indices.get_settings(index=index_name))
    start = perf_counter()
    time_indexing = 0

    with Manager() as manager:
        stop_event = manager.Event()

        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(index_file, file, index_name, stop_event, host, max_docs, batch_size) for file in files]

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
            num_docs, the_time = future.result()
            docs_indexed += num_docs
            time_indexing += the_time

    finish = perf_counter()
    logger.info(f'Done. {docs_indexed} were indexed in {(finish - start)/60} minutes.  Total accumulated time spent in `bulk` indexing: {time_indexing/60} minutes')
    # TODO set refresh interval back to 5s
    logger.debug(client.indices.get_settings(index=index_name))

if __name__ == "__main__":
    main()
