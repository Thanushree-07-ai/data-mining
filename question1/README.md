PS C:\Users\ub02-glab-019\data-mining\question1> docker compose up -d
[+] up 3/3
 ✔ Container q1-postgres Running                                                                                                                                   0.0s
 ✔ Container q1-minio    Running                                                                                                                                   0.0s
 ✔ Container q1-duckdb   Started                                                                                                                                   0.1s
PS C:\Users\ub02-glab-019\data-mining\question1> $env:MINIO_ENDPOINT="http://localhost:9000"
>> $env:DATA_DIR="$PWD\data"
>> $env:OUTPUT_DIR="$PWD\canonical"
>> py ingest\ingest.py
Starting Annapurna ingestion...
DATA_DIR = C:\Users\ub02-glab-019\data-mining\question1\data
Source files found: 4457
Processed 250/4457 files
Processed 500/4457 files
Processed 750/4457 files
Processed 1000/4457 files
Processed 1250/4457 files
Processed 1500/4457 files
Processed 1750/4457 files
Processed 2000/4457 files
Processed 2250/4457 files
Processed 2500/4457 files
Processed 2750/4457 files
Processed 3000/4457 files
Processed 3250/4457 files
Processed 3500/4457 files
Processed 3750/4457 files
Processed 4000/4457 files
Processed 4250/4457 files
Raw rows: 1,137,585
Rows after line-level deduplication: 1,120,924

========== INGESTION RESULT ==========
Raw rows:       1,137,585
Canonical rows: 1,120,924
Revenue:        522,865,735.75
Checksum:       554531d9a4d6cc1b0a3ef799b59f4a34329672f8d1b12988d1d82c4bc0607840
Output:         C:\Users\ub02-glab-019\data-mining\question1\canonical
=======================================
Uploaded 145 objects to s3://annapurna/canonical/
PS C:\Users\ub02-glab-019\data-mining\question1> 