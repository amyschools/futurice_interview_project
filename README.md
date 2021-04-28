# New Office Finder

### View the results! https://share.streamlit.io/amyschools/new_office_finder


This python script was created as part of an interview take-home project for a digital consulting company. It takes in three sources of data and uses them to find the best potential locations for a new office. 

Data Sources:
1. CSV file listing GDP for most EU countries, over the past few years (provided). Countries with an existing office do
not have GDPs listed and include the string "Offices in ..." instead. 
2. Eurostat data for the percentage of GDP which is used by the ICT sector.
3. Eurostat data for the percentage of cloud computing services used by enterprise companies.

The "Attractiveness Score" of a country = `GDP * percentage of ICT sector from GDP * usage of cloud computing in enterprises in a country`

The data from each of these sources is lightly cleaned and ingested into a SQL table. A table called "county_mapping" is also created in order to use for querying joins, since the GDP file only includes the full country name, and the eurostat data has a country abbreviation. Once the data is queried and the score has been found, limit the results to 10, and divide the score by 1,000,000 to create a score out of 100 for readability.


### Technical choices:

I used a SQLite database to store the raw data from each file and run the query to find the attractiveness. SQLite is
very small and fast, and is great for data analysis. However, if the user wanted to add this script as part of a larger application, a persistent database would be a better choice.

To access the Eurostat database, I used the python library <a href="https://pypi.org/project/eurostat/">eurostat</a>
 to request the data by using the internal code for that topic. This library allows the user to access a pandas dataframe directly without having to convert
it from it's original json-stat state.

To create a chart showing the data, and deploy my python script as a very small web app, I used <a href="streamlit.io">Streamlit</a> with an interactive bar chart from the data visualization library Altair. You can hover over the bars to see the exact score for that country.


### Ideas for "productionizing" this script:

1. Provide the output in a different format such as an API endpoint that provides JSON to be served to a front end client that will
display it as part of a more cohesive web app.
2. Use SQLAlchemy along with with SQLite to persist the database and expose the table schemata to a models.py file. Currently,
the tables in this script are meant to be temporary and rebuilt every time, but this wouldn't be efficient in the long term, or if the user wanted to do more complex analysis.
3. Move the db from SQLlite to a persistent relational db, and define the table schemas and relations more cleanly. The DB could be hosted on AWS for cost savings.
4. Move the script to AWS as a Lambda that can be run as-needed or scheduled to run at certain intervals.
5. Add infrastructure - tests, logging, monitoring.


### Other Notes:

1. Since the range of years available for each of the datasets is different, and some countries have missing data for recent years,
I used data from the last 3 years.
2. For a different aspect of attractiveness, the user could chart the growth of each data point over time and give countries a ranking based on the speed they're growing in ICT,GDP, or cloud computing, or a combination of these.
3. The user could also weight the various factors - maybe the percent of GDP should be given more weight than comparing countries' GDPs
directly, because if a GDP is smaller but the percent of IT is higher, this might be a good opportunity as well but
it won't end up ranked as high. for example, Malta has a high percent of ICT and CC, but a smaller GDP that means it won't rank as highly using this algorithm, but perhaps it should still be considered.
4.Supplement the GDP file with missing data - some countries do not have a recent GDP provided, which we need for the
attractiveness score. Look into using eurostat or another source for this data, especially for potentially attractive countries
such as the Netherlands and Portugal.




