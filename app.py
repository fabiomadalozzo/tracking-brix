#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Tracking BRIX - Versão com Gerenciamento de Usuários
Permite cadastrar/editar/excluir usuários diretamente pelo sistema
Escritório de contabilidade - Brasil
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import hashlib
import json

# Configuração da página
st.set_page_config(
    page_title="🚢 Sistema BRIX - Tracking com Usuários",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e1e8ed;
    }
    .cliente-badge {
        background: #27ae60;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 1rem 0;
    }
    .admin-badge {
        background: #e74c3c;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 1rem 0;
    }
    .user-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    .admin-user {
        border-left-color: #e74c3c !important;
    }
    .cliente-user {
        border-left-color: #27ae60 !important;
    }
</style>
""", unsafe_allow_html=True)

# Dados da empresa
DADOS_EMPRESA = {
    'nome': 'BRIX LOGÍSTICA',
    'endereco': 'Av Ranieri Mazzilli, 755',
    'cidade': 'Foz do Iguaçu - PR',
    'telefone': '(45) 3198-4037',
    'email': 'fabio@brixcontabilidade.com.br',
    'cnpj': '31.247.532/0001-51'
}

# Colunas do sistema
COLUNAS = [
    'CLIENTE', 'CONTAINER', 'CARREGAMENTO', 'EMBARQUE NAVIO',
    'SAIDA NAVIO', 'PREVISAO CHEGADA PARANAGUA', 'CHEGADA PARANAGUA',
    'CANAL RFB', 'LIBERAÇAO PARANAGUA', 'CHEGADA CIUDAD DEL ESTE PY',
    'DESCARREGAMENTO'
]

def inicializar_usuarios():
    """Inicializa a base de usuários se não existir"""
    if 'usuarios_db' not in st.session_state:
        st.session_state.usuarios_db = {
            "admin": {
                "senha": "admin123",
                "tipo": "admin",
                "cliente": None,
                "nome": "Administrador BRIX",
                "email": "admin@brixlogistica.com.br",
                "ativo": True,
                "data_criacao": "01/06/2025"
            },
            "empresa_abc": {
                "senha": "abc123",
                "tipo": "cliente",
                "cliente": "EMPRESA ABC LTDA",
                "nome": "Empresa ABC Ltda",
                "email": "contato@empresaabc.com.br",
                "ativo": True,
                "data_criacao": "01/06/2025"
            },
            "comercial_xyz": {
                "senha": "xyz123",
                "tipo": "cliente", 
                "cliente": "COMERCIAL XYZ S.A.",
                "nome": "Comercial XYZ S.A.",
                "email": "gerencia@comercialxyz.com.br",
                "ativo": True,
                "data_criacao": "01/06/2025"
            }
        }

def salvar_usuarios():
    """Simula salvamento dos usuários (em produção seria banco de dados)"""
    # Em produção, aqui você salvaria no banco de dados
    pass

def gerar_usuario_automatico(nome_cliente):
    """Gera usuário automático baseado no nome do cliente"""
    # Remove acentos e caracteres especiais, transforma em minúscula
    import unicodedata
    nome_limpo = unicodedata.normalize('NFD', nome_cliente)
    nome_limpo = ''.join(char for char in nome_limpo if unicodedata.category(char) != 'Mn')
    nome_limpo = nome_limpo.replace(' ', '_').replace('.', '').replace(',', '').lower()
    
    # Pega as primeiras palavras significativas
    palavras = [p for p in nome_limpo.split('_') if len(p) > 2 and p not in ['ltda', 'sa', 'epp', 'me']]
    usuario = '_'.join(palavras[:2]) if len(palavras) >= 2 else palavras[0] if palavras else nome_limpo
    
    return usuario[:20]  # Limita o tamanho

def gerar_senha_temporaria():
    """Gera senha temporária simples"""
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def verificar_login(usuario, senha):
    """Verifica credenciais do usuário"""
    inicializar_usuarios()
    if usuario in st.session_state.usuarios_db:
        user_data = st.session_state.usuarios_db[usuario]
        if user_data["senha"] == senha and user_data["ativo"]:
            return user_data
    return None

def inicializar_sessao():
    """Inicializa variáveis da sessão"""
    if 'logado' not in st.session_state:
        st.session_state.logado = False
    if 'usuario_info' not in st.session_state:
        st.session_state.usuario_info = None
    if 'df_tracking' not in st.session_state:
        st.session_state.df_tracking = pd.DataFrame(columns=COLUNAS)
    inicializar_usuarios()

def criar_dados_exemplo():
    """Cria dados de exemplo com múltiplos clientes"""
    dados_exemplo = [
        {
            'CLIENTE': 'EMPRESA ABC LTDA',
            'CONTAINER': 'TCLU1234567',
            'CARREGAMENTO': '15/05/2025',
            'EMBARQUE NAVIO': '18/05/2025',
            'SAIDA NAVIO': '20/05/2025',
            'PREVISAO CHEGADA PARANAGUA': '25/05/2025',
            'CHEGADA PARANAGUA': '24/05/2025',
            'CANAL RFB': 'VERDE',
            'LIBERAÇAO PARANAGUA': '24/05/2025',
            'CHEGADA CIUDAD DEL ESTE PY': '26/05/2025',
            'DESCARREGAMENTO': '28/05/2025'
        },
        {
            'CLIENTE': 'COMERCIAL XYZ S.A.',
            'CONTAINER': 'MSKU9876543',
            'CARREGAMENTO': '20/05/2025',
            'EMBARQUE NAVIO': '23/05/2025',
            'SAIDA NAVIO': '25/05/2025',
            'PREVISAO CHEGADA PARANAGUA': '30/05/2025',
            'CHEGADA PARANAGUA': '29/05/2025',
            'CANAL RFB': 'VERMELHO',
            'LIBERAÇAO PARANAGUA': '',
            'CHEGADA CIUDAD DEL ESTE PY': '',
            'DESCARREGAMENTO': ''
        }
    ]
    return pd.DataFrame(dados_exemplo)

def filtrar_dados_por_cliente(df, usuario_info):
    """Filtra dados baseado no tipo de usuário"""
    if usuario_info["tipo"] == "admin":
        return df
    else:
        return df[df['CLIENTE'] == usuario_info["cliente"]]

def colorir_linha(row):
    """Aplica cores baseado no canal RFB"""
    if row['CANAL RFB'] == 'VERDE':
        return ['background-color: #d5f4e6'] * len(row)
    elif row['CANAL RFB'] == 'VERMELHO':
        return ['background-color: #fadbd8'] * len(row)
    else:
        return [''] * len(row)

def pagina_gerenciar_usuarios():
    """Página para gerenciar usuários (só admin)"""
    st.header("👥 Gerenciamento de Usuários")
    
    # Tabs para organizar
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Usuários", "➕ Novo Usuário", "📊 Estatísticas"])
    
    with tab1:
        st.subheader("👤 Usuários Cadastrados")
        
        # Mostrar usuários em cards
        for usuario_id, dados in st.session_state.usuarios_db.items():
            card_class = "admin-user" if dados["tipo"] == "admin" else "cliente-user"
            status_emoji = "✅" if dados["ativo"] else "❌"
            tipo_emoji = "👑" if dados["tipo"] == "admin" else "👤"
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="user-card {card_class}">
                    <h4>{tipo_emoji} {dados['nome']} {status_emoji}</h4>
                    <p><strong>Usuário:</strong> {usuario_id}</p>
                    <p><strong>Email:</strong> {dados['email']}</p>
                    <p><strong>Tipo:</strong> {dados['tipo'].title()}</p>
                    {f"<p><strong>Cliente:</strong> {dados['cliente']}</p>" if dados['cliente'] else ""}
                    <p><strong>Criado:</strong> {dados['data_criacao']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"✏️ Editar", key=f"edit_{usuario_id}"):
                    st.session_state.editando_usuario = usuario_id
                    st.rerun()
            
            with col3:
                status_btn = "🔓 Ativar" if not dados["ativo"] else "🔒 Desativar"
                if st.button(status_btn, key=f"toggle_{usuario_id}"):
                    st.session_state.usuarios_db[usuario_id]["ativo"] = not dados["ativo"]
                    salvar_usuarios()
                    st.success(f"✅ Usuário {usuario_id} {'ativado' if dados['ativo'] else 'desativado'}!")
                    st.rerun()
            
            with col4:
                if usuario_id != "admin":  # Não pode excluir admin
                    if st.button(f"🗑️ Excluir", key=f"del_{usuario_id}"):
                        st.session_state.excluindo_usuario = usuario_id
        
        # Modal de confirmação para exclusão
        if 'excluindo_usuario' in st.session_state:
            st.error(f"⚠️ Tem certeza que deseja excluir o usuário '{st.session_state.excluindo_usuario}'?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Sim, excluir"):
                    del st.session_state.usuarios_db[st.session_state.excluindo_usuario]
                    del st.session_state.excluindo_usuario
                    salvar_usuarios()
                    st.success("🗑️ Usuário excluído!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancelar"):
                    del st.session_state.excluindo_usuario
                    st.rerun()
        
        # Formulário de edição
        if 'editando_usuario' in st.session_state:
            usuario_id = st.session_state.editando_usuario
            dados = st.session_state.usuarios_db[usuario_id]
            
            st.markdown("---")
            st.subheader(f"✏️ Editando: {dados['nome']}")
            
            with st.form("editar_usuario"):
                col1, col2 = st.columns(2)
                
                with col1:
                    novo_nome = st.text_input("Nome:", value=dados['nome'])
                    novo_email = st.text_input("Email:", value=dados['email'])
                    nova_senha = st.text_input("Nova Senha (deixe vazio para manter):", type="password")
                
                with col2:
                    if dados['tipo'] == 'cliente':
                        # Buscar clientes únicos dos dados
                        clientes_disponiveis = [""] + list(st.session_state.df_tracking['CLIENTE'].unique()) if not st.session_state.df_tracking.empty else [""]
                        cliente_atual_idx = clientes_disponiveis.index(dados['cliente']) if dados['cliente'] in clientes_disponiveis else 0
                        novo_cliente = st.selectbox("Cliente:", clientes_disponiveis, index=cliente_atual_idx)
                    else:
                        novo_cliente = None
                        st.info("👑 Usuário administrador - sem restrição de cliente")
                    
                    novo_ativo = st.checkbox("Ativo", value=dados['ativo'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                        # Atualizar dados
                        st.session_state.usuarios_db[usuario_id].update({
                            'nome': novo_nome,
                            'email': novo_email,
                            'cliente': novo_cliente,
                            'ativo': novo_ativo
                        })
                        
                        if nova_senha:
                            st.session_state.usuarios_db[usuario_id]['senha'] = nova_senha
                        
                        salvar_usuarios()
                        del st.session_state.editando_usuario
                        st.success("✅ Usuário atualizado!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Cancelar"):
                        del st.session_state.editando_usuario
                        st.rerun()
    
    with tab2:
        st.subheader("➕ Cadastrar Novo Usuário")
        
        # Método de criação
        metodo = st.radio("Escolha o método:", ["📝 Manual", "🤖 Automático (baseado em cliente)"])
        
        if metodo == "📝 Manual":
            with st.form("novo_usuario_manual"):
                col1, col2 = st.columns(2)
                
                with col1:
                    novo_usuario = st.text_input("Nome de Usuário:", placeholder="ex: empresa_nova")
                    novo_nome = st.text_input("Nome Completo:", placeholder="ex: Empresa Nova Ltda")
                    novo_email = st.text_input("Email:", placeholder="contato@empresa.com.br")
                
                with col2:
                    nova_senha = st.text_input("Senha:", type="password", placeholder="Senha temporária")
                    tipo_usuario = st.selectbox("Tipo:", ["cliente", "admin"])
                    
                    if tipo_usuario == "cliente":
                        # Buscar clientes únicos dos dados
                        clientes_disponiveis = list(st.session_state.df_tracking['CLIENTE'].unique()) if not st.session_state.df_tracking.empty else []
                        if clientes_disponiveis:
                            cliente_vinculado = st.selectbox("Cliente:", [""] + clientes_disponiveis)
                        else:
                            cliente_vinculado = st.text_input("Nome do Cliente:", placeholder="Digite o nome exato do cliente")
                    else:
                        cliente_vinculado = None
                        st.info("👑 Admin tem acesso a todos os dados")
                
                if st.form_submit_button("👤 Criar Usuário", type="primary"):
                    # Validações
                    erros = []
                    if not novo_usuario or novo_usuario in st.session_state.usuarios_db:
                        erros.append("❌ Nome de usuário inválido ou já existe")
                    if not novo_nome:
                        erros.append("❌ Nome completo é obrigatório")
                    if not nova_senha:
                        erros.append("❌ Senha é obrigatória")
                    if tipo_usuario == "cliente" and not cliente_vinculado:
                        erros.append("❌ Cliente é obrigatório para usuários tipo cliente")
                    
                    if erros:
                        for erro in erros:
                            st.error(erro)
                    else:
                        # Criar usuário
                        st.session_state.usuarios_db[novo_usuario] = {
                            "senha": nova_senha,
                            "tipo": tipo_usuario,
                            "cliente": cliente_vinculado if tipo_usuario == "cliente" else None,
                            "nome": novo_nome,
                            "email": novo_email,
                            "ativo": True,
                            "data_criacao": datetime.now().strftime("%d/%m/%Y")
                        }
                        
                        salvar_usuarios()
                        st.success(f"✅ Usuário '{novo_usuario}' criado com sucesso!")
                        
                        # Mostrar dados de acesso
                        st.info(f"""
                        🔐 **Dados de Acesso Criados:**
                        - **Usuário:** {novo_usuario}
                        - **Senha:** {nova_senha}
                        - **Tipo:** {tipo_usuario.title()}
                        {f"- **Cliente:** {cliente_vinculado}" if cliente_vinculado else ""}
                        
                        📧 Envie essas informações para o cliente por email seguro!
                        """)
        
        else:  # Automático
            st.info("🤖 Este método cria usuários automaticamente baseado nos clientes existentes nos dados")
            
            if st.session_state.df_tracking.empty:
                st.warning("⚠️ Carregue dados primeiro para usar este método")
            else:
                clientes_sem_usuario = []
                clientes_existentes = [dados['cliente'] for dados in st.session_state.usuarios_db.values() if dados['cliente']]
                
                for cliente in st.session_state.df_tracking['CLIENTE'].unique():
                    if cliente not in clientes_existentes:
                        clientes_sem_usuario.append(cliente)
                
                if not clientes_sem_usuario:
                    st.success("✅ Todos os clientes já possuem usuários!")
                else:
                    st.write("📋 Clientes sem usuário:")
                    for cliente in clientes_sem_usuario:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"🏢 {cliente}")
                        
                        with col2:
                            usuario_sugerido = gerar_usuario_automatico(cliente)
                            st.code(usuario_sugerido)
                        
                        with col3:
                            if st.button(f"➕ Criar", key=f"auto_{cliente}"):
                                senha_temp = gerar_senha_temporaria()
                                
                                st.session_state.usuarios_db[usuario_sugerido] = {
                                    "senha": senha_temp,
                                    "tipo": "cliente",
                                    "cliente": cliente,
                                    "nome": cliente,
                                    "email": f"contato@{usuario_sugerido.replace('_', '')}.com.br",
                                    "ativo": True,
                                    "data_criacao": datetime.now().strftime("%d/%m/%Y")
                                }
                                
                                salvar_usuarios()
                                st.success(f"✅ Usuário criado: {usuario_sugerido} / {senha_temp}")
                                st.rerun()
    
    with tab3:
        st.subheader("📊 Estatísticas de Usuários")
        
        # Métricas
        total_usuarios = len(st.session_state.usuarios_db)
        usuarios_ativos = sum(1 for u in st.session_state.usuarios_db.values() if u["ativo"])
        admins = sum(1 for u in st.session_state.usuarios_db.values() if u["tipo"] == "admin")
        clientes = sum(1 for u in st.session_state.usuarios_db.values() if u["tipo"] == "cliente")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total", total_usuarios)
        with col2:
            st.metric("✅ Ativos", usuarios_ativos)
        with col3:
            st.metric("👑 Admins", admins)
        with col4:
            st.metric("👤 Clientes", clientes)
        
        # Gráfico de tipos de usuário
        if total_usuarios > 0:
            tipos_count = {"Admin": admins, "Cliente": clientes}
            fig = px.pie(values=list(tipos_count.values()), names=list(tipos_count.keys()), 
                        title="📊 Distribuição por Tipo de Usuário")
            st.plotly_chart(fig, use_container_width=True)

def tela_login():
    """Exibe tela de login"""
    st.markdown("""
    <div class="main-header">
        <h1>🚢 BRIX LOGÍSTICA</h1>
        <h3>Sistema de Tracking Seguro</h3>
        <p>Acesso Restrito - Login Necessário</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown("### 🔐 Fazer Login")
    
    with st.form("login_form"):
        usuario = st.text_input("👤 Usuário:", placeholder="Digite seu usuário...")
        senha = st.text_input("🔑 Senha:", type="password", placeholder="Digite sua senha...")
        submitted = st.form_submit_button("🚀 Entrar", type="primary")
        
        if submitted:
            if usuario and senha:
                user_info = verificar_login(usuario, senha)
                if user_info:
                    st.session_state.logado = True
                    st.session_state.usuario_info = user_info
                    st.success(f"✅ Bem-vindo, {user_info['nome']}!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos, ou conta desativada!")
            else:
                st.warning("⚠️ Preencha todos os campos!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Informações de acesso para demonstração
    st.markdown("---")
    st.markdown("### 🎯 Contas de Demonstração:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **👑 Administrador:**
        - **Usuário:** `admin`
        - **Senha:** `admin123`
        - **Acesso:** Todos os dados + Gerenciar usuários
        """)
    
    with col2:
        # Mostrar alguns usuários cliente dinamicamente
        usuarios_cliente = {k: v for k, v in st.session_state.usuarios_db.items() if v["tipo"] == "cliente" and v["ativo"]}
        if usuarios_cliente:
            st.markdown("**👤 Clientes:**")
            for usuario_id, dados in list(usuarios_cliente.items())[:3]:  # Mostrar só os 3 primeiros
                st.markdown(f"- **Usuário:** `{usuario_id}` | **Senha:** `{dados['senha']}`")

def dashboard_principal():
    """Dashboard principal após login"""
    usuario_info = st.session_state.usuario_info
    
    # Cabeçalho
    st.markdown(f"""
    <div class="main-header">
        <h1>🚢 {DADOS_EMPRESA['nome']}</h1>
        <h3>Sistema de Tracking de Trânsito</h3>
        <p>📍 {DADOS_EMPRESA['endereco']} - {DADOS_EMPRESA['cidade']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Badge do usuário e controles
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        if usuario_info["tipo"] == "admin":
            st.markdown(f'<div class="admin-badge">👑 Admin: {usuario_info["nome"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="cliente-badge">👤 Cliente: {usuario_info["nome"]}</div>', unsafe_allow_html=True)
    
    with col2:
        if usuario_info["tipo"] == "admin":
            if st.button("👥 Usuários"):
                st.session_state.pagina_atual = "usuarios"
                st.rerun()
    
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.logado = False
            st.session_state.usuario_info = None
            if 'pagina_atual' in st.session_state:
                del st.session_state.pagina_atual
            st.rerun()
    
    # Verificar se está na página de usuários (só admin)
    if 'pagina_atual' in st.session_state and st.session_state.pagina_atual == "usuarios":
        if usuario_info["tipo"] == "admin":
            col1, col2 = st.columns([1, 6])
            with col1:
                if st.button("⬅️ Voltar"):
                    del st.session_state.pagina_atual
                    st.rerun()
            
            pagina_gerenciar_usuarios()
            return
        else:
            st.error("❌ Acesso negado!")
            return
    
    # Resto do dashboard (código anterior)
    # Sidebar
    with st.sidebar:
        st.header("🔧 Controles")
        
        if usuario_info["tipo"] == "admin":
            if st.button("📋 Carregar Dados de Exemplo", type="primary"):
                st.session_state.df_tracking = criar_dados_exemplo()
                st.success("✅ Dados carregados!")
                st.rerun()
        
        # Upload só para admin
        if usuario_info["tipo"] == "admin":
            st.subheader("📂 Importar Excel")
            uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=['xlsx', 'xls'])
            
            if uploaded_file is not None:
                try:
                    df_uploaded = pd.read_excel(uploaded_file)
                    colunas_faltando = set(COLUNAS) - set(df_uploaded.columns)
                    
                    if colunas_faltando:
                        st.error(f"❌ Colunas faltando: {', '.join(colunas_faltando)}")
                    else:
                        if st.button("📥 Importar Dados"):
                            st.session_state.df_tracking = df_uploaded[COLUNAS].copy()
                            st.success("✅ Dados importados!")
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        # Informações do usuário
        st.markdown("---")
        st.subheader("👤 Sua Conta")
        st.write(f"**Nome:** {usuario_info['nome']}")
        st.write(f"**Tipo:** {usuario_info['tipo'].title()}")
        if usuario_info['tipo'] == 'cliente':
            st.write(f"**Acesso:** {usuario_info['cliente']}")
        
        # Menu adicional para admin
        if usuario_info["tipo"] == "admin":
            st.markdown("---")
            st.subheader("⚙️ Administração")
            total_usuarios = len(st.session_state.usuarios_db)
            usuarios_ativos = sum(1 for u in st.session_state.usuarios_db.values() if u["ativo"])
            st.metric("👥 Usuários", f"{usuarios_ativos}/{total_usuarios}")
    
    if st.session_state.df_tracking.empty:
        if usuario_info["tipo"] == "admin":
            st.warning("⚠️ Nenhum dado encontrado. Use os controles da barra lateral para carregar dados.")
        else:
            st.info("📋 Nenhum tracking disponível no momento. Entre em contato com a BRIX para mais informações.")
        return
    
    # Filtrar dados baseado no usuário
    df_usuario = filtrar_dados_por_cliente(st.session_state.df_tracking, usuario_info)
    
    if df_usuario.empty:
        st.info(f"📋 Nenhum tracking encontrado para {usuario_info['nome']}.")
        return
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_registros = len(df_usuario)
    verde_count = len(df_usuario[df_usuario['CANAL RFB'] == 'VERDE'])
    vermelho_count = len(df_usuario[df_usuario['CANAL RFB'] == 'VERMELHO'])
    pendentes = len(df_usuario[df_usuario['CANAL RFB'].isin(['', None])])
    
    with col1:
        if usuario_info["tipo"] == "admin":
            st.metric("📦 Total Containers", total_registros)
        else:
            st.metric("📦 Seus Containers", total_registros)
    
    with col2:
        st.metric("🟢 Canal Verde", verde_count, delta=f"{(verde_count/total_registros*100):.1f}%" if total_registros > 0 else "0%")
    
    with col3:
        st.metric("🔴 Canal Vermelho", vermelho_count, delta=f"{(vermelho_count/total_registros*100):.1f}%" if total_registros > 0 else "0%")
    
    with col4:
        st.metric("⏳ Pendentes", pendentes)
    
    # Gráficos
    if len(df_usuario) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pizza - Canal RFB
            canal_counts = df_usuario['CANAL RFB'].value_counts()
            if not canal_counts.empty:
                title_grafico = "📊 Distribuição por Canal RFB" if usuario_info["tipo"] == "admin" else "📊 Seus Containers por Canal RFB"
                fig_pie = px.pie(
                    values=canal_counts.values,
                    names=canal_counts.index,
                    title=title_grafico,
                    color_discrete_map={'VERDE': '#27ae60', 'VERMELHO': '#e74c3c', '': '#95a5a6'}
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Timeline ou clientes (dependendo do tipo de usuário)
            if usuario_info["tipo"] == "admin":
                # Gráfico de clientes para admin
                cliente_counts = df_usuario['CLIENTE'].value_counts().head(10)
                if not cliente_counts.empty:
                    fig_bar = px.bar(
                        x=cliente_counts.values,
                        y=cliente_counts.index,
                        orientation='h',
                        title="📈 Top 10 Clientes",
                        color_discrete_sequence=['#3498db']
                    )
                    fig_bar.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                # Status timeline para clientes
                st.markdown("### 📅 Status dos Seus Containers")
                for _, row in df_usuario.iterrows():
                    status_emoji = "🟢" if row['CANAL RFB'] == 'VERDE' else "🔴" if row['CANAL RFB'] == 'VERMELHO' else "⏳"
                    previsao = row['PREVISAO CHEGADA PARANAGUA'] if row['PREVISAO CHEGADA PARANAGUA'] else "Não informado"
                    st.write(f"{status_emoji} **{row['CONTAINER']}** - Previsão: {previsao}")
    
    # Filtros
    st.subheader("🔍 Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if usuario_info["tipo"] == "admin":
            filtro_cliente = st.text_input("Cliente", placeholder="Digite o nome do cliente...")
        else:
            filtro_cliente = ""
    
    with col2:
        filtro_container = st.text_input("Container", placeholder="Digite o número do container...")
    
    with col3:
        filtro_canal = st.selectbox("Canal RFB", ['Todos', 'VERDE', 'VERMELHO'])
    
    # Aplicar filtros
    df_filtrado = df_usuario.copy()
    
    if filtro_cliente and usuario_info["tipo"] == "admin":
        df_filtrado = df_filtrado[df_filtrado['CLIENTE'].str.contains(filtro_cliente, case=False, na=False)]
    
    if filtro_container:
        df_filtrado = df_filtrado[df_filtrado['CONTAINER'].str.contains(filtro_container, case=False, na=False)]
    
    if filtro_canal != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['CANAL RFB'] == filtro_canal]
    
    # Tabela principal
    titulo_tabela = f"📋 Lista de Trackings ({len(df_filtrado)} registros)" if usuario_info["tipo"] == "admin" else f"📋 Seus Trackings ({len(df_filtrado)} registros)"
    st.subheader(titulo_tabela)
    
    if not df_filtrado.empty:
        # Aplicar cores à tabela
        styled_df = df_filtrado.style.apply(colorir_linha, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Download dos dados
        csv = df_filtrado.to_csv(index=False)
        nome_arquivo = f"tracking_todos_{datetime.now().strftime('%Y%m%d')}.csv" if usuario_info["tipo"] == "admin" else f"tracking_{usuario_info['nome'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
        label_download = "💾 Baixar Todos os Dados (CSV)" if usuario_info["tipo"] == "admin" else "💾 Baixar Seus Dados (CSV)"
        
        st.download_button(
            label=label_download,
            data=csv,
            file_name=nome_arquivo,
            mime="text/csv"
        )
        
        # Formulário para novo registro (só admin)
        if usuario_info["tipo"] == "admin":
            with st.expander("➕ Adicionar Novo Tracking"):
                with st.form("novo_tracking"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Sugerir clientes existentes
                        clientes_existentes = [""] + sorted(st.session_state.df_tracking['CLIENTE'].unique().tolist()) if not st.session_state.df_tracking.empty else [""]
                        
                        opcao_cliente = st.radio("Cliente:", ["Selecionar existente", "Digitar novo"])
                        
                        if opcao_cliente == "Selecionar existente":
                            novo_cliente = st.selectbox("Cliente *", clientes_existentes)
                        else:
                            novo_cliente = st.text_input("Cliente *", placeholder="Nome do novo cliente...")
                        
                        novo_container = st.text_input("Container *", placeholder="Número do container...")
                        carregamento = st.text_input("Carregamento", placeholder="DD/MM/AAAA")
                        embarque = st.text_input("Embarque Navio", placeholder="DD/MM/AAAA")
                        saida = st.text_input("Saída Navio", placeholder="DD/MM/AAAA")
                        previsao = st.text_input("Previsão Chegada Paranaguá", placeholder="DD/MM/AAAA")
                    
                    with col2:
                        chegada = st.text_input("Chegada Paranaguá", placeholder="DD/MM/AAAA")
                        canal_rfb = st.selectbox("Canal RFB", ['', 'VERDE', 'VERMELHO'])
                        liberacao = st.text_input("Liberação Paranaguá", placeholder="DD/MM/AAAA")
                        chegada_py = st.text_input("Chegada Ciudad del Este PY", placeholder="DD/MM/AAAA")
                        descarregamento = st.text_input("Descarregamento", placeholder="DD/MM/AAAA")
                        
                        # Checkbox para criar usuário automaticamente
                        criar_usuario_auto = st.checkbox("🤖 Criar usuário para este cliente automaticamente")
                    
                    submitted = st.form_submit_button("💾 Salvar Tracking", type="primary")
                    
                    if submitted:
                        if not novo_cliente or not novo_container:
                            st.error("❌ Cliente e Container são obrigatórios!")
                        else:
                            novo_registro = {
                                'CLIENTE': novo_cliente,
                                'CONTAINER': novo_container,
                                'CARREGAMENTO': carregamento,
                                'EMBARQUE NAVIO': embarque,
                                'SAIDA NAVIO': saida,
                                'PREVISAO CHEGADA PARANAGUA': previsao,
                                'CHEGADA PARANAGUA': chegada,
                                'CANAL RFB': canal_rfb,
                                'LIBERAÇAO PARANAGUA': liberacao,
                                'CHEGADA CIUDAD DEL ESTE PY': chegada_py,
                                'DESCARREGAMENTO': descarregamento
                            }
                            
                            novo_df = pd.DataFrame([novo_registro])
                            st.session_state.df_tracking = pd.concat([st.session_state.df_tracking, novo_df], ignore_index=True)
                            
                            # Criar usuário automaticamente se solicitado
                            if criar_usuario_auto:
                                # Verificar se cliente já tem usuário
                                cliente_ja_tem_usuario = any(
                                    dados['cliente'] == novo_cliente 
                                    for dados in st.session_state.usuarios_db.values() 
                                    if dados['cliente']
                                )
                                
                                if not cliente_ja_tem_usuario:
                                    usuario_auto = gerar_usuario_automatico(novo_cliente)
                                    senha_auto = gerar_senha_temporaria()
                                    
                                    # Verificar se usuário já existe
                                    if usuario_auto not in st.session_state.usuarios_db:
                                        st.session_state.usuarios_db[usuario_auto] = {
                                            "senha": senha_auto,
                                            "tipo": "cliente",
                                            "cliente": novo_cliente,
                                            "nome": novo_cliente,
                                            "email": f"contato@{usuario_auto.replace('_', '')}.com.br",
                                            "ativo": True,
                                            "data_criacao": datetime.now().strftime("%d/%m/%Y")
                                        }
                                        
                                        salvar_usuarios()
                                        
                                        st.success(f"✅ Tracking adicionado e usuário criado!")
                                        st.info(f"""
                                        🤖 **Usuário criado automaticamente:**
                                        - **Usuário:** {usuario_auto}
                                        - **Senha:** {senha_auto}
                                        - **Cliente:** {novo_cliente}
                                        
                                        📧 Envie essas credenciais para o cliente!
                                        """)
                                    else:
                                        st.success(f"✅ Tracking adicionado!")
                                        st.warning(f"⚠️ Usuário '{usuario_auto}' já existe")
                                else:
                                    st.success(f"✅ Tracking adicionado!")
                                    st.info(f"ℹ️ Cliente '{novo_cliente}' já possui usuário")
                            else:
                                st.success("✅ Tracking adicionado com sucesso!")
                            
                            st.rerun()
        
        # Edição de registros (só admin)
        if usuario_info["tipo"] == "admin":
            with st.expander("✏️ Editar/Excluir Tracking"):
                if not df_filtrado.empty:
                    opcoes_edicao = [f"{row['CLIENTE']} - {row['CONTAINER']}" for _, row in df_filtrado.iterrows()]
                    registro_selecionado = st.selectbox("Selecione o registro para editar:", opcoes_edicao)
                    
                    if registro_selecionado:
                        # Encontrar o índice do registro selecionado
                        idx_selecionado = df_filtrado.index[df_filtrado.apply(lambda x: f"{x['CLIENTE']} - {x['CONTAINER']}" == registro_selecionado, axis=1)].tolist()[0]
                        registro = st.session_state.df_tracking.loc[idx_selecionado]
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Editando:** {registro['CLIENTE']} - {registro['CONTAINER']}")
                        
                        with col2:
                            if st.button("🗑️ Excluir Registro", type="secondary"):
                                st.session_state.df_tracking = st.session_state.df_tracking.drop(idx_selecionado).reset_index(drop=True)
                                st.success("🗑️ Registro excluído!")
                                st.rerun()
                        
                        # Formulário de edição
                        with st.form("editar_tracking"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                edit_cliente = st.text_input("Cliente", value=registro['CLIENTE'])
                                edit_container = st.text_input("Container", value=registro['CONTAINER'])
                                edit_carregamento = st.text_input("Carregamento", value=registro['CARREGAMENTO'])
                                edit_embarque = st.text_input("Embarque Navio", value=registro['EMBARQUE NAVIO'])
                                edit_saida = st.text_input("Saída Navio", value=registro['SAIDA NAVIO'])
                                edit_previsao = st.text_input("Previsão Chegada Paranaguá", value=registro['PREVISAO CHEGADA PARANAGUA'])
                            
                            with col2:
                                edit_chegada = st.text_input("Chegada Paranaguá", value=registro['CHEGADA PARANAGUA'])
                                edit_canal = st.selectbox("Canal RFB", ['', 'VERDE', 'VERMELHO'], 
                                                        index=['', 'VERDE', 'VERMELHO'].index(registro['CANAL RFB']) if registro['CANAL RFB'] in ['', 'VERDE', 'VERMELHO'] else 0)
                                edit_liberacao = st.text_input("Liberação Paranaguá", value=registro['LIBERAÇAO PARANAGUA'])
                                edit_chegada_py = st.text_input("Chegada Ciudad del Este PY", value=registro['CHEGADA CIUDAD DEL ESTE PY'])
                                edit_descarregamento = st.text_input("Descarregamento", value=registro['DESCARREGAMENTO'])
                            
                            submitted_edit = st.form_submit_button("💾 Salvar Alterações", type="primary")
                            
                            if submitted_edit:
                                if not edit_cliente or not edit_container:
                                    st.error("❌ Cliente e Container são obrigatórios!")
                                else:
                                    # Atualizar o registro
                                    st.session_state.df_tracking.loc[idx_selecionado] = [
                                        edit_cliente, edit_container, edit_carregamento, edit_embarque,
                                        edit_saida, edit_previsao, edit_chegada, edit_canal,
                                        edit_liberacao, edit_chegada_py, edit_descarregamento
                                    ]
                                    st.success("✅ Registro atualizado com sucesso!")
                                    st.rerun()
    else:
        st.info("🔍 Nenhum registro encontrado com os filtros aplicados.")
    
    # Alertas específicos
    if not df_usuario.empty:
        containers_vermelho = df_usuario[df_usuario['CANAL RFB'] == 'VERMELHO']
        
        if not containers_vermelho.empty:
            if usuario_info["tipo"] == "admin":
                st.warning(f"⚠️ **Atenção:** {len(containers_vermelho)} container(s) no Canal Vermelho precisam de acompanhamento!")
            else:
                st.warning(f"⚠️ **Atenção:** Você tem {len(containers_vermelho)} container(s) no Canal Vermelho que precisam de acompanhamento!")
            
            with st.expander("Ver Containers no Canal Vermelho"):
                for _, row in containers_vermelho.iterrows():
                    if usuario_info["tipo"] == "admin":
                        st.write(f"🔴 **{row['CLIENTE']}** - Container: {row['CONTAINER']} - Previsão: {row['PREVISAO CHEGADA PARANAGUA']}")
                    else:
                        st.write(f"🔴 **Container:** {row['CONTAINER']} - **Previsão:** {row['PREVISAO CHEGADA PARANAGUA']}")

def main():
    """Função principal da aplicação"""
    inicializar_sessao()
    
    if not st.session_state.logado:
        tela_login()
    else:
        dashboard_principal()

if __name__ == "__main__":
    main()
