#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Tracking BRIX - Versão com Persistência REAL Corrigida
SOLUÇÃO: Dados persistem durante a sessão + Sistema de Backup Manual
Escritório de contabilidade - Brasil
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import base64

# Configuração da página
st.set_page_config(
    page_title="🚢 Sistema BRIX - Tracking Marítimo e Rodoviário",
    page_icon="🚢", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado + melhorias mobile
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
    .backup-container {
        background: #f8f9fa;
        border: 2px dashed #6c757d;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* FIX CRÍTICO: Tabela com texto preto SEMPRE */
    .stDataFrame, .stDataFrame * {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    .stDataFrame table, .stDataFrame table * {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    .stDataFrame td, .stDataFrame th, .stDataFrame tr {
        color: #000000 !important;
        background-color: #ffffff !important;
        border-color: #cccccc !important;
    }
    
    /* Forçar texto preto mesmo com cores de fundo */
    .stDataFrame td[style*="background-color"] {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* Fix específico para mobile */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem 1rem;
        }
        .main-header h1 {
            font-size: 1.5rem !important;
        }
        .login-container {
            margin: 0 1rem;
            padding: 1.5rem;
        }
        .stButton > button {
            width: 100%;
            padding: 0.75rem;
        }
        .stTextInput > div > div > input {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        .stSelectbox > div > div > div {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        
        /* FIX MOBILE: Tabela com texto preto forçado */
        .stDataFrame, .stDataFrame *, .stDataFrame table, .stDataFrame table * {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        
        .stDataFrame td, .stDataFrame th {
            color: #000000 !important;
            background-color: #ffffff !important;
            font-size: 14px !important;
        }
    }
    
    /* FIX GERAL: Garantir que inputs sejam visíveis */
    .stTextInput > div > div > input {
        color: #333333 !important;
        background-color: white !important;
        border: 1px solid #cccccc !important;
    }
    
    .stSelectbox > div > div {
        background-color: white !important;
        color: #333333 !important;
    }
    
    /* FIX EXTRA: Sobrescrever qualquer CSS do Streamlit */
    div[data-testid="stDataFrame"] {
        color: #000000 !important;
    }
    
    div[data-testid="stDataFrame"] table {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    div[data-testid="stDataFrame"] td {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    div[data-testid="stDataFrame"] th {
        color: #000000 !important;
        background-color: #f8f9fa !important;
    }
</style>
""", unsafe_allow_html=True)
# Dados da empresa
DADOS_EMPRESA = {
    'nome': 'BRIX LOGÍSTICA',
    'endereco': 'Av Ranieri Mazzilli, nº 755, Centro Civíco',
    'cidade': 'Foz do Iguaçu - PR',
    'telefone': '(45) 99115 0734',
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

def inicializar_sistema():
    """Inicializa o sistema com dados padrão se necessário"""
    
    # Inicializar dados básicos se não existirem
    if 'sistema_inicializado' not in st.session_state:
        
        # DADOS PADRÃO PARA CLIENTES
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
        
        # DADOS PADRÃO PARA USUÁRIOS
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
            "empresa_abc": {
                "senha": "abc123",
                "tipo": "cliente",
                "cliente_vinculado": "EMPRESA ABC LTDA",
                "nome": "Empresa ABC",
                "email": "contato@empresaabc.com.br",
                "ativo": True,
                "data_criacao": "01/06/2025"
            },
            "comercial_xyz": {
                "senha": "xyz123",
                "tipo": "cliente",
                "cliente_vinculado": "COMERCIAL XYZ S.A.",
                "nome": "Comercial XYZ",
                "email": "gerencia@comercialxyz.com.br", 
                "ativo": True,
                "data_criacao": "01/06/2025"
            }
        }
        
        # DADOS PADRÃO PARA TRACKINGS
        st.session_state.df_tracking = pd.DataFrame([
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
                'CLIENTE': 'EMPRESA ABC LTDA',
                'CONTAINER': 'ABCU7777777',
                'CARREGAMENTO': '22/05/2025',
                'EMBARQUE NAVIO': '25/05/2025',
                'SAIDA NAVIO': '27/05/2025',
                'PREVISAO CHEGADA PARANAGUA': '02/06/2025',
                'CHEGADA PARANAGUA': '',
                'CANAL RFB': '',
                'LIBERAÇAO PARANAGUA': '',
                'CHEGADA CIUDAD DEL ESTE PY': '',
                'DESCARREGAMENTO': ''
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
        ])
        
        # Outras variáveis de controle
        st.session_state.logado = False
        st.session_state.usuario_info = None
        st.session_state.pagina_atual = "dashboard"
        st.session_state.sistema_inicializado = True
        
        # Marcar que dados foram inicializados
        st.session_state.dados_inicializados = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def criar_backup_manual():
    """Cria backup manual dos dados para download"""
    backup_data = {
        'clientes': st.session_state.clientes_db,
        'usuarios': st.session_state.usuarios_db,
        'trackings': st.session_state.df_tracking.to_dict('records'),
        'metadata': {
            'data_backup': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'versao': '2.0',
            'total_clientes': len(st.session_state.clientes_db),
            'total_usuarios': len(st.session_state.usuarios_db),
            'total_trackings': len(st.session_state.df_tracking)
        }
    }
    
    json_backup = json.dumps(backup_data, ensure_ascii=False, indent=2)
    return json_backup

def restaurar_backup_manual(json_data):
    """Restaura dados a partir de backup manual"""
    try:
        backup_data = json.loads(json_data)
        
        # Validar estrutura do backup
        if not all(key in backup_data for key in ['clientes', 'usuarios', 'trackings']):
            return False, "❌ Arquivo de backup inválido!"
        
        # Restaurar dados
        st.session_state.clientes_db = backup_data['clientes']
        st.session_state.usuarios_db = backup_data['usuarios']
        st.session_state.df_tracking = pd.DataFrame(backup_data['trackings'])
        
        # Atualizar metadata
        st.session_state.dados_restaurados = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        return True, "✅ Backup restaurado com sucesso!"
        
    except Exception as e:
        return False, f"❌ Erro ao restaurar backup: {str(e)}"

def verificar_login(usuario, senha):
    """Verifica credenciais do usuário"""
    usuario_normalizado = usuario.strip().lower()
    senha_normalizada = senha.strip()
    
    for user_id, user_data in st.session_state.usuarios_db.items():
        if user_id.lower() == usuario_normalizado:
            if user_data["senha"] == senha_normalizada and user_data["ativo"]:
                return user_data
    
    return None

def filtrar_dados_por_cliente(df, usuario_info):
    """Filtra dados baseado no tipo de usuário"""
    if usuario_info["tipo"] == "admin":
        return df
    else:
        return df[df['CLIENTE'] == usuario_info["cliente_vinculado"]]

def colorir_linha(row):
    """Aplica cores baseado no canal RFB com texto preto forçado"""
    if row['CANAL RFB'] == 'VERDE':
        return ['background-color: #d5f4e6; color: #000000 !important; font-weight: bold;'] * len(row)
    elif row['CANAL RFB'] == 'VERMELHO':
        return ['background-color: #fadbd8; color: #000000 !important; font-weight: bold;'] * len(row)
    else:
        return ['color: #000000 !important;'] * len(row)

def gerar_usuario_automatico(razao_social):
    """Gera usuário automático baseado na razão social"""
    import unicodedata
    nome_limpo = unicodedata.normalize('NFD', razao_social)
    nome_limpo = ''.join(char for char in nome_limpo if unicodedata.category(char) != 'Mn')
    nome_limpo = nome_limpo.replace(' ', '_').replace('.', '').replace(',', '').lower()
    
    palavras = [p for p in nome_limpo.split('_') if len(p) > 2 and p not in ['ltda', 'sa', 'epp', 'me']]
    usuario = '_'.join(palavras[:2]) if len(palavras) >= 2 else palavras[0] if palavras else nome_limpo
    
    return usuario[:20]

def gerar_senha_temporaria():
    """Gera senha temporária"""
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def sidebar_backup_system():
    """Sistema de backup na sidebar - MOBILE FRIENDLY"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("💾 Dados Atuais")
        
        # Estatísticas
        st.write(f"🏢 Clientes: {len(st.session_state.clientes_db)}")
        st.write(f"👥 Usuários: {len(st.session_state.usuarios_db)}")
        st.write(f"📦 Trackings: {len(st.session_state.df_tracking)}")
        
        # Sistema automático com Dropbox (APENAS ADMIN)
        sistema_backup_automatico()
        
        # Backup manual simplificado (APENAS ADMIN)
        if st.session_state.usuario_info and st.session_state.usuario_info.get("tipo") == "admin":
            st.markdown("---")
            st.subheader("📱 Backup Manual")
            
            # Download sempre disponível
            if st.button("📤 Gerar Backup", help="Cria arquivo para download"):
                backup_json = criar_backup_manual()
                nome_arquivo = f"backup_brix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                st.download_button(
                    label="⬇️ Baixar JSON",
                    data=backup_json,
                    file_name=nome_arquivo,
                    mime="application/json",
                    key="download_backup"
                )
                st.success("✅ Backup criado!")
            
            # Restaurar por texto (alternativa mobile)
            with st.expander("📥 Restaurar por Texto"):
                st.info("💡 **Para mobile:** Cole o conteúdo do arquivo JSON aqui")
                
                json_text = st.text_area(
                    "Cole o JSON do backup:",
                    height=100,
                    placeholder='{"clientes": {...}, "usuarios": {...}, "trackings": [...]}'
                )
                
                if st.button("🔄 Restaurar Dados", type="secondary"):
                    if json_text.strip():
                        try:
                            backup_data = json.loads(json_text)
                            
                            # Validar estrutura
                            if not all(key in backup_data for key in ['clientes', 'usuarios', 'trackings']):
                                st.error("❌ JSON inválido! Verifique a estrutura.")
                            else:
                                # Restaurar dados
                                st.session_state.clientes_db = backup_data['clientes']
                                st.session_state.usuarios_db = backup_data['usuarios']
                                st.session_state.df_tracking = pd.DataFrame(backup_data['trackings'])
                                st.session_state.dados_restaurados = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                
                                st.success("✅ Dados restaurados com sucesso!")
                                st.rerun()
                                
                        except json.JSONDecodeError:
                            st.error("❌ JSON inválido! Verifique a formatação.")
                        except Exception as e:
                            st.error(f"❌ Erro: {str(e)}")
                    else:
                        st.warning("⚠️ Cole o conteúdo JSON primeiro!")
            
            # Status da última operação
            if 'dados_restaurados' in st.session_state:
                st.success(f"🕐 Última operação: {st.session_state.dados_restaurados}")
            
def sistema_backup_automatico():
    """Sistema de backup automático com Dropbox integrado - APENAS PARA ADMIN"""
    
    # Verificar se é admin
    if not st.session_state.usuario_info or st.session_state.usuario_info.get("tipo") != "admin":
        return  # Não mostra nada para clientes
    
    with st.sidebar:
        st.markdown("---")
        st.subheader("☁️ Sincronização Dropbox")
        
        # URL pré-configurada do seu Dropbox
        DROPBOX_URL = "https://www.dropbox.com/scl/fi/jiugv7kax7gmatyk19oto/backup_brix.json?rlkey=wvwru4wrnl10lsjib8c7d0zyl&dl=1"
        
        # Botões de sincronização
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Sincronizar", type="primary", help="Baixa dados do Dropbox"):
                try:
                    with st.spinner("🔄 Sincronizando..."):
                        import requests
                        response = requests.get(DROPBOX_URL, timeout=10)
                        
                        if response.status_code == 200:
                            backup_data = response.json()
                            
                            # Restaurar dados
                            st.session_state.clientes_db = backup_data['clientes']
                            st.session_state.usuarios_db = backup_data['usuarios']
                            st.session_state.df_tracking = pd.DataFrame(backup_data['trackings'])
                            st.session_state.dados_restaurados = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            
                            st.success("✅ Dados sincronizados do Dropbox!")
                            st.rerun()
                        else:
                            st.error(f"❌ Erro HTTP: {response.status_code}")
                            
                except requests.exceptions.RequestException as e:
                    st.error("❌ Erro de conexão. Verifique sua internet.")
                except json.JSONDecodeError:
                    st.error("❌ Arquivo JSON inválido no Dropbox.")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        with col2:
            if st.button("📤 Backup", help="Cria backup para atualizar Dropbox"):
                backup_json = criar_backup_manual()
                nome_arquivo = "backup_brix.json"
                
                st.download_button(
                    label="⬇️ Baixar",
                    data=backup_json,
                    file_name=nome_arquivo,
                    mime="application/json",
                    help="Substitua o arquivo no Dropbox"
                )
                st.info("💡 Substitua o arquivo 'backup_brix.json' na sua pasta do Dropbox")
        
        # Status da última sincronização
        if 'dados_restaurados' in st.session_state:
            st.success(f"🕐 Última sync: {st.session_state.dados_restaurados}")
        
        # Instruções simplificadas
        with st.expander("📋 Como funciona"):
            st.markdown("""
            **🔄 Para sincronizar dados:**
            1. **📥 Sincronizar** - baixa dados do Dropbox
            2. **📤 Backup** - cria arquivo para subir no Dropbox
            
            **📂 Localização do arquivo:**
            `C:\\Users\\FABIO MADALOZZO\\Dropbox\\tracking-brix\\backup_brix.json`
            
            **💡 Dica:** Sempre sincronize ao abrir o sistema!
            """)
        
        # Informações do arquivo atual
        st.markdown("### 📄 Dados no Dropbox:")
        st.write("🏢 Clientes: 3 (ABC, XYZ, MC)")
        st.write("👥 Usuários: 4 (admin, abc, xyz, aristide)")
        st.write("📦 Trackings: 4")
        st.write("📅 Última atualização: 06/06/2025")
        
def tela_login():
    """Tela de login - CORRIGIDA para mobile"""
    st.markdown("""
    <div class="main-header">
        <h1>🚢 BRIX LOGÍSTICA</h1>
        <h3>Sistema de Tracking de Trânsito</h3>
        <p>Acesso Seguro - Login Necessário</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Alert sobre persistência
    st.info("""
    ℹ️ **Importante sobre os dados:**
    - Os dados ficam salvos **durante sua sessão**
    - Para backup permanente, use o **Sistema de Backup** após fazer login
    - Sempre faça backup antes de fechar o navegador!
    """)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown("### 🔐 Fazer Login")
    
    # Usar columns ao invés de form para melhor compatibilidade mobile
    col1, col2 = st.columns([1, 1])
    
    with col1:
        usuario = st.text_input(
            "👤 Usuário:", 
            placeholder="Digite seu usuário...",
            key="mobile_login_user"
        )
    
    with col2:
        senha = st.text_input(
            "🔑 Senha:", 
            type="password", 
            placeholder="Digite sua senha...",
            key="mobile_login_pass"
        )
    
    # Botão de login
    if st.button("🚀 Entrar", type="primary", use_container_width=True):
        if usuario and senha:
            usuario_limpo = str(usuario).strip().lower()
            senha_limpa = str(senha).strip()
            
            user_encontrado = None
            for user_id, user_data in st.session_state.usuarios_db.items():
                if str(user_id).lower() == usuario_limpo:
                    if str(user_data["senha"]) == senha_limpa and user_data["ativo"]:
                        user_encontrado = user_data
                        break
            
            if user_encontrado:
                st.session_state.logado = True
                st.session_state.usuario_info = user_encontrado
                st.success(f"✅ Bem-vindo, {user_encontrado['nome']}!")
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos!")
        else:
            st.warning("⚠️ Preencha todos os campos!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Informações de suporte
    st.markdown("---")
    st.markdown("### 📞 Suporte & Contas de Teste")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📞 Contato:**
        - Tel: (45) 99115 0734
        - Email: fabio@brixcontabilidade.com.br
        - Horário: Seg-Sex 8h-18h
        """)
    
            
def pagina_clientes():
    """Página para gerenciar clientes"""
    st.header("🏢 Gerenciamento de Clientes")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Clientes", "➕ Novo Cliente", "📊 Estatísticas"])
    
    with tab1:
        st.subheader("🏢 Clientes Cadastrados")
        
        if not st.session_state.clientes_db:
            st.info("📋 Nenhum cliente cadastrado ainda.")
        else:
            for razao_social, dados in st.session_state.clientes_db.items():
                status_emoji = "✅" if dados["ativo"] else "❌"
                
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="card cliente-card">
                        <h4>🏢 {dados['nome_fantasia']} {status_emoji}</h4>
                        <p><strong>Razão Social:</strong> {dados['razao_social']}</p>
                        <p><strong>CNPJ:</strong> {dados['cnpj']}</p>
                        <p><strong>Email:</strong> {dados['email']}</p>
                        <p><strong>Telefone:</strong> {dados['telefone']}</p>
                        <p><strong>Contato:</strong> {dados['contato']}</p>
                        <p><strong>Cadastrado:</strong> {dados['data_cadastro']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"✏️ Editar", key=f"edit_cliente_{razao_social}"):
                        st.session_state.editando_cliente = razao_social
                        st.rerun()
                
                with col3:
                    status_btn = "🔓 Ativar" if not dados["ativo"] else "🔒 Desativar"
                    if st.button(status_btn, key=f"toggle_cliente_{razao_social}"):
                        st.session_state.clientes_db[razao_social]["ativo"] = not dados["ativo"]
                        st.success(f"✅ Cliente {razao_social} {'ativado' if not dados['ativo'] else 'desativado'}!")
                        st.rerun()
                
                with col4:
                    if st.button(f"🗑️ Excluir", key=f"del_cliente_{razao_social}"):
                        st.session_state.excluindo_cliente = razao_social
        
        # Modal de confirmação para exclusão
        if 'excluindo_cliente' in st.session_state:
            st.error(f"⚠️ Tem certeza que deseja excluir o cliente '{st.session_state.excluindo_cliente}'?")
            st.warning("🚨 Isso também excluirá todos os trackings e usuários vinculados!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Sim, excluir"):
                    razao_social = st.session_state.excluindo_cliente
                    
                    # Excluir cliente
                    del st.session_state.clientes_db[razao_social]
                    
                    # Excluir trackings do cliente
                    st.session_state.df_tracking = st.session_state.df_tracking[
                        st.session_state.df_tracking['CLIENTE'] != razao_social
                    ].reset_index(drop=True)
                    
                    # Excluir usuários vinculados
                    usuarios_para_excluir = [
                        user_id for user_id, user_data in st.session_state.usuarios_db.items()
                        if user_data.get('cliente_vinculado') == razao_social
                    ]
                    for user_id in usuarios_para_excluir:
                        del st.session_state.usuarios_db[user_id]
                    
                    del st.session_state.excluindo_cliente
                    st.success("🗑️ Cliente e dados relacionados excluídos!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancelar"):
                    del st.session_state.excluindo_cliente
                    st.rerun()
        
        # Formulário de edição
        if 'editando_cliente' in st.session_state:
            razao_social = st.session_state.editando_cliente
            dados = st.session_state.clientes_db[razao_social]
            
            st.markdown("---")
            st.subheader(f"✏️ Editando: {dados['nome_fantasia']}")
            
            with st.form("editar_cliente"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nova_razao = st.text_input("Razão Social:", value=dados['razao_social'])
                    novo_fantasia = st.text_input("Nome Fantasia:", value=dados['nome_fantasia'])
                    novo_cnpj = st.text_input("CNPJ:", value=dados['cnpj'])
                    novo_email = st.text_input("Email:", value=dados['email'])
                
                with col2:
                    novo_telefone = st.text_input("Telefone:", value=dados['telefone'])
                    novo_endereco = st.text_input("Endereço:", value=dados['endereco'])
                    novo_contato = st.text_input("Contato:", value=dados['contato'])
                    novo_ativo = st.checkbox("Ativo", value=dados['ativo'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                        # Se mudou a razão social, precisa atualizar referências
                        if nova_razao != razao_social:
                            # Atualizar trackings
                            st.session_state.df_tracking.loc[
                                st.session_state.df_tracking['CLIENTE'] == razao_social, 'CLIENTE'
                            ] = nova_razao
                            
                            # Atualizar usuários vinculados
                            for user_data in st.session_state.usuarios_db.values():
                                if user_data.get('cliente_vinculado') == razao_social:
                                    user_data['cliente_vinculado'] = nova_razao
                            
                            # Remover cliente antigo e adicionar novo
                            del st.session_state.clientes_db[razao_social]
                        
                        # Atualizar dados do cliente
                        st.session_state.clientes_db[nova_razao] = {
                            'razao_social': nova_razao,
                            'nome_fantasia': novo_fantasia,
                            'cnpj': novo_cnpj,
                            'email': novo_email,
                            'telefone': novo_telefone,
                            'endereco': novo_endereco,
                            'contato': novo_contato,
                            'ativo': novo_ativo,
                            'data_cadastro': dados['data_cadastro']
                        }
                        
                        del st.session_state.editando_cliente
                        st.success("✅ Cliente atualizado!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Cancelar"):
                        del st.session_state.editando_cliente
                        st.rerun()
    
    with tab2:
        st.subheader("➕ Cadastrar Novo Cliente")
        
        with st.form("novo_cliente"):
            col1, col2 = st.columns(2)
            
            with col1:
                razao_social = st.text_input("Razão Social *:", placeholder="ex: NOVA EMPRESA LTDA")
                nome_fantasia = st.text_input("Nome Fantasia *:", placeholder="ex: Nova Empresa")
                cnpj = st.text_input("CNPJ:", placeholder="ex: 12.345.678/0001-90")
                email = st.text_input("Email *:", placeholder="contato@novaempresa.com.br")
            
            with col2:
                telefone = st.text_input("Telefone:", placeholder="(11) 1234-5678")
                endereco = st.text_input("Endereço:", placeholder="Rua A, 123 - Cidade/UF")
                contato = st.text_input("Pessoa de Contato:", placeholder="João Silva")
                criar_usuario = st.checkbox("🤖 Criar usuário automaticamente")
            
            if st.form_submit_button("🏢 Cadastrar Cliente", type="primary"):
                # Validações
                erros = []
                if not razao_social:
                    erros.append("❌ Razão Social é obrigatória")
                if not nome_fantasia:
                    erros.append("❌ Nome Fantasia é obrigatório")
                if not email:
                    erros.append("❌ Email é obrigatório")
                if razao_social in st.session_state.clientes_db:
                    erros.append("❌ Cliente já cadastrado")
                
                if erros:
                    for erro in erros:
                        st.error(erro)
                else:
                    # Cadastrar cliente
                    st.session_state.clientes_db[razao_social] = {
                        'razao_social': razao_social,
                        'nome_fantasia': nome_fantasia,
                        'cnpj': cnpj,
                        'email': email,
                        'telefone': telefone,
                        'endereco': endereco,
                        'contato': contato,
                        'ativo': True,
                        'data_cadastro': datetime.now().strftime("%d/%m/%Y")
                    }
                    
                    mensagem_sucesso = f"✅ Cliente '{nome_fantasia}' cadastrado com sucesso!"
                    
                    # Criar usuário se solicitado
                    if criar_usuario:
                        usuario_auto = gerar_usuario_automatico(razao_social)
                        senha_auto = gerar_senha_temporaria()
                        
                        if usuario_auto not in st.session_state.usuarios_db:
                            st.session_state.usuarios_db[usuario_auto] = {
                                "senha": senha_auto,
                                "tipo": "cliente",
                                "cliente_vinculado": razao_social,
                                "nome": nome_fantasia,
                                "email": email,
                                "ativo": True,
                                "data_criacao": datetime.now().strftime("%d/%m/%Y")
                            }
                            
                            mensagem_sucesso += f"\n\n🤖 **Usuário criado automaticamente:**\n- **Usuário:** {usuario_auto}\n- **Senha:** {senha_auto}"
                    
                    st.success(mensagem_sucesso)
                    st.rerun()
    
    with tab3:
        st.subheader("📊 Estatísticas de Clientes")
        
        total_clientes = len(st.session_state.clientes_db)
        clientes_ativos = sum(1 for c in st.session_state.clientes_db.values() if c["ativo"])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏢 Total", total_clientes)
        with col2:
            st.metric("✅ Ativos", clientes_ativos)
        with col3:
            # Contar trackings por cliente
            if not st.session_state.df_tracking.empty:
                clientes_com_tracking = st.session_state.df_tracking['CLIENTE'].nunique()
                st.metric("📦 Com Trackings", clientes_com_tracking)
            else:
                st.metric("📦 Com Trackings", 0)
        with col4:
            # Contar usuários vinculados
            usuarios_vinculados = sum(1 for u in st.session_state.usuarios_db.values() if u.get("cliente_vinculado"))
            st.metric("👤 Com Usuários", usuarios_vinculados)

def pagina_usuarios():
    """Página para gerenciar usuários"""
    st.header("👥 Gerenciamento de Usuários")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Usuários", "➕ Novo Usuário", "📊 Estatísticas"])
    
    with tab1:
        st.subheader("👤 Usuários Cadastrados")
        
        for usuario_id, dados in st.session_state.usuarios_db.items():
            card_class = "usuario-card" if dados["tipo"] == "admin" else "card"
            status_emoji = "✅" if dados["ativo"] else "❌"
            tipo_emoji = "👑" if dados["tipo"] == "admin" else "👤"
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                cliente_info = f"<p><strong>Cliente:</strong> {dados['cliente_vinculado']}</p>" if dados['cliente_vinculado'] else ""
                st.markdown(f"""
                <div class="{card_class}">
                    <h4>{tipo_emoji} {dados['nome']} {status_emoji}</h4>
                    <p><strong>Usuário:</strong> {usuario_id}</p>
                    <p><strong>Email:</strong> {dados['email']}</p>
                    <p><strong>Tipo:</strong> {dados['tipo'].title()}</p>
                    {cliente_info}
                    <p><strong>Criado:</strong> {dados['data_criacao']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"✏️ Editar", key=f"edit_user_{usuario_id}"):
                    st.session_state.editando_usuario = usuario_id
                    st.rerun()
            
            with col3:
                status_btn = "🔓 Ativar" if not dados["ativo"] else "🔒 Desativar"
                if st.button(status_btn, key=f"toggle_user_{usuario_id}"):
                    st.session_state.usuarios_db[usuario_id]["ativo"] = not dados["ativo"]
                    st.success(f"✅ Usuário {usuario_id} {'ativado' if not dados['ativo'] else 'desativado'}!")
                    st.rerun()
            
            with col4:
                if usuario_id != "admin":
                    if st.button(f"🗑️ Excluir", key=f"del_user_{usuario_id}"):
                        st.session_state.excluindo_usuario = usuario_id
        
        # Modal de confirmação para exclusão
        if 'excluindo_usuario' in st.session_state:
            st.error(f"⚠️ Tem certeza que deseja excluir o usuário '{st.session_state.excluindo_usuario}'?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Sim, excluir"):
                    del st.session_state.usuarios_db[st.session_state.excluindo_usuario]
                    del st.session_state.excluindo_usuario
                    st.success("🗑️ Usuário excluído!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancelar"):
                    del st.session_state.excluindo_usuario
                    st.rerun()
        
        # Formulário de edição de usuário
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
                        clientes_disponiveis = [""] + list(st.session_state.clientes_db.keys())
                        cliente_atual_idx = clientes_disponiveis.index(dados['cliente_vinculado']) if dados['cliente_vinculado'] in clientes_disponiveis else 0
                        novo_cliente = st.selectbox("Cliente:", clientes_disponiveis, index=cliente_atual_idx)
                    else:
                        novo_cliente = None
                        st.info("👑 Usuário administrador - sem restrição de cliente")
                    
                    novo_ativo = st.checkbox("Ativo", value=dados['ativo'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                        st.session_state.usuarios_db[usuario_id].update({
                            'nome': novo_nome,
                            'email': novo_email,
                            'cliente_vinculado': novo_cliente,
                            'ativo': novo_ativo
                        })
                        
                        if nova_senha:
                            st.session_state.usuarios_db[usuario_id]['senha'] = nova_senha
                        
                        del st.session_state.editando_usuario
                        st.success("✅ Usuário atualizado!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Cancelar"):
                        del st.session_state.editando_usuario
                        st.rerun()
    
    with tab2:
        st.subheader("➕ Cadastrar Novo Usuário")
        
        with st.form("novo_usuario"):
            col1, col2 = st.columns(2)
            
            with col1:
                novo_usuario = st.text_input("Nome de Usuário *:", placeholder="ex: novo_usuario")
                novo_nome = st.text_input("Nome Completo *:", placeholder="ex: João Silva")
                novo_email = st.text_input("Email *:", placeholder="joao@empresa.com")
                nova_senha = st.text_input("Senha *:", type="password", placeholder="Senha temporária")
            
            with col2:
                tipo_usuario = st.selectbox("Tipo *:", ["cliente", "admin"])
                
                if tipo_usuario == "cliente":
                    clientes_disponiveis = list(st.session_state.clientes_db.keys())
                    if clientes_disponiveis:
                        cliente_vinculado = st.selectbox("Cliente *:", [""] + clientes_disponiveis)
                    else:
                        st.warning("⚠️ Cadastre clientes primeiro!")
                        cliente_vinculado = ""
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
                if not novo_email:
                    erros.append("❌ Email é obrigatório")
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
                        "cliente_vinculado": cliente_vinculado if tipo_usuario == "cliente" else None,
                        "nome": novo_nome,
                        "email": novo_email,
                        "ativo": True,
                        "data_criacao": datetime.now().strftime("%d/%m/%Y")
                    }
                    
                    st.success(f"✅ Usuário '{novo_usuario}' criado com sucesso!")
                    
                    # Mostrar dados de acesso
                    st.info(f"""
                    🔐 **Dados de Acesso Criados:**
                    - **Usuário:** {novo_usuario}
                    - **Senha:** {nova_senha}
                    - **Tipo:** {tipo_usuario.title()}
                    {f"- **Cliente:** {cliente_vinculado}" if cliente_vinculado else ""}
                    
                    📧 Envie essas informações para o usuário por email seguro!
                    """)
                    st.rerun()
    
    with tab3:
        st.subheader("📊 Estatísticas de Usuários")
        
        total_usuarios = len(st.session_state.usuarios_db)
        usuarios_ativos = sum(1 for u in st.session_state.usuarios_db.values() if u["ativo"])
        admins = sum(1 for u in st.session_state.usuarios_db.values() if u["tipo"] == "admin")
        clientes_usuarios = sum(1 for u in st.session_state.usuarios_db.values() if u["tipo"] == "cliente")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total", total_usuarios)
        with col2:
            st.metric("✅ Ativos", usuarios_ativos)
        with col3:
            st.metric("👑 Admins", admins)
        with col4:
            st.metric("👤 Clientes", clientes_usuarios)

def dashboard_principal():
    """Dashboard principal"""
    usuario_info = st.session_state.usuario_info
    
    # Cabeçalho
    st.markdown(f"""
    <div class="main-header">
        <h1>🚢 {DADOS_EMPRESA['nome']}</h1>
        <h3>Sistema de Tracking de Trânsito</h3>
        <p>📍 {DADOS_EMPRESA['endereco']} - {DADOS_EMPRESA['cidade']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Badge do usuário e menu
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
    
    with col1:
        if usuario_info["tipo"] == "admin":
            st.markdown(f'<div class="admin-badge">👑 Admin: {usuario_info["nome"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="cliente-badge">👤 Cliente: {usuario_info["nome"]}</div>', unsafe_allow_html=True)
    
    if usuario_info["tipo"] == "admin":
        with col2:
            if st.button("🏢 Clientes"):
                st.session_state.pagina_atual = "clientes"
                st.rerun()
        
        with col3:
            if st.button("👥 Usuários"):
                st.session_state.pagina_atual = "usuarios"
                st.rerun()
        
        with col4:
            if st.button("📊 Dashboard"):
                st.session_state.pagina_atual = "dashboard"
                st.rerun()
    
    with col5:
        if st.button("🚪 Logout"):
            st.session_state.logado = False
            st.session_state.usuario_info = None
            st.session_state.pagina_atual = "dashboard"
            st.rerun()
    
    # Verificar página atual
    if st.session_state.pagina_atual == "clientes" and usuario_info["tipo"] == "admin":
        pagina_clientes()
        return
    elif st.session_state.pagina_atual == "usuarios" and usuario_info["tipo"] == "admin":
        pagina_usuarios()
        return
    
    # Dashboard principal
    sidebar_backup_system()
    
    # Verificar se tem dados para mostrar
    if st.session_state.df_tracking.empty:
        if usuario_info["tipo"] == "admin":
            st.info("📋 Nenhum tracking cadastrado ainda. Use o sistema de backup para restaurar dados ou adicione um novo tracking abaixo.")
            
            # Mostrar formulário para adicionar primeiro tracking
            with st.expander("➕ Adicionar Primeiro Tracking", expanded=True):
                if not st.session_state.clientes_db:
                    st.warning("⚠️ Cadastre clientes primeiro! Use o menu 'Clientes' acima.")
                else:
                    with st.form("primeiro_tracking"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            clientes_disponiveis = list(st.session_state.clientes_db.keys())
                            cliente_selecionado = st.selectbox("Cliente *", clientes_disponiveis)
                            container = st.text_input("Container *", placeholder="ex: TCLU1234567")
                            carregamento = st.text_input("Carregamento", placeholder="DD/MM/AAAA")
                            embarque = st.text_input("Embarque Navio", placeholder="DD/MM/AAAA")
                        
                        with col2:
                            saida = st.text_input("Saída Navio", placeholder="DD/MM/AAAA")
                            previsao = st.text_input("Previsão Chegada Paranaguá", placeholder="DD/MM/AAAA")
                            canal_rfb = st.selectbox("Canal RFB", ['', 'VERDE', 'VERMELHO'])
                            chegada = st.text_input("Chegada Paranaguá", placeholder="DD/MM/AAAA")
                        
                        if st.form_submit_button("📦 Adicionar Tracking", type="primary"):
                            if cliente_selecionado and container:
                                novo_tracking = {
                                    'CLIENTE': cliente_selecionado,
                                    'CONTAINER': container,
                                    'CARREGAMENTO': carregamento,
                                    'EMBARQUE NAVIO': embarque,
                                    'SAIDA NAVIO': saida,
                                    'PREVISAO CHEGADA PARANAGUA': previsao,
                                    'CHEGADA PARANAGUA': chegada,
                                    'CANAL RFB': canal_rfb,
                                    'LIBERAÇAO PARANAGUA': '',
                                    'CHEGADA CIUDAD DEL ESTE PY': '',
                                    'DESCARREGAMENTO': ''
                                }
                                
                                novo_df = pd.DataFrame([novo_tracking])
                                st.session_state.df_tracking = pd.concat([st.session_state.df_tracking, novo_df], ignore_index=True)
                                st.success("✅ Primeiro tracking adicionado!")
                                st.rerun()
                            else:
                                st.error("❌ Cliente e Container são obrigatórios!")
        else:
            st.info("📋 Nenhum tracking disponível no momento. Entre em contato com a BRIX para mais informações.")
        return
    
    # Filtrar dados baseado no usuário
    df_usuario = filtrar_dados_por_cliente(st.session_state.df_tracking, usuario_info)
    
    if df_usuario.empty:
        if usuario_info["tipo"] == "cliente":
            st.info(f"📋 Nenhum tracking encontrado para {usuario_info['nome']}.")
        else:
            st.info("📋 Nenhum tracking encontrado.")
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
            if usuario_info["tipo"] == "admin":
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
        # Criar DataFrame com emojis para melhor visualização mobile
        df_display = df_filtrado.copy()
        
        # Aplicar emojis para identificar status
        for idx, row in df_display.iterrows():
            if row['CANAL RFB'] == 'VERDE':
                df_display.loc[idx, 'CANAL RFB'] = '🟢 VERDE'
            elif row['CANAL RFB'] == 'VERMELHO':
                df_display.loc[idx, 'CANAL RFB'] = '🔴 VERMELHO'
            elif row['CANAL RFB'] == '':
                df_display.loc[idx, 'CANAL RFB'] = '⏳ PENDENTE'
        
        # Mostrar tabela
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Legenda
        st.info("🟢 Verde = Liberado | 🔴 Vermelho = Inspeção | ⏳ Pendente = Aguardando")
        
        # Download dos dados (SEM DUPLICAÇÃO)
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
                if not st.session_state.clientes_db:
                    st.warning("⚠️ Cadastre clientes primeiro! Use o menu 'Clientes' acima.")
                else:
                    with st.form("novo_tracking"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            clientes_disponiveis = list(st.session_state.clientes_db.keys())
                            cliente_selecionado = st.selectbox("Cliente *", clientes_disponiveis)
                            container = st.text_input("Container *", placeholder="ex: TCLU1234567")
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
                        
                        submitted = st.form_submit_button("💾 Salvar Tracking", type="primary")
                        
                        if submitted:
                            if not cliente_selecionado or not container:
                                st.error("❌ Cliente e Container são obrigatórios!")
                            else:
                                novo_registro = {
                                    'CLIENTE': cliente_selecionado,
                                    'CONTAINER': container,
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
                                st.success("✅ Tracking adicionado!")
                                st.rerun()
        
        # Edição de registros (só admin)
        if usuario_info["tipo"] == "admin":
            with st.expander("✏️ Editar/Excluir Tracking"):
                if not df_filtrado.empty:
                    opcoes_edicao = [f"{row['CLIENTE']} - {row['CONTAINER']}" for _, row in df_filtrado.iterrows()]
                    registro_selecionado = st.selectbox("Selecione o registro para editar:", opcoes_edicao)
                    
                    if registro_selecionado:
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
                                clientes_disponiveis = list(st.session_state.clientes_db.keys())
                                cliente_atual_idx = clientes_disponiveis.index(registro['CLIENTE']) if registro['CLIENTE'] in clientes_disponiveis else 0
                                edit_cliente = st.selectbox("Cliente", clientes_disponiveis, index=cliente_atual_idx)
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
                                    st.session_state.df_tracking.loc[idx_selecionado] = [
                                        edit_cliente, edit_container, edit_carregamento, edit_embarque,
                                        edit_saida, edit_previsao, edit_chegada, edit_canal,
                                        edit_liberacao, edit_chegada_py, edit_descarregamento
                                    ]
                                    st.success("✅ Registro atualizado!")
                                    st.rerun()
    else:
        st.info("🔍 Nenhum registro encontrado com os filtros aplicados.")
    
    # Alertas
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
    # Sempre inicializar o sistema primeiro
    inicializar_sistema()
    
    # Verificar se está logado
    if not st.session_state.logado:
        tela_login()
    else:
        dashboard_principal()

if __name__ == "__main__":
    main()
