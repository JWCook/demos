# SQLite FTS5 demo
Some notes and demo scripts to go along with a presentation on full text search with
[SQLite FTS5](https://www.sqlite.org/fts5.html).

# Intro
* Full text search is a database with indexes optimized for very quickly searching large volumes of text
* When would you want to use this? When you've outgrown basic string comparison queries, but don't need/want a server or SaaS solution (Elasticsearch, Algolia, etc.).
* Think autocomplete interfaces, or searching document contents in a CMS system
* Other "intermediate" options would include FTS features in Postgres, Redis, and MongoDB (free, less maintenance than ES, and you may already be using it)
* If your application has a shared filesystem and isn't massively parellel (hundreds of threads/processes), SQLite FTS will likely suit your needs


# Simple example: apt package search

## Load
```sh
sqlite3 demo.db
```
```sql
CREATE VIRTUAL TABLE pkg_fts USING fts5(name, desc);
```

Dump apt package names and split name, description into a CSV file:
```sh
apt-cache search . > apt-pkgs.txt
sed -i 's/,//; s/ - /","/; s/.*/"&"/' apt-pkgs.txt
```

Load contents (one row per line) into the FTS table:
```sql
.import apt-pkgs.txt pkg_fts
```

## Query

Query the FTS table:
```sql
SELECT * FROM pkg_fts WHERE name MATCH 'python';
```

Use `*` operator (as a token prefix query, not a wildcard)
```sql
SELECT * FROM pkg_fts WHERE name MATCH 'sql*';
```

Show the difference between `MATCH` and `LIKE`:
```sql
SELECT name FROM pkg_fts WHERE name LIKE '%sql%';

SELECT name FROM pkg_fts WHERE name LIKE '%sql%' AND NAME NOT IN
    (SELECT name FROM pkg_fts WHERE name MATCH 'sql*');
```

Match multiple words (ordering doesn't matter):
```sql
SELECT * FROM pkg_fts WHERE name MATCH 'fonts core';
```

Boolean operators:
```sql
SELECT * FROM pkg_fts WHERE name MATCH 'core fonts NOT dejavu';
SELECT * FROM pkg_fts WHERE name MATCH 'fonts OR dejavu';
```

Compare performance with `apt-cache search`:
```sh
time apt-cache search lib32
time sqlite3 demo.db "SELECT * FROM pkg_fts WHERE name MATCH 'lib32*'"
```

## Tokenizers
Try a different tokenizer:
```sh
sqlite3 demo-porter.db
```
```sql
.open demo-porter.db
CREATE VIRTUAL TABLE pkg_fts USING fts5(name, desc, tokenize = 'porter ascii');
.import apt-pkgs.txt pkg_fts
SELECT * FROM pkg_fts WHERE name MATCH 'race';
```
Note that with [porter](https://tartarus.org/martin/PorterStemmer/) tokenizer, 'race' matches 'racing',


## Triggers
Instead of loading directly to an FTS table, you may want it to be automatically populated by some source table.

```sql
CREATE VIRTUAL TABLE pkg_fts USING fts5(name, desc, tokenize = 'porter ascii');
CREATE TABLE pkg (name TEXT, desc TEXT);
CREATE TRIGGER pkg_insert AFTER INSERT ON pkg BEGIN
  INSERT INTO pkg_fts (name, desc) VALUES (new.name, new.desc);
END;
CREATE TRIGGER pkg_delete AFTER DELETE ON pkg BEGIN
  DELETE FROM pkg_fts WHERE name = old.name;
END;
CREATE TRIGGER pkg_update AFTER UPDATE ON pkg BEGIN
  DELETE FROM pkg_fts WHERE name = old.name;
  INSERT INTO pkg_fts (name, desc) VALUES (new.name, new.desc);
END;

DELETE FROM pkg_fts;
.import apt-pkgs.txt pkg
```

Test the triggers:
```sql
SELECT (SELECT COUNT(*) FROM pkg) as src, (SELECT COUNT(*) FROM pkg_fts) as fts;

-- insert
INSERT INTO pkg (name, desc) VALUES ('libsb', 'strong bads cool library for attractive people');
SELECT * FROM pkg_fts WHERE name='libsb-dev';

-- delete
DELETE FROM pkg WHERE name ='soft-serve';
SELECT (SELECT COUNT(*) FROM pkg) as src, (SELECT COUNT(*) FROM pkg_fts) as fts;

-- update
UPDATE pkg SET desc='some garbage library' WHERE name='libgc-dev';
SELECT * FROM pkg_fts WHERE name='libgc-dev';

```


# Example wrappers
See included shell and python scripts


# Advanced example

## Motivation
* Goal: Use taxonomy text search on [iNat](https://www.inaturalist.org) in an application
* Check a simple search for 'cow':
  ```sql
  SELECT taxon_id, name FROM taxon_fts WHERE name MATCH 'cow' LIMIT 10;
  ```
* Compare those against text search results on inaturalist.org
* What's different? Search rank weights!

## API
There is an API, but it is slow and rate-limited:
```sh
http 'https://api.inaturalist.org/v1/taxa/autocomplete?q=lixus' | jq '.results[] | .name'
```
As a function:
```fish

function taxon-search -a query
  http "https://api.inaturalist.org/v1/taxa/autocomplete?q=$query" \
    | jq '.results[] | .name'
end

function taxon-search -a query
  http "https://api.inaturalist.org/v1/taxa/autocomplete?q=$query" \
    | jq -r '.results[] | (.id | tostring) + "\t| " + (.name | tostring)'
end

time taxon-search weevil
```

## Data source
iNat taxonomy archive exported to [GBIF](https://www.gbif.org)

Taxon records (w/ scientific names)
```csv
id,kingdom,phylum,class,order,family,genus,specificEpithet,infraspecificEpithet,modified,scientificName,taxonRank
1,Animalia,,,,,,,,2021-11-02T06:05:44Z,Animalia,kingdom
2,Animalia,Chordata,,,,,,,2021-11-23T00:40:18Z,Chordata,phylum
3,Animalia,Chordata,Aves,,,,,,2021-11-01T23:54:30Z,Aves,class
```

Common names
```csv
id,vernacularName,language,locality,countryCode,source,lexicon,contributor,created
7,Limpkin,en,"","",English,,2008-03-13T02:35:09Z
19,Sunbittern,en,"","",English,,2008-03-13T02:35:09Z
34,Whooping Crane,en,"","",English,,2008-03-13T02:35:11Z
```

## Processing
* Goal: weigh taxon search results by how commonly it's observed
* For ranks higher than species, we need aggregate stats
  * i.e., direct observations of 'Bovines' (ID'd at familiy level) + all genera + all species
* Need to traverse the entire taxonomy tree to get observation counts
* Normalize counts; example with `numpy`:
  ```py
  import numpy as np

  def normalize(series):
    series = np.log(series.copy())
    return (series - series.mean()) / series.std()
  ```
* Add as a column on the FTS table, and now we can use it to customize search rankings!
* Alternative: [auxiliary functions](https://www.sqlite.org/fts5.html#_auxiliary_functions_)

## Example queries
New in FTS5: a `rank` parameter indicates relevance, for example:
```sql
SELECT taxon_id, name FROM taxon_fts
WHERE name MATCH 'cow' ORDER BY rank;
```

Combine with custom ranking:
```sql
SELECT taxon_id, name, (rank - count_rank) AS combined_rank FROM taxon_fts
WHERE name MATCH 'cow' ORDER BY COMBINED_RANK;

SELECT taxon_id, name, rank, count_rank, (rank - count_rank) AS combined_rank FROM taxon_fts
WHERE name MATCH 'cow' ORDER BY COMBINED_RANK;

```

## Pre-built database
If you want to test out these queries, you can download a pre-built SQLite db here (full taxonomy + FTS):
```sh
curl -LO https://github.com/pyinat/naturtag/releases/latest/download/taxonomy_full.tar.gz
tar xvf taxonomy_full.tar.gz
sqlite3 naturtag.db
```
