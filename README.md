# New Office Finder

This python script was created as part of an interview take-home project for a digital consulting company.

It takes in three sources of data and uses them to find the 10 best potential locations for a
new office.

Data Sources:
1. CSV file listing GDP for most EU countries, over the past few years (provided). Countries with an existing office do
not have GDPs listed and include the string "Offices in ..." instead.
2. Eurostat data for the percentage of GDP which is used by the ICT sector.
3. Eurostat data for the percentage of cloud computing services used by enterprise companies.

The "Attractiveness Score" of a country = GDP * percentage of ICT sector from GDP * usage of cloud computing in enterprises in a country


Notes:
Since the range of years available for each of the datasets is different, and some countries have missing data for recent years,
I used data from the last 3 years to supplement.

I used a SQLite database to store the raw data from each file and run the query to find the attractiveness. SQLite is
very small and fast, and is great for data analysis. However, if the user wanted to add this script as part of an application,
 a more persistent database would be a better choice.

To access the Eurostat database, I used the python library eurostat to request the data by using the internal code
for that topic. This library allows the user to access a pandas dataframe directly without having to convert
it from it's original json-stat state.


This is a very rough version of this script and is not meant to be production-ready. Here are some ideas for improvements:
1. Instead of a file, provide the output in a different format to be served to a front end client that will
display it with more style.
2. Chart the growth of each data point over time and give countries a ranking based on the speed they're growing in ICT,
GDP, or cloud computing, or a combination of factors.
3. Weight the various factors - maybe the percent of GDP should be given more weight than comparing countries' GDPs
directly, because if a GDP is smaller but the percent of IT is higher, this might be a good opportunity as well but
it won't end up ranked as high. for example, Malta has a high percent of ICT and CC, but a smaller GDP.
4.Supplement the GDP file with missing data - some countries do not have a recent GDP provided, which we need for the
attractiveness score. Look into using eurostat or another source for this data, especially for potentially attractive countries
such as the Netherlands and Portugal.
5. Use SQLAlchemy along with with SQLite to persist the database and expose the table schemata to a models.py file. Currently,
the tables in this script are meant to be temporary and rebuilt every time, but this wouldn't be efficient in the long term.
6. Add tests!