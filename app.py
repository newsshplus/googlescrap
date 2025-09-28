import streamlit as st
import pandas as pd
from main import search_products, download_images

st.set_page_config(page_title="GoogleScrap — Streamlit", layout="wide")
st.title("🔎 GoogleScrap — Streamlit")
st.write("Busque produtos, veja detalhes e baixe imagens diretamente no navegador.")

# Parâmetros da busca
keywords = st.text_input("Palavras-chave", "")
max_results = st.number_input("Máx. resultados", min_value=1, max_value=50, value=10)
country = st.text_input("País (ccTLD, ex: us)", "us")
language = st.text_input("Idioma (ex: en)", "en")

if st.button("Buscar"):
    if not keywords.strip():
        st.error("Digite pelo menos uma palavra-chave!")
    else:
        with st.spinner("Buscando produtos..."):
            df = search_products(keywords, max_results=max_results, country=country, language=language)
            if df.empty:
                st.warning("Nenhum resultado encontrado.")
            else:
                st.success(f"Busca concluída — {len(df)} resultados encontrados")
                for idx, row in df.iterrows():
                    st.markdown(f"### {row['Título']}")
                    st.markdown(f"**Preço:** {row['Preço']}")
                    st.markdown(f"[Ver no Google Shopping]({row['Link']})")
                    if row.get("Imagem"):
                        st.image(row["Imagem"], width=200)
                
                if st.button("Baixar imagens"):
                    download_images(df)
                    st.success("Imagens baixadas na pasta 'images/'")
