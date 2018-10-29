# Elasticsearch template. To be used only once.    .
curl -XPOST  'atlas-kibana.mwt2.org:9200/_template/stress' -d '{
    "order": 0,
    "index_patterns": "stress",
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },    
    "mappings": {
      "docs": {
        "properties": {
          "filename": {
            "type": "keyword"
          },
          "path": {
            "type": "keyword"
          },
          "filesize": {
            "type": "long"
          },
          "status": {
            "type": "keyword"
          },
          "timestamp": {
            "type": "date"
          },
          "updated_at": {
            "type": "date"
          },
          "origin": {
            "type": "keyword"
          },
          "rate": {
            "type": "float"
          }
        }
      }
    }
  }
}'
