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
import concurrent.futures

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

# NOTE: this is not a complete list of fields.  If you wish to add more, put in the appropriate XPath expression.
# TODO: is there a way to do this using XPath/XSL Functions so that we don't have to maintain a big list?
mappings = [
    "productId/text()", "productId",
    "sku/text()", "sku",
    "name/text()", "name",
    "type/text()", "type",
    "startDate/text()", "startDate",
    "active/text()", "active",
    "regularPrice/text()", "regularPrice",
    "salePrice/text()", "salePrice",
    "artistName/text()", "artistName",
    "onSale/text()", "onSale",
    "digital/text()", "digital",
    "frequentlyPurchasedWith/*/text()", "frequentlyPurchasedWith",  # Note the match all here to get the subfields
    "accessories/*/text()", "accessories",  # Note the match all here to get the subfields
    "relatedProducts/*/text()", "relatedProducts",  # Note the match all here to get the subfields
    "crossSell/text()", "crossSell",
    "salesRankShortTerm/text()", "salesRankShortTerm",
    "salesRankMediumTerm/text()", "salesRankMediumTerm",
    "salesRankLongTerm/text()", "salesRankLongTerm",
    "bestSellingRank/text()", "bestSellingRank",
    "url/text()", "url",
    "categoryPath/*/name/text()", "categoryPath",  # Note the match all here to get the subfields
    "categoryPath/*/id/text()", "categoryPathIds",  # Note the match all here to get the subfields
    "categoryPath/category[last()]/id/text()", "categoryLeaf",
    "count(categoryPath/*/name)", "categoryPathCount",
    "customerReviewCount/text()", "customerReviewCount",
    "customerReviewAverage/text()", "customerReviewAverage",
    "inStoreAvailability/text()", "inStoreAvailability",
    "onlineAvailability/text()", "onlineAvailability",
    "releaseDate/text()", "releaseDate",
    "shippingCost/text()", "shippingCost",
    "shortDescription/text()", "shortDescription",
    "shortDescriptionHtml/text()", "shortDescriptionHtml",
    "class/text()", "class",
    "classId/text()", "classId",
    "subclass/text()", "subclass",
    "subclassId/text()", "subclassId",
    "department/text()", "department",
    "departmentId/text()", "departmentId",
    "bestBuyItemId/text()", "bestBuyItemId",
    "description/text()", "description",
    "manufacturer/text()", "manufacturer",
    "modelNumber/text()", "modelNumber",
    "image/text()", "image",
    "condition/text()", "condition",
    "inStorePickup/text()", "inStorePickup",
    "homeDelivery/text()", "homeDelivery",
    "quantityLimit/text()", "quantityLimit",
    "color/text()", "color",
    "depth/text()", "depth",
    "height/text()", "height",
    "weight/text()", "weight",
    "shippingWeight/text()", "shippingWeight",
    "width/text()", "width",
    "longDescription/text()", "longDescription",
    "longDescriptionHtml/text()", "longDescriptionHtml",
    "features/*/text()", "features"  # Note the match all here to get the subfields

]


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


def index_file(file, index_name, host="localhost", max_docs=2000000, batch_size=200):
    docs_indexed = 0
    ### W4: S1: Load the model.  # We do this here to avoid threading issues
    client = get_opensearch(host)
    logger.info(f'Processing file : {file}')
    tree = etree.parse(file)
    root = tree.getroot()
    children = root.findall("./product")
    docs = []
    for child in children:
        if docs_indexed >= max_docs:
            break
        doc = {}
        for idx in range(0, len(mappings), 2):
            xpath_expr = mappings[idx]
            key = mappings[idx + 1]
            doc[key] = child.xpath(xpath_expr)
        # print(doc)
        if 'productId' not in doc or len(doc['productId']) == 0:
            continue
        docs.append({'_index': index_name, '_id': doc['sku'][0], '_source': doc})
        docs_indexed += 1
        if docs_indexed % batch_size == 0:
            bulk(client, docs, request_timeout=60)
            docs = []
    if len(docs) > 0:
        bulk(client, docs, request_timeout=60)
        logger.info(f'{docs_indexed} documents indexed')
    return docs_indexed


@click.command()
@click.option('--source_dir', '-s', help='XML files source directory')
@click.option('--index_name', '-i', default="bbuy_products", help="The name of the index to write to")
@click.option('--workers', '-w', default=8, help="The name of the index to write to")
@click.option('--host', '-o', default="localhost", help="The name of the host running OpenSearch")
@click.option('--max_docs', '-m', default=200000, help="The maximum number of docs to be indexed PER WORKER.")
@click.option('--batch_size', '-b', default=200, help="The number of docs to send per request. Max of 5000")
def main(source_dir: str, index_name: str, workers: int, host: str, max_docs: int, batch_size: int):
    batch_size = min(batch_size, 5000)
    logger.info(
        f"Indexing {source_dir} to {index_name} with {workers} workers to host {host} with a maximum number of docs sent per worker of {max_docs} and {batch_size} per request.")
    files = glob.glob(source_dir + "/*.xml")
    docs_indexed = 0
    # Set refresh interval to -1
    client = get_opensearch(host)
    refresh_settings = {
        'settings': {
            'index': {
                'refresh_interval': -1
            }
        }
    }

    client.indices.put_settings(index = index_name, body= refresh_settings)
    logger.info(client.indices.get_settings(index=index_name))
    start = perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(index_file, file, index_name, host, max_docs, batch_size) for file in files]
        for future in concurrent.futures.as_completed(futures):
            docs_indexed += future.result()
            if docs_indexed >= max_docs * workers:
                logger.info("Breaking out of file loop, as we've reached our limit of docs")
                break

    finish = perf_counter()
    logger.info(f'Done. Total docs: {docs_indexed} in {(finish - start) / 60} minutes')
    # set refresh interval back to 5s
    refresh_settings = {
        'settings': {
            'index': {
                'refresh_interval': "5s"
            }
        }
    }
    client.indices.put_settings(index = index_name, body= refresh_settings)
    logger.info(client.indices.get_settings(index=index_name))

if __name__ == "__main__":
    main()
