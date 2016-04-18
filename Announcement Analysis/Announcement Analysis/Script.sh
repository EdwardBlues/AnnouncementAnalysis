#!/bin/bash

set -x

# Create a index called stock
# curl -XPUT 'localhost:9200/stock?pretty'; echo

# Create a index called stock and then set stock index mapping
curl -XPUT 'localhost:9200/stock?pretty' -d '{
	"mappings": {
		"announcements": {
			"properties": {
				"time": {
					"type": "date"
				},
				"code": {
					"type": "string",
					"index": "not_analyzed"
				},
				"title": {
					"type": "string",
					"analyzer": "ik_max_word"
				},
				"url": {
					"type": "string",
					"index": "not_analyzed"
				}
			}
		}
	},
	"settings": {
	}
}'; echo

# Insert a sample with id=1
curl -XPOST 'localhost:9200/stock/announcements/1?pretty' -d '{
	"time": "2016-01-22",
	"code": "002240",
	"title": "关于召开2016年第二次（临时）股东大会的通知",
	"url": "www.cninfo.com.cn/cninfo-new/disclosure/szse/bulletin_detail/true/1201932814?announceTime=2016-01-22"
}'; echo

# Check term vector
curl -XGET 'localhost:9200/stock/announcements/1/_termvectors?pretty' -d '{
  "fields" : ["title"],
  "offsets" : true,
  "payloads" : true,
  "positions" : true,
  "term_statistics" : true,
  "field_statistics" : true
}'; echo

# Elasticsearch is a near real time search platform.
# It means there is a slight latency (normally one second) from the time index a document until the time it becomes searchable.
sleep 1.5

# Search
curl -XPOST 'localhost:9200/stock/_search?pretty' -d '{
	"query" : {
		"match": {
			"title": "股东大会"
		}
	},
	"highlight": {
		"fields": {
			"title": {}
		}
	}
}'; echo

# Delete index
# curl -XDELETE 'localhost:9200/stock?pretty'