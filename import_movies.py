import mvdb.data


subdir = "archives/"

file = subdir + "movies.csv"
output = subdir + "movies.yml"

daMovies = mvdb.data.import_movies(file)
daYammies = mvdb.data.dump_movies_yaml(daMovies)

mvdb.data.export_movies_yaml(daYammies, output)