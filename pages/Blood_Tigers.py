import json
import pathlib

import pandas as pd
import streamlit as st
import altair as alt

from collections import defaultdict

CSV = pathlib.Path("CSV")
TEAM = "Blood Tigers"


def quarter_scoring(s, g):
    data = pd.DataFrame(game(s, g)["breakdown"])
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            y=alt.X("Quarter", sort=["1st", "2nd", "3rd", "4th"]),
            x="sum(PTS)",
            color=alt.Color("Team"),
        )
    )


def records(team):
    made = []

    recorded = {"PTS": 0, "3PM": 0, "REB": 0, "AST": 0, "STL": 0, "BLK": 0}
    r_to_p = defaultdict(list)
    for filename in (CSV / "s1" / "boxscores" / f"{team}").glob("*.csv"):
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

    return pd.DataFrame.from_records(
        made,
        columns=[
            "Stat",
            "Player(s)",
            "Record",
        ],
    )


def game(sc, gc):
    with open(CSV / "s1" / "games.json", "r") as f:
        return json.load(f)[str(sc)][str(gc)]


def summary(team, season=1):
    players = []
    games = []

    made = []
    for filename in (CSV / f"s{season}" / "boxscores" / f"{team}").glob("*.csv"):
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

    return pd.DataFrame.from_records(
        made,
        columns=[
            "Player",
            "GP",
            "FGM",
            "FGA",
            "FG%",
            "3PM",
            "3PA",
            "3P%",
            "TRB",
            "AST",
            "STL",
            "BLK",
            "TOV",
            "PTS",
        ],
    )


if __name__ == "__main__":
    # st.set_page_config(layout="wide")

    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.image(
        "https://user-images.githubusercontent.com/8785025/179428151-7be15af8-bf02-42c1-8b77-37d4b4422a39.png"
    )

    st.write(f"# Beantown Blood Tigers")

    st.header("Season Totals")

    df = summary(TEAM).sort_values(by=["PTS"], ascending=False)
    st.dataframe(
        df.style.format(
            {
                "FGM": "{:.0f}",
                "FGA": "{:.0f}",
                "FG%": "{:.2f}",
                "3PM": "{:.0f}",
                "3PA": "{:.0f}",
                "3P%": "{:.2f}",
                "TRB": "{:.2f}",
                "AST": "{:.2f}",
                "STL": "{:.2f}",
                "BLK": "{:.2f}",
                "TOV": "{:.2f}",
                "PTS": "{:.2f}",
            }
        )
    )

    st.header("Replays and Boxscores")

    # col1, col2 = st.columns(2)
    # s = col1.selectbox('Season', [1])

    boxscores = (CSV / f"s1" / "boxscores" / f"{TEAM}").glob("*.csv")
    games_list = [f.name.split(".")[0][1] for f in boxscores]
    g = st.selectbox("Game", games_list)

    gdata = game(1, g)
    if gdata["stream"] != "":
        st.video(gdata["stream"])
    else:
        st.markdown(f"##### *{gdata['title']}*")
        st.warning(f"No stream available for game S{1}G{g}.")

    st.table(pd.read_csv(CSV / f"s{1}" / "boxscores" / TEAM / f"g{g}.csv"))

    breakdown = quarter_scoring(1, g)
    st.altair_chart(breakdown, use_container_width=True)

    st.header("Single-Game Records")
    st.table(records(TEAM))
