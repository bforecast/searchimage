@REM docker run --name neo4j --publish=7474:7474 --publish=7687:7687 --env NEO4J_PLUGINS=["gdc"] neo4j
docker run -p 7474:7474 -p 7687:7687 -v d:/neo4j/plugins:/plugins --name neo4j-apoc neo4j:5.20.0
@REM docker run -p 7474:7474 -p 7687:7687 --name neo4j-apoc --env NEO4J_AUTH=none neo4j
