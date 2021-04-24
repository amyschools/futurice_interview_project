import sqlite3
import pandas
import eurostat


def load_country_data(conn, filename):
    df = pandas.read_csv(filename)
    df.to_sql("country_mapping", conn, if_exists="replace")


def load_country_gdp(conn, filename):
    df = pandas.read_csv(filename, sep="|", keep_default_na=False)
    df.rename(columns={"Country": "country_name"}, inplace=True)
    df.replace(",", "", regex=True, inplace=True)
    df = df[~df["2008"].str.startswith("Office")]
    df.to_sql("gdp_by_country", conn, if_exists="replace", index=False)


def load_percent_ict_of_gdp(conn):
    df = eurostat.get_data_df("tin00074")
    df = df[df["nace_r2"].isin(["ICT"])]
    df.drop(columns="nace_r2", inplace=True)
    df.rename(columns={"time\geo": "country_label"}, inplace=True)
    df.to_sql("percent_ict_of_gdp", conn, if_exists="replace", index=False)


def load_percent_ent_using_cloud_computing(conn):
    df = eurostat.get_data_df("isoc_cicce_use")
    df = df[
        df["unit"].isin(["PC_ENT"])
        & df["indic_is"].isin(["E_CC"])
        & df["sizen_r2"].isin(["10_C10_S951_XK"])
    ]
    df.drop(columns=["unit", "sizen_r2", "indic_is"], inplace=True)
    df.rename(columns={"time\geo": "country_label"}, inplace=True)
    df.to_sql("percent_ent_using_cc", conn, if_exists="replace", index=False)


def calculate_results(conn, filename):
    query = """
            SELECT 
            c.country_name,
            COALESCE(g."2019", g."2018") AS country_gdp,
            COALESCE(e."2020", e."2018") AS percent_ecc,
            COALESCE(i."2018", i."2017") AS percent_ict,
            COALESCE(g."2019", g."2018") * COALESCE(e."2020", e."2018") * COALESCE(i."2018", i."2017") AS attractiveness_score
            FROM gdp_by_country g
            JOIN countries c ON g.country_name= c.country_name
            JOIN cc_percent_ent e ON e.country_label = c.country_label
            JOIN ict_percent_gdp i ON i.country_label = c.country_label
            ORDER BY attractiveness_score DESC
            LIMIT 10
        """
    df = pandas.read_sql(query, conn)
    df.to_csv(filename, index=False)


if __name__ == "__main__":
    with sqlite3.connect("location_data.db") as conn:
        load_country_data(conn, "country_mapping.csv")
        load_country_gdp(conn, "gdp_data.csv")
        load_percent_ict_of_gdp(conn)
        load_percent_ent_using_cloud_computing(conn)
        calculate_results(conn, "top_10_most_attractive_locations.csv")


# NOTES
# skipped importing the countries with offices into the country gdp table
# the custom query on the eurostat db for percent cc did not include 2020 but I included it in this

# Attractiveness of a country = GDP * percentage of ICT sector from GDP * usage of cloud computing in enterprises in a country
