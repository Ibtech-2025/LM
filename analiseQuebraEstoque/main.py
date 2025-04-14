import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monitor de Estoque Zerado", layout="wide")
st.title("📦 Monitor de Produtos Zerados e Pedidos")

# Upload dos arquivos
c6 = st.file_uploader("🔼 Upload C6 (Pedidos)", type=["csv"])
zza_cd = st.file_uploader("🔼 Upload ZZA Centros de Distribuição", type=["csv"])
zza_matriz = st.file_uploader("🔼 Upload ZZA Matriz", type=["csv"])

if c6 and zza_cd and zza_matriz:
    # Leitura dos arquivos CSV
    df_c6 = pd.read_csv(c6, dtype=str)
    df_zza_cd = pd.read_csv(zza_cd, dtype=str)
    df_zza_matriz = pd.read_csv(zza_matriz, dtype=str)

    # Conversão das colunas de data
    df_c6['Dt Emissao'] = pd.to_datetime(df_c6['Dt Emissao'], format='%Y%m%d', errors='coerce')
    df_c6['Data Faturamento'] = pd.to_datetime(df_c6['Data Faturamento'], format='%Y%m%d', errors='coerce')
    df_zza_cd['Data'] = pd.to_datetime(df_zza_cd['Data'], format='%Y%m%d', errors='coerce')
    df_zza_matriz['Data'] = pd.to_datetime(df_zza_matriz['Data'], format='%Y%m%d', errors='coerce')

    # Convertendo a coluna de saldo para numérico
    df_zza_cd['Fechamento Saldo Dia'] = pd.to_numeric(df_zza_cd['Fechamento Saldo Dia'], errors='coerce')
    df_zza_matriz['Fechamento Saldo Dia'] = pd.to_numeric(df_zza_matriz['Fechamento Saldo Dia'], errors='coerce')

    st.subheader("📄 Visualização Completa da Planilha ZZA Centros de Distribuição")
    st.dataframe(df_zza_cd, use_container_width=True)

    # Identificando os produtos zerados
    df_zza_cd['Zerado'] = df_zza_cd['Fechamento Saldo Dia'] == 0
    zerados = df_zza_cd[df_zza_cd['Zerado']]

    resultado = []

    for (unidade, produto), grupo in zerados.groupby(['Unidade', 'Produto']):
        # Última data que o saldo ficou zerado
        ultima_data_zerado = grupo['Data'].max()

        primeira_ocorrencia = grupo.sort_values('Data').iloc[0]
        filial = primeira_ocorrencia['Filial']
        descricao = primeira_ocorrencia['Descrição Produto']

        # Verificando se há pedido para o produto e quando chegou
        pedido = df_c6[(df_c6['Produto'] == produto) & 
                       (df_c6['Dt Emissao'] >= ultima_data_zerado)]

        if not pedido.empty:
            data_pedido = pedido['Dt Emissao'].min()
            data_chegada = pedido['Data Faturamento'].min()
            dias_zerado = (data_chegada - ultima_data_zerado).days if pd.notnull(data_chegada) else "Ainda não chegou"
        else:
            data_pedido = "Sem pedido"
            data_chegada = "Sem chegada"
            dias_zerado = "Ainda zerado"

        # Verificando o estoque exato do produto na matriz na última data
        estoque_matriz = df_zza_matriz[(df_zza_matriz['Produto'] == produto) & 
                                       (df_zza_matriz['Unidade'] == unidade) & 
                                       (df_zza_matriz['Data'] <= ultima_data_zerado)]

        # Pegando o estoque na data mais recente antes ou na última data zerada
        if not estoque_matriz.empty:
            estoque_matriz_qtd = estoque_matriz.sort_values('Data', ascending=False).iloc[0]['Fechamento Saldo Dia']
        else:
            estoque_matriz_qtd = 0  # Caso não haja estoque para o produto na matriz na data específica

        resultado.append({
            'Unidade': unidade,
            'Filial': filial,
            'Produto': produto,
            'Descrição Produto': descricao,
            'Última Data Zerado': ultima_data_zerado.date(),
            'Data do pedido': data_pedido if isinstance(data_pedido, str) else data_pedido.date(),
            'Data da chegada': data_chegada if isinstance(data_chegada, str) else data_chegada.date(),
            'Tempo Zerado (dias)': dias_zerado,
            'Estoque na Matriz (Qtd)': estoque_matriz_qtd
        })

    # Criando o DataFrame de resultado
    df_resultado = pd.DataFrame(resultado)

    # Convertendo colunas relevantes para string para exibição
    for col in ['Produto', 'Filial', 'Unidade', 'Descrição Produto']:
        df_resultado[col] = df_resultado[col].astype(str)

    st.subheader("📋 Tabela de Produtos Zerados por Unidade")
    st.dataframe(df_resultado, use_container_width=True)

    # Gerando o botão para download do arquivo CSV
    csv = df_resultado.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Resultado (.csv)", data=csv, file_name="produtos_zerados_por_unidade.csv", mime='text/csv')
