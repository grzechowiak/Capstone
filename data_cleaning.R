url <- "https://www1.nyc.gov/assets/planning/download/zip/data-maps/open-data/nyc_pluto_18v2_1_csv.zip"
filename <- "pluto_data.zip"
files <- unzip(download.file(url, filename))
df <- read.csv("pluto_18v2_1.csv")
file.remove(c(filename, "PLUTODD18v2.1.pdf", "PlutoReadme18v2.1.pdf"))
colnames(df)
