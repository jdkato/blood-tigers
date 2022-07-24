import pathlib
import datetime
import sqlite3

import streamlit as st
import pandas as pd

DB = pathlib.Path("2kaveragejoes.sqlite3")


@st.cache(allow_output_mutation=True)
def get_database_connection():
    return sqlite3.connect(DB, check_same_thread=False)


@st.cache(hash_funcs={sqlite3.Connection: id})
def get_standings(conn):
    df = pd.read_sql_query("SELECT * from Standings", conn)
    df = df.drop('index', axis=1)
    df.index = df.index + 1
    return df


@st.cache(hash_funcs={sqlite3.Connection: id})
def get_highs(conn):
    df = pd.read_sql_query("SELECT * from Highs", conn)
    df = df.drop('index', axis=1)
    df.index = df.index + 1
    return df


@st.cache(hash_funcs={sqlite3.Connection: id})
def get_team_summary(conn):
    df = pd.read_sql_query("SELECT * from Team", conn)
    df = df.drop('index', axis=1)
    df.index = df.index + 1
    return df


@st.cache(hash_funcs={sqlite3.Connection: id})
def get_opp_summary(conn):
    df = pd.read_sql_query("SELECT * from Opponent", conn)
    df = df.drop('index', axis=1)
    df.index = df.index + 1
    return df


@st.cache(hash_funcs={sqlite3.Connection: id})
def get_diff_summary(conn):
    df = pd.read_sql_query("SELECT * from Differential", conn)
    df = df.drop('index', axis=1)
    df.index = df.index + 1
    return df


@st.cache(hash_funcs={sqlite3.Connection: id})
def get_leaders(stat, gp, conn):
    df = pd.read_sql_query(f"SELECT * from {stat}", conn)
    df = df.drop('index', axis=1)
    df = df[(df["GP"] >= gp)]
    df = df.head(10)
    df = df.reset_index(drop=True)
    df.index = df.index + 1
    return df


if __name__ == "__main__":
    m_timestamp = DB.stat().st_mtime
    m_time = datetime.datetime.fromtimestamp(m_timestamp)
    m_day = m_time.strftime("%m/%d/%Y")

    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.warning("""
    ❗Please see the [screenshot guide][1] for information on how to best provide images of game boxscores.
    
    [1]: https://github.com/jdkato/blood-tigers#data-collection
    """)

    st.write(
        f"""
        # Welcome! :wave:
        
        **Last updated**: {m_day}
        
        This app tracks season-by-season stats for the [@2kaveragejoes][1] 
        league. The app is open source and maintained by **@The57thPick**. 
        
        See [GitHub][2] for more information.
        
        [1]: https://discord.gg/2VBR8dQ2gb
        [2]: https://github.com/jdkato/blood-tigers
        """
    )

    st.info(
        """
        👀 You can learn more about the league on [Instagram][1], [TikTok][2], or [Discord][3].
        
        [1]: https://www.instagram.com/2kaveragejoes/
        [2]: https://www.tiktok.com/@2kaveragejoes
        [3]: https://discord.gg/2VBR8dQ2gb
        """
    )

    db = get_database_connection()

    st.header("Season Standings")
    standings_df = get_standings(db)

    tab1, tab2 = st.tabs(["Overall", "By Group"])
    tab1.table(standings_df.style.format({"PCT": "{:.2f}", "Margin": "{:.2f}"}))

    g1_col, g2_col = tab2.columns(2)

    g1_col.caption("Group A")
    standings_a = standings_df.loc[standings_df['Team'].isin(["Blood Tigers", "Mudkats", "Eagles"])]
    standings_a = standings_a.reset_index(drop=True)
    g1_col.table(standings_a.style.format({"PCT": "{:.2f}", "Margin": "{:.2f}"}))

    g1_col.caption("Group B")
    standings_b = standings_df.loc[standings_df['Team'].isin(["CT6", "J2K", "Mambas"])]
    standings_b = standings_b.reset_index(drop=True)
    g1_col.table(standings_b.style.format({"PCT": "{:.2f}", "Margin": "{:.2f}"}))

    g2_col.caption("Group C")
    standings_c = standings_df.loc[standings_df['Team'].isin(["Kamikaze", "Hollywood", "Brick City"])]
    standings_c = standings_c.reset_index(drop=True)
    g2_col.table(standings_c.style.format({"PCT": "{:.2f}", "Margin": "{:.2f}"}))

    g2_col.caption("Group D")
    standings_d = standings_df.loc[standings_df['Team'].isin(["Deathrow", "Savage Air", "BMB"])]
    standings_d = standings_d.reset_index(drop=True)
    g2_col.table(standings_d.style.format({"PCT": "{:.2f}", "Margin": "{:.2f}"}))

    st.header(f"Team Stats")
    tab3, tab4, tab5 = st.tabs(["Team", "Opponent", "Differential"])



    st.header(f"Individual Stats")
    MIN_GP = st.slider('Minimum games', 1, 15, value=3)
    off_col, def_col = st.columns(2)

    # Offense

    off_col.caption("Points Per Game")
    pts_df = get_leaders("PTS", MIN_GP, db)
    off_col.table(pts_df.style.format({"PTS": "{:.2f}", "FG%": "{:.2f}"}))

    off_col.caption("Assists Per Game")
    ast_df = get_leaders("AST", MIN_GP, db)
    off_col.table(ast_df.style.format({"AST": "{:.2f}"}))

    off_col.caption("3 Pointers Per Game")
    tpm_df = get_leaders("TPG", MIN_GP, db)
    off_col.table(tpm_df.style.format({"3PG": "{:.2f}", "3P%": "{:.2f}"}))

    # Defense

    def_col.caption("Rebounds Per Game")
    reb_df = get_leaders("REB", MIN_GP, db)
    def_col.table(reb_df.style.format({"TRB": "{:.2f}"}))

    def_col.caption("Blocks Per Game")
    blk_df = get_leaders("BLK", MIN_GP, db)
    def_col.table(blk_df.style.format({"BLK": "{:.2f}"}))

    def_col.caption("Steals Per Game")
    stl_df = get_leaders("STL", MIN_GP, db)
    def_col.table(stl_df.style.format({"STL": "{:.2f}"}))

    st.header("Season Records")
    highs_df = get_highs(db)
    st.table(highs_df)
