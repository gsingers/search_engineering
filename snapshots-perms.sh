docker exec -it --user root opensearch-node1 /bin/bash -c  "chown opensearch snapshots; chgrp opensearch snapshots"
docker exec -it --user root opensearch-node2 /bin/bash -c  "chown opensearch snapshots; chgrp opensearch snapshots"
docker exec -it --user root opensearch-node2 /bin/bash -c  "ls -l"