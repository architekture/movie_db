import configparser
import csv
import yaml


def dump_movies_yaml(movie_list: list):
    """Transforms Python-native list of movies into YAML for Nornir.

    Args:
      movie_list(list):
        List of movies returned via data.import_movies func.
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


def import_current_genres(file: str):
    """Reads genres.ini file via ConfigParser and imports data.

    Args:
      file(str):
        Name including the file path of the INI file for ConfigParser
        to read and intepret.
    """
    parser = configparser.ConfigParser()
    parser.read(file)
    genres = parser["GENRES"]["genres"].split(",")
    subgenres = parser["GENRES"]["subgenres"].split(",")
    descriptors = parser["DESCRIPTORS"]["descriptors"].split(",")
    genres.extend(subgenres)
    genres.extend(descriptors)

    return genres


def import_genres(csv_row: dict, movie_dict: dict):
    """Appends genre and descriptor data for movie database.
    
    Args:
      csv_row(dict):
        An individual row read into mem using the data.import_movies
        func.
      movie_dict(dict):
        Transformed Python-native dict synthesized from csv_row data
        using the data.import_movies func.
    """
    genres = []
    if csv_row["action"] == "TRUE":
        genres.append("action")
    if csv_row["comedy"] == "TRUE":
        genres.append("comedy")
    if csv_row["fantasy"] == "TRUE":
        genres.append("fantasy")
    if csv_row["horror"] == "TRUE":
        genres.append("horror")
    if csv_row["mystery"] == "TRUE":
        genres.append("mystery")
    if csv_row["sciFi"] == "TRUE":
        genres.append("science fiction")
    if csv_row["western"] == "TRUE":
        genres.append("western")
    if csv_row["crime"] == "TRUE":
        genres.append("crime")
    if csv_row["noir"] == "TRUE":
        genres.append("noir")
    if csv_row["heist"] == "TRUE":
        genres.append("heist")
    if csv_row["martialArts"] == "TRUE":
        genres.append("martial arts")
    if csv_row["wuxia"] == "TRUE":
        genres.append("wuxia")
    if csv_row["dark"] == "TRUE":
        genres.append("dark")
    if csv_row["gritty"] == "TRUE":
        genres.append("gritty")
    if csv_row["dystopian"] == "TRUE":
        genres.append("dystopian")
    if csv_row["period"] == "TRUE":
        genres.append("period")
    if csv_row["violent"] == "TRUE":
        genres.append("violent")

    for v in movie_dict.values():
        v["data"]["genres"] = genres


def import_movies(file: str):
    """Converts movie .CSV file into structured Python data.
    
    Args:
      file(str):
        The file name of the movie DB in .CSV format.

    Returns:
      movies(list):
        Each element is a dict representing a single movie.
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
    with open(file) as f:
        csvr = csv.DictReader(f)
        for i in csvr:
            groups = []
            name = i["title"].lower().replace(" ", "_")
            name = name.replace(":_", "-")
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
                        "director" : i["director"],
                        "crew" : {
                            "writer" : i["writer"],
                            "cinematographer" : i["cinematographer"],
                            "composer" : i["composer"],
                            "editor" : i["editor"]
                        },
                        "aspect_ratio" : float(i["aspectRatio"]),
                        "publisher" : i["publisher"],
                        "discs" : int(i["discs"])
                    }
                }
            }
            if i["mpaa"] != "":
                import_mpaa_data(i, mv)
            import_genres(i, mv)
            split_collaborators(mv)
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
    if "," in csv_row["mpaa_reason"]:
        csv_row["mpaa_reason"] = csv_row["mpaa_reason"].split(",")
    elif csv_row["mpaa_reason"] == "":
        csv_row["mpaa_reason"] = None
    if ";" in csv_row["alt_title"]:
        csv_row["alt_title"] = csv_row["alt_title"].split("; ")
    elif csv_row["alt_title"] == "":
        csv_row["alt_title"] = None
    mpaa = {
        "rating" : csv_row["mpaa"].upper(),
        "reason" : csv_row["mpaa_reason"],
        "distributor" : csv_row["distributor"],
        "alt_title" : csv_row["alt_title"]
    }
    for k,v in movie_dict.items():
        v["data"]["mpaa"] = mpaa


def split_collaborators(movie_dict: dict):
    """Converts str values into lists for applicable crew fields.

    Args:
      movie_dict(dict):
        Transformed Python-native dict synthesized from csv_row data
        using the data.import_movies func.
    """
    for i in movie_dict.values():
        director = i["data"]["director"]
        writer = i["data"]["crew"]["writer"]
        cinematographer = i["data"]["crew"]["cinematographer"]
        composer = i["data"]["crew"]["composer"]
        editor = i["data"]["crew"]["editor"]
        if "," in director:
            i["data"]["director"] = director.split(",")
        if "," in writer:
            i["data"]["crew"]["writer"] = writer.split(",")
        if "," in cinematographer:
            i["data"]["crew"]["cinematographer"] = cinematographer.split(",")
        if "," in composer:
            i["data"]["crew"]["composer"] = composer.split(",")
        if "," in editor:
            i["data"]["crew"]["editor"] = editor.split(",")
