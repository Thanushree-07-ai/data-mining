
setubid=# \copy notices FROM '/tmp/notices_load.csv' WITH (FORMAT csv, HEADER true);
COPY 12000
setubid=# \copy lsh_buckets FROM '/tmp/lsh_buckets_load.csv' WITH (FORMAT csv, HEADER true);
COPY 384000
setubid=# ANALYZE notices;
ANALYZE lsh_buckets;
ANALYZE
ANALYZE
setubid=# SELECT COUNT(*) FROM notices;
 count 
-------
 12000
(1 row)

setubid=# SELECT COUNT(*) FROM lsh_buckets;
 count  
--------
 384000
(1 row)





setubid=# SELECT band, bucket, COUNT(*) AS bucket_size
FROM lsh_buckets
GROUP BY band, bucket
ORDER BY bucket_size DESC
LIMIT 1;
 band |                  bucket                  | bucket_size 
------+------------------------------------------+-------------
   17 | 657e9c468c85cb31e9b8d23accedb4b076f1615d |        3421
(1 row)



setubid=# EXPLAIN (ANALYZE, BUFFERS)
SELECT notice_id
FROM lsh_buckets
WHERE band = 17
  AND bucket = '657e9c468c85cb31e9b8d23accedb4b076f1615d';
                                                               QUERY PLAN                                                                
-----------------------------------------------------------------------------------------------------------------------------------------
 Index Only Scan using lsh_buckets_pkey on lsh_buckets  (cost=0.42..14.84 rows=121 width=8) (actual time=0.031..0.387 rows=3421 loops=1)
   Index Cond: ((band = 17) AND (bucket = '657e9c468c85cb31e9b8d23accedb4b076f1615d'::text))
   Heap Fetches: 0
   Buffers: shared hit=46
 Planning:
   Buffers: shared hit=3
 Planning Time: 0.108 ms
 Execution Time: 0.509 ms
(8 rows)




setubid=# SET enable_indexscan = off;
SET
setubid=# SET enable_bitmapscan = off;
SET
setubid=# EXPLAIN (ANALYZE, BUFFERS)
SELECT notice_id
FROM lsh_buckets
WHERE band = 17
  AND bucket = '657e9c468c85cb31e9b8d23accedb4b076f1615d';
                                                        QUERY PLAN                                                         
---------------------------------------------------------------------------------------------------------------------------
 Gather  (cost=1000.00..7404.10 rows=121 width=8) (actual time=0.593..7.489 rows=3421 loops=1)
   Workers Planned: 2
   Workers Launched: 2
   Buffers: shared hit=3992
   ->  Parallel Seq Scan on lsh_buckets  (cost=0.00..6392.00 rows=50 width=8) (actual time=2.669..4.362 rows=1140 loops=3)
         Filter: ((band = 17) AND (bucket = '657e9c468c85cb31e9b8d23accedb4b076f1615d'::text))
         Rows Removed by Filter: 126860
         Buffers: shared hit=3992
 Planning Time: 0.103 ms
 Execution Time: 7.607 ms
(10 rows)

setubid=# RESET enable_indexscan;
RESET
setubid=# RESET enable_indexscan;
RESET


section e 
S C:\Users\ub02-glab-019\data-mining\question2> py .\scripts\section_e.py
======================================================================
SECTION E - CORPUS SKEW AND MITIGATION
======================================================================
Notices: 12000
Labelled pairs: 900

Building BASELINE representation...

BASELINE
num_buckets: 210099
mean: 1.8277097939542788
median: 1.0
p95: 4.0
p99: 9.0
max: 954
Runtime: 19.495 sec

Building MITIGATED representation...

MITIGATED
num_buckets: 71278
mean: 5.387356547602346
median: 1.0
p95: 13.0
p99: 74.0
max: 2593
Runtime: 21.264 sec

LABELLED-PAIR RETRIEVAL QUALITY
Baseline candidate survival:  0.3700
Mitigated candidate survival: 0.5722

Saved:
results/section_e_before_after.csv
Saved:
results/section_e_bucket_distribution.png

======================================================================
SECTION E COMPLETE
======================================================================
PS C:\Users\ub02-glab-019\data-mining\question2> 






========== SECTION A ==========

Mean similarity by label:
           unigram_similarity  trigram_similarity
label                                            
different            0.570897            0.383806
same                 0.734429            0.653410

Example SAME pair:
notice_id_a notice_id_b  unigram_similarity  trigram_similarity
    N010018     N010020            0.364162            0.278125

Example DIFFERENT pair:
notice_id_a notice_id_b  unigram_similarity  trigram_similarity
    N007876     N008565            0.541152            0.287234

ADOPTED CHOICE:
Word 3-grams.

Signal:
substantive tender wording, scope, eligibility and work description.

Noise:
portal boilerplate, reference numbers, dates, monetary formatting,
emails, phone numbers and standalone identifiers.

Similarity:
Jaccard similarity = intersection / union.




========== SECTION B ==========
MinHash size: 128
Signature creation time: 2.492 seconds
Mean absolute error: 0.02753
95th percentile error: 0.073662
Maximum error: 0.118946

APPLICATION REQUIREMENT:
Mean absolute estimation error <= 0.05
and 95th percentile error <= 0.10.

ADOPTED:
128 MinHash values.

The realised error above is measured against the trusted labelled
pairs rather than assumed from a tutorial.


========== FULL CORPUS SIGNATURES ==========
Processed: 1000
Processed: 2000
Processed: 3000
Processed: 4000
Processed: 5000
Processed: 6000
Processed: 7000
Processed: 8000
Processed: 9000
Processed: 10000
Processed: 11000
Processed: 12000
Full signature construction time: 17.767 seconds


========== SECTION C ==========
Bands: 32
Rows per band: 4
Candidate recall: 0.645556
Average candidate count: 4623.19
Median candidate count: 4616
Maximum candidate count: 8767
Curve saved: C:\Users\ub02-glab-019\data-mining\question2\results\candidate_recall_curve.png

========== SECTION E ==========
Number of buckets: 67869
Mean bucket size: 5.66
Median bucket size: 1
P95 bucket size: 13.0
P99 bucket size: 68.32
Maximum bucket size: 3421

Top 10 buckets:
(17, '657e9c468c85cb31e9b8d23accedb4b076f1615d', 3421)
(3, '758b1d56e13682754f5bff63a98dc270601851c8', 2871)
(11, '4d5fee0e612e1fde7cb6ee27b23800952b47e2ac', 2611)
(30, '0987aebf1ea6b180fc56bd1af0f153bd115a4b80', 2481)
(6, '40a2afbd23a452b16370288abc2ed730392b973a', 2148)
(21, 'e4962c8948d41685d6f00b00b74c5a64a14981bf', 2033)
(15, 'a1d12868c17ae44287a1be38aded2394fc15cc44', 1914)
(9, 'c665d994787e8544510f3ca7eee4e7c4b5560806', 1867)
(7, '0e3b1a294919ffdd57e55d2b3318eac67c542116', 1757)
(20, '0db212071835cd2a57885d05c47be8c0ac2e8e9c', 1674)



COPY 12000
COPY 384000

SELECT COUNT(*) FROM notices;
12000

SELECT COUNT(*) FROM lsh_buckets;
384000



Indexed PostgreSQL Query

Index Only Scan using lsh_buckets_pkey on lsh_buckets
(cost=0.42..14.84 rows=121 width=8)
(actual time=0.031..0.387 rows=3421 loops=1)

Index Cond: ((band = 17) AND
(bucket = '657e9c468c85cb31e9b8d23accedb4b076f1615d'::text))

Heap Fetches: 0
Buffers: shared hit=46

Planning Time: 0.108 ms
Execution Time: 0.509 ms





Sequential Scan
Gather
(cost=1000.00..7404.10 rows=121 width=8)
(actual time=0.593..7.489 rows=3421 loops=1)

Workers Planned: 2
Workers Launched: 2
Buffers: shared hit=3992

-> Parallel Seq Scan on lsh_buckets
(cost=0.00..6392.00 rows=50 width=8)
(actual time=2.669..4.362 rows=1140 loops=3)

Filter: ((band = 17) AND
(bucket = '657e9c468c85cb31e9b8d23accedb4b076f1615d'::text))

Rows Removed by Filter: 126860
Buffers: shared hit=3992

Planning Time: 0.103 ms
Execution Time: 7.607 ms


Latest Section E Run

BASELINE
num_buckets: 210099
mean: 1.8277097939542788
median: 1.0
p95: 4.0
p99: 9.0
max: 954
Runtime: 19.495 sec

MITIGATED
num_buckets: 71278
mean: 5.387356547602346
median: 1.0
p95: 13.0
p99: 74.0
max: 2593
Runtime: 21.264 sec

LABELLED-PAIR RETRIEVAL QUALITY
Baseline candidate survival:  0.3700
Mitigated candidate survival: 0.5722