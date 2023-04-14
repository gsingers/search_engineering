These are some helpful packages you may want to install in the OpenSearch containers.  We purposefully don't install them for you so that we don't have to ship and maintain a custom package for this class.

To begin, you'll need to attach to the running OpenSearch instance as root:

        docker exec -it --user root opensearch-node1 /bin/bash

 Now install the appropriate packages that you see fit.  Some that we did:
 
        yum install procps less