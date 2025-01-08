import csv
import yaml as ym


subdir = "archives/"
fileName = (subdir + "movies.csv")
movies = []
boutiques = [
    "Arrow Video",
    "Kino Lorber Studio Classics",
    "Shout! Factory LLC",
    "The Criterion Collection",
    "Unearthed Films"
]
# print(fileName)
export = "---"
with open(fileName) as f:
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
        for i in mv.values():
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
        blob = ym.dump(mv, sort_keys=False).replace("- ", "  - ")
        export += f"\n{blob}"

with open(f"{subdir}movies.yml", "w") as f:
    f.write(export)