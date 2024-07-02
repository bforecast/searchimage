docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest
@REM docker run -p 9200:9200  -e "discovery.type=single-node"  -e "xpack.security.enabled=false" -e "xpack.license.self_generated.type=trial" docker.elastic.co/elasticsearch/elasticsearch:8.13.2
