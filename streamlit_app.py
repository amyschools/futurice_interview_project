import sqlite3
import pandas as pd
import eurostat
import streamlit as st
import altair as alt


st.title("Top 10 Potential Office Locations")
st.text(
    "The countries are ranked on their Attractiveness Score, which is:"
    "\nGDP * percentage of GDP made up of the ICT sector * usage of cloud"
    "\ncomputing in enterprise businesses."
)


@st.cache(hash_funcs={sqlite3.Connection: id})
def load_country_data(db_connection: sqlite3.Connection, filename: str) -> None:
    """
    Load a mapping of country names and country labels into the db to use for query joins,
    since the eurostat only returns an abbreviation and the GDP file only contains the
    full name.
    """
    df = pd.read_csv(filename)
    df.to_sql("country_mapping", db_connection, if_exists="replace")


@st.cache(hash_funcs={sqlite3.Connection: id})
def load_country_gdp(db_connection: sqlite3.Connection, filename: str) -> None:
    """
    Load a CSV file with GDP in billions per year per country.
    """
    df = pd.read_csv(filename, sep="|", keep_default_na=False)
    df.rename(columns={"Country": "country_name"}, inplace=True)
    df.replace(",", "", regex=True, inplace=True)
    # Ignore countries with existing offices
    df = df[~df["2008"].str.startswith("Office")]
    df.to_sql("gdp_by_country", db_connection, if_exists="replace", index=False)


@st.cache(hash_funcs={sqlite3.Connection: id})
def load_percent_ict_of_gdp(db_connection: sqlite3.Connection) -> None:
    """
    Request the json-stat data from eurostat for the percentage of GDP that is created by the ICT sector.
    Load dataframe into a db table.
    """
    df = eurostat.get_data_df("tin00074")
    df = df[df["nace_r2"].isin(["ICT"])]
    # Ignore unnecessary data
    df.drop(columns="nace_r2", inplace=True)
    df.rename(columns={"time\geo": "country_label"}, inplace=True)
    df.to_sql("percent_ict_of_gdp", db_connection, if_exists="replace", index=False)


@st.cache(hash_funcs={sqlite3.Connection: id})
def load_percent_ent_using_cloud_computing(db_connection: sqlite3.Connection) -> None:
    """
    Request the json-stat data from eurostat for the percentage of cloud computing services used by enterprise companies.
    Load dataframe into a db table.
    """
    df = eurostat.get_data_df("isoc_cicce_use")
    # Filter the data to match the custom query
    df = df[
        df["unit"].isin(["PC_ENT"])
        & df["indic_is"].isin(["E_CC"])
        & df["sizen_r2"].isin(["10_C10_S951_XK"])
    ]
    # Ignore unnecessary data
    df.drop(columns=["unit", "sizen_r2", "indic_is"], inplace=True)
    df.rename(columns={"time\geo": "country_label"}, inplace=True)
    df.to_sql("percent_ent_using_cc", db_connection, if_exists="replace", index=False)


@st.cache(hash_funcs={sqlite3.Connection: id}, suppress_st_warning=True)
def calculate_and_display_results(db_connection: sqlite3.Connection) -> None:
    """
    Query the sqlite db and output the results to a CSV file.
    """
    query = """
            SELECT 
            c.country_name,
            COALESCE(g."2019", g."2018") * COALESCE(e."2020", e."2018") * COALESCE(i."2018", i."2017")/1000000 
            AS attractiveness_score
            FROM gdp_by_country g
            JOIN countries c ON g.country_name= c.country_name
            JOIN cc_percent_ent e ON e.country_label = c.country_label
            JOIN ict_percent_gdp i ON i.country_label = c.country_label
            ORDER BY attractiveness_score DESC
            LIMIT 10
        """
    df = pd.read_sql(query, db_connection)
    c = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x="attractiveness_score",
            y=alt.Y("country_name", sort="-x"),
            tooltip=["attractiveness_score", "country_name"]
        )
    )

    st.altair_chart(c, use_container_width=True)

st.text("Made by Amy Schools")


if __name__ == "__main__":
    with sqlite3.connect("location_data.db") as conn:
        load_country_data(conn, "country_mapping.csv")
        load_country_gdp(conn, "gdp_data.csv")
        load_percent_ict_of_gdp(conn)
        load_percent_ent_using_cloud_computing(conn)
        calculate_and_display_results(conn)
