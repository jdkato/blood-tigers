import json
import pathlib

import pandas as pd
import streamlit as st

DATA = pathlib.Path("data")


def records():
    made = pd.DataFrame([], columns=[
        'Title',
        'Player',
        'Record',
    ])

    recorded = {'PTS': 0, '3PM': 0, 'REB': 0, 'AST': 0, 'STL': 0, 'BLK': 0}
    r_to_p = {}
    for filename in (DATA / "s1").iterdir():
        gdf = pd.read_csv(filename)
        for k, v in recorded.items():
            rdf = gdf.loc[gdf[k].idxmax()]
            most = rdf[k]
            if int(most) > v:
                recorded[k] = most
                r_to_p[k] = rdf["Player"]

    for k, v in recorded.items():
        made = made.append({
            'Title': k,
            'Player': r_to_p[k],
            'Record': v
        }, ignore_index=True)

    return made


def game(sc, gc):
    with open(DATA / "games.json", "r") as f:
        return json.load(f)[str(sc)][str(gc)]


def summary(season=1):
    players = []
    games = []

    made = pd.DataFrame([], columns=[
        'Player',
        'GP',
        'FGM',
        'FGA',
        'FG%',
        '3PM',
        '3PA',
        '3P%',
        'TRB',
        'AST',
        'STL',
        'BLK',
        'TOV',
        'PTS'
    ])

    for filename in (DATA / f"s{season}").iterdir():
        gdf = pd.read_csv(filename)
        games.append(gdf)
        players.extend(gdf['Player'])

    totals = pd.concat(games, axis=0, ignore_index=True)
    for player in set(players):
        games_played = players.count(player)

        fgm = float(totals.loc[totals['Player'] == player, 'FGM'].sum())
        fga = float(totals.loc[totals['Player'] == player, 'FGA'].sum())

        tpm = float(totals.loc[totals['Player'] == player, '3PM'].sum())
        tpa = float(totals.loc[totals['Player'] == player, '3PA'].sum())

        made = made.append({
            'Player': player,
            'GP': games_played,
            'FGM': fgm,
            'FGA': fga,
            'FG%': fgm / fga,
            '3PM': tpm,
            '3PA': tpa,
            '3P%': tpm / tpa,
            'TRB': totals.loc[totals['Player'] == player, 'REB'].sum() / games_played,
            'AST': totals.loc[totals['Player'] == player, 'AST'].sum() / games_played,
            'STL': totals.loc[totals['Player'] == player, 'STL'].sum() / games_played,
            'BLK': totals.loc[totals['Player'] == player, 'BLK'].sum() / games_played,
            'TOV': totals.loc[totals['Player'] == player, 'TO'].sum() / games_played,
            'PTS': totals.loc[totals['Player'] == player, 'PTS'].sum() / games_played
        }, ignore_index=True)

    return made


if __name__ == "__main__":
    st.image("https://user-images.githubusercontent.com/8785025/179428151-7be15af8-bf02-42c1-8b77-37d4b4422a39.png")

    st.write(
        """
        # Beantown Blood Tigers
        
        Welcome! :wave:
        
        This app tracks season-by-season stats for the *Beantown Blood Tigers*, a team in the [@2kaveragejoes][1] 
        league (NBA 2K22; Xbox current gen).
        
        [1]: https://discord.gg/2VBR8dQ2gb
        """)

    st.info(
        """
        💫️ You can learn more about the league on [Instagram][1], [TikTok][2], or [Discord][3].
        
        [1]: https://www.instagram.com/2kaveragejoes/
        [2]: https://www.tiktok.com/@2kaveragejoes
        [3]: https://discord.gg/2VBR8dQ2gb
        """
    )

    st.header("Totals")

    df = summary().sort_values(by=['PTS'], ascending=False)
    st.dataframe(df.style.format({
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
        "PTS": "{:.2f}"
    }))

    st.header("Games")

    col1, col2 = st.columns(2)
    # TODO: dynamic ...
    s = col1.selectbox('Season', [1])
    g = col2.selectbox('Game', [1, 2, 3, 4])

    gdata = game(s, g)
    if gdata["stream"] != "":
        st.video(gdata["stream"])
    else:
        st.markdown(f"##### *{gdata['title']}*")
        st.warning(f"No stream available for game S{s}G{g}.")

    st.table(pd.read_csv(DATA / f"s{s}" / f"Game {g}.csv"))

    st.header("Records")
    st.table(records())
