import streamlit as st
import pandas as pd

RESULTS = "https://docs.google.com/spreadsheets/d/1J0_5OF5S6kFcyjmcPtwFZHbsIOh5AQjS4nk1Ej3pLdU/export?format=csv"


def compute_records(teams, results):
    records = []
    for team in teams:
        records.append(compute_record(team, results))
    return pd.DataFrame(records).sort_values(by=['PCT'], ascending=False)


def compute_record(team, results):
    record = {"Team": team, "GP": 0, "Wins": 0, 'PCT': 0, "Margin": []}

    for _, row in results.iterrows():
        teams = [row['Away'], row['Home']]
        if team in teams:
            idx = teams.index(team)
            score = [int(s) for s in row['Result'].split(" - ")]

            record["GP"] += 1
            if max(score) == score[idx]:
                record["Wins"] += 1
                record["Margin"].append((max(score) - min(score)))
            else:
                record["Margin"].append((min(score)) - (max(score)))

    record['PCT'] = record['Wins'] / record['GP']
    record['Margin'] = sum(record['Margin']) / len(record['Margin'])

    return record


if __name__ == "__main__":
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.write(
        f"""
        # Welcome! :wave:
        
        This app tracks season-by-season stats for the [@2kaveragejoes][1] 
        league (NBA 2K22; Xbox current gen).
        
        [1]: https://discord.gg/2VBR8dQ2gb
        """)

    st.info(
        """
        👀 You can learn more about the league on [Instagram][1], [TikTok][2], or [Discord][3].
        
        [1]: https://www.instagram.com/2kaveragejoes/
        [2]: https://www.tiktok.com/@2kaveragejoes
        [3]: https://discord.gg/2VBR8dQ2gb
        """
    )

    results_df = pd.read_csv(RESULTS)

    teams = pd.unique(results_df[['Home', 'Away']].values.ravel('K'))
    st.table(compute_records(teams, results_df).style.format({
        "PCT": "{:.2f}",
        "Margin": "{:.2f}",
    }))