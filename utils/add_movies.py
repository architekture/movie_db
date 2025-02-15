"""Imports new movies via CSV and adds to archives/movies.yml

Reads & parses "archives/movies.yml" into memory as movieList. Next,
importCSV is read & parsed into mem and resulting list is used to extend
existing movieList before being transformed into YAML.

Script should be executed from the root dir of this repo as a module
using the following syntax:

    python -m utils.add_movies

Upon successful execution of this script, the resulting release
candidate inventory file will be written to "archives/movies.yml.rc"
and can be compared with existing movies.yml file before being renamed
for use with Nornir.
"""

import yaml

import mvdb.data


subdir = "archives/"
movieFile = subdir + "movies.yml"
exportYML = subdir + "movies.yml.rc"
importCSV = "user_input/movie_import_template.csv"


if __name__ == "__main__":
    movieList = []
    with open(movieFile) as f:
        yaml_blob = f.read()
    movieDict = yaml.safe_load(yaml_blob)
    for key,val in movieDict.items():
        movie = {key : val}
        movieList.append(movie)
    newMovies = mvdb.data.import_movies(importCSV)
    movieList.extend(newMovies)
    sortKeys = mvdb.data.fetch_sortKeys(movieList)
    list.sort(sortKeys)
    movies = mvdb.data.sort_catalog(
        movie_list=movieList,
        sortKey_list=sortKeys,
        data_header="sort_key"
    )
    movies_yml = mvdb.data.dump_movies_yaml(movies)

    mvdb.data.export_movies_yaml(movies_yml, exportYML)