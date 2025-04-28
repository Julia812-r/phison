import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO  # Importando BytesIO

# ================== CONFIGURAÇÃO INICIAL ==================
st.set_page_config(page_title="Controle de Alunos - Phison", layout="wide")

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

# ========== LOGIN ==========
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

# ========== CABEÇALHO ==========
st.markdown('<header><h1>Controle de Alunos - Phison Centro de Treinamento</h1></header>', unsafe_allow_html=True)

# ========== BASE DE DADOS ==========
if 'alunos' not in st.session_state:
    st.session_state.alunos = pd.DataFrame(columns=[
        'Nome', 'Email', 'Data de Nascimento', 'Aniversário', 'CPF', 'Telefone', 'Vencimento do Plano'
    ])

# ========== FORMULÁRIO DE CADASTRO ==========
with st.expander("Cadastrar Novo Aluno"):
    with st.form("formulario_cadastro"):
        st.subheader("Adicionar Aluno")
        nome = st.text_input("Nome completo")
        email = st.text_input("Email")
        data_nascimento = st.date_input("Data de Nascimento")
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

# ========== FUNÇÕES ==========
def gerar_excel(df):
    # Cria um buffer em memória
    buffer = BytesIO()
    
    # Salva o DataFrame como uma planilha Excel no buffer
    df.to_excel(buffer, index=False, engine='openpyxl')
    
    # Move o ponteiro do buffer para o início para leitura
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

# ========== ALERTAS ==========
st.divider()
st.subheader("Alertas de Vencimento de Planos")
vencimentos = checar_vencimentos(st.session_state.alunos)
if vencimentos:
    for nome, status in vencimentos:
        st.warning(f"Aluno {nome}: {status}")
else:
    st.success("Nenhum plano vencendo nos próximos 7 dias.")

# ========== ANIVERSARIANTES ==========
st.divider()
st.subheader("Aniversariantes do Mês")
aniversariantes = aniversariantes_mes(st.session_state.alunos)
if not aniversariantes.empty:
    st.table(aniversariantes)
else:
    st.info("Nenhum aniversariante este mês.")

# ========== LISTA DE ALUNOS ==========
st.divider()
st.subheader("Lista de Alunos Cadastrados")

# Opções de Edição e Exclusão
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

# Mostrar tabela
st.dataframe(st.session_state.alunos, use_container_width=True)

# ========== DOWNLOAD ==========
st.download_button(
    label="Baixar lista de alunos em Excel",
    data=gerar_excel(st.session_state.alunos),
    file_name="alunos_phison.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
