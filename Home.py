import pathlib
import datetime

import streamlit as st
import pandas as pd

from collections import defaultdict

DATA = pathlib.Path("csv")
MIN_GP = 3


def leaders(stat, show, stats_df, min):
    df = stats_df.sort_values(stat, ascending=False)
    df = df[(df["GP"] >= min)]
    df = df.head(10)
    df = df.reset_index(drop=True)

    return df[show]


def summary(season=1):
    players = []
    games = []

    made = []
    for filename in (DATA / f"s{season}" / "boxscores").glob("**/*.csv"):
        gdf = pd.read_csv(filename)
        games.append(gdf)
        players.extend(gdf["Player"])

    totals = pd.concat(games, axis=0, ignore_index=True)
    for player in set(players):
        games_played = players.count(player)

        fgm = float(totals.loc[totals["Player"] == player, "FGM"].sum())
        fga = float(totals.loc[totals["Player"] == player, "FGA"].sum())

        tpm = float(totals.loc[totals["Player"] == player, "3PM"].sum())
        tpa = float(totals.loc[totals["Player"] == player, "3PA"].sum())

        made.append(
            {
                "Player": player,
                "GP": games_played,
                "FGM": fgm,
                "FGA": fga,
                "FG%": fgm / fga if fga else 0,
                "3PM": tpm,
                "3PA": tpa,
                "3PG": tpm / games_played,
                "3P%": tpm / tpa if tpa else 0,
                "TRB": totals.loc[totals["Player"] == player, "REB"].sum()
                / games_played,
                "AST": totals.loc[totals["Player"] == player, "AST"].sum()
                / games_played,
                "STL": totals.loc[totals["Player"] == player, "STL"].sum()
                / games_played,
                "BLK": totals.loc[totals["Player"] == player, "BLK"].sum()
                / games_played,
                "TOV": totals.loc[totals["Player"] == player, "TO"].sum()
                / games_played,
                "PTS": totals.loc[totals["Player"] == player, "PTS"].sum()
                / games_played,
            },
        )

    df = pd.DataFrame.from_records(
        made,
        columns=[
            "Player",
            "GP",
            "FGM",
            "FGA",
            "FG%",
            "3PM",
            "3PA",
            "3PG",
            "3P%",
            "TRB",
            "AST",
            "STL",
            "BLK",
            "TOV",
            "PTS",
        ],
    )

    df = df.sort_values(by=["PTS"], ascending=False)
    df = df.reset_index(drop=True)

    return df


def compute_records():
    teams = pd.read_csv(DATA / "s1" / "teams.csv")

    records = []
    for i, entry in teams.iterrows():
        records.append(compute_record(entry["Team"]))

    df = pd.DataFrame(records)
    df = df.sort_values(by=["PCT", "GP"], ascending=False)
    df = df.reset_index(drop=True)

    return df


def compute_record(team):
    record = {"Team": team, "GP": 0, "Wins": 0, "PCT": 0, "Margin": []}

    games = (DATA / "s1" / "games").glob("**/*")
    for game in games:
        teams = [t.split(".csv")[0] for t in game.name.split("-")]
        if team in teams:
            idx = teams.index(team)
            rdf = pd.read_csv(game.absolute())

            team_score = rdf.iloc[idx, 5]
            high_score = rdf["Total"].max()

            record["GP"] += 1
            if high_score == team_score:
                record["Wins"] += 1
                record["Margin"].append(high_score - rdf["Total"].min())
            else:
                record["Margin"].append(team_score - high_score)

    if record["GP"] != 0:
        record["PCT"] = record["Wins"] / record["GP"]
        record["Margin"] = sum(record["Margin"]) / len(record["Margin"])
    else:
        record["PCT"] = 0.0
        record["Margin"] = 0.0

    return record


def highs():
    made = []

    recorded = {"PTS": 0, "3PM": 0, "REB": 0, "AST": 0, "STL": 0, "BLK": 0}
    r_to_p = defaultdict(list)
    for filename in (DATA / f"s1" / "boxscores").glob("**/*.csv"):
        gdf = pd.read_csv(filename)
        for k, v in recorded.items():
            rdf = gdf.loc[gdf[k].idxmax()]
            most = int(rdf[k])
            if most > v:
                recorded[k] = most
                r_to_p[k] = [rdf["Player"]]
            elif most == v:
                r_to_p[k].append(rdf["Player"])

    for k, v in recorded.items():
        made.append({"Stat": k, "Player(s)": ", ".join(r_to_p[k]), "Record": v})

    return pd.DataFrame(
        made,
        columns=[
            "Stat",
            "Player(s)",
            "Record",
        ],
    )


if __name__ == "__main__":
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    m_timestamp = DATA.stat().st_mtime
    m_time = datetime.datetime.fromtimestamp(m_timestamp)

    st.warning("""
    ❗Please see the [screenshot guide][1] for information on how to best provide images of game boxscores.
    
    [1]: https://github.com/jdkato/blood-tigers#data-collection
    """)

    st.write(
        f"""
        # Welcome! :wave:
        
        **Last updated**: {m_time.strftime("%m/%d/%Y")}
        
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

    stats_df = summary(season=1)

    st.header("Season Standings")
    standings_df = compute_records()

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

    st.header(f"Season Leaders")
    MIN_GP = st.slider('Minimum games', 1, 15, value=3)
    off_col, def_col = st.columns(2)

    # Offense

    off_col.caption("Points Per Game")
    pts_df = leaders("PTS", ["Player", "GP", "PTS", "FG%"], stats_df, MIN_GP)
    off_col.table(pts_df.style.format({"PTS": "{:.2f}", "FG%": "{:.2f}"}))

    off_col.caption("Assists Per Game")
    ast_df = leaders("AST", ["Player", "GP", "AST"], stats_df, MIN_GP)
    off_col.table(ast_df.style.format({"AST": "{:.2f}"}))

    off_col.caption("3 Pointers Per Game")
    tpm_df = leaders("3PG", ["Player", "GP", "3PG", "3P%"], stats_df, MIN_GP)
    off_col.table(tpm_df.style.format({"3PG": "{:.2f}", "3P%": "{:.2f}"}))

    # Defense

    def_col.caption("Rebounds Per Game")
    reb_df = leaders("TRB", ["Player", "GP", "TRB"], stats_df, MIN_GP)
    def_col.table(reb_df.style.format({"TRB": "{:.2f}"}))

    def_col.caption("Blocks Per Game")
    blk_df = leaders("BLK", ["Player", "GP", "BLK"], stats_df, MIN_GP)
    def_col.table(blk_df.style.format({"BLK": "{:.2f}"}))

    def_col.caption("Steals Per Game")
    stl_df = leaders("STL", ["Player", "GP", "STL"], stats_df, MIN_GP)
    def_col.table(stl_df.style.format({"STL": "{:.2f}"}))

    st.header("Season Records")
    st.table(highs())
