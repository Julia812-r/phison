import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# ================== CONFIGURAÇÃO INICIAL ==================
st.set_page_config(page_title="Controle Phison", layout="wide")

# Cores e Estilo
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    header {
        background-color: #003566;
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ================== LOGIN ==================
senha_correta = "phison2025"

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("Login - Phison Centro de Treinamento")
    senha = st.text_input("Digite a senha:", type="password")
    if st.button("Entrar"):
        if senha == senha_correta:
            st.session_state.logado = True
            st.success("Login realizado com sucesso!")
        else:
            st.error("Senha incorreta. Tente novamente.")
    st.stop()

# ================== CABEÇALHO ==================
st.markdown('<header><h1>Controle de Alunos - Phison Centro de Treinamento</h1></header>', unsafe_allow_html=True)

# ================== SIDEBAR ==================
aba = st.sidebar.selectbox("Menu", [
    "Cadastrar Alunos",
    "Lista de Alunos",
    "Horários",
    "Despesas Mensais",
    "Controle Financeiro Diário",
    "Controle de Carga Horária"
])

# ================== BASES DE DADOS ==================
if 'alunos' not in st.session_state:
    st.session_state.alunos = pd.DataFrame(columns=[
        'Nome', 'Email', 'Data de Nascimento', 'Aniversário', 'CPF', 'Telefone', 'Vencimento do Plano'
    ])

if 'despesas' not in st.session_state:
    st.session_state.despesas = pd.DataFrame(columns=['Gasto', 'Valor', 'Vencimento'])

if 'financeiro' not in st.session_state:
    st.session_state.financeiro = pd.DataFrame(columns=['Data', 'Tipo', 'Valor'])

if 'carga_horaria' not in st.session_state:
    st.session_state.carga_horaria = {}

# ================== FUNÇÕES ==================
def gerar_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer

def checar_vencimentos(df):
    hoje = datetime.now()
    alerta = []
    for idx, row in df.iterrows():
        vencimento = datetime.strptime(row['Vencimento do Plano'], "%d/%m/%Y")
        dias_para_vencer = (vencimento - hoje).days
        if dias_para_vencer < 0:
            alerta.append((row['Nome'], "VENCIDO"))
        elif dias_para_vencer <= 7:
            alerta.append((row['Nome'], f"Vence em {dias_para_vencer} dias"))
    return alerta

def aniversariantes_mes(df):
    mes_atual = datetime.now().month
    aniversariantes = df[df['Data de Nascimento'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").month) == mes_atual]
    return aniversariantes[['Nome', 'Aniversário']]

# ================== ABAS ==================

if aba == "Cadastrar Alunos":
    with st.expander("Cadastrar Novo Aluno"):
        with st.form("formulario_cadastro"):
            st.subheader("Adicionar Aluno")
            nome = st.text_input("Nome completo")
            email = st.text_input("Email")
            
            # Restrição de data de nascimento entre 1960 e 2025
            data_nascimento = st.date_input(
                "Data de Nascimento",
                min_value=datetime(1960, 1, 1),  # Ano mínimo de 1960
                max_value=datetime(2025, 12, 31),  # Ano máximo de 2025
            )
            
            cpf = st.text_input("CPF")
            telefone = st.text_input("Telefone")
            vencimento = st.date_input("Data de Vencimento do Plano")
            
            submitted = st.form_submit_button("Adicionar")
            if submitted:
                novo_aluno = {
                    'Nome': nome,
                    'Email': email,
                    'Data de Nascimento': data_nascimento.strftime("%d/%m/%Y"),
                    'Aniversário': data_nascimento.strftime("%d/%m"),
                    'CPF': cpf,
                    'Telefone': telefone,
                    'Vencimento do Plano': vencimento.strftime("%d/%m/%Y")
                }
                st.session_state.alunos = pd.concat(
                    [st.session_state.alunos, pd.DataFrame([novo_aluno])],
                    ignore_index=True
                )
                st.success(f"Aluno {nome} adicionado com sucesso!")

elif aba == "Lista de Alunos":
    st.subheader("Alertas de Vencimento de Planos")
    vencimentos = checar_vencimentos(st.session_state.alunos)
    if vencimentos:
        for nome, status in vencimentos:
            st.warning(f"Aluno {nome}: {status}")
    else:
        st.success("Nenhum plano vencendo nos próximos 7 dias.")

    st.subheader("Aniversariantes do Mês")
    aniversariantes = aniversariantes_mes(st.session_state.alunos)
    if not aniversariantes.empty:
        st.table(aniversariantes)
    else:
        st.info("Nenhum aniversariante este mês.")

    st.subheader("Lista de Alunos Cadastrados")
    editar_aluno = st.selectbox("Selecionar um aluno para editar ou excluir:", options=[""] + st.session_state.alunos['Nome'].tolist())

    if editar_aluno:
        aluno_idx = st.session_state.alunos[st.session_state.alunos['Nome'] == editar_aluno].index[0]
        with st.form("editar_aluno"):
            st.write("Editar informações do aluno:")
            nome_editado = st.text_input("Nome", value=st.session_state.alunos.loc[aluno_idx, 'Nome'])
            email_editado = st.text_input("Email", value=st.session_state.alunos.loc[aluno_idx, 'Email'])
            data_nascimento_editado = st.date_input("Data de Nascimento", value=datetime.strptime(st.session_state.alunos.loc[aluno_idx, 'Data de Nascimento'], "%d/%m/%Y"))
            cpf_editado = st.text_input("CPF", value=st.session_state.alunos.loc[aluno_idx, 'CPF'])
            telefone_editado = st.text_input("Telefone", value=st.session_state.alunos.loc[aluno_idx, 'Telefone'])
            vencimento_editado = st.date_input("Vencimento do Plano", value=datetime.strptime(st.session_state.alunos.loc[aluno_idx, 'Vencimento do Plano'], "%d/%m/%Y"))
            
            salvar = st.form_submit_button("Salvar Alterações")
            excluir = st.form_submit_button("Excluir Aluno")

            if salvar:
                st.session_state.alunos.loc[aluno_idx] = {
                    'Nome': nome_editado,
                    'Email': email_editado,
                    'Data de Nascimento': data_nascimento_editado.strftime("%d/%m/%Y"),
                    'Aniversário': data_nascimento_editado.strftime("%d/%m"),
                    'CPF': cpf_editado,
                    'Telefone': telefone_editado,
                    'Vencimento do Plano': vencimento_editado.strftime("%d/%m/%Y")
                }
                st.success("Aluno atualizado com sucesso!")

            if excluir:
                st.session_state.alunos = st.session_state.alunos.drop(aluno_idx).reset_index(drop=True)
                st.success("Aluno excluído com sucesso!")

    st.dataframe(st.session_state.alunos, use_container_width=True)

    st.download_button(
        label="Baixar lista de alunos em Excel",
        data=gerar_excel(st.session_state.alunos),
        file_name="alunos_phison.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif aba == "Horários":
    st.title("Horários de Aula")
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    horas = [f"{h:02d}:00" for h in range(5, 22)]
    for dia in dias:
        with st.expander(dia):
            for hora in horas:
                alunos = st.text_input(f"{dia} - {hora}", value="", key=f"{dia}_{hora}")

elif aba == "Despesas Mensais":
    st.title("Despesas Mensais")
    despesas_padrao = ["Aluguel", "Água", "Internet", "Energia", "Contabilidade", "Impostos", "Maquininha", "TV", "Professor"]

    # Exibindo as despesas padrão
    for gasto in despesas_padrao:
        valor = st.number_input(f"Valor de {gasto}", min_value=0.0, format="%.2f", key=gasto)
        vencimento = st.date_input(f"Vencimento de {gasto}", key=f"v_{gasto}")
        if st.button(f"Salvar {gasto}"):
            nova_despesa = {'Gasto': gasto, 'Valor': valor, 'Vencimento': vencimento.strftime("%d/%m/%Y")}
            st.session_state.despesas = pd.concat(
                [st.session_state.despesas, pd.DataFrame([nova_despesa])],
                ignore_index=True
            )
            st.success(f"{gasto} salvo com sucesso!")

    st.subheader("Adicionar Nova Despesa")
    with st.form("nova_despesa"):
        novo_gasto = st.text_input("Nome da Despesa")
        novo_valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        novo_vencimento = st.date_input("Vencimento")
        if st.form_submit_button("Adicionar Despesa"):
            nova_despesa = {'Gasto': novo_gasto, 'Valor': novo_valor, 'Vencimento': novo_vencimento.strftime("%d/%m/%Y")}
            st.session_state.despesas = pd.concat(
                [st.session_state.despesas, pd.DataFrame([nova_despesa])],
                ignore_index=True
            )
            st.success(f"Despesa {novo_gasto} adicionada com sucesso!")

    st.subheader("Excluir Despesa")
    despesa_excluir = st.selectbox("Selecione uma despesa para excluir:", options=[""] + st.session_state.despesas['Gasto'].tolist())
    if despesa_excluir:
        if st.button("Excluir"):
            st.session_state.despesas = st.session_state.despesas[st.session_state.despesas['Gasto'] != despesa_excluir].reset_index(drop=True)
            st.success(f"Despesa {despesa_excluir} excluída com sucesso!")

    st.dataframe(st.session_state.despesas, use_container_width=True)

elif aba == "Controle Financeiro Diário":
    st.title("Controle Financeiro Diário")
    mes = st.selectbox("Escolha o mês", options=[f"{i:02d}" for i in range(1, 13)])
    ano = datetime.now().year

    for dia in range(1, 32):
        col1, col2 = st.columns(2)
        with col1:
            entrada = st.number_input(f"Entrada {dia}/{mes}", min_value=0.0, format="%.2f", key=f"e_{mes}_{dia}")
            if entrada > 0:
                novo = {'Data': f"{dia}/{mes}/{ano}", 'Tipo': 'Entrada', 'Valor': entrada}
                st.session_state.financeiro = pd.concat([st.session_state.financeiro, pd.DataFrame([novo])], ignore_index=True)
        with col2:
            saida = st.number_input(f"Saída {dia}/{mes}", min_value=0.0, format="%.2f", key=f"s_{mes}_{dia}")
            if saida > 0:
                novo = {'Data': f"{dia}/{mes}/{ano}", 'Tipo': 'Saída', 'Valor': saida}
                st.session_state.financeiro = pd.concat([st.session_state.financeiro, pd.DataFrame([novo])], ignore_index=True)

    df_mes = st.session_state.financeiro[st.session_state.financeiro['Data'].str.contains(f"/{mes}/{ano}")]
    total_entrada = df_mes[df_mes['Tipo'] == 'Entrada']['Valor'].sum()
    total_saida = df_mes[df_mes['Tipo'] == 'Saída']['Valor'].sum() 