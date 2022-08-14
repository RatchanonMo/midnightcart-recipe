import streamlit as st
import pandas as pd
import numpy as np
import SessionState
import os
from PIL import Image

import config, rec_sys
from ingredient_parser import ingredient_parser

from word2vec_rec import get_recs

import nltk

import streamlit as st
import mysql.connector
import pandas as pd
import requests


# Initialize connection.
# Uses st.experimental_singleton to only run once.



def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])


conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.


def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")

st.set_page_config(
    layout="wide",

)

def make_clickable(name, link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = name
    return f'<a target="_blank" href="{link}">{text}</a>'


def main():

    st.markdown("# *What's Cooking? :cooking:*")

    col1, col2 = st.columns(2)

    with col1:
        session_state = SessionState.get(
            recipe_df="",
            recipes="",
            model_computed=False,
            execute_recsys=False,
            recipe_df_clean="",
        )

        rows = run_query("SELECT * from stock;")
        ingredients = []
        # Print results.
        for row in rows:
            ingredients.append(row[1])
        
        session_state.execute_recsys 
        st.text(ingredients)


        with st.form("my_form"):
            st.subheader("Add Items")
            # option = st.selectbox(
            #     'Which item did you just add?',
            #     ('apple', 'banana'))
            name = st.text_input('Name', '')

            number = st.number_input('Quantity', format='%d', value=1, min_value=1)
            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.write(name, number)
                run_query(f"INSERT INTO stock (id, name, price, amount) VALUES (null, '{name}', '10', '{number}')")
                conn.commit()
                st.experimental_rerun()
        

       

    with col2:
        if session_state.execute_recsys == False:

            gif_runner = st.image("input/cooking_gif1.gif")
            # recipe = rec_sys.RecSys(ingredients)
            recipe = get_recs(ingredients, mean=True)
            gif_runner.empty()
            session_state.recipe_df_clean = recipe.copy()
            # link is the column with hyperlinks
            recipe["url"] = recipe.apply(
                lambda row: make_clickable(row["recipe"], row["url"]), axis=1
            )
            recipe_display = recipe[["recipe", "url", "ingredients"]]
            session_state.recipe_display = recipe_display.to_html(escape=False)
            session_state.recipes = recipe.recipe.values.tolist()
            session_state.model_computed = True
            session_state.execute_recsys = False

        if session_state.model_computed:
            #  st.write("Either pick a particular recipe or see the top 5 recommendations.")
            # recipe_all_box = st.selectbox(
            #     ["Select a single recipe"],
            # )
            # if recipe_all_box == "Show me them all!":
            #     st.write(session_state.recipe_display, unsafe_allow_html=True)
            # else:
                selection = st.selectbox(
                    "Select a delicious recipe", options=session_state.recipes
                )
                selection_details = session_state.recipe_df_clean.loc[
                    session_state.recipe_df_clean.recipe == selection
                ]
                st.markdown(f"# {selection_details.recipe.values[0]}")
                st.subheader(f"Website: {selection_details.url.values[0]}")
                ingredients_disp = selection_details.ingredients.values[0].split(",")

                st.subheader("Ingredients:")
                ingredients_disp = [
                    ingred
                    for ingred in ingredients_disp
                    if ingred
                    not in [
                        " skin off",
                        " bone out",
                        " from sustainable sources",
                        " minced",
                    ]
                ]
                ingredients_disp1 = ingredients_disp[len(ingredients_disp) // 2 :]
                ingredients_disp2 = ingredients_disp[: len(ingredients_disp) // 2]
                for ingred in ingredients_disp1:
                    st.markdown(f"* {ingred}")
                for ingred in ingredients_disp2:
                    st.markdown(f"* {ingred}")
                # st.write(f"Score: {selection_details.score.values[0]}")

    


if __name__ == "__main__":
    main()
