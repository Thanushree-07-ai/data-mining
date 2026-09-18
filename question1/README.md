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


S C:\Users\ub02-glab-019\data-mining\question1> docker compose run --rm duckdb -c ".read /workspace/duckdb/analytics.sql"
Container question1-duckdb-run-fa8b9f3b8b3f Creating 
Container question1-duckdb-run-fa8b9f3b8b3f Created 
┌───────────────┬─────────────┐
│ parquet_files │ total_bytes │
│     int64     │   int128    │
├───────────────┼─────────────┤
│           144 │    16879938 │
└───────────────┴─────────────┘
┌───────────────────────┬───────────────────────┐
│ files_for_S01_october │ bytes_for_S01_october │
│         int64         │        int128         │
├───────────────────────┼───────────────────────┤
│                     1 │                184982 │
└───────────────────────┴───────────────────────┘
┌───────────┬───────────┐
│ raw_files │ raw_bytes │
│   int64   │  int128   │
├───────────┼───────────┤
│      4457 │  68706877 │
└───────────┴───────────┘
┌────────────────┐
│ canonical_rows │
│     int64      │
├────────────────┤
│    1120924     │
│ (1.12 million) │
└────────────────┘
┌───────────────────────┐
│ unique_bill_line_keys │
│         int64         │
├───────────────────────┤
│        1120924        │
│    (1.12 million)     │
└───────────────────────┘
┌──────────────────────────┐
│ duplicate_bill_line_keys │
│          int64           │
├──────────────────────────┤
│                        0 │
└──────────────────────────┘
┌──────────┬─────────────────────┬─────────────┬──────────────────────┬─────────────┬────────────┬────────────────────┐
│ store_id │     store_name      │ category_id │    category_name     │ day_of_week │   month    │      revenue       │
│ varchar  │       varchar       │   varchar   │       varchar        │   varchar   │    date    │       double       │
├──────────┼─────────────────────┼─────────────┼──────────────────────┼─────────────┼────────────┼────────────────────┤
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Friday      │ 2024-01-01 │  89952.17999999998 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Monday      │ 2024-01-01 │ 130620.62999999999 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Saturday    │ 2024-01-01 │ 100609.76999999999 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Sunday      │ 2024-01-01 │ 120780.54000000002 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Thursday    │ 2024-01-01 │           88083.54 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Tuesday     │ 2024-01-01 │ 109777.48999999998 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Wednesday   │ 2024-01-01 │  94671.39999999998 │
│ S01      │ Annapurna Jayanagar │ C11         │ Bakery               │ Friday      │ 2024-01-01 │            14729.4 │
│ S01      │ Annapurna Jayanagar │ C11         │ Bakery               │ Monday      │ 2024-01-01 │           11438.56 │
│ S01      │ Annapurna Jayanagar │ C11         │ Bakery               │ Saturday    │ 2024-01-01 │ 16404.260000000002 │
│ S01      │ Annapurna Jayanagar │ C11         │ Bakery               │ Sunday      │ 2024-01-01 │ 19594.890000000007 │
│ S01      │ Annapurna Jayanagar │ C11         │ Bakery               │ Thursday    │ 2024-01-01 │ 11898.519999999999 │
│ S01      │ Annapurna Jayanagar │ C11         │ Bakery               │ Tuesday     │ 2024-01-01 │ 13423.969999999998 │
│ S01      │ Annapurna Jayanagar │ C11         │ Bakery               │ Wednesday   │ 2024-01-01 │ 17492.090000000004 │
│ S01      │ Annapurna Jayanagar │ C03         │ Beverages            │ Friday      │ 2024-01-01 │ 31436.890000000007 │
│ S01      │ Annapurna Jayanagar │ C03         │ Beverages            │ Monday      │ 2024-01-01 │ 25576.780000000002 │
│ S01      │ Annapurna Jayanagar │ C03         │ Beverages            │ Saturday    │ 2024-01-01 │           41614.39 │
│ S01      │ Annapurna Jayanagar │ C03         │ Beverages            │ Sunday      │ 2024-01-01 │ 30299.289999999997 │
│ S01      │ Annapurna Jayanagar │ C03         │ Beverages            │ Thursday    │ 2024-01-01 │ 23242.980000000007 │
│ S01      │ Annapurna Jayanagar │ C03         │ Beverages            │ Tuesday     │ 2024-01-01 │           22691.68 │
│  ·       │          ·          │  ·          │     ·                │   ·         │     ·      │               ·    │
│  ·       │          ·          │  ·          │     ·                │   ·         │     ·      │               ·    │
│  ·       │          ·          │  ·          │     ·                │   ·         │     ·      │               ·    │
│ S12      │ Annapurna Salt Lake │ C06         │ Spices & Masala      │ Monday      │ 2024-12-01 │ 18212.069999999996 │
│ S12      │ Annapurna Salt Lake │ C06         │ Spices & Masala      │ Saturday    │ 2024-12-01 │ 28880.079999999998 │
│ S12      │ Annapurna Salt Lake │ C06         │ Spices & Masala      │ Sunday      │ 2024-12-01 │ 31045.629999999997 │
│ S12      │ Annapurna Salt Lake │ C06         │ Spices & Masala      │ Thursday    │ 2024-12-01 │           17424.84 │
│ S12      │ Annapurna Salt Lake │ C06         │ Spices & Masala      │ Tuesday     │ 2024-12-01 │            21202.8 │
│ S12      │ Annapurna Salt Lake │ C06         │ Spices & Masala      │ Wednesday   │ 2024-12-01 │            8368.89 │
│ S12      │ Annapurna Salt Lake │ C04         │ Staples & Grains     │ Friday      │ 2024-12-01 │ 112147.64000000004 │
│ S12      │ Annapurna Salt Lake │ C04         │ Staples & Grains     │ Monday      │ 2024-12-01 │           92640.46 │
│ S12      │ Annapurna Salt Lake │ C04         │ Staples & Grains     │ Saturday    │ 2024-12-01 │  174046.8099999999 │
│ S12      │ Annapurna Salt Lake │ C04         │ Staples & Grains     │ Sunday      │ 2024-12-01 │          164940.45 │
│ S12      │ Annapurna Salt Lake │ C04         │ Staples & Grains     │ Thursday    │ 2024-12-01 │  64438.86999999999 │
│ S12      │ Annapurna Salt Lake │ C04         │ Staples & Grains     │ Tuesday     │ 2024-12-01 │           96211.97 │
│ S12      │ Annapurna Salt Lake │ C04         │ Staples & Grains     │ Wednesday   │ 2024-12-01 │  78688.26000000001 │
│ S12      │ Annapurna Salt Lake │ C14         │ Stationery & General │ Friday      │ 2024-12-01 │           26536.68 │
│ S12      │ Annapurna Salt Lake │ C14         │ Stationery & General │ Monday      │ 2024-12-01 │  33974.48000000001 │
│ S12      │ Annapurna Salt Lake │ C14         │ Stationery & General │ Saturday    │ 2024-12-01 │  37211.01000000002 │
│ S12      │ Annapurna Salt Lake │ C14         │ Stationery & General │ Sunday      │ 2024-12-01 │  54237.44999999999 │
│ S12      │ Annapurna Salt Lake │ C14         │ Stationery & General │ Thursday    │ 2024-12-01 │  23369.06000000001 │
│ S12      │ Annapurna Salt Lake │ C14         │ Stationery & General │ Tuesday     │ 2024-12-01 │ 22349.840000000007 │
│ S12      │ Annapurna Salt Lake │ C14         │ Stationery & General │ Wednesday   │ 2024-12-01 │ 25708.230000000003 │
└──────────┴─────────────────────┴─────────────┴──────────────────────┴─────────────┴────────────┴────────────────────┘
  14112 rows (40 shown)                           use .last to show entire result                           7 columns
┌───────────────────────┬──────────────┬────────────┬──────────────┬──────────────────────────┬─────────────┬─────────────┬───────────────┬───────────────┬────────────────┬──────────────┐
│      period_name      │ report_month │ product_sk │ product_code │       product_name       │ category_id │ revision_id │      mrp      │ selling_price │ effective_from │ effective_to │
│        varchar        │     date     │   int64    │   varchar    │         varchar          │   varchar   │    int64    │ decimal(12,2) │ decimal(12,2) │      date      │     date     │
├───────────────────────┼──────────────┼────────────┼──────────────┼──────────────────────────┼─────────────┼─────────────┼───────────────┼───────────────┼────────────────┼──────────────┤
│ March 2024            │ 2024-03-01   │       1001 │ P100005      │ Thums Up Mango Juice 25… │ C03         │      500003 │        115.86 │        103.45 │ 2023-11-09     │ 2024-06-13   │
│ March 2024            │ 2024-03-01   │       1002 │ P100007      │ Vim Dishwash Bar 1kg     │ C08         │      500006 │        144.95 │        129.42 │ 2023-09-19     │ 2024-05-23   │
│ March 2024            │ 2024-03-01   │       1003 │ P100019      │ Sunfeast Cookies 150g    │ C01         │      500009 │         70.50 │         62.95 │ 2022-01-01     │ 2024-04-13   │
│ March 2024            │ 2024-03-01   │       1004 │ P100026      │ Dhara Rice Bran Oil 5L   │ C05         │      500014 │        341.19 │        304.63 │ 2024-01-30     │ 2024-10-22   │
│ March 2024            │ 2024-03-01   │       1005 │ P100033      │ Gold Winner Mustard Oil… │ C05         │      500018 │        854.69 │        763.12 │ 2023-07-19     │ 2024-07-12   │
│ March 2024            │ 2024-03-01   │       1006 │ P100035      │ Huggies Diapers Small    │ C09         │      500021 │       1631.36 │       1456.57 │ 2023-07-26     │ 2024-04-25   │
│ March 2024            │ 2024-03-01   │       1007 │ P100044      │ Mamypoko Baby Powder XL  │ C09         │      500028 │        825.50 │        737.05 │ 2024-02-16     │ 9999-12-31   │
│ March 2024            │ 2024-03-01   │       1008 │ P100049      │ Britannia Cream Biscuit… │ C01         │      500029 │         74.98 │         66.95 │ 2022-01-01     │ 2024-06-19   │
│ March 2024            │ 2024-03-01   │       1009 │ P100057      │ McCain French Fries 1kg  │ C10         │      500033 │        241.86 │        215.95 │ 2022-01-01     │ 2024-07-20   │
│ March 2024            │ 2024-03-01   │       1010 │ P100066      │ Bru Mango Juice 500g     │ C03         │      500038 │        281.37 │        251.22 │ 2023-05-15     │ 9999-12-31   │
│ March 2024            │ 2024-03-01   │       1011 │ P100074      │ MDH Sambar Powder 200g   │ C06         │      500040 │         64.71 │         57.78 │ 2024-01-27     │ 9999-12-31   │
│ March 2024            │ 2024-03-01   │       1012 │ P100077      │ Catch Sambar Powder 100g │ C06         │      500042 │        203.19 │        181.42 │ 2023-04-04     │ 2024-07-11   │
│ March 2024            │ 2024-03-01   │       1013 │ P100086      │ Heritage Ghee 1L         │ C02         │      500045 │         99.62 │         88.95 │ 2022-01-01     │ 2024-10-02   │
│ March 2024            │ 2024-03-01   │       1014 │ P100095      │ Modern Rusk 6 pc         │ C11         │      500047 │        104.10 │         92.95 │ 2022-01-01     │ 2024-10-03   │
│ March 2024            │ 2024-03-01   │       1015 │ P100100      │ Sumeru French Fries 400g │ C10         │      500050 │        387.87 │        346.31 │ 2023-12-18     │ 2024-03-12   │
│ March 2024            │ 2024-03-01   │       1016 │ P100106      │ Real Mango Juice 500g    │ C03         │      500057 │        321.91 │        287.42 │ 2023-10-22     │ 2024-06-17   │
│ March 2024            │ 2024-03-01   │       1017 │ P100112      │ Bikano Khakhra 400g      │ C01         │      500059 │        102.98 │         91.95 │ 2022-01-01     │ 2024-07-25   │
│ March 2024            │ 2024-03-01   │       1018 │ P100121      │ English Oven Pav Bun 40… │ C11         │      500063 │        114.68 │        102.39 │ 2023-11-19     │ 2024-06-15   │
│ March 2024            │ 2024-03-01   │       1019 │ P100131      │ Huggies Baby Powder Med… │ C09         │      500066 │        713.38 │        636.95 │ 2022-01-01     │ 2024-03-27   │
│ March 2024            │ 2024-03-01   │       1020 │ P100135      │ Eastern Coriander Powde… │ C06         │      500070 │         75.79 │         67.67 │ 2023-11-18     │ 2024-04-23   │
│     ·                 │     ·        │         ·  │    ·         │            ·             │  ·          │         ·   │           ·   │           ·   │     ·          │     ·        │
│     ·                 │     ·        │         ·  │    ·         │            ·             │  ·          │         ·   │           ·   │           ·   │     ·          │     ·        │
│     ·                 │     ·        │         ·  │    ·         │            ·             │  ·          │         ·   │           ·   │           ·   │     ·          │     ·        │
│ Last month in dataset │ 2024-11-01   │       2181 │ P108262      │ Patanjali Face Wash 180… │ C07         │      504173 │        663.70 │        592.59 │ 2024-06-12     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2182 │ P108272      │ McCain Idli Batter 400g  │ C10         │      504176 │        136.63 │        121.99 │ 2024-09-05     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2183 │ P108275      │ Mamaearth Bathing Soap … │ C07         │      504180 │        565.07 │        504.53 │ 2024-05-19     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2184 │ P108282      │ Nandini Cheese Slices 1L │ C02         │      504184 │        529.73 │        472.97 │ 2024-08-28     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2185 │ P108292      │ Farm Fresh Apple 1kg     │ C12         │      504188 │        116.50 │        104.02 │ 2023-12-08     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2186 │ P108300      │ Patanjali Bathing Soap … │ C07         │      504192 │        326.39 │        291.42 │ 2024-08-05     │ 2024-11-07   │
│ Last month in dataset │ 2024-11-01   │       2187 │ P108302      │ Sundrop Groundnut Oil 2L │ C05         │      504195 │        958.22 │        855.55 │ 2023-09-14     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2188 │ P108313      │ ITC Master Chef Frozen … │ C10         │      504198 │        459.48 │        410.25 │ 2024-10-12     │ 2024-11-12   │
│ Last month in dataset │ 2024-11-01   │       2189 │ P108319      │ Sundrop Mustard Oil 5L   │ C05         │      504204 │        294.32 │        262.79 │ 2024-10-26     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2190 │ P108326      │ Classmate Ball Pen 1 pc  │ C14         │      504207 │        530.75 │        473.88 │ 2024-05-24     │ 2024-11-13   │
│ Last month in dataset │ 2024-11-01   │       2191 │ P108335      │ Farm Fresh Onion 500g    │ C12         │      504212 │        210.12 │        187.61 │ 2024-10-25     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2192 │ P108338      │ Amul Choco Chewing Gum … │ C13         │      504215 │        244.92 │        218.68 │ 2024-01-11     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2193 │ P108346      │ Milky Mist Ghee 200ml    │ C02         │      504218 │        598.16 │        534.07 │ 2024-08-12     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2194 │ P108356      │ Camlin Pencil Box Pack … │ C14         │      504223 │        262.84 │        234.68 │ 2024-09-30     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2195 │ P108361      │ India Gate Chana Dal 10… │ C04         │      504226 │         76.63 │         68.42 │ 2024-06-28     │ 2024-11-09   │
│ Last month in dataset │ 2024-11-01   │       2196 │ P108369      │ Paper Boat Mineral Wate… │ C03         │      504232 │        384.38 │        343.20 │ 2024-10-10     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2197 │ P108374      │ Fortune Toor Dal 5kg     │ C04         │      504237 │       1587.36 │       1417.29 │ 2024-09-25     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2198 │ P108379      │ Sumeru Frozen Peas 1kg   │ C10         │      504241 │        336.80 │        300.71 │ 2024-09-16     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2199 │ P108389      │ Gold Winner Sunflower O… │ C05         │      504245 │        937.78 │        837.30 │ 2024-09-27     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2200 │ P108397      │ Sumeru Ready Paratha 40… │ C10         │      504247 │        320.35 │        286.03 │ 2024-03-02     │ 9999-12-31   │
└───────────────────────┴──────────────┴────────────┴──────────────┴──────────────────────────┴─────────────┴─────────────┴───────────────┴───────────────┴────────────────┴──────────────┘
  2385 rows (40 shown)                                                             use .last to show entire result                                                             11 columns

┌─────────────────────────────┐
│┌───────────────────────────┐│
││       Physical Plan       ││
│└───────────────────────────┘│
└─────────────────────────────┘
┌───────────────────────────┐
│          ORDER_BY         │
│    ────────────────────   │
│       s.store_id ASC      │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│       HASH_GROUP_BY       │
│    ────────────────────   │
│          Groups:          │
│             #0            │
│             #1            │
│                           │
│    Aggregates: sum(#2)    │
│                           │
│       ~259,659 rows       │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│          store_id         │
│         store_name        │
│          revenue          │
│                           │
│       ~259,660 rows       │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         HASH_JOIN         │
│    ────────────────────   │
│      Join Type: INNER     │
│                           │
│        Conditions:        ├──────────────┐
│    store_id = store_id    │              │
│                           │              │
│       ~259,660 rows       │              │
└─────────────┬─────────────┘              │
┌─────────────┴─────────────┐┌─────────────┴─────────────┐
│         PROJECTION        ││       POSTGRES_SCAN       │
│    ────────────────────   ││    ────────────────────   │
│             #0            ││       Table: stores       │
│             #2            ││                           │
│                           ││        Projections:       │
│                           ││          store_id         │
│                           ││         store_name        │
│                           ││                           │
│       ~259,660 rows       ││          ~93 rows         │
└─────────────┬─────────────┘└───────────────────────────┘
┌─────────────┴─────────────┐
│           FILTER          │
│    ────────────────────   │
│ ((line_type = 'SALE') OR  │
│ (line_type = 'RETURN') OR │
│  (line_type = 'DISCOUNT') │
│  OR (line_type = 'VOID')) │
│                           │
│       ~259,660 rows       │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│        READ_PARQUET       │
│    ────────────────────   │
│         Function:         │
│        READ_PARQUET       │
│                           │
│        Projections:       │
│          store_id         │
│         line_type         │
│          revenue          │
│                           │
│          Filters:         │
│  optional: line_type IN ( │
│     'SALE', 'RETURN',     │
│    'DISCOUNT', 'VOID')    │
│                           │
│      ~1,298,304 rows      │
└───────────────────────────┘
┌──────────┬──────────────────────────┬────────────────────┐
│ store_id │        store_name        │      revenue       │
│ varchar  │         varchar          │       double       │
├──────────┼──────────────────────────┼────────────────────┤
│ S01      │ Annapurna Jayanagar      │  56995199.14000011 │
│ S02      │ Annapurna Koramangala    │  47194947.02000004 │
│ S03      │ Annapurna T Nagar        │   61864894.4600002 │
│ S04      │ Annapurna Kukatpally     │  40201258.52999999 │
│ S05      │ Annapurna Kochi Marine   │  30159037.53999997 │
│ S06      │ Annapurna Andheri West   │  52584302.70000005 │
│ S07      │ Annapurna Baner          │ 35219585.449999996 │
│ S08      │ Annapurna Satellite      │  34477161.42999998 │
│ S09      │ Annapurna Vaishali       │ 27978995.769999925 │
│ S10      │ Annapurna Rajouri Garden │  59327041.98000011 │
│ S11      │ Annapurna Gomti Nagar    │ 32429712.909999963 │
│ S12      │ Annapurna Salt Lake      │ 44433598.819999985 │
└──────────┴──────────────────────────┴────────────────────┘
  12 rows                                        3 columns
┌────────────┬───────────────────┐
│   month    │      revenue      │
│    date    │      double       │
├────────────┼───────────────────┤
│ 2024-01-01 │ 38446071.33000016 │
│ 2024-02-01 │ 34887085.55000002 │
│ 2024-03-01 │ 41971649.09000032 │
│ 2024-04-01 │  37958457.3700002 │
│ 2024-05-01 │ 41764716.40000027 │
│ 2024-06-01 │ 38987082.82000016 │
│ 2024-07-01 │ 40295160.11000012 │
│ 2024-08-01 │ 45252181.75000013 │
│ 2024-09-01 │ 44615037.46000008 │
│ 2024-10-01 │ 56359195.91999994 │
│ 2024-11-01 │ 51583838.46999993 │
│ 2024-12-01 │ 50745259.47999988 │
└────────────┴───────────────────┘
  12 rows              2 columns
┌──────────────────────┐
│ october_2024_revenue │
│        double        │
├──────────────────────┤
│  56359195.91999995   │
│   (56.36 million)    │
└──────────────────────┘
┌─────────┬────────────┬─────────────┬──────────────────────────────────┐
│  month  │ closed_on  │ revenue_inr │          signed_off_by           │
│ varchar │    date    │   double    │             varchar              │
├─────────┼────────────┼─────────────┼──────────────────────────────────┤
│ 2024-01 │ 2024-02-09 │ 38446071.33 │ A. Krishnan (Finance Controller) │
│ 2024-02 │ 2024-03-11 │ 34887085.55 │ A. Krishnan (Finance Controller) │
│ 2024-03 │ 2024-04-09 │ 42457899.09 │ A. Krishnan (Finance Controller) │
│ 2024-04 │ 2024-05-10 │ 37958457.37 │ A. Krishnan (Finance Controller) │
│ 2024-05 │ 2024-06-09 │  41764716.4 │ A. Krishnan (Finance Controller) │
│ 2024-06 │ 2024-07-10 │ 38987082.82 │ A. Krishnan (Finance Controller) │
│ 2024-07 │ 2024-08-09 │ 40527291.81 │ A. Krishnan (Finance Controller) │
│ 2024-08 │ 2024-09-09 │ 45252181.75 │ A. Krishnan (Finance Controller) │
│ 2024-09 │ 2024-10-10 │ 44615037.46 │ A. Krishnan (Finance Controller) │
│ 2024-10 │ 2024-11-09 │ 56359195.92 │ A. Krishnan (Finance Controller) │
│ 2024-11 │ 2024-12-10 │ 51583838.47 │ A. Krishnan (Finance Controller) │
│ 2024-12 │ 2025-01-09 │  50745209.0 │ A. Krishnan (Finance Controller) │
└─────────┴────────────┴─────────────┴──────────────────────────────────┘
  12 rows                                                     4 columns


Q1-A Partitioning / Object Store
┌───────────────┬─────────────┐
│ parquet_files │ total_bytes │
│     int64     │   int128    │
├───────────────┼─────────────┤
│           144 │    16879938 │
└───────────────┴─────────────┘

┌───────────────────────┬───────────────────────┐
│ files_for_S01_october │ bytes_for_S01_october │
│         int64         │        int128         │
├───────────────────────┼───────────────────────┤
│                     1 │                184982 │
└───────────────────────┴───────────────────────┘

┌───────────┬───────────┐
│ raw_files │ raw_bytes │
│   int64   │  int128   │
├───────────┼───────────┤
│      4457 │  68706877 │
└───────────┴───────────┘


Q1-B
PS C:\Users\ub02-glab-019\data-mining\question1> $env:MINIO_ENDPOINT="http://localhost:9000"
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
PS C:\Users\ub02-glab-019\data-mining\question1> $env:MINIO_ENDPOINT="http://localhost:9000"
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
PS C:\Users\ub02-glab-019\data-mining\question1> py ingest\ingest.py
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



Q1-C — Dashboard Aggregation
┌──────────┬─────────────────────┬─────────────┬──────────────────────┬─────────────┬────────────┬────────────────────┐
│ store_id │     store_name      │ category_id │    category_name     │ day_of_week │   month    │      revenue       │
├──────────┼─────────────────────┼─────────────┼──────────────────────┼─────────────┼────────────┼────────────────────┤
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Friday      │ 2024-01-01 │  89952.17999999998 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Monday      │ 2024-01-01 │ 130620.62999999999 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Saturday    │ 2024-01-01 │ 100609.76999999999 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Sunday      │ 2024-01-01 │ 120780.54000000002 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Thursday    │ 2024-01-01 │           88083.54 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Tuesday     │ 2024-01-01 │ 109777.48999999998 │
│ S01      │ Annapurna Jayanagar │ C09         │ Baby Care            │ Wednesday   │ 2024-01-01 │  94671.39999999998 │
│ ·        │ ·                   │ ·           │ ·                    │ ·           │ ·          │ ·                  │
│ S12      │ Annapurna Salt Lake │ C14         │ Stationery & General │ Wednesday   │ 2024-12-01 │ 25708.230000000003 │
└──────────┴─────────────────────┴─────────────┴──────────────────────┴─────────────┴────────────┴────────────────────┘

14112 rows (40 shown)                           use .last to show entire result                           7 columns




Q1-D — Historical Price
┌───────────────────────┬──────────────┬────────────┬──────────────┬──────────────────────────┬─────────────┬─────────────┬───────────────┬───────────────┬────────────────┬──────────────┐
│      period_name      │ report_month │ product_sk │ product_code │       product_name       │ category_id │ revision_id │      mrp      │ selling_price │ effective_from │ effective_to │
├───────────────────────┼──────────────┼────────────┼──────────────┼──────────────────────────┼─────────────┼─────────────┼───────────────┼───────────────┼────────────────┼──────────────┤
│ March 2024            │ 2024-03-01   │       1001 │ P100005      │ Thums Up Mango Juice 25… │ C03         │      500003 │        115.86 │        103.45 │ 2023-11-09     │ 2024-06-13   │
│ March 2024            │ 2024-03-01   │       1002 │ P100007      │ Vim Dishwash Bar 1kg     │ C08         │      500006 │        144.95 │        129.42 │ 2023-09-19     │ 2024-05-23   │
│ March 2024            │ 2024-03-01   │       1003 │ P100019      │ Sunfeast Cookies 150g    │ C01         │      500009 │         70.50 │         62.95 │ 2022-01-01     │ 2024-04-13   │
│ March 2024            │ 2024-03-01   │       1004 │ P100026      │ Dhara Rice Bran Oil 5L   │ C05         │      500014 │        341.19 │        304.63 │ 2024-01-30     │ 2024-10-22   │
│ March 2024            │ 2024-03-01   │       1005 │ P100033      │ Gold Winner Mustard Oil… │ C05         │      500018 │        854.69 │        763.12 │ 2023-07-19     │ 2024-07-12   │
│ ·                     │ ·            │ ·          │ ·            │ ·                        │ ·           │ ·           │ ·             │ ·             │ ·              │ ·            │
│ Last month in dataset │ 2024-11-01   │       2181 │ P108262      │ Patanjali Face Wash 180… │ C07         │      504173 │        663.70 │        592.59 │ 2024-06-12     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2182 │ P108272      │ McCain Idli Batter 400g  │ C10         │      504176 │        136.63 │        121.99 │ 2024-09-05     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2183 │ P108275      │ Mamaearth Bathing Soap … │ C07         │      504180 │        565.07 │        504.53 │ 2024-05-19     │ 9999-12-31   │
│ Last month in dataset │ 2024-11-01   │       2184 │ P108282      │ Nandini Cheese Slices 1L │ C02         │      504184 │        529.73 │        472.97 │ 2024-08-28     │ 9999-12-31   │
│ ·                     │ ·            │ ·          │ ·            │ ·                        │ ·           │ ·           │ ·             │ ·             │ ·              │ ·            │
└───────────────────────┴──────────────┴────────────┴──────────────┴──────────────────────────┴─────────────┴─────────────┴───────────────┴───────────────┴────────────────┴──────────────┘

2385 rows (40 shown)                                                             use .last to show entire result                                                             11 columns



Q1-E — Cross-System Query

┌───────────────────────────┐
│       Physical Plan       │
└───────────────────────────┘

┌───────────────────────────┐
│          ORDER_BY         │
│       s.store_id ASC      │
└─────────────┬─────────────┘

        ...

┌─────────────┴─────────────┐┌─────────────┴─────────────┐
│         PROJECTION        ││       POSTGRES_SCAN       │
│                           ││       Table: stores       │
│                           ││                           │
│                           ││        Projections:       │
│                           ││          store_id         │
│                           ││         store_name        │
└─────────────┬─────────────┘└───────────────────────────┘

        ...

┌─────────────┴─────────────┐
│           READ_PARQUET    │
│                           │
│        Function:          │
│        READ_PARQUET       │
│                           │
│        Projections:       │
│          store_id         │
│          line_type        │
│          revenue          │
└───────────────────────────┘


Q1-F — Finance Reconciliation

┌─────────┬────────────────────┬─────────────────┬────────────┬────────────────────────────────────┬─────────────────────────────────────────────────────┐
│  month  │ calculated_revenue │ finance_revenue │ difference │           classification           │                       action                        │
├─────────┼────────────────────┼─────────────────┼────────────┼────────────────────────────────────┼─────────────────────────────────────────────────────┤
│ 2024-01 │        38446071.33 │     38446071.33 │        0.0 │ MATCH                              │ No action                                           │
│ 2024-02 │        34887085.55 │     34887085.55 │        0.0 │ MATCH                              │ No action                                           │
│ 2024-03 │        41971649.09 │     42457899.09 │  -486250.0 │ REVENUE DEFINITION DIFFERENCE      │ Take revenue definition difference to finance       │
│ 2024-04 │        37958457.37 │     37958457.37 │        0.0 │ MATCH                              │ No action                                           │
│ 2024-05 │         41764716.4 │      41764716.4 │        0.0 │ MATCH                              │ No action                                           │
│ 2024-06 │        38987082.82 │     38987082.82 │        0.0 │ MATCH                              │ No action                                           │
│ 2024-07 │        40295160.11 │     40527291.81 │  -232131.7 │ SOURCE ISSUE                       │ Take source gap to finance                          │
│ 2024-08 │        45252181.75 │     45252181.75 │        0.0 │ MATCH                              │ No action                                           │
│ 2024-09 │        44615037.46 │     44615037.46 │        0.0 │ MATCH                              │ No action                                           │
│ 2024-10 │        56359195.92 │     56359195.92 │        0.0 │ MATCH                              │ No action                                           │
│ 2024-11 │        51583838.47 │     51583838.47 │        0.0 │ MATCH                              │ No action                                           │
│ 2024-12 │        50745259.48 │      50745209.0 │      50.48 │ PIPELINE BUG / ROUNDING DIFFERENCE │ Take small pipeline/rounding discrepancy to finance │
└─────────┴────────────────────┴─────────────────┴────────────┴────────────────────────────────────┴─────────────────────────────────────────────────────┘
  12 rows                                                                                                                                      6 columns
