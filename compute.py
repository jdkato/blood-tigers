import pathlib

import pandas as pd
import streamlit as st

from collections import defaultdict
from sqlalchemy import create_engine


DATA = pathlib.Path("csv")


def leaders(stat, show, stats_df):
    df = stats_df.sort_values(stat, ascending=False)
    # df = df[(df["GP"] >= min)]
    # df = df.head(10)
    df = df.reset_index(drop=True)

    return df[show]


def totals(season=1):
    teams = pd.read_csv(DATA / "s1" / "teams.csv")

    made = []
    for _, entry in teams.iterrows():
        p = DATA / f"s{season}" / "boxscores" / entry["Team"]

        games = []
        for filename in p.glob("*.csv"):
            gdf = pd.read_csv(filename)
            games.append(gdf)

        totals = pd.concat(games, axis=0, ignore_index=True)

        games_played = len(games)

        fgm = float(totals["FGM"].sum())
        fga = float(totals["FGA"].sum())

        tpm = float(totals["3PM"].sum())
        tpa = float(totals["3PA"].sum())

        made.append(
            {
                "Team": entry["Team"],
                "GP": games_played,
                "FGM": fgm / games_played,
                "FGA": fga / games_played,
                "FG%": fgm / fga if fga else 0,
                "3PM": tpm / games_played,
                "3PA": tpa / games_played,
                "3P%": tpm / tpa if tpa else 0,
                "TRB": totals["REB"].sum() / games_played,
                "AST": totals["AST"].sum() / games_played,
                "STL": totals["STL"].sum() / games_played,
                "BLK": totals["BLK"].sum() / games_played,
                "TOV": totals["TO"].sum() / games_played,
                "PTS": totals["PTS"].sum() / games_played,
            },
        )

    df = pd.DataFrame.from_records(
        made,
        columns=[
            "Team",
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

    df = df.sort_values(by=["PTS"], ascending=False)
    df = df.reset_index(drop=True)

    return df


def op_totals(season=1):
    teams = pd.read_csv(DATA / "s1" / "teams.csv")

    made = []
    for _, entry in teams.iterrows():
        p = DATA / f"s{season}" / "boxscores"

        games = []
        for team in p.iterdir():
            if team.name == entry["Team"]:
                continue

            for filename in team.glob("*.csv"):
                if entry["Team"] not in filename.name:
                    continue
                gdf = pd.read_csv(filename)
                games.append(gdf)

        totals = pd.concat(games, axis=0, ignore_index=True)

        games_played = len(games)

        fgm = float(totals["FGM"].sum())
        fga = float(totals["FGA"].sum())

        tpm = float(totals["3PM"].sum())
        tpa = float(totals["3PA"].sum())

        made.append(
            {
                "Team": entry["Team"],
                "GP": games_played,
                "FGM": fgm / games_played,
                "FGA": fga / games_played,
                "FG%": fgm / fga if fga else 0,
                "3PM": tpm / games_played,
                "3PA": tpa / games_played,
                "3P%": tpm / tpa if tpa else 0,
                "TRB": totals["REB"].sum() / games_played,
                "AST": totals["AST"].sum() / games_played,
                "STL": totals["STL"].sum() / games_played,
                "BLK": totals["BLK"].sum() / games_played,
                "TOV": totals["TO"].sum() / games_played,
                "PTS": totals["PTS"].sum() / games_played,
            },
        )

    df = pd.DataFrame.from_records(
        made,
        columns=[
            "Team",
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

    df = df.sort_values(by=["PTS"], ascending=True)
    df = df.reset_index(drop=True)

    return df


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
    engine = create_engine(st.secrets["DB_URL"])

    stats_df = summary(season=1)

    standings_df = compute_records()
    standings_df.to_sql(name="Standings", con=engine)
    # standings_df.to_csv("build/standings.csv", sep=',', index=False)

    pts_df = leaders("PTS", ["Player", "GP", "PTS"], stats_df)
    pts_df.to_sql(name="PTS", con=engine)

    fgp_df = leaders("FG%", ["Player", "GP", "FG%", "FGM"], stats_df)
    fgp_df.to_sql(name="FGP", con=engine)

    ast_df = leaders("AST", ["Player", "GP", "AST"], stats_df)
    ast_df.to_sql(name="AST", con=engine)

    tmp_df = leaders("3PG", ["Player", "GP", "3PG"], stats_df)
    tmp_df.to_sql(name="TPG", con=engine)

    tpp_df = leaders("3P%", ["Player", "GP", "3P%", "3PM"], stats_df)
    tpp_df.to_sql(name="TPP", con=engine)

    reb_df = leaders("TRB", ["Player", "GP", "TRB"], stats_df)
    reb_df.to_sql(name="REB", con=engine)

    blk_df = leaders("BLK", ["Player", "GP", "BLK"], stats_df)
    blk_df.to_sql(name="BLK", con=engine)

    stl_df = leaders("STL", ["Player", "GP", "STL"], stats_df)
    stl_df.to_sql(name="STL", con=engine)

    high_df = highs()
    high_df.to_sql(name="Highs", con=engine)

    total_df = totals()
    total_df.to_sql(name="Team", con=engine)
    #total_df.to_csv("build/total.csv", sep=',', index=False)

    opp_df = op_totals()
    opp_df.to_sql(name="Opponent", con=engine)
    #opp_df.to_csv("build/opp.csv", sep=',', index=False)

    rows = []
    for i, row in total_df.iterrows():
        team = row["Team"]
        entry = {"Team": team, "GP": row["GP"]}
        for k in ["FGM", "FGA", "FG%", "3PM", "3PA", "3P%", "TRB", "AST", "STL", "BLK", "TOV", "PTS"]:
            i = row[k] - opp_df.loc[opp_df["Team"] == team, k]
            entry[k] = list(i)[0]
        rows.append(entry)

    diff_df = pd.DataFrame(rows)
    diff_df = diff_df.sort_values(by=["PTS"], ascending=False)
    diff_df = diff_df.reset_index(drop=True)
    diff_df.to_sql(name="Differential", con=engine)
    #diff_df.to_csv("build/diff.csv", sep=',', index=False)

