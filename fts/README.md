# SQLite FTS5 demo
Some notes and demo scripts to go along with a presentation on full text search with
[SQLite FTS5](https://www.sqlite.org/fts5.html).


# Simple example: apt package search
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

Query the FTS table:
```sql
SELECT * FROM pkg_fts WHERE name MATCH 'python';
```

Show the difference between `MATCH` and `LIKE`:
```sql
SELECT name FROM pkg_fts WHERE name LIKE '%sql%' AND NAME NOT IN
    (SELECT name FROM pkg_fts WHERE name MATCH 'sql*');
```

# Detailed example

## Motivation
* Goal: Use taxonomy text search on [iNat](https://www.inaturalist.org) in an application
* There is an API, but it is slow and rate-limited:
```sh
http 'https://api.inaturalist.org/v1/taxa/autocomplete?q=lixus' | jq '.results[] | .name'
```
As a function:
```fish
function taxon-search -a query
  http "https://api.inaturalist.org/v1/taxa/autocomplete?q=$query" \
    | jq -r '.results[] | (.id | tostring) + "\t| " + (.name | tostring)'
    #| jq '.results[] | .name'
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
