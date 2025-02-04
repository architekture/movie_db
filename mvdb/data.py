import configparser
import csv
import yaml


def dump_movies_yaml(movie_list: list):
    """Transforms Python-native list of movies into YAML for Nornir.

    Args:
      movie_list(list):
        List of movies returned via data.import_movies func.

    Returns:
      A string value of the imported movie list transformed into YAML
      for use with Nornir.
    """
    export ="---"
    for i in movie_list:
        ym_blob = yaml.dump(i, sort_keys=False).replace("- ", "  - ")
        export += f"\n{ym_blob}"
    
    return export


def export_movies_yaml(yaml_blob: str, file_name: str):
    """Writes YAML file of the movie database for use with Nornir.

    Args:
      yaml_blob(str):
        The str blob returned via data.dump_movies_yaml func.
      file_name(str):
        The file name for the resulting YAML document.
    """
    with open(file_name, "w") as f:
        f.write(yaml_blob)


def import_current_genres(file: str="archives/genres.ini"):
    """Reads genres.ini file via ConfigParser and imports data.

    Args:
      file(str):
        Name including the file path of the INI file for ConfigParser
        to read and intepret. The default value is "archives/genres.ini".

    Returns:
      A list of currently supported genres, with each element
      representing a genre, subgenre or descriptor.
    """
    parser = configparser.ConfigParser()
    parser.read(file)
    genres = parser["GENRES"]["genres"].split(",")
    subgenres = parser["GENRES"]["subgenres"].split(",")
    descriptors = parser["DESCRIPTORS"]["descriptors"].split(",")
    genres.extend(subgenres)
    genres.extend(descriptors)

    return genres


def import_genres(csv_row: dict, movie_dict: dict, valid_genres: list):
    """Appends genre and descriptor data for movie database.
    
    Args:
      csv_row(dict):
        An individual row read into mem using the data.import_movies
        func.
      movie_dict(dict):
        Transformed Python-native dict synthesized from csv_row data
        using the data.import_movies func.
      valid_genres(list):
        List of genres imported using the import_current_genres func.
    """
    genres = []
    for genre in valid_genres:
        try:
            if csv_row[genre].lower() == "true":
                genres.append(genre)
        except KeyError:
            pass
    for v in movie_dict.values():
        v["data"]["genres"] = genres


def import_movies(file: str):
    """Converts movie .CSV file into structured Python data.
    
    Args:
      file(str):
        The file name of the movie DB in .CSV format.

    Returns:
      A list wherein each element is a dict representing a single movie.
    """
    movies = []
    # List of boutique publishers
    boutiques = [
        "Arrow Video",
        "Kino Lorber Studio Classics",
        "Shout! Factory LLC",
        "The Criterion Collection",
        "Unearthed Films"
    ]
    genres = import_current_genres()
    with open(file) as f:
        csvr = csv.DictReader(f)
        for i in csvr:
            groups = []
            name = i["title"].lower().replace(" ", "_")
            name = name.replace(":_", "-")
            name = name.replace("'", "")
            director = cell_sort(i["director"])
            writer = cell_sort(i["writer"])
            dp = cell_sort(i["cinematographer"])
            composer = cell_sort(i["composer"])
            editor = cell_sort(i["editor"])
            groups.append(i["format"].lower())
            if i["color"].lower() == "false":
                groups.append("black_white")
            if i["animation"].lower() == "true":
                groups.append("animation")
            if i["hdr"] == "dolby vision":
                groups.append("hdr10_dv")
            elif i["hdr"] == "hdr10":
                groups.append("hdr10")
            if i["publisher"] in boutiques:
                groups.append("boutique")
            if i["steelbook"].lower() == "true":
                groups.append("steelbook")
            if i["slipcover"].lower() == "true":
                groups.append("slipcover")
            if i["caseReplacement"].lower() == "true":
                groups.append("case_replacement")
            mv = {
                name : {
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
                        "aspect_ratio" : float(i["aspectRatio"]),
                        "publisher" : i["publisher"],
                        "discs" : int(i["discs"])
                    }
                }
            }
            import_mpaa_data(i, mv)
            import_genres(i, mv, genres)
            movies.append(mv)
    
    return movies


def import_mpaa_data(csv_row: dict, movie_dict: dict):
    """Appends MPAA ratings data for eligible pictures.
    
    Args:
      csv_row(dict):
        An individual row read into mem using the data.import_movies
        func.
      movie_dict(dict):
        Transformed Python-native dict synthesized from csv_row data
        using the data.import_movies func.
    """
    rating = cell_sort(csv_row["mpaa"])
    if isinstance(rating, str):
        rating = rating.upper()
    reason = cell_sort(csv_row["mpaa_reason"])
    # distro = cell_sort(csv_row["distributor"])
    alt_title = cell_sort(csv_row["alt_title"], "; ")
    mpaa = {"rating" : rating}
    if rating is not None:
        mpaa["reason"] = reason
        mpaa["distributor"] = csv_row["distributor"]
        mpaa["alt_title"] = alt_title
        mpaa["certificate"] = int(csv_row["mpaa_cert"])
    for v in movie_dict.values():
        v["data"]["mpaa"] = mpaa


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
