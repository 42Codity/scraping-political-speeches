require(readr)
require(koRpus)
install.koRpus.lang("en")
require("koRpus.lang.en")
mean.na <- function(x) {
  mean(x, na.rm = T)
}

# Load in the dataframe of maiden speeches and new MPs scraped from Hansard data
maiden_speeches <- read_csv("~/Thesis - political language and voting behaviour/R - thesis analysis/scraped_maiden_speeches.csv")
maiden_speeches$date <- as.Date(maiden_speeches$date, format = "%d/%m/%Y")

# Then we want to save each speech as new .txt file with the name of the MP and their cohort as identifiers:
for (i in 1:length(maiden_speeches$mp_name)) {
  custom_file_name <- paste0("~/Thesis - political language and voting behaviour/R - thesis analysis/txtspeeches/",
                            maiden_speeches$first_name[i], "_", maiden_speeches$surname[i], "_", maiden_speeches$cohort[i])
  cleaned_speech <- data.frame(gsub("\n", " ", maiden_speeches$speech[i]))
  write_tsv(cleaned_speech, custom_file_name)
}
# Now we have a folder full of saved .txt files containing each maiden speech

# The following function extracts the Automated Readability Index (ARI) for a given text file. First, the MP's first and last name
# are combined to make a label for the speech. Then the speech is tokenized, i.e. broken down into individual words as components.
# The next step is to hyphenate the speech, which automatically breaks the speech up into syllables. Finally, ARI is calculated from
# this list of tokens and its hyphenated counterpart - and the final ARI is returned as the output
extractARI <- function(speech, first_name, surname) {
  doc_label <- paste0(first_name, "_", surname)
  tokenized_speech <- koRpus::tokenize(speech, lang = "en", doc_id = doc_label)
  hyphen_speech <- koRpus::hyphen(tokenized_speech)
  readability_speech <- koRpus::readability(tokenized_speech, hyphen = hyphen_speech)
  ari_speech <- readability_speech[1]
  return(ari_speech)
}

# We iteratively apply this function to every maiden speech for each MP in the dataset, save the results to a vector, and then enter
# this as a column in the dataframe
ARI <- vector("list", length = length(maiden_speeches$mp_name))
for (i in 1:length(maiden_speeches$mp_name)) {
  custom_file_name <- paste0("~/Thesis - political language and voting behaviour/R - thesis analysis/txtspeeches/",
                             maiden_speeches$first_name[i], "_", maiden_speeches$surname[i], "_", maiden_speeches$cohort[i])
  ARI[i] <- extractARI(custom_file_name, maiden_speeches$first_name[i], maiden_speeches$surname[i])
}
maiden_speeches$ARI <- unlist(ARI)

# We can see how the ARI of speeches have changed over time, and for each party
plot(x = maiden_speeches$date, y = maiden_speeches$ARI,
     xlab = "Date of speech", ylab = "Automated Readability Index", 
     main = "ARI of maiden speeches over time")
plot(x = maiden_speeches[maiden_speeches$party == "Lab",]$date, y = maiden_speeches[maiden_speeches$party == "Lab",]$ARI, col = "red",
     xlab = "Date of speech", ylab = "Automated Readability Index", 
     main = "ARI of Labour maiden speeches over time")
plot(x = maiden_speeches[maiden_speeches$party == "Con",]$date, y = maiden_speeches[maiden_speeches$party == "Con",]$ARI, col = "blue",
     xlab = "Date of speech", ylab = "Automated Readability Index", 
     main = "ARI of Conservative maiden speeches over time")

# The between-party pattern is a little hard to see, so we can aggregate (mean) by cohort and party:
agg.maiden_speeches <- maiden_speeches
agg.maiden_speeches[agg.maiden_speeches$cohort == "1974a" | agg.maiden_speeches$cohort == "1974b",9] <- "1974"
agg.maiden_speeches$cohort <- as.numeric(agg.maiden_speeches$cohort)
agg.maiden_speeches <- aggregate(data = agg.maiden_speeches, ARI ~ cohort + party, mean.na)
head(agg.maiden_speeches)

# Then we can plot these results, to see how Conservative and Labour maiden speech ARIs change over time
plotdata <- subset(agg.maiden_speeches, party %in% c("Lab", "Con"))
require(ggplot2)
ggplot(data = plotdata, aes(x = cohort, y = ARI)) + 
  geom_line(aes(colour = party)) +
  scale_color_manual(values = c("blue", "red")) +
  xlab("Year") + ylab("Automated Reading Index (ARI) score") +
  labs(title = "Readability of maiden speeches by party over time",
       caption = "Higher ARI scores indicate less readable (i.e. more complex) language. Lower ARI scores are more accessible to readers of lower education levels. An ARI below 8 should be accessible to 12-13 year olds, whereas an ARI above 12 is accessible to 16-17 year olds.")

# We can also rearrange the data into a wide format and then take the difference between average ARIs for each party in each cohort:
require(tidyr)
wider_plotdata <- pivot_wider(plotdata, id_cols = "cohort", values_from = "ARI", names_from = "party")
wider_plotdata$diff <- wider_plotdata$Con - wider_plotdata$Lab
# We can plot this difference along with colours indicating which party was in power at the time
ggplot(data = wider_plotdata, aes(x = cohort, y = diff)) +
  geom_line() + geom_hline(aes(yintercept = 0)) + 
  geom_rect(aes(xmin = 1935, xmax = 1945, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1945, xmax = 1951, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 1951, xmax = 1964, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1964, xmax = 1970, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 1970, xmax = 1974, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1974, xmax = 1979, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 1979, xmax = 1997, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1997, xmax = 2010, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 2010, xmax = 2021, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  xlab("Year") + ylab("Difference in readability of maiden speeches (Conservative - Labour)") +
  labs(title = "Difference in readability of Conservative and Labour maiden speeches over time",
       caption = "Positive values indicate periods where Labour maiden speeches were more readable (i.e. accessible) than Conservative maiden speeches. Negative values indicate periods where Conservative maiden speeches were more readable than those from Labour.")
  

# We can produce a different function for the Flesch reading ease measure
extractFRE <- function(speech, first_name, surname) {
  doc_label <- paste0(first_name, "_", surname)
  tokenized_speech <- koRpus::tokenize(speech, lang = "en", doc_id = doc_label)
  hyphen_speech <- koRpus::hyphen(tokenized_speech)
  readability_speech <- koRpus::readability(tokenized_speech, hyphen = hyphen_speech)
  fre_speech <- readability_speech[8]
  return(fre_speech)
}
# Then iteratively apply this function to each MP's speech and save the results to a vector, FRE
FRE <- vector("list", length = length(maiden_speeches$mp_name))
for (i in 1:length(maiden_speeches$mp_name)) {
  custom_file_name <- paste0("~/Thesis - political language and voting behaviour/R - thesis analysis/txtspeeches/",
                             maiden_speeches$first_name[i], "_", maiden_speeches$surname[i], "_", maiden_speeches$cohort[i])
  FRE[i] <- extractFRE(custom_file_name, maiden_speeches$first_name[i], maiden_speeches$surname[i])
}
# Then add this vector of results back into the original dataframe
maiden_speeches$FRE <- unlist(FRE)
# Plot the results by date
plot(x = maiden_speeches$date, y = maiden_speeches$FRE,
     xlab = "Date of speech", ylab = "Flesch reading ease measure", 
     main = "Flesch reading ease of maiden speeches over time")
plot(x = maiden_speeches[maiden_speeches$party == "Lab",]$date, y = maiden_speeches[maiden_speeches$party == "Lab",]$FRE, col = "red",
     xlab = "Date of speech", ylab = "Flesch reading ease measure", 
     main = "Flesch reading ease of Labour maiden speeches over time")
plot(x = maiden_speeches[maiden_speeches$party == "Con",]$date, y = maiden_speeches[maiden_speeches$party == "Con",]$FRE, col = "blue",
     xlab = "Date of speech", ylab = "Flesch reading ease measure", 
     main = "Flesch reading ease of Conservative maiden speeches over time")

# Again, we can aggregate by cohort to see the between-party pattern more clearly
agg.maiden_speeches <- maiden_speeches
agg.maiden_speeches[agg.maiden_speeches$cohort == "1974a" | agg.maiden_speeches$cohort == "1974b",9] <- "1974"
agg.maiden_speeches$cohort <- as.numeric(agg.maiden_speeches$cohort)
agg.maiden_speeches <- aggregate(data = agg.maiden_speeches, FRE ~ cohort + party, mean.na)
head(agg.maiden_speeches)
# Then we can plot these results, to see how Conservative and Labour maiden speech FREs change over time
plotdata <- subset(agg.maiden_speeches, party %in% c("Lab", "Con"))
require(ggplot2)
ggplot(data = plotdata, aes(x = cohort, y = FRE)) + 
  geom_line(aes(colour = party)) +
  scale_color_manual(values = c("blue", "red")) +
  xlab("Year") + ylab("Flesch reading ease (FRE) score") +
  labs(title = "Readability of maiden speeches by party over time",
       caption = "Higher FRE scores indicate more readable (i.e. less complex) language. Lower FRE scores are less accessible to readers of lower education levels. An FRE above 70 should be fairly easy for adult native speakers, whereas an FRE below 50 will be difficult for the average reader.")

# We can also rearrange the data into a wide format and then take the difference between average ARIs for each party in each cohort:
require(tidyr)
wider_plotdata <- pivot_wider(plotdata, id_cols = "cohort", values_from = "FRE", names_from = "party")
wider_plotdata$diff <- wider_plotdata$Lab - wider_plotdata$Con
# We can plot this difference along with colours indicating which party was in power at the time
ggplot(data = wider_plotdata, aes(x = cohort, y = diff)) +
  geom_line() + geom_hline(aes(yintercept = 0)) + 
  geom_rect(aes(xmin = 1935, xmax = 1945, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1945, xmax = 1951, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 1951, xmax = 1964, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1964, xmax = 1970, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 1970, xmax = 1974, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1974, xmax = 1979, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 1979, xmax = 1997, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1997, xmax = 2010, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 2010, xmax = 2021, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  xlab("Year") + ylab("Difference in readability of maiden speeches (Labour - Conservative)") +
  labs(title = "Difference in readability of Conservative and Labour maiden speeches over time",
       caption = "Positive values indicate periods where Labour maiden speeches were more readable (i.e. accessible) than Conservative maiden speeches. Negative values indicate periods where Conservative maiden speeches were more readable than those from Labour.")

wider_plotdata$lab_winner <- c(T, T, F, F, F, T, T, F, T, F, F, F, F, T, T, T, F, F, F, F)
wider_plotdata$lab_future_winner <- c(NA, T, T, F, F, F, T, T, F, T, F, F, F, F, T, T, T, F, F, F)
wider_plotdata$con_winner <- c(F, F, T, T, T, F, F, T, F, T, T, T, T, F, F, F, T, T, T, T)
wider_plotdata$con_future_winner <- c(NA, F, F, T, T, T, F, F, T, F, T, T, T, T, F, F, F, T, T, T)

require(estimatr)
# What types of maiden speeches are associated with Labour electoral victories?
naive_lab_lm <- lm_robust(data = wider_plotdata,
                          lab_winner ~ Lab + Con)
summary(naive_lab_lm)
# After Labour victories, Labour MPs tend to offer up less readable maiden speeches (and Conservatives offer more readable speeches)
naive_con_lm <- lm_robust(data = wider_plotdata,
                          con_winner ~ Lab + Con)
summary(naive_con_lm)
# And after Conservative victories, Conservative MPs have less readable maiden speeches (and Labour MPs have more readable speeches)
# So parties that have just won an election are likely to produce less readable speeches than MPs who end up in opposition

# What about when we use readability to forecast future electoral behaviour?
naive_lab_fut_lm <- lm_robust(data = wider_plotdata,
                          lab_future_winner ~ Lab + Con)
summary(naive_lab_fut_lm)
# Future Labour victories are (significantly) associated with reductions in the FRE (i.e. less readable maiden speeches in the parliament before)
# Moreover, a swing in the direction of complex/less readable speeches in general tends to forecast Labour success
naive_con_fut_lm <- lm_robust(data = wider_plotdata,
                          con_future_winner ~ Lab + Con)
summary(naive_con_fut_lm)
# And increases in readability from both Labour and Conservative MPs are associated with subsequent Conservative success


ggplot(data = plotdata, aes(x = cohort, y = FRE)) + 
  geom_line(aes(colour = party)) +
  scale_color_manual(values = c("blue", "red")) +
  geom_rect(aes(xmin = 1935, xmax = 1945, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1945, xmax = 1951, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 1951, xmax = 1964, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1964, xmax = 1970, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 1970, xmax = 1974, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1974, xmax = 1979, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 1979, xmax = 1997, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  geom_rect(aes(xmin = 1997, xmax = 2010, ymin = -Inf, ymax = Inf),
            fill = "red", alpha = 0.01) +
  geom_rect(aes(xmin = 2010, xmax = 2021, ymin = -Inf, ymax = Inf),
            fill = "blue", alpha = 0.01) +
  xlab("Year") + ylab("Flesch reading ease (FRE) score") +
  labs(title = "Readability of maiden speeches by party over time",
       caption = "Higher FRE scores indicate more readable (i.e. less complex) language. Lower FRE scores are less accessible to readers of lower education levels. An FRE above 70 should be fairly easy for adult native speakers, whereas an FRE below 50 will be difficult for the average reader.")
