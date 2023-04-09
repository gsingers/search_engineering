# These are some helpful packages you may want to install in the OpenSearch containers.

To begin, you'll need to attach to the running OpenSearch instance as root:

        docker exec -it --user root opensearch-node1 /bin/bash

 Now install the appropriate packages that you see fit.  Some that we did:
 
        yum install procps less