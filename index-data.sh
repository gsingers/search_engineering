usage()
{
  echo "Usage: $0 [-y /path/to/python/indexing/code] [-k week number, as in week1] [-b batch size of number of docs to send in one request.]  [-o hostname where OpenSearch is running. Default is localhost] [-m max docs PER WORKER. Default: 2000000] [-w number of threads. Default: 8] [-d /path/to/kaggle/best/buy/datasets] [-p /path/to/bbuy/products/field/mappings] [ -g /path/to/write/logs/to ]"
  echo "Example: ./index-data.sh  -y /Users/grantingersoll/projects/corise/search_engineering/src/main/python/search_eng/week1_finished   -d /Users/grantingersoll/projects/corise/datasets/bbuy  -p /Users/grantingersoll/projects/corise/search_engineering/src/main/conf/bbuy_products.json -g /tmp"
  exit 2
}

CURRENT_DIR=$(cd "$(dirname "$0")/."; pwd)

DATASETS_DIR="$CURRENT_DIR/downloads"
WEEK="$CURRENT_DIR/week1" #Default indexing is in utilities
PRODUCTS_JSON_FILE="$WEEK/bbuy_products.json"
HOST="localhost"
INDEX_NAME="bbuy_products"
LOGS_DIR="$CURRENT_DIR/logs"
WORKERS=8
MAX_DOCS=2000000
BATCH_SIZE=200
REFRESH_INTERVAL=-1

while getopts ':p:b:k:i:o:g:d:m:w:h' c
do
  case $c in
    b) BATCH_SIZE=$OPTARG ;;
    d) DATASETS_DIR=$OPTARG ;;
    g) LOGS_DIR=$OPTARG ;;
    k) WEEK=$OPTARG ;;
    i) INDEX_NAME=$OPTARG ;;
    m) MAX_DOCS=$OPTARG ;;
    o) HOST=$OPTARG ;;
    p) PRODUCTS_JSON_FILE=$OPTARG ;;
    r) REFRESH_INTERVAL=$OPTARG ;;
    w) WORKERS=$OPTARG ;;
    h) usage ;;
    [?])
      echo "Invalid option: -${OPTARG}"
      usage ;;
  esac
done

shift $((OPTIND -1))

mkdir -p $LOGS_DIR

set -x

cd $WEEK

for refresh in "-1" "1s" "60s"; do
  echo "Deleting Products"
  curl -sk -X DELETE -u admin:admin https://localhost:9200/bbuy_products

  echo "Creating index settings and mappings"
  if [ -f $PRODUCTS_JSON_FILE ]; then
    echo " Product file: $PRODUCTS_JSON_FILE"
    curl -k -X PUT -u admin:admin  "https://$HOST:9200/$INDEX_NAME" -H 'Content-Type: application/json' -d "@$PRODUCTS_JSON_FILE"
    if [ $? -ne 0 ] ; then
      echo "Failed to create index with settings of $PRODUCTS_JSON_FILE"
      exit 2
    fi

    if [ -f index.py ]; then
      echo "Indexing product data in $DATASETS_DIR/product_data/products and writing logs to $LOGS_DIR/index.log"
      python index.py -w $WORKERS -r "$refresh" -m $MAX_DOCS -b $BATCH_SIZE -s "$DATASETS_DIR/product_data/products" -o "$HOST" -i "$INDEX_NAME" >> "$LOGS_DIR/index.log" &
      wait
      if [ $? -ne 0 ] ; then
        echo "Failed to index products"
        exit 2
      fi
    fi
  fi
done
