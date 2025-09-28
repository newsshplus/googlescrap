import streamlit as st
import pandas as pd
from scraper import search_products

st.set_page_config(page_title="GoogleScrap — Streamlit", layout="wide")

st.title("🔎 GoogleScrap — Streamlit")
st.write("Busque produtos, veja detalhes e baixe imagens diretamente no navegador.")

# Parâmetros da busca
keywords = st.text_input("Palavras-chave")
max_results = st.number_input("Máx. resultados", min_value=1, max_value=100, value=10)
country = st.text_input("País (ccTLD)", value="us")
language = st.text_input("Idioma", value="en")

if st.button("Buscar"):
    if not keywords:
        st.warning("Digite alguma palavra-chave.")
    else:
        with st.spinner("Buscando..."):
            try:
                df = search_products(keywords, max_results=max_results, country=country, language=language)
                if df.empty:
                    st.info("Nenhum resultado encontrado.")
                else:
                    st.success(f"Busca concluída — {len(df)} resultados encontrados")
                    st.dataframe(df)
            except Exception as e:
                st.error(f"Erro na busca: {e}")
