import streamlit as st
from PIL import Image
import io
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import pathlib
import textwrap
from IPython.display import display
from google_auth import get_logged_in_user_email, show_login_button
from st_paywall import add_auth
import mysql.connector
import pandas as pd

st.set_page_config(
    page_title="Math Teacher",
    page_icon="🤖"
)
st.title("🤖 AI Matek Tanár")

login_button_text="Login with Google"
login_button_color="#FD504D"
login_sidebar=True
user_email = get_logged_in_user_email()

if not user_email:
    show_login_button(
        text=login_button_text, color=login_button_color, sidebar=login_sidebar
    )
    st.stop()

st.session_state.user_subscribed = True

if st.sidebar.button("Logout", type="primary"):
    del st.session_state.email
    del st.session_state.user_subscribed
    st.rerun()

st.write("Bejelentkeztél")
st.write("Email címed: " + str(st.session_state.email))

load_dotenv()
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Adatbázis kapcsolat
def get_db_connection():
    connection = mysql.connector.connect(
        host='db4free.net',
        user='dadani2',
        password='dadanivok',
        database='streamlit2'
    )
    return connection

# Adatbázis kapcsolat létrehozása
connection = get_db_connection()

# Cursor létrehozása
cursor = connection.cursor()

# Lekérdezés végrehajtása
cursor.execute("SELECT * FROM tablename1")
data = cursor.fetchall()

# DataFrame létrehozása
df = pd.DataFrame(data, columns=cursor.column_names)

# Ellenőrizzük, hogy van-e már sor a táblában
if len(df) == 0:
    # Ha nincs, hozzáadjuk az alapértelmezett értékekkel
    cursor.execute("INSERT INTO tablename1 (gombnyomas) VALUES (0)")
    connection.commit()

    # Újra lekérdezzük az adatokat és frissítjük a DataFrame-et
    cursor.execute("SELECT * FROM tablename1")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)

def call_gemini(image):
    model = genai.GenerativeModel(st.secrets["MODEL"])
    model_prompt = st.secrets["PROMPT"]
    with st.spinner("Dolgozok a megoldáson..."):
        response = model.generate_content([model_prompt, image], stream=True)
        response.resolve()
    response_text = response.text
    st.subheader("Megoldás")
    st.write(response_text)

    # Növeljük a számlálót az adatbázisban
    cursor.execute("UPDATE tablename1 SET gombnyomas = gombnyomas + 1")
    connection.commit()

    # Újra lekérdezzük az adatokat és frissítjük a DataFrame-et
    cursor.execute("SELECT * FROM tablename1")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)

    # Megjelenítjük a frissített adatokat
    st.dataframe(df)

def main():
    st.caption("🚀 Tölts fel egy képet a matematika feladatról!")

    uploaded_file = st.file_uploader("Feladat feltöltése", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image_display_width = 300
        st.image(image, caption='Feladat', use_column_width=False, width=image_display_width)
        
        if st.button('Megoldás'):
            call_gemini(image)
        else:
            st.write('Kattints a "Megoldás" gombra!')

if __name__ == "__main__":
    main()

# Cursor és kapcsolat bezárása
cursor.close()
connection.close()
