# Scraping Hansard in full

Archives of scraped Hansard debates are available in XML format from [TheyWorkForYou](https://www.theyworkforyou.com). In order to prepare these for analysis in Python, it is useful to access these XML files, and extract variables of interest. In particular, we are interested in:
 * _Date_ of the speech, for time series and trend comparisons;
 * _Content_ of the speech, for NLP/computational text analysis;
 * _Speaker_, in order to match speech characteristics with the social background of the speaker, e.g. using the [History of Parliament Online](https://membersafter1832.historyofparliamentonline.org/about) database;
 
 These variables of interest can then be saved to a Pandas DataFrame for merging with other contextual variables (e.g. speaker's social background) for analysis at a later date.
 
 The files in this folder should be run as follows:
 1. Run `hansard_scraper.ipynb` to get debate XML from the TheyWorkForYou site - target URLs are saved to `debate_urls.csv` and obtained XML are saved within the `debates_xml` folder;
 2. Run `mps_data.ipynb` to open a JSON file from the [ParlParse](http://parser.theyworkforyou.com/) project with details on MPs names, party affiliation, date of birth, etc. - these details are saved to `people.csv`. These files are needed to convert from 'speaker_ids', used by the TheyWorkForYou archive, and standardised speaker names;
 3. Run `hansard_parser.ipynb` to open each debate XML individually and parse it to obtain variables of interest - these are then stored in a Pandas DataFrame, saved to disk as `hansard_debates.csv`. This parser is dependent on `people.csv` for cross-tabulation between MP IDs and person IDs;
 4. Run `merging_speeches_and_mps.ipynb` to merge Hansard speeches with MPs name data - the merged dataset is saved to `hansard_with_mp_details.csv`;