usage()
{
  echo "Usage: $0 [-y /path/to/python/indexing/code] [-b batch size of number of docs to send in one request.]  [-o hostname where OpenSearch is running. Default is localhost] [-m max docs PER WORKER. Default: 2000000] [-w number of threads. Default: 8] [-d /path/to/kaggle/best/buy/datasets] [-p /path/to/bbuy/products/field/mappings] [ -g /path/to/write/logs/to ]"
  echo "Example: ./index-data.sh  -y /Users/grantingersoll/projects/corise/search_engineering/src/main/python/search_eng/week1_finished   -d /Users/grantingersoll/projects/corise/datasets/bbuy  -p /Users/grantingersoll/projects/corise/search_engineering/src/main/conf/bbuy_products.json -g /tmp"
  exit 2
}

PRODUCTS_JSON_FILE="/workspace/search_engineering/conf/bbuy_products.json"
DATASETS_DIR="/workspace/datasets"
PYTHON_LOC="/workspace/search_engineering/utilities"
HOST="localhost"
LOGS_DIR="/workspace/logs"
WORKERS=8
MAX_DOCS=2000000
BATCH_SIZE=200
while getopts ':p:b:o:g:y:d:m:w:h' c
do
  case $c in
    b) BATCH_SIZE=$OPTARG ;;
    d) DATASETS_DIR=$OPTARG ;;
    g) LOGS_DIR=$OPTARG ;;
    m) MAX_DOCS=$OPTARG ;;
    o) HOST=$OPTARG ;;
    p) PRODUCTS_JSON_FILE=$OPTARG ;;
    w) WORKERS=$OPTARG ;;
    y) PYTHON_LOC=$OPTARG ;;
    h) usage ;;
    [?])
      echo "Invalid option: -${OPTARG}"
      usage ;;
  esac
done
shift $((OPTIND -1))

mkdir $LOGS_DIR

cd $PYTHON_LOC || exit
echo "Running python scripts from $PYTHON_LOC"

#eval "$(pyenv init -)"
#eval "$(pyenv virtualenv-init -)"
set -x

#pyenv activate search_eng
echo "Creating index settings and mappings"
if [ -f $PRODUCTS_JSON_FILE ]; then
  echo " Product file: $PRODUCTS_JSON_FILE"
  curl -k -X PUT -u admin  "https://$HOST:9200/bbuy_products" -H 'Content-Type: application/json' -d "@$PRODUCTS_JSON_FILE"
  if [ $? -ne 0 ] ; then
    echo "Failed to create index with settings of $PRODUCTS_JSON_FILE"
    exit 2
  fi

  if [ -f index.py ]; then
    echo "Indexing product data in $DATASETS_DIR/product_data/products and writing logs to $LOGS_DIR/index.log"
    nohup python index.py -w $WORKERS -m $MAX_DOCS -b $BATCH_SIZE -s "$DATASETS_DIR/product_data/products" -o "$HOST" > "$LOGS_DIR/index.log" &
    if [ $? -ne 0 ] ; then
      echo "Failed to index products"
      exit 2
    fi
  fi
fi