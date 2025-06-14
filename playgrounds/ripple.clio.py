#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/clio"
# indexer = AthenahIndexer("local", "id", "dist", "clio", "v1")
# indexer.build_from_dirs(
#     path,
#     ["src", "docs"],
#     False,
# )

from athenah_ai.client import AthenahClient

prompt: str = """
```
#include <lmdb.h>
#include <string.h>
#include <time.h>
#include <stdio.h>

// Constants
#define DB_PATH "/path/to/lmdb"
#define MAX_DBS 10
#define MAX_KEY_SIZE 256

// LMDB environment and database
MDB_env *env;
MDB_dbi dbi;

// Initialize LMDB
int init_db() {
    int rc;
    rc = mdb_env_create(&env);
    if (rc != 0) return rc;
    
    rc = mdb_env_set_maxdbs(env, MAX_DBS);
    if (rc != 0) return rc;
    
    rc = mdb_env_open(env, DB_PATH, 0, 0664);
    if (rc != 0) return rc;
    
    MDB_txn *txn;
    rc = mdb_txn_begin(env, NULL, 0, &txn);
    if (rc != 0) return rc;
    
    rc = mdb_dbi_open(txn, "price_stats", MDB_CREATE, &dbi);
    if (rc != 0) {
        mdb_txn_abort(txn);
        return rc;
    }
    
    return mdb_txn_commit(txn);
}

// Update price bucket when a trade occurs
int update_price_stats(const char *token_id, double price, double volume, uint64_t timestamp) {
    int rc;
    MDB_txn *txn;
    
    // Start transaction
    rc = mdb_txn_begin(env, NULL, 0, &txn);
    if (rc != 0) return rc;
    
    // Update different time buckets
    rc = update_bucket(txn, token_id, "5min", price, volume, timestamp);
    if (rc != 0) {
        mdb_txn_abort(txn);
        return rc;
    }
    
    rc = update_bucket(txn, token_id, "1hour", price, volume, timestamp);
    if (rc != 0) {
        mdb_txn_abort(txn);
        return rc;
    }
    
    rc = update_bucket(txn, token_id, "day", price, volume, timestamp);
    if (rc != 0) {
        mdb_txn_abort(txn);
        return rc;
    }
    
    // Commit transaction
    return mdb_txn_commit(txn);
}

// Helper function to update a specific bucket
int update_bucket(MDB_txn *txn, const char *token_id, const char *bucket_type, 
                 double price, double volume, uint64_t timestamp) {
    
    // Calculate bucket start time
    uint64_t bucket_start;
    if (strcmp(bucket_type, "5min") == 0) {
        bucket_start = timestamp - (timestamp % 300);  // 5 minutes in seconds
    } else if (strcmp(bucket_type, "1hour") == 0) {
        bucket_start = timestamp - (timestamp % 3600); // 1 hour in seconds
    } else if (strcmp(bucket_type, "day") == 0) {
        bucket_start = timestamp - (timestamp % 86400); // 1 day in seconds
    } else {
        return -1; // Invalid bucket type
    }
    
    // Create key: token_id:bucket_type:timestamp
    char key[MAX_KEY_SIZE];
    snprintf(key, MAX_KEY_SIZE, "%s:%s:%lu", token_id, bucket_type, bucket_start);
    
    MDB_val db_key, db_value;
    db_key.mv_size = strlen(key);
    db_key.mv_data = key;
    
    price_bucket_t bucket;
    int rc = mdb_get(txn, dbi, &db_key, &db_value);
    
    if (rc == MDB_NOTFOUND) {
        // New bucket
        memset(&bucket, 0, sizeof(bucket));
        bucket.open_price = price;
        bucket.high_price = price;
        bucket.low_price = price;
        bucket.close_price = price;
        bucket.volume = volume;
        bucket.transaction_count = 1;
        bucket.last_update_timestamp = timestamp;
    } else if (rc == 0) {
        // Existing bucket
        memcpy(&bucket, db_value.mv_data, sizeof(bucket));
        
        // Update stats
        bucket.high_price = (price > bucket.high_price) ? price : bucket.high_price;
        bucket.low_price = (price < bucket.low_price) ? price : bucket.low_price;
        bucket.close_price = price;
        bucket.volume += volume;
        bucket.transaction_count++;
        bucket.last_update_timestamp = timestamp;
    } else {
        return rc; // Database error
    }
    
    // Store updated bucket
    db_value.mv_size = sizeof(bucket);
    db_value.mv_data = &bucket;
    
    return mdb_put(txn, dbi, &db_key, &db_value, 0);
}

// Get price change over a period
int get_price_change(const char *token_id, const char *bucket_type, 
                    uint64_t end_time, uint64_t periods, double *change) {
    
    int rc;
    MDB_txn *txn;
    
    // Start read transaction
    rc = mdb_txn_begin(env, NULL, MDB_RDONLY, &txn);
    if (rc != 0) return rc;
    
    // Calculate time period in seconds
    uint64_t period_seconds;
    if (strcmp(bucket_type, "5min") == 0) {
        period_seconds = 300;
    } else if (strcmp(bucket_type, "1hour") == 0) {
        period_seconds = 3600;
    } else if (strcmp(bucket_type, "day") == 0) {
        period_seconds = 86400;
    } else {
        mdb_txn_abort(txn);
        return -1; // Invalid bucket type
    }
    
    // Calculate current and past bucket start times
    uint64_t current_bucket = end_time - (end_time % period_seconds);
    uint64_t past_bucket = current_bucket - (period_seconds * periods);
    
    // Get current price
    char current_key[MAX_KEY_SIZE];
    snprintf(current_key, MAX_KEY_SIZE, "%s:%s:%lu", token_id, bucket_type, current_bucket);
    
    MDB_val db_key, db_value;
    db_key.mv_size = strlen(current_key);
    db_key.mv_data = current_key;
    
    rc = mdb_get(txn, dbi, &db_key, &db_value);
    if (rc != 0) {
        mdb_txn_abort(txn);
        return rc;
    }
    
    price_bucket_t current_bucket_data;
    memcpy(&current_bucket_data, db_value.mv_data, sizeof(price_bucket_t));
    
    // Get past price
    char past_key[MAX_KEY_SIZE];
    snprintf(past_key, MAX_KEY_SIZE, "%s:%s:%lu", token_id, bucket_type, past_bucket);
    
    db_key.mv_size = strlen(past_key);
    db_key.mv_data = past_key;
    
    rc = mdb_get(txn, dbi, &db_key, &db_value);
    if (rc != 0) {
        mdb_txn_abort(txn);
        return rc;
    }
    
    price_bucket_t past_bucket_data;
    memcpy(&past_bucket_data, db_value.mv_data, sizeof(price_bucket_t));
    
    // Calculate change
    *change = ((current_bucket_data.close_price - past_bucket_data.close_price) / 
               past_bucket_data.close_price) * 100.0;
    
    mdb_txn_abort(txn);
    return 0;
}

// Get 24h volume
int get_24h_volume(const char *token_id, double *volume) {
    int rc;
    MDB_txn *txn;
    
    // Start read transaction
    rc = mdb_txn_begin(env, NULL, MDB_RDONLY, &txn);
    if (rc != 0) return rc;
    
    // Calculate current time and 24h ago
    uint64_t current_time = time(NULL);
    uint64_t day_ago = current_time - 86400;
    
    // Use hourly buckets for more accurate results
    uint64_t current_hour = current_time - (current_time % 3600);
    uint64_t start_hour = day_ago - (day_ago % 3600);
    
    *volume = 0.0;
    
    // Sum up volumes for each hour
    for (uint64_t t = start_hour; t <= current_hour; t += 3600) {
        char key[MAX_KEY_SIZE];
        snprintf(key, MAX_KEY_SIZE, "%s:1hour:%lu", token_id, t);
        
        MDB_val db_key, db_value;
        db_key.mv_size = strlen(key);
        db_key.mv_data = key;
        
        rc = mdb_get(txn, dbi, &db_key, &db_value);
        if (rc == 0) {  // Skip if not found
            price_bucket_t bucket;
            memcpy(&bucket, db_value.mv_data, sizeof(bucket));
            *volume += bucket.volume;
        }
    }
    
    mdb_txn_abort(txn);
    return 0;
}
```

I was given the above idea to index some token data on the XRPL. This uses LMDB but I wanted to use clio for this. Can you create all the files required.

"""
client = AthenahClient("id", "dist", "clio")
response = client.promptv1(prompt)
print(response)
