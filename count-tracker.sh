# A simple loop that can be run to check on counts for our two indices as you are indexing.  Ctrl-c to get out.
usage()
{
  echo "Usage: $0 [-o hostname where OpenSearch is running. Default is localhost] "
  echo "Example: ./count-tracker.sh  -o opensearch-node1"
  exit 2
}
HOST="localhost"

while getopts ':o:h' c
do
  case $c in
    o) HOST=$OPTARG ;;
    h) usage ;;
    [?])
      echo "Invalid option: -${OPTARG}"
      usage ;;
  esac
done
shift $((OPTIND -1))


while [ true ];
do
  echo "Products:"
  curl -k -XGET -u admin:admin  "https://@$HOST:9200/_cat/count/bbuy_products";
  sleep 30;
done