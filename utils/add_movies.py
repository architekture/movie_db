"""Imports new movies via CSV and adds to archives/movies.yml

Reads & parses "archives/movies.yml" into memory as dict movies. Next,
importCSV is read & parsed into mem and resulting dict newMovies'
keys are added to dict movies.

User supplies the import file name and chooses how to handle duplicate
entries. By default, duplicates are discarded and the existing entries
remain in place.

Script should be executed from the root dir of this repo as a module
using the following syntax:

    python -m utils.add_movies

Upon successful execution of this script, the resulting release
candidate inventory file will be written to "archives/movies.yml.rc"
and can be compared with existing movies.yml file before being renamed
for use with Nornir.
"""

import yaml

from mvdb import HEADER
import mvdb.data


subdir = "archives/"
barcodes = subdir + "barcodes.ini"
barcodesRC = barcodes + ".rc"
movieFile = subdir + "movies.yml"
movieRC = movieFile + ".rc"
importDir = "user_input/"
importCSV = "movie_import_template.csv"


def select_file(dir: str=importDir, default: str=importCSV,
  header: str=HEADER):
    """Prompts user to specify the import file name.

    Args:
      dir(str):
        The specified directory where the file is located. Defaults to
        importDir.
      default(str):
        The optional default value. Defaults to importCSV.
      header(str):
        Section break header, defaults to mvdb.data.header.

      Returns:
        The target file name to import.
    """
    while True:
        print(
            f"\n{header}\n"
            '\nEnter import file name in .CSV format (Default is '
              f'"{importCSV}").'
            )
        selection = input("\nFile name: ") or default
        if selection.lower().endswith(".csv"):
            break
        else:
            print(f'\nERR: "{selection}" is not a valid file name!')
    fileName = dir + selection

    return fileName


def overwrite_select(header: str=HEADER):
    """Prompts user to choose how to handle potential duplicate imports.

    Args:
      header(str):
        Header string, defaults to mvdb.data.header.

    Returns:
      Overwrite selection as a boolean value.
    """
    print(
        f"\n{header}\n"
        '\nChoose how to handle duplicate imports. "True" will overwrite '
          'existing entries with the newer duplicates, "False" will skip the '
          'new entries without modifying the existing ones. (True or False, '
          'defaults to False).'
    )
    overwrite = False
    while True:
        selection = input("\nOverwrite? [True/False]: ").lower() or "f"
        if(selection == "true" or selection == "t"):
            overwrite = True
            break
        elif(selection == "false" or selection == "f"):
            break
        else:
            print(
                f'\nERR: "{selection}" is not a valid selection! Please enter '
                  'True or False.'
            )

    return overwrite


def summarize(rcFile: str, ogFile: str, header: str=HEADER):
    """Summarizes task and prints summary to terminal.

    Args:
      rcFile(str):
        The release candidate file.
      ogFile(str):
        The original file to be compared against before overwriting
        with the release candidate.
      header(str):
        Section break header.

    Returns:
      None
    """
    print(
        f"\n{header}\n"
        f'\nExport written to file as "{rcFile}". Compare to "{ogFile}" '
          "before renaming the release candidate."
    )


if __name__ == "__main__":
    with open(movieFile) as f:
        yaml_blob = f.read()
    movies = yaml.safe_load(yaml_blob)
    importFile = select_file()
    newMovies = mvdb.data.import_movies_csv(importFile)
    overwrite = overwrite_select()
    mvdb.data.add_movies(movies, newMovies, overwrite=overwrite)
    sortKeys = mvdb.data.fetch_sortKeys(movies)
    list.sort(sortKeys)
    movies = mvdb.data.sort_catalog(
        movieDict=movies,
        sortKey_list=sortKeys,
        dataHeader="sort_key"
    )
    mvdb.data.write_barcodes(movies, barcodesRC)
    movies_yml = mvdb.data.dump_movies_yaml(movies)

    mvdb.data.export_movies_yaml(movies_yml, movieRC)

    summarize(rcFile=barcodesRC, ogFile=barcodes)
    summarize(rcFile=movieRC, ogFile=movieFile)
    print(f"\n{HEADER}")
