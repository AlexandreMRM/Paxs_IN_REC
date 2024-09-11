import pandas as pd
import mysql.connector
import decimal
import streamlit as st

def gerar_df_phoenix(vw_name):
    # Parametros de Login AWS
    config = {
    'user': 'user_automation_jpa',
    'password': 'luck_jpa_2024',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_recife'
    }
    # Conexão as Views
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()

    request_name = f'SELECT * FROM {vw_name}'

    # Script MySql para requests
    cursor.execute(
        request_name
    )
    # Coloca o request em uma variavel
    resultado = cursor.fetchall()
    # Busca apenas o cabecalhos do Banco
    cabecalho = [desc[0] for desc in cursor.description]

    # Fecha a conexão
    cursor.close()
    conexao.close()

    # Coloca em um dataframe e muda o tipo de decimal para float
    df = pd.DataFrame(resultado, columns=cabecalho)
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return df

st.set_page_config(layout='wide')

if 'mapa_router' not in st.session_state:

    st.session_state.mapa_router = gerar_df_phoenix('vw_router')

st.title('Paxs IN')

st.divider()

row0 = st.columns(2)

with row0[0]:

    periodo = st.date_input('Período', value=[] ,format='DD/MM/YYYY')

with row0[1]:

    container_dados = st.container()

    atualizar_dados = container_dados.button('Carregar Dados do Phoenix', use_container_width=True)

if atualizar_dados:

    st.session_state.mapa_router = gerar_df_phoenix('vw_router')

st.divider()

if len(periodo)>1:

    data_inicial = periodo[0]

    data_final = periodo[1]

    df_mapa_filtrado = st.session_state.mapa_router[(st.session_state.mapa_router['Data Execucao'] >= data_inicial) & 
                                                    (st.session_state.mapa_router['Data Execucao'] <= data_final) & 
                                                    (st.session_state.mapa_router['Tipo de Servico']=='IN') & 
                                                    (st.session_state.mapa_router['Status do Servico']!='CANCELADO') & 
                                                    (st.session_state.mapa_router['Status do Servico']!='RASCUNHO')].reset_index(drop=True)
    
    df_mapa_filtrado['Paxs Totais'] = df_mapa_filtrado['Total ADT'] + df_mapa_filtrado['Total CHD']

    adt_in = int(df_mapa_filtrado['Total ADT'].sum())

    chd_in = int(df_mapa_filtrado['Total CHD'].sum())

    chd_in_metade = int(chd_in/2)

    st.success(f'No período selecionado existem {adt_in + chd_in} passageiros.')

    df_mapa_filtrado_group = df_mapa_filtrado.groupby('Servico')['Paxs Totais'].sum().reset_index()

    st.dataframe(df_mapa_filtrado_group.sort_values(by='Paxs Totais', ascending=False), hide_index=True)
