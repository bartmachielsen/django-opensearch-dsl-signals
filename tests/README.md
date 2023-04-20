# Django Opensearch DSL Signals Tests


## Getting started
Start opensearch container: 
```.bash
docker run -p 9200:9200 -p 9600:9600 -e "discovery.type=single-node" -d opensearchproject/opensearch:latest
```