###Roger Valdez
###Data Science 
###Capstone Project

df <- read.csv("pluto_18v2_1.csv")
t(t(names(df)))

varlist <- df(c("block", "lot", "cd", "schooldist", "council", "zipcode", "firecomp", "policeprct",
                "zonedist1", "spdist1", "ltdheight", "landuse", "ownertype", "lotarea", "numbldgs",
                "numfloors", "unitsres", "unitstotal", "unitstotal", "ext", "irrlotcode", "lottype",
                "assessland", "assesstot", "yearbuilt", "yearalter1", "yearalter2", "borocode", "xcoord",
                "ycoord", "zonemap", "zmcode", "edesignum", "sanitdistrict", "healthcenterdistrict"))

