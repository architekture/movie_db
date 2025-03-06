from configparser import ConfigParser, NoOptionError, NoSectionError
import csv
import yaml

from mvdb import mvdbBaseException, DuplicateMovieError, HEADER


def add_movies(
    currentMovies: dict,
    newMovies: dict,
    overwrite: bool=False,
    header: str=HEADER
):
    """Adds new movies to catalog in place.

    The key for each movie in newMovies is checked against
    currentMovies.keys to verify new titles are unique. If a match is
    found, the current movie is skipped and the next import is
    attempted. An informational warning is printed to terminal if this
    condition is triggered.

    This default behavior can be modified and matched titles can be
    overwritten if the overwrite boolean is set to True.

    If the movie's key is unique, it is added to the currentMovies
    dict. This addition happens in place and the function itself returns
    a None value when import is complete.

    Args:
      currentMovies(dict):
        The entire movie catalog imported using the yaml.safe_load func.
      newMovies(dict):
        New films to be added to the catalog imported using the
        mvdb.import_movies_csv func.
      overwrite(bool):
        Boolean which defines how to handle duplicate imports. Defaults
        to False.
      header(str):
        Section break header.

    Returns:
      None
    """
    print(
        f"\n{header}\n"
        "\nAdding new movies...\n"
    )
    for movie in newMovies.keys():
        title = newMovies[movie]["data"]["title"]
        if not overwrite:
            try:
                detect_duplicates(currentMovies, movie)
            except mvdbBaseException:
                print(f'"{title}" already in catalog! Skipping...')
            else:
                currentMovies[movie] = newMovies[movie]
                print(f'"{title}" added to catalog.')
        else:
            currentMovies[movie] = newMovies[movie]
            print(f'"{title}" added to catalog.')

    print("\n--Import complete.")

    return None


def cell_sort(cell: str, delimiter: str=","):
    """Evaluates cell string and modifies the data type as needed.

    The function first checks whether the cell's string value is empty.
    If it is, the cell's value is replace with None.

    Else, the function looks for compound values. If the supplied
    delimiter is present in the cell value, the value is transformed
    into a list using the built-in split method using the delimiter
    given. The default delimiter is "," but any string value can be
    passed.

    If neither of these conditions are present, the value is left
    unmodified. The value is returned, regardless of transformation.

    Args:
      cell(str):
        String value for a given field in the movies.csv spreadsheet.
      delimiter(str):
        The delimiting character used to separate compound values. The
        default value is ",".

    Returns:
      The modified or unmodified cell value.
    """
    if cell == "":
        cell = None
    elif delimiter in cell:
        cell = cell.split(delimiter)
    
    return cell


def detect_duplicates(movieDict: dict, movieKey: str):
    """Checks if movie key is unique, else raises an exception.

    Args:
      movieDict(dict):
        Dict of movies returned via data.import_movies_csv func.
      movieKey(str):
        Top-level key for a single movie dict inside movieDict.

    Returns:
      None.
    """
    if movieKey in movieDict.keys():
        title = movieDict[movieKey]["data"]["title"]
        raise DuplicateMovieError(f'"{title}" already in movie catalog!')


def dump_movies_yaml(movieDict: dict):
    """Transforms Python-native dict of movies into YAML for Nornir.

    Args:
      movieDict(dict):
        Dict of movies returned via data.import_movies_csv func.

    Returns:
      A string value of the imported movie list transformed into YAML
      for use with Nornir.
    """
    export ="---"
    for mv in movieDict.keys():
        mv = {mv : movieDict[mv]}
        ym_blob = yaml.dump(mv, sort_keys=False).replace("- ", "  - ")
        export += f"\n{ym_blob}"
    
    return export


def export_movies_yaml(yamlBlob: str, fileName: str):
    """Writes YAML file of the movie database for use with Nornir.

    Args:
      yamlBlob(str):
        The str blob returned via data.dump_movies_yaml func.
      fileName(str):
        The file name for the resulting YAML document.
    """
    with open(fileName, "w") as f:
        f.write(yamlBlob)


def fetch_sortKeys(movieDict: dict, keyHeader: str="sort_key"):
    """Retrieves list of sortKeys from passed movie dict.

    Args:
      movieDict(dict):
        Python dict with root keys representing each title in the
        catalog.
      keyHeader(str):
        Key for stored sortKey value. Defaults to "sort_key".

    Returns:
      List of sortKeys from passed movie dict.
    """
    keyList = []

    for movie in movieDict.keys():
        keyList.append(movieDict[movie][keyHeader])
    
    return keyList


def gen_sort_key(title: str):
    """Converts the title for use in alpha sorting the database.

    The film's title is first transformed using the transform_title
    func before being evaluated to see if the the title starts with an
    article. 

    If the title starts with an article, it is removed using the
    built-in replace func. Foreign language articles are not considered
    (e.g. Le Cercle Rouge) and left in place.

    Args:
      title(str):
        The film's official title.

    Returns:
      The formatted sort_key.
    """
    subs = {
        "the_" : "",
        "a_" : "",
    }
    sort_key = transform_title(title)
    for k,v in subs.items():
        if sort_key.startswith(k):
            sort_key = sort_key.replace(k, v, 1)
    
    return sort_key


def import_boutiques(parser: ConfigParser, dataHeader: str):
    """Imports boutique label names from INI file.

    Args:
      parser(ConfigParser):
        ConfigParser object which has already read the INI file into
        memory and stored in class instance using
        ConfigParser.read(INIfile) method.
      data_header(str):
        Section header for boutique labels in INI file.

    Returns:
      List of boutique labels.
    """
    boutiqueLabels = parser.get(dataHeader, "labels").split(",")

    return boutiqueLabels


def import_current_genres(parser: ConfigParser, dataHeader: str):
    """Imports current genres, subgenres & descriptors from INI file.

    Args:
      parser(ConfigParser):
        ConfigParser object which has already read the INI file into
        memory and stored in class instance using
        ConfigParser.read(INIfile) method.
      data_header(str):
        Section header for genres, subgenres & descriptors in INI file.

    Returns:
      A list of currently supported genres, subgenres & descriptors.
    """
    genres = parser.get(dataHeader, "genres").split(",")
    subgenres = parser.get(dataHeader, "subgenres").split(",")
    descriptors = parser.get(dataHeader, "descriptors").split(",")
    genres.extend(subgenres)
    genres.extend(descriptors)

    return genres


def import_genres(csvRow: dict, movieDict: dict, validGenres: list):
    """Appends genre and descriptor data for movie database.

    Args:
      csvRow(dict):
        An individual row read into mem using the data.import_movies_csv
        func.
      movieDict(dict):
        Transformed Python-native dict synthesized from csv_row data
        using the data.import_movies_csv func.
      validGenres(list):
        List of genres imported using the import_current_genres func.
    """
    genres = []
    for genre in validGenres:
        try:
            if csvRow[genre].lower() == "true":
                genres.append(genre)
        except KeyError:
            pass
    movieDict["data"]["genres"] = genres


def import_movies_csv(file: str, iniFile: str="archives/tech_specs.ini",
  upcs: str = "archives/barcodes.ini", header: str=HEADER):
    """Converts movie .CSV file into structured Python data.

    Args:
      file(str):
        The file name of the movie DB in .CSV format.
      ini_file(str):
        Formatted INI file to be read & parsed for importing certain
        attributes. Defaults to "archives/tech_specs.ini".
      header(str):
        Section break header.

    Returns:
      A list wherein each element is a dict representing a single movie.
    """
    print(
        f"\n{header}\n"
        "\nImporting movies from file...\n"
    )
    parser = ConfigParser()
    parser.read(iniFile)
    bcParser = ConfigParser()
    bcParser.read(upcs)
    
    movies = {}
    boutiques = import_boutiques(
        parser=parser,
        dataHeader="boutiqueLabels"
    )
    genres = import_current_genres(
        parser=parser,
        dataHeader="summary"
    )
    sortKey_swaps = import_sort_overrides(
        parser=parser,
        dataHeader="sortKeys"
    )
    with open(file) as f:
        csvr = csv.DictReader(f)
        for i in csvr:
            print(f'"{i["title"]}" imported.')
            groups = []
            name = transform_title(i["title"])
            sort_key = gen_sort_key(i["title"])
            if sort_key in sortKey_swaps.keys():
                sort_key = sortKey_swaps[sort_key]
            director = cell_sort(i["director"])
            writer = cell_sort(i["writer"])
            dp = cell_sort(i["cinematographer"])
            composer = cell_sort(i["composer"])
            editor = cell_sort(i["editor"])
            if i["hdr"].lower() == "dolby vision":
                groups.append("hdr10_dv")
            elif i["hdr"].lower() == "hdr10":
                groups.append("hdr10")
            else:
                groups.append(i["format"].lower())
            if i["color"].lower() == "false":
                groups.append("black_white")
            if i["animation"].lower() == "true":
                groups.append("animation")
            if i["publisher"] in boutiques:
                groups.append("boutique")
            if i["steelbook"].lower() == "true":
                groups.append("steelbook")
            if i["slipcover"].lower() == "true":
                groups.append("slipcover")
            if i["caseReplacement"].lower() == "true":
                groups.append("case_replacement")
            mv = {
                "groups" : groups,
                "data" : {
                    "title" : i["title"],
                    "year" : int(i["releaseYear"]),
                    "runtime" : int(i["runtime"]),
                    "director" : director,
                    "crew" : {
                        "writer" : writer,
                        "cinematographer" : dp,
                        "composer" : composer,
                        "editor" : editor
                    },
                },
                "sort_key" : sort_key,
            }
            import_release_data(i, mv, bcParser, name)
            import_mpaa_data(i, mv)
            import_genres(i, mv, genres)
            movies[name] = mv
    print("\n--Import complete.")
    
    return movies


def import_mpaa_data(csvRow: dict, movieDict: dict):
    """Appends MPAA ratings data for eligible pictures.

    Args:
      csvRow(dict):
        An individual row read into mem using the data.import_movies_csv
        func.
      movieDict(dict):
        Transformed Python-native dict synthesized from csv_row data
        using the data.import_movies_csv func.
    """
    rating = cell_sort(csvRow["mpaa"])
    if isinstance(rating, str):
        rating = rating.upper()
    reason = cell_sort(csvRow["mpaa_reason"])
    alt_title = cell_sort(csvRow["alt_title"], "; ")
    if rating is not None:
        mpaa = {
            "certificate" : int(csvRow["mpaa_cert"]),
            "rating" : rating,
            "reason" : reason,
            "distributor" : csvRow["distributor"],
            "alt_title" : alt_title,
        }
        movieDict["data"]["mpaa"] = mpaa


def import_release_data(
    csvRow: dict,
    movieDict: dict,
    parser: ConfigParser,
    mvName: str,
    dataHeader: str="barcodes"
):
    """Imports details specific to the release for each movie in DB.

    Adds the publisher info, number of discs, and aspect ratio details
    for each movie. Func also attempts to add the UPC data from the CSV
    file. If it is not found there, it checks the barcodes.ini file in
    archives. If the UPC value still is not present, the value is set to
    None.

    The import is handled in place with no value returned by the func.

    Args:
      csvRow(dict):
        An individual row read into mem using the data.import_movies_csv
      movieDict(dict):
        Dict of movies returned via data.import_movies_csv func.
      parser(ConfigParser):
        ConfigParser object which has already read the INI file into
        memory and stored in class instance using
        ConfigParser.read(INIfile) method.
        func.
      mvName(str):
        Top-level key for a single movie dict inside movieDict.
      dataHeader(str):
        Section header for barcode data in INI file.

    Returns:
      None
    """
    release = {
        "publisher" : csvRow["publisher"],
        "upc" : None,
        "discs" : int(csvRow["discs"]),
        "aspect_ratio" : float(csvRow["aspectRatio"])
    }
    try:
        release["upc"] = int(csvRow["upc"])
    except(KeyError, ValueError):
        try:
            release["upc"] = int(parser.get(dataHeader, mvName))
        except NoOptionError:
            pass
    movieDict["data"]["release"] = release


def import_sort_overrides(parser: ConfigParser, dataHeader: str):
    """Imports sortKey overrides from INI file.

    To prevent Python from producing an undesirable alpha sort of the
    catalog data, certain manual overrides are stored via INI file and
    read into memory by ConfigParser. These overrides are then
    substituted in place by the import_movies_csv func.

    This override data is stored and returned as key/value pairs in a
    dict using the following format:

        {
            "matrix" : "martix_1",
            "matrix_reloaded" : "matrix_2-reloaded",
            "matrix_revolutions" : "matrix_3-revolutions"
        }

    Args:
      parser(ConfigParser):
        ConfigParser object which has already read the INI file into
        memory and stored in class instance using
        ConfigParser.read(INIfile) method.
      data_header(str):
        Section header for sortKey override pairs in INI file.

    Returns:
      A dict of override substitution pairs.
    """
    overrides = {}
    keys = parser.options(dataHeader)
    for key in keys:
        overrides[key] = parser.get(dataHeader, key)
    
    return overrides


def sort_catalog(movieDict: dict, sortKey_list: list, dataHeader: str):
    """Sorts movie list into desired order.

    The entire movie DB dict is reordered using the sortKey_list as a
    sequence guide. The sortKey_list should already have been sorted
    into the desired order prior to being passed to sort_catalog func
    as it is not transformed.

    This reordered dict is returned and can subsequently be exported
    for use with Nornir.

    Args:
      movieDict(dict):
        Comprehensive dict of movies, created via CSV or YML import.
      sortKey_list(list):
        List of sortKeys. Should already be in desired sort order.
      dataHeader(str):
        Key used to access sortKey value inside the movie dicts.

    Returns:
      Sorted comprehensive dict ready for export.
    """
    sortedDict = {}
    for sortKey in sortKey_list:
        for movie in movieDict.keys():
            if movieDict[movie][dataHeader] == sortKey:
                sortedDict[movie] = movieDict[movie]
    
    return sortedDict


def transform_title(title: str):
    """Formats the title to set as key value inside Nornir inventory.

    The key/value pairs of dict "subs" are used to make punctuation
    substitutions in the film's title before returning it in a
    lowercase string.

    Args:
      title(str):
        The film's official title.

    Returns:
      The newly formatted name.
    """
    subs = {
        "'" : "",
        "." : "",
        ": " : "-",
        " " : "_",
    }

    for k,v in subs.items():
        title = title.replace(k, v)
    
    return title.lower()


def write_barcodes(
    movieDict: dict,
    iniFile: str="archives/barcodes.ini",
    dataHeader: str="barcodes"
):
    """Exports the current inventory's UPCs to INI file.

    Generates dict of barcodes with the inventory's movie keys & UPC
    values stored as KV pairs.

    The function then instantiates a ConfigParser instance using the
    dataHeader value as the default section. The barcodes are
    written by ConfigParser to the specified INI file.

    Args:
      movieDict(dict):
        Python dict with root keys representing each title in the
        catalog.
      iniFile(str):
        The name of the ini file written by this method. Defaults
        to 'archives.barcodes.ini'.
      dataHeader(str):
        Section header for barcode data in resulting INI file.

    Returns:
      None
    """
    barcodes = {}
    for movie in movieDict.keys():
        barcodes[movie] = movieDict[movie]["data"]["release"]["upc"]
    parser = ConfigParser(default_section=dataHeader)
    parser[dataHeader] = barcodes

    with open(iniFile, "w") as f:
        parser.write(f)
