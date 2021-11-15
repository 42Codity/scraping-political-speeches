library(readr)
library(stringr)

# We need to read in the set of debate urls from TheyWorkForYou:
debate_urls <- read_csv("~/Thesis - political language and voting behaviour/R - thesis analysis/debate_urls.csv")

# We can extract the speech date from each of these urls, as well as the suffix after the date
debate_urls$speech_date <- as.Date(substr(debate_urls$url_name, 8, 17))
debate_urls$suffix <- str_sub(debate_urls$url_name, 18, -5) 
head(debate_urls)

# Then we can convert the suffixes to a numeric code: 0 represents "", 1 represents "a", 2 represents "b", and so on:
debate_urls$numeric_suffix <- ifelse(debate_urls$suffix == "", 0,
                                     ifelse(debate_urls$suffix == "a", 1,
                                            ifelse(debate_urls$suffix == "b", 2,
                                                   ifelse(debate_urls$suffix == "c", 3,
                                                          ifelse(debate_urls$suffix == "d", 4,
                                                                 ifelse(debate_urls$suffix == "e", 5, 
                                                                        ifelse(debate_urls$suffix == "f", 6,
                                                                               ifelse(debate_urls$suffix == "g", 7,
                                                                                      NA))))))))
head(debate_urls)
sum(is.na(debate_urls$numeric_suffix))
# So we've captured all of the suffixes with our numeric code

# Then we can aggregate(max) by date to find the highest numeric suffix for each date
suffixes <- aggregate(data = debate_urls, numeric_suffix ~ speech_date, max)
suffixes$suffix <- ifelse(suffixes$numeric_suffix == 0, "",
                          ifelse(suffixes$numeric_suffix == 1, "a",
                                 ifelse(suffixes$numeric_suffix == 2, "b",
                                        ifelse(suffixes$numeric_suffix == 3, "c",
                                               ifelse(suffixes$numeric_suffix == 4, "d",
                                                      ifelse(suffixes$numeric_suffix == 5, "e",
                                                             ifelse(suffixes$numeric_suffix == 6, "f",
                                                                    ifelse(suffixes$numeric_suffix == 7, "g",
                                                                           NA_character_))))))))
suffixes <- suffixes[,-2]
head(suffixes)

# Then we can save this list of suffixes as a .csv, and use it as the 'scrape_version' in our extractMaidenSpeech function
write_csv(suffixes, "~/Thesis - political language and voting behaviour/R - thesis analysis/suffixes.csv")
