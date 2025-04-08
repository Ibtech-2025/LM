import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="Busca de Produtos - Mercado Livre", layout="wide")
st.title("🔎 Buscador de Produtos no Mercado Livre")

produto = st.text_input("Digite o nome do produto que deseja pesquisar", value="notebook")

def format_price(preco_str):
    preco_str = preco_str.replace(".", "").replace(",", ".").strip()
    try:
        return float(preco_str)
    except:
        return None

def scrape_mercadolivre(produto, num_paginas=2):
    resultados = []

    for pagina in range(1, num_paginas + 1):
        url = f"https://lista.mercadolivre.com.br/{produto}_Desde_{(pagina - 1) * 48 + 1}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', class_='ui-search-result__wrapper')

        for item in items:
            try:
                nome_tag = item.find('a', class_='poly-component__title')
                nome = nome_tag.text.strip() if nome_tag else None
                link = nome_tag['href'] if nome_tag else None

                marca_tag = item.find('span', class_='poly-component__brand')
                marca = marca_tag.text.strip() if marca_tag else None

                preco_atual_tag = item.find('span', class_='andes-money-amount__fraction')
                preco_atual = format_price(preco_atual_tag.text) if preco_atual_tag else None

                preco_original_tag = item.find('span', class_='andes-money-amount__fraction andes-money-amount__discount')
                preco_original = format_price(preco_original_tag.text) if preco_original_tag else None

                desconto = None
                if preco_original and preco_atual:
                    desconto = round((1 - preco_atual / preco_original) * 100, 2)

                parcelamento_tag = item.find('span', class_='poly-price__installments')
                parcelamento = parcelamento_tag.text.strip() if parcelamento_tag else None

                frete_tag = item.find('div', class_='poly-component__shipping')
                frete = frete_tag.text.strip() if frete_tag else None

                resultados.append({
                    "Marca": marca,
                    "Nome": nome,
                    "Preço Atual (R$)": preco_atual,
                    "Preço Original (R$)": preco_original,
                    "Desconto (%)": desconto,
                    "Parcelamento": parcelamento,
                    "Frete": frete,
                    "Link": link
                })
            except Exception as e:
                continue

    return pd.DataFrame(resultados)

if produto:
    with st.spinner("Buscando produtos..."):
        df = scrape_mercadolivre(produto)

    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Produtos encontrados", len(df))
        col2.metric("💰 Preço médio", f"R$ {df['Preço Atual (R$)'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if df['Desconto (%)'].notna().any():
            col3.metric("🔥 Maior desconto", f"{df['Desconto (%)'].max()}%")

        st.subheader("📋 Resultados da busca")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar como CSV", csv, file_name="produtos_mercadolivre.csv", mime="text/csv")
    else:
        st.warning("Nenhum produto encontrado.")
