import streamlit as st
import mysql.connector
import pandas as pd
import requests

# Initialize connection.
# Uses st.experimental_singleton to only run once.


@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])


conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.


def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


st.title("🗃️ MidnightCart Stock")

col1, col2 = st.columns(2)

with col1:
    with st.form("my_form"):
        st.subheader("Add Items")
        option = st.selectbox(
            'Which item did you just add?',
            ('apple', 'banana'))

        number = st.number_input('Quantity', format='%d', value=1, min_value=1)
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(option, number)
            run_query(f"UPDATE stock SET amount = amount + {number} WHERE name = '{option}' ")
            conn.commit()
            st.experimental_rerun()


with col2:

    rows = run_query("SELECT * from stock;")
    # Print results.
    for row in rows:
        st.write(f"{row[1]} : {row[3]} ")

        if row[3] == 0:
            url = 'https://notify-api.line.me/api/notify'
            token = 'An4nrpLh30uFvdyyBdscL6HAcI10v4mna7wIWpIzwOd'
            headers = {'content-type': 'application/x-www-form-urlencoded',
                       'Authorization': 'Bearer '+token}

            msg = f"{row[1]} out of stock"
            r = requests.post(url, headers=headers, data={'message': msg})
            print(r.text)

    if st.button('update'):
        if row[3] != 0 :
            run_query("UPDATE stock SET amount = amount - '10' WHERE id = '1' ")
            conn.commit()
            st.experimental_rerun()
        else :
            st.write("STOP IT. GET SOME HELP.")
