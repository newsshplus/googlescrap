# app.py
import os
import time
import traceback
import pandas as pd
import streamlit as st

from main import search_products
from details import fetch_details
from imagedownloader import download_images

@st.cache_data(show_spinner=False)
def run_search(keywords: str, max_results: int = 20, country: str = "br", language: str = "pt"):
    df = search_products(keywords, max_results=max_results, country=country, language=language)
    expected_cols = ["title", "price", "store", "rating", "product_url", "image_url", "source", "timestamp"]
    for c in expected_cols:
        if c not in df.columns:
            df[c] = None
    return df[expected_cols]

def render_result(row: pd.Series, idx: int):
    left, right = st.columns([1, 3])
    with left:
        if row.get("image_url"):
            st.image(row["image_url"], use_container_width=True)
        else:
            st.write("Sem imagem")
    with right:
        st.subheader(row.get("title") or "Sem título")
        meta = []
        if row.get("price"): meta.append(f"**Preço:** {row['price']}")
        if row.get("store"): meta.append(f"**Loja:** {row['store']}")
        if row.get("rating"): meta.append(f"**Avaliação:** {row['rating']}")
        if row.get("source"): meta.append(f"**Fonte:** {row['source']}")
        st.markdown("  |  ".join(meta) if meta else "—")
        if row.get("product_url"):
            st.markdown(f"[Abrir produto]({row['product_url']})")

        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if row.get("product_url"):
                if st.button("Detalhes", key=f"details_{idx}"):
                    with st.spinner("Carregando detalhes…"):
                        try:
                            details = fetch_details(row["product_url"])
                            st.json(details)
                        except Exception as e:
                            st.error(f"Erro: {e}")
        with c2:
            if row.get("image_url"):
                if st.button("Baixar imagem", key=f"img_{idx}"):
                    with st.spinner("Baixando imagem…"):
                        try:
                            paths = download_images([row["image_url"]], out_dir="downloads/images")
                            st.success(f"Imagem salva: {', '.join(paths)}")
                            for p in paths:
                                st.image(p, caption=os.path.basename(p))
                        except Exception as e:
                            st.error(f"Erro: {e}")
        with c3:
            st.caption(f"Gravado em: {row.get('timestamp') or '—'}")

def main():
    st.set_page_config(page_title="GoogleScrap App", page_icon="🔎", layout="wide")
    st.title("🔎 GoogleScrap — Streamlit")
    st.write("Busque produtos, veja detalhes e baixe imagens diretamente no navegador.")

    st.sidebar.header("Parâmetros da busca")
    keywords = st.sidebar.text_input("Palavras-chave", value="", help="Separe por vírgulas")
    max_results = st.sidebar.number_input("Máx. resultados", min_value=5, max_value=50, value=20, step=5)
    country = st.sidebar.text_input("País (ccTLD)", value="br")
    language = st.sidebar.text_input("Idioma", value="pt")

    if st.button("Executar busca"):
        if not keywords:
            st.warning("Insira ao menos uma palavra-chave.")
            st.stop()
        try:
            t0 = time.time()
            df = run_search(keywords, max_results=max_results, country=country, language=language)
            elapsed = time.time() - t0
            st.success(f"Busca concluída em {elapsed:.2f}s — {len(df)} resultados encontrados")
        except Exception as e:
            st.error("Erro na busca")
            st.code(traceback.format_exc())
            st.stop()

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.subheader("Resultados em cartões")
        for i, row in df.reset_index(drop=True).iterrows():
            render_result(row, i)
            st.markdown("---")

if __name__ == "__main__":
    main()
