import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Busca produtos LM", layout="wide")
st.title("Busca produtos LM")

produto = st.text_input("Digite o nome do produto que deseja pesquisar", value="")

def format_price(preco_str):
    preco_str = preco_str.replace(".", "").replace(",", ".").strip()
    try:
        return float(preco_str)
    except:
        return None

def extrair_float_desconto(desconto_str):
    try:
        return float(desconto_str.strip().replace("%", "").replace("OFF", "").strip())
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

                if nome:
                    palavras_busca = produto.lower().split()
                    nome_lower = nome.lower()
                    if not all(palavra in nome_lower for palavra in palavras_busca):
                        continue

                marca_tag = item.find('span', class_='poly-component__brand')
                marca = marca_tag.text.strip() if marca_tag else None

                # Preço original com centavos
                preco_inteiro_tag = item.find('span', class_='andes-money-amount__fraction')
                preco_centavos_tag = item.find('span', class_='andes-money-amount__cents')
                preco_str = None
                if preco_inteiro_tag:
                    preco_str = preco_inteiro_tag.text.strip()
                    if preco_centavos_tag:
                        preco_str += "," + preco_centavos_tag.text.strip()

                preco_float = format_price(preco_str) if preco_str else None

                desconto_tag = item.find('span', class_='andes-money-amount__discount')
                desconto = desconto_tag.text.strip() if desconto_tag else "Sem desconto"

                preco_com_desconto = None
                if desconto != "Sem desconto" and preco_float:
                    desconto_float = extrair_float_desconto(desconto)
                    if desconto_float is not None:
                        preco_com_desconto = round(preco_float * (1 - desconto_float / 100), 2)

                parcelamento_tag = item.find('span', class_='poly-price__installments')
                parcelamento = parcelamento_tag.text.strip() if parcelamento_tag else None

                frete_tag = item.find('div', class_='poly-component__shipping')
                frete = frete_tag.text.strip() if frete_tag else "À parte"

                resultados.append({
                    "Marca": marca,
                    "Nome": nome,
                    "Preço Original (R$)": preco_str,
                    "Desconto": desconto,
                    "Preço com Desconto (R$)": preco_com_desconto,
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
        df["Preço Float"] = df["Preço com Desconto (R$)"].apply(lambda x: x if isinstance(x, float) else None)

        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Produtos encontrados", len(df))
        if df["Preço Float"].notna().any():
            col2.metric("💰 Preço médio", f"R$ {df['Preço Float'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            col3.metric("📈 Faixa de preço", 
                f"R$ {df['Preço Float'].min():,.2f} - R$ {df['Preço Float'].max():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

        st.subheader("📋 Resultados da busca")
        st.dataframe(df.drop(columns=["Preço Float"]), use_container_width=True)

        csv = df.drop(columns=["Preço Float"]).to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar como CSV", csv, file_name="produtos_mercadolivre.csv", mime="text/csv")
    else:
        st.warning("Nenhum produto encontrado.")
