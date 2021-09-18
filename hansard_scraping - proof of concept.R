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

# Proof of concept with Kim Leadbeater's 9th Sep 2021 maiden speech
dat <- readDebateXML("https://www.theyworkforyou.com/pwdata/scrapedxml/debates/debates2021-09-09c.xml")
kim_speeches <- subset(dat, speaker == "Kim Leadbeater")
maiden_speech <- kim_speeches[which.min(as.POSIXlt(paste(kim_speeches$date, kim_speeches$time))),]
maiden_speech <- maiden_speech[,c(3,5)]
maiden_speech
