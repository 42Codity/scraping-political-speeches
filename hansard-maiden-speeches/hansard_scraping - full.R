require(XML)
require(stringi)

readFile <- function(fileName) {
  lines <- readLines(fileName, encoding = "UTF-8")
  return(paste(lines, collapse = '\n'))
}

readDebateDir <- function(dir) {
  files <- list.files(dir, full.names = TRUE, recursive = TRUE, pattern = "\\.xml$")
  result <- data.frame()
  for(file in files){
    result <- rbind(result, readDebateXML(file))
  }
  return(result)
}

readDebateXML <- function(file) {
  cat('Reading', file, '\n')
  xml <- xmlParse(readFile(file))
  result <- data.frame()
  for(speech in getNodeSet(xml, '//speech')){
    values <- getSpeech(speech)
    temp <- data.frame(date = values[[1]], 
                       time = values[[2]], 
                       speaker = values[[3]], 
                       personId = values[[4]], 
                       text = values[[5]], 
                       file = file, stringsAsFactors = FALSE)
    result <- rbind(result, temp)
  }
  return(result)
}

getSpeech <- function(speech) {
  
  attribs <- xmlAttrs(speech)
  #print(xmlAttrs(speech, "speakername"))
  if ("speakername" %in% names(attribs)){
    speaker = attribs[['speakername']]
  } else {
    speaker = ""
  }
  if ("person_id" %in% names(attribs)){
    personId = getPersonId(attribs[['person_id']])
  } else {
    personId = ""
  }
  if ("id" %in% names(attribs)){
    date = getDate(attribs[['id']])
  } else {
    date = ""
  }
  if ("time" %in% names(attribs)){
    time = getTime(attribs[['time']])
  } else {
    time = ""
  }
  text <- getSpeechText(speech)
  list(date, time, speaker, personId, text)
}

getSpeechText <- function(x) {
  ps <- unlist(xpathApply(x, './p', xmlValue))
  text <- paste(unlist(ps), collapse = "\n")
  return(stri_trim(text))
}

getTime <- function(x) {
  
  parts <- unlist(stri_split_fixed(x, ':'))
  h <- as.numeric(parts[1])
  m <- as.numeric(parts[2])
  s <- as.numeric(parts[3])
  return(paste(h, m, s, sep = ':'))
}

getDate <- function(x) {
  parts <- unlist(stri_split_fixed(x, '/'))
  date <- stri_sub(parts[3], 1, 10)
  return(date)
}

getPersonId <- function(x) {
  parts <- unlist(stri_split_fixed(x, '/'))
  return(parts[3])
}

require(readr)
require(stringr)

# In order to effectively scrape maiden speeches from Hansard, we need to be able to first search for dates upon which maiden speeches were given,
# and then subset by speaker name. Then, we take their first speech of the day - and this is the maiden speech for that MP
maiden_speeches <- read_csv("~/Thesis - political language and voting behaviour/R - thesis analysis/maiden_speeches.csv")
maiden_speeches$date <- as.Date(maiden_speeches$date, format = "%d/%m/%Y")
head(maiden_speeches)

# We need to combine this dataset with the list of suffixes extracted separately
suffixes <- read_csv("~/Thesis - political language and voting behaviour/R - thesis analysis/suffixes.csv")
head(suffixes)
# TheyWorkForYou maintain several different 'scrape versions' for each debate day. We need to specify which scrape version we want to access - the
# most recent one: suffixes.csv contains the scrape version for the most recent of each of these dates (and NA where no version can be found)
maiden_speeches <- merge(maiden_speeches, suffixes, by.x = "date", by.y = "speech_date", all.x = T)
head(maiden_speeches)

# We can create a function which takes MP names, debate dates, and scrape versions as inputs. The debate date and scrape version are pasted together
# to make a URL from which the debate .xml file can be read. Then, we subset for those speeches in the .xml file where the name of the MP appears in
# the name of the speech-giver (with non-alphabetical or space characters removed - sometimes speakers names are formatted weirdly on TheyWorkForYou
# so 'Mr. Bootle' is entered as 'Mr. Bootle (', with the unclosed bracket throwing an error in R), or vice versa. We return the speech column (index 
# 5) of the first entry (index 1) - otherwise, if no matching speaker can be identified, NA is returned
extractMaidenSpeech <- function(speaker_name, debate_date, scrape_version) {
  url <- paste0("https://www.theyworkforyou.com/pwdata/scrapedxml/debates/debates", debate_date, scrape_version, ".xml")
  dat <- readDebateXML(url)
  speeches <- subset(dat, str_detect(str_to_lower(gsub("[^a-zA-Z]", "", speaker)), str_to_lower(gsub("[^a-zA-Z]", "", speaker_name))) | 
                       str_detect(str_to_lower(gsub("[^a-zA-Z]", "", speaker_name)), str_to_lower(gsub("[^a-zA-Z]", "", speaker))))
  if (length(speeches > 0)) {
    return(speeches[1,5])
  }
  else NA
}

# We can then apply this function to each row of the maiden_speeches dataset, using mp_name to identify target speakers, date to find the debate_date,
# and suffix for the scrape_version. In some cases, where suffix = NA, then no debate can be found for that particular date, and so NA is returned
maiden_speech_results <- vector("list", length = length(maiden_speeches$mp_name))
for (i in 1:length(maiden_speeches$mp_name)) {
  maiden_speech_results[i] <- ifelse(!is.na(maiden_speeches$suffix[i]),
                                     extractMaidenSpeech(speaker_name = maiden_speeches$mp_name[i],
                                                         debate_date = maiden_speeches$date[i],
                                                         scrape_version = maiden_speeches$suffix[i]),
                                     NA)
}

# We can then save this vector in a character format
maiden_speeches$speech <- maiden_speech_results
sum(is.na(maiden_speeches$speech))
# So, we're missing speeches for 926 MPs

# Then we can subset for MPs for which we have no maiden speech:
missing_speeches <- subset(maiden_speeches, is.na(maiden_speeches$speech))
missing_speech_results <- vector("list", length = length(missing_speeches$surname))
for (i in 1:length(missing_speech_results$surname)) {
  missing_speech_results[i] <- ifelse(!is.na(missing_speeches$suffix[i]),
                                     extractMaidenSpeech(speaker_name = missing_speeches$surname[i],
                                                         debate_date = missing_speeches$date[i],
                                                         scrape_version = missing_speeches$suffix[i]),
                                     NA)
}
missing_speeches$speech <- missing_speech_results
sum(is.na(missing_speeches$speech))
# Now only 215 missing speeches - we can check to see their distribution
hist(missing_speeches[is.na(missing_speeches$speech),]$date, breaks = 10,
     xlab = "Date", main = "Missing maiden speeches by date of speech")
# We have a lot of missing speeches towards the start of the sample, and lots missing from the 1997 intake
barplot(sort(summary.factor(missing_speeches[is.na(missing_speeches$speech),]$party), decreasing = T),
        col = c("red", "blue", "yellow", "gold", "lightblue", "grey", "white", "darkgreen", "darkred"),
        xlab = "Party", ylab = "Number of missing maiden speeches", main = "Missing maiden speeches by political party")


# Then we can combine these surname-matched speeches with the maiden speeches identified with full names:
maiden_speeches <- maiden_speeches[!is.na(maiden_speeches$speech),]
maiden_speeches <- rbind(maiden_speeches, missing_speeches)

# Then some descriptive statistics on the maiden speeches we have:
hist(maiden_speeches[!is.na(maiden_speeches$speech),]$date, breaks = 10,
     xlab = "Date", main = "Maiden speeches by date of speech")
# A fairly even distribution - which is good to see
barplot(sort(summary.factor(maiden_speeches[!is.na(maiden_speeches$speech),]$party), decreasing = T)[1:10],
        col = c("red", "blue", "yellow", "gold", "lightblue", "yellow", "white", "grey", "darkgreen", "green"),
        xlab = "Party", ylab = "Number of maiden speeches", main = "Maiden speeches by political party")
# A clear majority for the two major parties
hist(maiden_speeches[!is.na(maiden_speeches$speech) & maiden_speeches$party == "Lab",]$date, breaks = 10,
     xlab = "Date", main = "Maiden speeches from Labour MPs by date of speech", col = "red")
# Good to see that spikes in maide speeches come with the change in fortunes of major parties - lots of Labour maiden speeches in 1945, 1964, and 1997
hist(maiden_speeches[!is.na(maiden_speeches$speech) & maiden_speeches$party == "Con",]$date, breaks = 10,
     xlab = "Date", main = "Maiden speeches from Conservative MPs by date of speech", col = "blue")
# Lots of Conservative maiden speeches in 1951, 1974, 1979, and 2010

# So, after a quick inspection, we can write this maiden speech dataset into a .csv file
write_csv(maiden_speeches, "~/Thesis - political language and voting behaviour/R - thesis analysis/scraped_maiden_speeches.csv")
