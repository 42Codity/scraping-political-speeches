# PMQs transcripts

Archives of scraped Hansard debates are available in XML format from [TheyWorkForYou](https://www.theyworkforyou.com). These contain transcripts of PMQs, which has occured roughly weekly during Parliamentary sittings since the 1970s. To prepare these for analysis in Python, it is useful to access these XML files, identify which of them contain PMQs sessions, and then to parse those PMQs sessions into a tabular format. In particular, we are interested in:
 * _Date_ of the PMQs session, for time series and trend comparisons;
 * _Question characteristics_: we want to know the identity of the questioner, their constituency, party, age, and place of birth, as well as the raw text of the question;
 * _Answer characteristics_: the same characteristics but for the answerer, i.e. the Prime Minister;
 
These variables of interest can then be saved to a Pandas DataFrame with question/answer pairs.
 
 The files in this folder should be run as follows:
 1. Run `pmqs_finder.ipynb` to use the `hansard-in-full/debates_xml` folder of debates (may required decompression first) to identify potential dates of PMQs sessions, and save to `pmqs_dates.csv`;
 2. Run `pmqs_parser.ipynb` to search individual debate transcripts for a PMQs session, and extract question/answer pairs, then join with biographical and parliamentary details of particular MPs using `hansard-in-full/people.csv`;
