# WARNING: this will silently delete both of your indexes
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

echo "Deleting Products"
set -x
curl -k -X DELETE -u admin  "https://$HOST:9200/bbuy_products"
if [ $? -ne 0 ] ; then
  echo "Failed to delete products index"
  exit 2
fi
