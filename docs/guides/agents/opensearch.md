# OpenSearch Agent Guide

The OpenSearch agents provide powerful search and analytics capabilities for log data, security events, and observability metrics with semantic understanding of your data patterns.

## Overview

- **OpenSearchAgent** - AI-powered natural language to OpenSearch DSL queries
- **OpenSearchPassthroughAgent** - Direct query DSL execution without AI interpretation

## OpenSearchAgent (AI-Assisted)

The OpenSearchAgent understands:
- OpenSearch query DSL and aggregations
- Log patterns and security event schemas
- Time-based data analysis
- Index patterns and mappings

### Basic Usage

```python
from louieai.notebook import lui

# Simple log queries
lui("Show me all error logs from the API service today", agent="OpenSearchAgent")

# Security analysis
lui("Find failed authentication attempts in the last hour", agent="OpenSearchAgent")

# Performance monitoring
lui("What are the slowest API endpoints this week?", agent="OpenSearchAgent")
```

### Security Analytics

```python
# Threat detection
lui("""
Identify potential security threats by analyzing
authentication patterns and network anomalies
""", agent="OpenSearchAgent")

# Incident investigation
lui("""
Trace all activities from IP address 192.168.1.100
across all security indices for the last 24 hours
""", agent="OpenSearchAgent")

# Compliance monitoring
lui("""
Find all access attempts to sensitive data endpoints
and verify they comply with our access policies
""", agent="OpenSearchAgent")
```

### Log Analysis

```python
# Error pattern analysis
lui("""
Analyze application error patterns and group
similar errors together with their frequency
""", agent="OpenSearchAgent")

# Distributed tracing
lui("""
Trace a request through all microservices using
the correlation ID and show the complete flow
""", agent="OpenSearchAgent")

# Performance analysis
lui("""
Calculate p50, p95, and p99 response times
for each API endpoint over the last week
""", agent="OpenSearchAgent")
```

### Observability & Monitoring

```python
# Service health monitoring
lui("""
Show the health status of all services including
error rates, response times, and availability
""", agent="OpenSearchAgent")

# Resource utilization
lui("""
Analyze CPU and memory usage patterns across
our Kubernetes clusters to identify bottlenecks
""", agent="OpenSearchAgent")

# Alert correlation
lui("""
Correlate alerts from the last incident to
understand the root cause and impact
""", agent="OpenSearchAgent")
```

## OpenSearchPassthroughAgent (Direct Query DSL)

For direct OpenSearch query DSL execution:

### Basic Queries

```python
# Direct query DSL
lui("""
{
  "query": {
    "bool": {
      "must": [
        {"match": {"level": "ERROR"}},
        {"range": {"@timestamp": {"gte": "now-1h"}}}
      ],
      "filter": [
        {"term": {"service.name": "api-gateway"}}
      ]
    }
  },
  "aggs": {
    "errors_over_time": {
      "date_histogram": {
        "field": "@timestamp",
        "fixed_interval": "5m"
      },
      "aggs": {
        "by_error_type": {
          "terms": {
            "field": "error.type",
            "size": 10
          }
        }
      }
    }
  },
  "size": 100
}
""", agent="OpenSearchPassthroughAgent")
```

### Advanced Aggregations

```python
# Complex analytics with pipeline aggregations
lui("""
{
  "query": {
    "range": {
      "@timestamp": {
        "gte": "now-7d"
      }
    }
  },
  "aggs": {
    "daily_stats": {
      "date_histogram": {
        "field": "@timestamp",
        "calendar_interval": "day"
      },
      "aggs": {
        "total_requests": {
          "value_count": {
            "field": "request.id"
          }
        },
        "error_count": {
          "filter": {
            "term": {"response.status_code": 500}
          }
        },
        "error_rate": {
          "bucket_script": {
            "buckets_path": {
              "errors": "error_count._count",
              "total": "total_requests"
            },
            "script": "params.errors / params.total * 100"
          }
        },
        "response_time_percentiles": {
          "percentiles": {
            "field": "response.duration_ms",
            "percents": [50, 95, 99]
          }
        }
      }
    },
    "avg_error_rate": {
      "avg_bucket": {
        "buckets_path": "daily_stats>error_rate"
      }
    }
  }
}
""", agent="OpenSearchPassthroughAgent")
```

### Security Event Queries

```python
# Advanced security analytics
lui("""
{
  "query": {
    "bool": {
      "should": [
        {
          "bool": {
            "must": [
              {"term": {"event.category": "authentication"}},
              {"term": {"event.outcome": "failure"}},
              {"range": {"event.count": {"gte": 5}}}
            ]
          }
        },
        {
          "bool": {
            "must": [
              {"term": {"event.category": "network"}},
              {"range": {"network.bytes": {"gte": 1000000000}}}
            ]
          }
        }
      ],
      "minimum_should_match": 1,
      "filter": [
        {"range": {"@timestamp": {"gte": "now-1h"}}}
      ]
    }
  },
  "aggs": {
    "suspicious_ips": {
      "terms": {
        "field": "source.ip",
        "size": 20,
        "order": {"threat_score": "desc"}
      },
      "aggs": {
        "threat_score": {
          "scripted_metric": {
            "init_script": "state.events = []",
            "map_script": "state.events.add(['category': doc['event.category'].value, 'outcome': doc['event.outcome'].value])",
            "combine_script": "return state.events",
            "reduce_script": """
              int score = 0;
              for (state in states) {
                for (event in state) {
                  if (event.category == 'authentication' && event.outcome == 'failure') score += 10;
                  if (event.category == 'network') score += 5;
                }
              }
              return score;
            """
          }
        }
      }
    }
  }
}
""", agent="OpenSearchPassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use OpenSearchAgent when:**
- You want to describe searches in natural language
- You need help constructing complex queries
- You want automatic time range selection
- You're exploring log patterns

**Use OpenSearchPassthroughAgent when:**
- You have exact query DSL to execute
- You need specific aggregation pipelines
- You want precise control over scoring
- You're using advanced features like scripts

### Index Management

```python
# AI suggests index strategies
lui("""
Analyze our log volume and suggest an optimal
index rotation and retention strategy
""", agent="OpenSearchAgent")

# Direct index template
lui("""
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.lifecycle.name": "logs-lifecycle-policy",
      "index.lifecycle.rollover_alias": "logs-current"
    },
    "mappings": {
      "properties": {
        "@timestamp": {"type": "date"},
        "message": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "level": {"type": "keyword"},
        "service.name": {"type": "keyword"},
        "trace.id": {"type": "keyword"},
        "response.duration_ms": {"type": "float"}
      }
    }
  }
}
""", agent="OpenSearchPassthroughAgent")
```

### Performance Optimization

```python
# AI optimizes queries
lui("""
Optimize this security monitoring query to run
faster across our large dataset
""", agent="OpenSearchAgent")

# Direct optimization with filters
lui("""
{
  "query": {
    "bool": {
      "filter": [
        {"range": {"@timestamp": {"gte": "now-1h", "lte": "now"}}},
        {"terms": {"security.risk_score": [8, 9, 10]}}
      ],
      "must": [
        {"match": {"event.action": "login-failed"}}
      ]
    }
  },
  "aggs": {
    "high_risk_users": {
      "terms": {
        "field": "user.name",
        "size": 100,
        "min_doc_count": 5
      }
    }
  },
  "_source": false,
  "size": 0
}
""", agent="OpenSearchPassthroughAgent")
```

## Common Patterns

### Alerting Rules

```python
# AI creates alert conditions
lui("""
Create an alert for detecting brute force attacks
based on failed login patterns
""", agent="OpenSearchAgent")

# Direct monitor query
lui("""
{
  "query": {
    "bool": {
      "filter": [
        {"range": {"@timestamp": {"gte": "now-5m"}}},
        {"term": {"event.action": "authentication_failed"}}
      ]
    }
  },
  "aggs": {
    "by_user": {
      "terms": {
        "field": "user.name",
        "min_doc_count": 10,
        "size": 50
      },
      "aggs": {
        "unique_ips": {
          "cardinality": {
            "field": "source.ip"
          }
        }
      }
    }
  }
}
""", agent="OpenSearchPassthroughAgent")
```

### Correlation Analysis

```python
# AI performs correlation
lui("""
Correlate application errors with infrastructure
metrics to identify root causes
""", agent="OpenSearchAgent")

# Direct correlation query
lui("""
{
  "query": {
    "bool": {
      "should": [
        {
          "bool": {
            "must": [
              {"exists": {"field": "error.message"}},
              {"range": {"@timestamp": {"gte": "now-30m"}}}
            ]
          }
        },
        {
          "bool": {
            "must": [
              {"range": {"system.cpu.usage": {"gte": 0.9}}},
              {"range": {"@timestamp": {"gte": "now-30m"}}}
            ]
          }
        }
      ]
    }
  },
  "aggs": {
    "time_correlation": {
      "date_histogram": {
        "field": "@timestamp",
        "fixed_interval": "1m"
      },
      "aggs": {
        "error_count": {
          "filter": {"exists": {"field": "error.message"}}
        },
        "high_cpu_count": {
          "filter": {"range": {"system.cpu.usage": {"gte": 0.9}}}
        }
      }
    }
  }
}
""", agent="OpenSearchPassthroughAgent")
```

### Anomaly Detection

```python
# AI detects anomalies
lui("""
Find anomalous patterns in user behavior that
might indicate compromised accounts
""", agent="OpenSearchAgent")

# Direct anomaly detection
lui("""
{
  "query": {
    "function_score": {
      "query": {
        "range": {"@timestamp": {"gte": "now-24h"}}
      },
      "functions": [
        {
          "script_score": {
            "script": {
              "source": """
                // Anomaly scoring based on multiple factors
                double score = 0;
                
                // Unusual time
                int hour = doc['@timestamp'].value.getHour();
                if (hour < 6 || hour > 22) score += 20;
                
                // Unusual location
                if (doc['geo.country_iso_code'].size() > 0 && 
                    !doc['geo.country_iso_code'].value.equals('US')) {
                  score += 30;
                }
                
                // High data transfer
                if (doc['network.bytes'].size() > 0 && 
                    doc['network.bytes'].value > 1000000) {
                  score += 25;
                }
                
                return score;
              """
            }
          }
        }
      ],
      "score_mode": "sum",
      "min_score": 50
    }
  },
  "sort": ["_score"],
  "size": 100
}
""", agent="OpenSearchPassthroughAgent")
```

## Integration with Other Agents

```python
# Search logs with OpenSearch
lui("Find all database errors from the last hour", agent="OpenSearchAgent")
error_logs = lui.df

# Analyze patterns
lui("What patterns do you see in these database errors?", agent="LouieAgent")

# Generate monitoring code
lui("Create Python code to automatically categorize these errors", agent="CodeAgent")

# Create visualization
lui("Generate a dashboard showing error trends over time", agent="PerspectiveAgent")
```

## OpenSearch-Specific Features

### Index Lifecycle Management

```python
# AI configures ILM
lui("""
Set up index lifecycle management for our logs
with hot-warm-cold architecture
""", agent="OpenSearchAgent")

# Direct ILM policy
lui("""
{
  "policy": {
    "description": "Logs lifecycle policy",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [
          {
            "rollover": {
              "min_size": "50gb",
              "min_age": "1d"
            }
          }
        ],
        "transitions": [
          {
            "state_name": "warm",
            "conditions": {
              "min_age": "7d"
            }
          }
        ]
      },
      {
        "name": "warm",
        "actions": [
          {
            "replica_count": {
              "number_of_replicas": 1
            }
          },
          {
            "shrink": {
              "number_of_shards": 1
            }
          }
        ],
        "transitions": [
          {
            "state_name": "cold",
            "conditions": {
              "min_age": "30d"
            }
          }
        ]
      },
      {
        "name": "cold",
        "actions": [
          {
            "snapshot": {
              "repository": "logs-backup"
            }
          }
        ],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_age": "90d"
            }
          }
        ]
      }
    ]
  }
}
""", agent="OpenSearchPassthroughAgent")
```

### Machine Learning

```python
# AI creates ML job
lui("""
Set up anomaly detection for unusual spike in
error rates using OpenSearch ML
""", agent="OpenSearchAgent")

# Direct ML detector
lui("""
{
  "name": "error-rate-anomaly-detector",
  "description": "Detect anomalous error rates",
  "time_field": "@timestamp",
  "indices": ["logs-*"],
  "feature_attributes": [
    {
      "feature_name": "error_rate",
      "feature_enabled": true,
      "aggregation_query": {
        "error_rate_agg": {
          "filter": {
            "term": {"level": "ERROR"}
          },
          "aggs": {
            "error_count": {
              "value_count": {
                "field": "message"
              }
            }
          }
        }
      }
    }
  ],
  "detection_interval": {
    "period": {
      "interval": 5,
      "unit": "Minutes"
    }
  },
  "window_delay": {
    "period": {
      "interval": 1,
      "unit": "Minutes"
    }
  }
}
""", agent="OpenSearchPassthroughAgent")
```

## Next Steps

- Learn about [Splunk Agent](splunk.md) for SPL queries
- Explore [Kusto Agent](kusto.md) for Azure Data Explorer
- See [Perspective Agent](perspective.md) for data visualization
- Check the [Query Patterns Guide](../query-patterns.md) for more examples