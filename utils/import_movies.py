"""Imports movies.csv master spreadsheet for use with Nornir.

Reads & parses "archives/movies.csv" into memory before transforming
into YAML.

Script should be executed from the root dir of this repo as a module
using the following syntax:

    python -m utils.import_movies

Upon successful execution of this script, the resulting inventory file
will be written to "archives/movies.yml" and can subsequently be used
with Nornir.
"""

import mvdb.data


subdir = "archives/"
file = subdir + "movies.csv"
output = subdir + "movies.yml"


if __name__ == "__main__":
    movies = mvdb.data.import_movies_csv(file)
    sortKeys = mvdb.data.fetch_sortKeys(movies)
    list.sort(sortKeys)
    movies = mvdb.data.sort_catalog(movies, sortKeys, "sort_key")
    moviesYML = mvdb.data.dump_movies_yaml(movies)

    mvdb.data.export_movies_yaml(moviesYML, output)