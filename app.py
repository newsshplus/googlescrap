# app.py
import os
import time
import traceback
from typing import List, Dict, Any

import streamlit as st
import pandas as pd

# Imports do próprio projeto (na raiz)
import main as gs_main
import details as gs_details
import imagedownloader as gs_images


# ============== Helpers de integração ==============
@st.cache_data(show_spinner=False)
def run_search_cached(
    keywords: str,
    max_results: int,
    country: str,
    language: str,
) -> pd.DataFrame:
    """
    Chama a função de busca do projeto e retorna um DataFrame.
    Ajuste a chamada para bater na sua função real de busca no main.py.
    """
    # TODO: vincular à sua função real
    # Esperado: uma lista de dicts ou DataFrame com colunas como:
    # ["title", "price", "store", "product_url", "image_url", "source", "timestamp"]
    data = gs_main.search_products(
        keywords=keywords,
        max_results=max_results,
        country=country,
        language=language,
    )
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.DataFrame(data)

    # Normaliza colunas esperadas no app
    wanted_cols = ["title", "price", "store", "product_url", "image_url", "source", "timestamp"]
    for c in wanted_cols:
        if c not in df.columns:
            df[c] = None

    # Garantir tipos e ordem
    df = df[wanted_cols]
    return df


def run_details(url: str) -> Dict[str, Any]:
    """
    Chama a função de detalhes do projeto para 1 produto.
    """
    # TODO: vincular à sua função real
    return gs_details.fetch_details(url)


def run_download_images(urls: List[str], out_dir: str) -> List[str]:
    """
    Chama o downloader de imagens do projeto e retorna paths locais baixados.
    """
    # TODO: vincular à sua função real
    os.makedirs(out_dir, exist_ok=True)
    paths = gs_images.download_images(urls, out_dir=out_dir)
    return paths


# ============== UI ==============
def sidebar_controls() -> Dict[str, Any]:
    st.sidebar.header("Parâmetros da busca")
    keywords = st.sidebar.text_input("Palavras-chave", value="", help="Separe por vírgulas para múltiplos termos.")
    max_results = st.sidebar.number_input("Máx. resultados", min_value=5, max_value=500, value=50, step=5)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        country = st.text_input("País (ccTLD)", value="br", help="Ex.: br, pt, us, es…")
    with col2:
        language = st.text_input("Idioma (código)", value="pt", help="Ex.: pt, en, es…")

    st.sidebar.caption("Dicas: use termos específicos e teste variações de idioma/país.")
    return {
        "keywords": keywords.strip(),
        "max_results": int(max_results),
        "country": country.strip(),
        "language": language.strip(),
    }


def render_result_card(row: pd.Series, idx: int):
    left, right = st.columns([1, 3])
    with left:
        if pd.notna(row.get("image_url")) and row.get("image_url"):
            st.image(row["image_url"], use_container_width=True)
        else:
            st.write("Sem imagem")

    with right:
        title = row.get("title") or "Sem título"
        st.subheader(title)
        meta = []
        if row.get("price"): meta.append(f"**Preço:** {row['price']}")
        if row.get("store"): meta.append(f"**Loja:** {row['store']}")
        if row.get("source"): meta.append(f"**Fonte:** {row['source']}")
        st.markdown("  |  ".join(meta) if meta else "—")

        if row.get("product_url"):
            st.markdown(f"[Abrir produto]({row['product_url']})")

        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if row.get("product_url"):
                if st.button("Detalhes", key=f"btn_details_{idx}"):
                    with st.spinner("Carregando detalhes…"):
                        try:
                            details = run_details(row["product_url"])
                            st.json(details)
                        except Exception as e:
                            st.error(f"Erro ao buscar detalhes: {e}")
                            st.exception(e)
        with c2:
            if row.get("image_url"):
                if st.button("Baixar imagem", key=f"btn_img_{idx}"):
                    with st.spinner("Baixando imagem…"):
                        try:
                            paths = run_download_images([row["image_url"]], out_dir="downloads/images")
                            st.success(f"Imagem salva: {', '.join(paths)}")
                            for p in paths:
                                st.image(p, caption=os.path.basename(p))
                        except Exception as e:
                            st.error(f"Erro ao baixar imagem: {e}")
                            st.exception(e)
        with c3:
            st.caption(f"Gravado em: {row.get('timestamp') or '—'}")


def main():
    st.set_page_config(page_title="GoogleScrap App", page_icon="🔎", layout="wide")
    st.title("🔎 GoogleScrap — Streamlit")
    st.write("Interface Streamlit com todas as funcionalidades: **busca**, **detalhes** e **download de imagens**.")

    params = sidebar_controls()

    run = st.button("Executar busca", type="primary")
    if run:
        if not params["keywords"]:
            st.warning("Insira ao menos uma palavra-chave.")
            st.stop()

        with st.status("Rodando busca…", expanded=False) as status:
            try:
                t0 = time.time()
                df = run_search_cached(
                    keywords=params["keywords"],
                    max_results=params["max_results"],
                    country=params["country"],
                    language=params["language"],
                )
                elapsed = time.time() - t0
                status.update(label=f"Busca concluída em {elapsed:.2f}s", state="complete")
            except Exception:
                status.update(label="Falha na busca", state="error")
                st.error("Ocorreu um erro ao executar a busca.")
                st.code(traceback.format_exc())
                st.stop()

        if df.empty:
            st.info("Nenhum resultado encontrado.")
            st.stop()

        # Controles rápidos
        with st.expander("Filtros rápidos"):
            q = st.text_input("Filtrar por texto no título/loja/fonte")
            if q:
                mask = (
                    df["title"].fillna("").str.contains(q, case=False, na=False) |
                    df["store"].fillna("").str.contains(q, case=False, na=False) |
                    df["source"].fillna("").str.contains(q, case=False, na=False)
                )
                df = df[mask]

        st.success(f"{len(df)} resultados")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Resultados em cartões")
        for i, row in df.reset_index(drop=True).iterrows():
            render_result_card(row, i)
            st.markdown("---")


if __name__ == "__main__":
    main()
