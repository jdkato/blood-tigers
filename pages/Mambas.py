import streamlit as st
import pandas as pd

from pages import Blood_Tigers as Tigers

TEAM = "Mambas"


if __name__ == "__main__":
    # st.set_page_config(layout="wide")

    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.write(f"# {TEAM}")
    st.header("Season Totals")

    df = Tigers.summary(TEAM).sort_values(by=["PTS"], ascending=False)
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

    st.header("Boxscores")

    boxscores = sorted(list((Tigers.CSV / f"s1" / "boxscores" / f"{TEAM}").glob("*.csv")))
    games_list = [f.name.split(".")[0][1] for f in boxscores]
    g = st.selectbox("Game", sorted(games_list))

    st.table(pd.read_csv(list(boxscores)[int(g)-1]))

    st.header("Single-Game Records")
    st.table(Tigers.records(TEAM))
