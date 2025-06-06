#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Tracking BRIX - Versão Universal
Funciona perfeitamente em computador e celular
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
import os

# Configuração da página - UNIVERSAL
st.set_page_config(
    page_title="🚢 BRIX Tracking",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="auto"  # Adaptativo
)

# CSS responsivo universal
st.markdown("""
<style>
    /* Design responsivo universal */
    .main-header {
        background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
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
    
    .cliente-badge, .admin-badge {
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    .cliente-badge {
        background: #27ae60;
    }
    
    .admin-badge {
        background: #e74c3c;
    }
    
    .card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    
    .cliente-card {
        border-left-color: #27ae60 !important;
    }
    
    .usuario-card {
        border-left-color: #e74c3c !important;
    }
    
    /* Responsividade para mobile */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        
        .main-header h1 {
            font-size: 1.5rem !important;
        }
        
        .main-header h3 {
            font-size: 1.1rem !important;
        }
        
        .main-header p {
            font-size: 0.9rem !important;
        }
        
        .login-container {
            padding: 1.5rem;
            margin: 0 1rem;
        }
        
        .stButton > button {
            width: 100%;
            padding: 0.75rem;
            font-size: 0.9rem;
        }
        
        .card {
            padding: 0.75rem;
            margin: 0.5rem 0;
        }
        
        .card h4 {
            font-size: 1rem !important;
        }
        
        .card p {
            font-size: 0.85rem !important;
            margin: 0.25rem 0 !important;
        }
    }
    
    /* Melhorias gerais */
    .stSelectbox > div > div {
        background-color: white;
    }
    
    .stTextInput > div > div > input {
        background-color: white;
    }
    
    /* Botões responsivos */
    .stButton > button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
    }
    
    /* Tabela responsiva */
    .dataframe {
        font-size: 0.85rem;
    }
    
    @media (max-width: 768px) {
        .dataframe {
            font-size: 0.75rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Dados da empresa
DADOS_EMPRESA = {
    'nome': 'BRIX LOGÍSTICA',
    'endereco': 'Rua das Flores, 123 - Centro',
    'cidade': 'Curitiba - PR',
    'telefone': '(41) 3333-4444',
    'email': 'contato@brixlogistica.com.br',
    'cnpj': '12.345.678/0001-90'
}

# Colunas do sistema
COLUNAS = [
    'CLIENTE', 'CONTAINER', 'CARREGAMENTO', 'EMBARQUE NAVIO',
    'SAIDA NAVIO', 'PREVISAO CHEGADA PARANAGUA', 'CHEGADA PARANAGUA',
    'CANAL RFB', 'LIBERAÇAO PARANAGUA', 'CHEGADA CIUDAD DEL ESTE PY',
    'DESCARREGAMENTO'
]

def inicializar_dados():
    """Inicializa dados com chaves únicas para evitar conflitos"""
    
    # Força limpeza de cache se necessário
    if 'sistema_inicializado' not in st.session_state:
        st.session_state.clear()
        st.session_state.sistema_inicializado = True
    
    # Clientes padrão
    if 'clientes_db' not in st.session_state:
        st.session_state.clientes_db = {
            "EMPRESA ABC LTDA": {
                "razao_social": "EMPRESA ABC LTDA",
                "nome_fantasia": "ABC Importadora",
                "cnpj": "12.345.678/0001-01",
                "email": "contato@empresaabc.com.br",
                "telefone": "(11) 1111-1111",
                "endereco": "Rua A, 123 - São Paulo/SP",
                "contato": "João Silva",
                "ativo": True,
                "data_cadastro": "01/06/2025"
            },
            "COMERCIAL XYZ S.A.": {
                "razao_social": "COMERCIAL XYZ S.A.",
                "nome_fantasia": "XYZ Trading",
                "cnpj": "98.765.432/0001-02",
                "email": "gerencia@comercialxyz.com.br",
                "telefone": "(21) 2222-2222",
                "endereco": "Av. B, 456 - Rio de Janeiro/RJ",
                "contato": "Maria Santos",
                "ativo": True,
                "data_cadastro": "01/06/2025"
            }
        }
    
    # Usuários padrão
    if 'usuarios_db' not in st.session_state:
        st.session_state.usuarios_db = {
            "admin": {
                "senha": "admin123",
                "tipo": "admin",
                "cliente_vinculado": None,
                "nome": "Administrador BRIX",
                "email": "admin@brixlogistica.com.br",
                "ativo": True,
                "data_criacao": "01/06/2025"
            },
            "empresaabc": {
                "senha": "abc123",
                "tipo": "cliente",
                "cliente_vinculado": "EMPRESA ABC LTDA",
                "nome": "Empresa ABC",
                "email": "contato@empresaabc.com.br",
                "ativo": True,
                "data_criacao": "01/06/2025"
            },
            "comercialxyz": {
                "senha": "xyz123",
                "tipo": "cliente", 
                "cliente_vinculado": "COMERCIAL XYZ S.A.",
                "nome": "Comercial XYZ",
                "email": "gerencia@comercialxyz.com.br",
                "ativo": True,
                "data_criacao": "01/06/2025"
            }
        }
    
    # Trackings
    if 'df_tracking' not in st.session_state:
        st.session_state.df_tracking = pd.DataFrame(columns=COLUNAS)
    
    # Variáveis de sessão
    if 'logado' not in st.session_state:
        st.session_state.logado = False
    if 'usuario_info' not in st.session_state:
        st.session_state.usuario_info = None
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = "dashboard"

def detectar_dispositivo():
    """Detecta se é mobile ou desktop"""
    # JavaScript para detectar largura da tela
    js_code = """
    <script>
    function getScreenWidth() {
        return window.innerWidth;
    }
    </script>
    """
    
    # Por enquanto, vamos assumir que telas < 768px são mobile
    # Em produção, você pode usar JavaScript para detectar
    return "mobile"  # Para fins de demonstração

def criar_dados_exemplo():
    """Cria dados de exemplo"""
    dados_tracking = [
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
    
    df = pd.DataFrame(dados_tracking)
    st.session_state.df_tracking = df
    return df

def verificar_login(usuario, senha):
    """Verifica credenciais - normaliza entrada"""
    # Normalizar entrada (remove espaços, converte para minúscula)
    usuario_limpo = usuario.strip().lower()
    senha_limpa = senha.strip()
    
    # Verificar em todos os usuários
    for user_id, user_data in st.session_state.usuarios_db.items():
        if user_id.lower() == usuario_limpo:
            if user_data["senha"] == senha_limpa and user_data["ativo"]:
                return user_data
    
    return None

def filtrar_dados_por_cliente(df, usuario_info):
    """Filtra dados baseado no tipo de usuário"""
    if usuario_info["tipo"] == "admin":
        return df
    else:
        return df[df['CLIENTE'] == usuario_info["cliente_vinculado"]]

def colorir_linha(row):
    """Aplica cores baseado no canal RFB"""
    if row['CANAL RFB'] == 'VERDE':
        return ['background-color: #d5f4e6'] * len(row)
    elif row['CANAL RFB'] == 'VERMELHO':
        return ['background-color: #fadbd8'] * len(row)
    else:
        return [''] * len(row)

def gerar_usuario_automatico(razao_social):
    """Gera usuário automático"""
    import unicodedata
    nome_limpo = unicodedata.normalize('NFD', razao_social)
    nome_limpo = ''.join(char for char in nome_limpo if unicodedata.category(char) != 'Mn')
    nome_limpo = nome_limpo.replace(' ', '').replace('.', '').replace(',', '').lower()
    
    palavras = [p for p in nome_limpo.split() if len(p) > 2 and p not in ['ltda', 'sa', 'epp', 'me']]
    usuario = ''.join(palavras[:2]) if len(palavras) >= 2 else palavras[0] if palavras else nome_limpo
    
    return usuario[:15]

def gerar_senha_temporaria():
    """Gera senha temporária"""
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def cabecalho_responsivo():
    """Cria cabeçalho que se adapta ao dispositivo"""
    # Detectar se é mobile (simplificado)
    # Em produção, use JavaScript real para detectar
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🚢 {DADOS_EMPRESA['nome']}</h1>
        <h3>Sistema de Tracking</h3>
        <p>📍 {DADOS_EMPRESA['cidade']} | 📞 {DADOS_EMPRESA['telefone']}</p>
    </div>
    """, unsafe_allow_html=True)

def tela_login():
    """Tela de login universal"""
    cabecalho_responsivo()
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown("### 🔐 Acesso ao Sistema")
    
    # Informações do dispositivo
    st.info("💡 Este sistema funciona em qualquer dispositivo - computador, tablet ou celular!")
    
    with st.form("login_form", clear_on_submit=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            usuario = st.text_input(
                "👤 Usuário:", 
                placeholder="Digite seu usuário...",
                help="Não diferencia maiúsculas/minúsculas"
            )
            senha = st.text_input(
                "🔑 Senha:", 
                type="password", 
                placeholder="Digite sua senha...",
                help="Sua senha pessoal"
            )
        
        # Botão de login responsivo
        submitted = st.form_submit_button("🚀 Entrar", type="primary", use_container_width=True)
        
        if submitted:
            if usuario and senha:
                user_info = verificar_login(usuario, senha)
                if user_info:
                    st.session_state.logado = True
                    st.session_state.usuario_info = user_info
                    st.success(f"✅ Bem-vindo(a), {user_info['nome']}!")
                    
                    # Forçar refresh para mobile
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos!")
                    st.warning("🔍 Verifique se digitou corretamente. O sistema não diferencia maiúsculas/minúsculas.")
            else:
                st.warning("⚠️ Preencha todos os campos!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Seção de suporte
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📞 Suporte Técnico")
        st.markdown(f"""
        **Telefone:** {DADOS_EMPRESA['telefone']}  
        **Email:** {DADOS_EMPRESA['email']}  
        **Horário:** Segunda a Sexta, 8h às 18h
        """)
    
    with col2:
        st.markdown("### 💡 Ajuda")
        st.markdown("""
        **Esqueceu a senha?**  
        Entre em contato com o suporte
        
        **Primeiro acesso?**  
        Suas credenciais foram enviadas por email
        """)
    
    # Contas de teste apenas para desenvolvimento
    if st.checkbox("🧪 Mostrar contas de teste", help="Apenas para desenvolvimento"):
        st.markdown("### 🧪 Contas de Teste")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.code("Usuário: admin\nSenha: admin123")
            st.caption("👑 Administrador - Acesso total")
        
        with col2:
            st.code("Usuário: empresaabc\nSenha: abc123")
            st.caption("👤 Cliente - Acesso restrito")

def menu_superior_responsivo(usuario_info):
    """Menu superior que se adapta ao dispositivo"""
    # Para mobile, menu mais compacto
    if usuario_info["tipo"] == "admin":
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            if usuario_info["tipo"] == "admin":
                st.markdown(f'<div class="admin-badge">👑 {usuario_info["nome"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="cliente-badge">👤 {usuario_info["nome"]}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("🏢", help="Clientes"):
                st.session_state.pagina_atual = "clientes"
                st.rerun()
        
        with col3:
            if st.button("👥", help="Usuários"):
                st.session_state.pagina_atual = "usuarios"
                st.rerun()
        
        with col4:
            if st.button("📊", help="Dashboard"):
                st.session_state.pagina_atual = "dashboard"
                st.rerun()
        
        with col5:
            if st.button("🚪", help="Sair"):
                st.session_state.logado = False
                st.session_state.usuario_info = None
                st.session_state.pagina_atual = "dashboard"
                st.rerun()
    else:
        # Menu para cliente
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f'<div class="cliente-badge">👤 {usuario_info["nome"]}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("🚪 Sair"):
                st.session_state.logado = False
                st.session_state.usuario_info = None
                st.rerun()

def dashboard_responsivo():
    """Dashboard que se adapta ao dispositivo"""
    usuario_info = st.session_state.usuario_info
    
    cabecalho_responsivo()
    
    # Menu superior
    menu_superior_responsivo(usuario_info)
    
    # Verificar página atual para admin
    if st.session_state.pagina_atual == "clientes" and usuario_info["tipo"] == "admin":
        pagina_clientes_mobile()
        return
    elif st.session_state.pagina_atual == "usuarios" and usuario_info["tipo"] == "admin":
        pagina_usuarios_mobile()
        return
    
    # Sidebar responsivo
    with st.sidebar:
        st.header("🔧 Controles")
        
        if usuario_info["tipo"] == "admin":
            if st.button("📋 Dados de Exemplo", type="primary", use_container_width=True):
                criar_dados_exemplo()
                st.success("✅ Dados carregados!")
                st.rerun()
        
        # Informações do usuário
        st.markdown("---")
        st.subheader("👤 Sua Conta")
        st.write(f"**Nome:** {usuario_info['nome']}")
        st.write(f"**Tipo:** {usuario_info['tipo'].title()}")
        if usuario_info['tipo'] == 'cliente':
            st.write(f"**Cliente:** {usuario_info['cliente_vinculado']}")
    
    # Verificar dados
    if st.session_state.df_tracking.empty:
        if usuario_info["tipo"] == "admin":
            st.info("📋 Nenhum tracking cadastrado. Use 'Dados de Exemplo' na barra lateral.")
        else:
            st.info("📋 Nenhum tracking disponível no momento.")
        return
    
    # Filtrar dados
    df_usuario = filtrar_dados_por_cliente(st.session_state.df_tracking, usuario_info)
    
    if df_usuario.empty:
        st.info(f"📋 Nenhum tracking encontrado para {usuario_info['nome']}.")
        return
    
    # Métricas responsivas
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(df_usuario)
    verde = len(df_usuario[df_usuario['CANAL RFB'] == 'VERDE'])
    vermelho = len(df_usuario[df_usuario['CANAL RFB'] == 'VERMELHO'])
    pendentes = total - verde - vermelho
    
    with col1:
        st.metric("📦 Total", total)
    with col2:
        st.metric("🟢 Verde", verde)
    with col3:
        st.metric("🔴 Vermelho", vermelho)
    with col4:
        st.metric("⏳ Pendente", pendentes)
    
    # Filtros responsivos
    st.subheader("🔍 Filtros")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if usuario_info["tipo"] == "admin":
            filtro_cliente = st.text_input("Cliente", placeholder="Nome do cliente...")
        else:
            filtro_cliente = ""
    
    with col2:
        filtro_container = st.text_input("Container", placeholder="Número...")
    
    filtro_canal = st.selectbox("Canal RFB", ['Todos', 'VERDE', 'VERMELHO'])
    
    # Aplicar filtros
    df_filtrado = df_usuario.copy()
    
    if filtro_cliente and usuario_info["tipo"] == "admin":
        df_filtrado = df_filtrado[df_filtrado['CLIENTE'].str.contains(filtro_cliente, case=False, na=False)]
    
    if filtro_container:
        df_filtrado = df_filtrado[df_filtrado['CONTAINER'].str.contains(filtro_container, case=False, na=False)]
    
    if filtro_canal != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['CANAL RFB'] == filtro_canal]
    
    # Tabela responsiva
    st.subheader(f"📋 Trackings ({len(df_filtrado)} registros)")
    
    if not df_filtrado.empty:
        # Para mobile, mostrar dados mais compactos
        styled_df = df_filtrado.style.apply(colorir_linha, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Download
        csv = df_filtrado.to_csv(index=False)
        st.download_button(
            label="💾 Baixar Dados",
            data=csv,
            file_name=f"tracking_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("🔍 Nenhum registro encontrado.")

def pagina_clientes_mobile():
    """Página de clientes otimizada"""
    st.header("🏢 Clientes")
    
    # Botão voltar
    if st.button("⬅️ Voltar ao Dashboard"):
        st.session_state.pagina_atual = "dashboard"
        st.rerun()
    
    # Lista simplificada para mobile
    st.subheader("📋 Lista de Clientes")
    
    for razao_social, dados in st.session_state.clientes_db.items():
        with st.expander(f"🏢 {dados['nome_fantasia']}", expanded=False):
            st.write(f"**Razão Social:** {dados['razao_social']}")
            st.write(f"**Email:** {dados['email']}")
            st.write(f"**Telefone:** {dados['telefone']}")
            st.write(f"**Status:** {'✅ Ativo' if dados['ativo'] else '❌ Inativo'}")

def pagina_usuarios_mobile():
    """Página de usuários otimizada"""
    st.header("👥 Usuários")
    
    # Botão voltar
    if st.button("⬅️ Voltar ao Dashboard"):
        st.session_state.pagina_atual = "dashboard"
        st.rerun()
    
    # Lista simplificada
    st.subheader("📋 Lista de Usuários")
    
    for usuario_id, dados in st.session_state.usuarios_db.items():
        tipo_emoji = "👑" if dados["tipo"] == "admin" else "👤"
        status_emoji = "✅" if dados["ativo"] else "❌"
        
        with st.expander(f"{tipo_emoji} {dados['nome']} {status_emoji}", expanded=False):
            st.write(f"**Usuário:** {usuario_id}")
            st.write(f"**Email:** {dados['email']}")
            st.write(f"**Tipo:** {dados['tipo'].title()}")
            if dados['cliente_vinculado']:
                st.write(f"**Cliente:** {dados['cliente_vinculado']}")

def main():
    """Função principal universal"""
    inicializar_dados()
    
    if not st.session_state.logado:
        tela_login()
    else:
        dashboard_responsivo()

if __name__ == "__main__":
    main()
