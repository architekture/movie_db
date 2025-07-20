"""Forces sortKey update of inventory from INI file.

Script reads archives/movies.yml and archives/tech_specs.ini into
memory. Each movie's key is compared to the override keys. If a match is
found, the movie's sort_key is replaced with the override value.

The films are then resorted using the updated sortKeys before a release
candidate YAML file is written to the archives.

Script should be executed from the root dir of this repo as a module
using the following syntax:

    python -m utils.update_sort_keys

Note: If a match is made, the overide value is substituted for the
current value, even if they are the same. The diff should reflect only
the changes, if any, made to the inventory's sortKeys.
"""

from configparser import ConfigParser
import yaml

# from mvdb import HEADER
import mvdb.data


subdir = "archives/"
movieFile = subdir + "movies.yml"
rcFile = movieFile + ".rc"


if __name__ == "__main__":
    with open(movieFile) as f:
        movieBlob = f.read()
    movies = yaml.safe_load(movieBlob)

    cp = ConfigParser()
    cp.read("archives/tech_specs.ini")
    overrides = mvdb.data.import_sort_overrides(
        parser=cp,
        dataHeader="sortKeys"
    )
    for movie in movies:
        sortKey = movies[movie]["sort_key"]
        if sortKey in overrides.keys():
            movies[movie]["sort_key"] = overrides[sortKey]

    sortKeys = mvdb.data.fetch_sortKeys(movies)
    list.sort(sortKeys)

    movies = mvdb.data.sort_catalog(
        movieDict=movies,
        sortKey_list=sortKeys,
        dataHeader="sort_key"
    )

    moviesYML = mvdb.data.dump_movies_yaml(movies)
    mvdb.data.export_movies_yaml(moviesYML, rcFile)