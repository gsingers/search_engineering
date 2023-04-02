# Welcome to Search Engineering

Search Engineering is a four week class taught by [Grant Ingersoll](https://www.linkedin.com/in/grantingersoll/) and [Dave Anderson](https://www.linkedin.com/in/daveandersonncsu/) and is focused on helping students
quickly get up to speed on search best practices related to performance, scaling, fault tolerance, backups and recovery.  

Students will first learn about common search architecture and data modeling practices, then work on optimizing a single node of search, before scaling out to a multi-node cluster. Finally, students will look into key factors in creating a reliable search 
system like security, monitoring and backup/recovery. 

The class is a hands-on project-driven course where students will work with real data and the [Opensearch](https://opensearch.com)/Elasticsearch ecosystem.

# Class code layout (e.g. where the projects are)

For our class, we have four weekly projects.  Each project
is a standalone Python application that interacts with an OpenSearch server (and perhaps other services).  

You will find these four projects in the directories below them organized in the following way:

- Week 1:
    - week1 -- The unfinished template for the week's project, annotated with instructions.
- Week 2:
    - week2 -- The unfinished template for the week's project, annotated with instructions.
- Week 3 and 4: you get the picture

Our instructor annotated results for each project will be provided during the class.  Please note, these represent our way of doing the assignment and may differ from your results, as there is often more than one way of doing things in search.

You will also find several supporting directories and files for Docker and Gitpod.

# Prerequisites

1. You will need a [Gitpod](https://gitpod.io) account or the ability to run [Docker](https://docker.com) containers.
   1. If running locally, you will want at least 16GB of RAM and 30GB of disk space, with more being better!
2. For this class, you will need a Kaggle account and a [Kaggle API token](https://www.kaggle.com/docs/api).

# Downloading the Best Buy Dataset

1. Run the install [Kaggle API token](https://www.kaggle.com/docs/api) script and follow the instructions:

        ./install-kaggle-token.sh
2. Accept *both* the overall Kaggle terms (if you've just setup a new Kaggle account) *and* the [kaggle competition rules](https://www.kaggle.com/c/acm-sf-chapter-hackathon-big/rules) for this specific dataset.  If not, you'll get `403 - Forbidden` in the next step.
3. Run the download data script:

        ./download-data.sh


# Working Locally (Officially Supported)

To run locally or in your own cloud instance using Docker, you will need a few things:

1. [Docker](https://docker.com/) and the ability to pull from Docker Hub.
1. A [Git](https://git-scm.com/) client
2. [cURL](https://curl.se/) and [wget](https://www.gnu.org/software/wget/)
                                                                         

NOTE: If you are on a Mac, you will probably want to enable the `VirtioFS` option for I/O.  Even with that on, file I/O performance is not great. YMMV.

Our basic setup will be to run the Gitpod dockerfile (published as `gsingers/search_engineering` on Docker Hub, with the appropriate networking and volume mounts to provide a standard dev environment
while also allowing for local file editing.

1. Create a "parent" directory somewhere on your local filesystem, such as `~/projects/corise/search_engineering` and change into that directory
   2. Git clone this repository underneath that directory
   3. `mkdir datasets` 
2. You can proceed as required by the project with downloading the data, etc. 
3. (Optional) Run docker by attaching volumes for the repo and the dataset: 
   3. Interactive: `docker run -v <PATH TO WHERE YOU CLONED THIS REPO>:/workspace/search_engineering -v ~/projects/corise/search_engineering/datasets:/workspace/datasets --network docker_opensearch-net --name search_engineering -it gsingers/search_engineering:latest`
   4. You can also run natively, but our ability to support you will be limited.  If you do, please see the `.gitpod.Dockerfile` for system requirements, Python versions, etc.
5. If you are running locally, be sure to `pip install` the `requirements.txt` file located in the root directory into a virtual environment running Python 3.9.7.  Again, see `.gitpod.Dockerfile` if you are not sure.
   



# Working in Gitpod (Officially Supported)

*NOTE*: The Gitpod free tier comes with 50 hours of use per month.  We expect our work will be done in less time than that.  However, you may wish to conserve time on the platform by being sure to stop your workspace when you are done with it.  Gitpod will time you out (don't worry, your work will be saved), but that may take longer to detect.
*NOTE*: Gitpod is not optimal for things like scaling out a search cluster.  We will note in the content when this is the case, even though it should still work.

The following things must be done each time you create a new Gitpod Workspace (unfortunately, we can't automate this)

1. Fork this repository.
1. Launch a new Gitpod workspace based on this repository.  



# Starting OpenSearch
                     

1. `cd /workspace/search_engineering/docker`
2. Start the OpenSearch instance associated with the week you are working on, e.g.:
   2. `docker-compose -f docker-compose-w1.yml up`
1. You should now have a running Opensearch instance (port 9200) and a running Opensearch Dashboards instance (port 5601)
1. Login to the dashboards at `https://5601-<$GITPOD_URL>/` or `https://localhost:5601` (if running locally) with default username `admin` and password `admin`. This should popup automatically as a new tab, unless you have blocked popups.  Also note, that in the real world, you would change your password.  Since these ports are blocked if you aren't logged into Gitpod, it's OK.

        $GITPOD_URL is a placeholder for your ephemeral Gitpod host name, e.g. silver-grasshopper-8czadqyn.ws-us25.gitpod.io




# Exploring the OpenSearch Sample Dashboards and Data

1. Login to OpenSearch and point your browser at `https://5601-<$GITPOD_URL>/app/opensearch_dashboards_overview#/` (or `https://localhost:5601`)
1. Click the "Add sample data" link
1. Click the "Add Data" link for any of the 3 projects listed. In the class, we chose the "Sample flight data", but any of the three are fine for exploration.



# Indexing the Best Buy Data

After you have installed your Kaggle token and downloaded the data, it's time to index it.  Complete the following steps from the command line:

1. Gitpod Install:
   2. `pyenv activate search_eng` 
   2. `./index-data.sh`
2. Local Install:
   3. `./index-data.sh -o opensearch-node1`


# Running the Weekly Project

At the command line, do the following steps to run the example.  

1. Activate your Python Virtual Environment.  We use `pyenv` (Pyenv website)[https://github.com/pyenv/pyenv] and `pyenv-virtualenv` (Pyenv Virtualenv)[https://github.com/pyenv/pyenv-virtualenv].
    1. `pyenv activate search_eng` -- Activate the Virtualenv. 
1. Optional: You can run `ipython` if you like.
