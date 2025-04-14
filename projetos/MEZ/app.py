import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monitor de Estoque Zerado", layout="wide")
st.title("📦 Monitor de Produtos Zerados e Pedidos")

# Upload dos arquivos
c6 = st.file_uploader("🔼 Upload C6 (Pedidos)", type=["csv"])
zza = st.file_uploader("🔼 Upload ZZA (Saldos)", type=["csv"])

if c6 and zza:
    df_c6 = pd.read_csv(c6, dtype=str)
    df_zza = pd.read_csv(zza, dtype=str)

    # Conversão das datas (depois do read_csv)
    df_c6['Dt Emissao'] = pd.to_datetime(df_c6['Dt Emissao'], format='%Y%m%d', errors='coerce')
    df_c6['Data Faturamento'] = pd.to_datetime(df_c6['Data Faturamento'], format='%Y%m%d', errors='coerce')
    df_zza['Data'] = pd.to_datetime(df_zza['Data'], format='%Y%m%d', errors='coerce')

    # Conversão da coluna de saldo para numérica
    df_zza['Fechamento Saldo Dia'] = pd.to_numeric(df_zza['Fechamento Saldo Dia'], errors='coerce')

    # Mostra todos os dados da ZZA
    st.subheader("📄 Visualização Completa da Planilha ZZA")
    st.dataframe(df_zza, use_container_width=True)

    # Marca produtos zerados
    df_zza['Zerado'] = df_zza['Fechamento Saldo Dia'] == 0
    zerados = df_zza[df_zza['Zerado']]

    resultado = []

    # Agrupa por unidade e produto
    for (unidade, produto), grupo in zerados.groupby(['Unidade', 'Produto']):
        primeira_data_zerado = grupo['Data'].min()

        # Obtem dados fixos da primeira ocorrência
        primeira_ocorrencia = grupo.sort_values('Data').iloc[0]
        filial = primeira_ocorrencia['Filial']
        descricao = primeira_ocorrencia['Descrição Produto']

        # Verifica se teve pedido após o produto zerar
        pedido = df_c6[(df_c6['Produto'] == produto) & 
                       (df_c6['Dt Emissao'] >= primeira_data_zerado)]

        if not pedido.empty:
            data_pedido = pedido['Dt Emissao'].min()
            data_chegada = pedido['Data Faturamento'].min()
            dias_zerado = (data_chegada - primeira_data_zerado).days if pd.notnull(data_chegada) else "Ainda não chegou"
        else:
            data_pedido = "Sem pedido"
            data_chegada = "Sem chegada"
            dias_zerado = "Ainda zerado"

        resultado.append({
            'Unidade': unidade,
            'Filial': filial,
            'Produto': produto,
            'Descrição Produto': descricao,
            'Zerado desde': primeira_data_zerado.date(),
            'Data do pedido': data_pedido if isinstance(data_pedido, str) else data_pedido.date(),
            'Data da chegada': data_chegada if isinstance(data_chegada, str) else data_chegada.date(),
            'Tempo Zerado (dias)': dias_zerado
        })

    df_resultado = pd.DataFrame(resultado)

    # Corrige os tipos para strings antes de mostrar
    for col in ['Produto', 'Filial', 'Unidade', 'Descrição Produto']:
        df_resultado[col] = df_resultado[col].astype(str)

    st.subheader("📋 Tabela de Produtos Zerados por Unidade")
    st.dataframe(df_resultado, use_container_width=True)

    # Download
    csv = df_resultado.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Resultado (.csv)", data=csv, file_name="produtos_zerados_por_unidade.csv", mime='text/csv')
