# MirAI-API_Agents 🤖

[🇧🇷 Versão em Português](#pt) | [🇺🇸 English Version](#en)

---

<a id="pt"></a>
# 🇧🇷 MirAI-API_Agents

## Sobre o Projeto

O **MirAI-API_Agents** é uma API FastAPI que orquestra diferentes agentes de IA especializados para processamento de linguagem natural e geração de conteúdo. O projeto implementa uma arquitetura modular com agentes específicos para diferentes tarefas como planejamento, ensino, validação de esquemas e processamento de linguagem natural.

## ⚠️ Aviso Importante

**Este repositório é apenas para visualização** - não está pronto para uso real pois requer:
- Chaves de API privadas (Google Gemini)
- Configuração de Redis
- Configuração de PostgreSQL/MySQL
- Outras integrações privadas que não são fornecidas

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **LangChain** - Framework para aplicações com LLM
- **Google Gemini AI** - Modelo de linguagem da Google
- **Pydantic** - Validação de dados
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL/MySQL** - Banco de dados
- **Redis** - Cache e armazenamento em memória
- **Uvicorn** - Servidor ASGI
- **Python 3.x**

## 📦 Instalação

⚠️ **Não é possível instalar ou executar este projeto** sem as configurações privadas necessárias:

```bash
# Instalação das dependências (não funcionará sem as configurações)
pip install -r requirements.txt

# Execução (falhará sem as chaves de API)
python main.py
```

## 📁 Estrutura do Projeto

```
MirAI-API_Agents/
├── app/
│   ├── mirai_agents/          # Agentes especializados
│   │   ├── planner_agent.py   # Agente de planejamento
│   │   ├── teacher_agent.py   # Agente de ensino
│   │   ├── schema_agent.py    # Agente de validação de esquemas
│   │   ├── speaking_agent.py  # Agente de processamento de linguagem
│   │   └── guardrails.py      # Validações e controles
│   ├── routers/               # Endpoints da API
│   └── models/                # Modelos de dados
├── main.py                    # Aplicação principal
├── settings.py               # Configurações
└── requirements.txt          # Dependências
```

## 📄 Licença

Este projeto não possui licença específica definida.

## 📞 Contato

Para mais informações sobre este projeto, entre em contato através dos canais apropriados.

---

<a id="en"></a>
# 🇺🇸 MirAI-API_Agents

## About the Project

**MirAI-API_Agents** is a FastAPI that orchestrates different specialized AI agents for natural language processing and content generation. The project implements a modular architecture with specific agents for different tasks such as planning, teaching, schema validation, and natural language processing.

## ⚠️ Important Notice

**This repository is for viewing only** - it is not ready for real use as it requires:
- Private API keys (Google Gemini)
- Redis configuration
- PostgreSQL/MySQL configuration
- Other private integrations that are not provided

## 🛠️ Technologies Used

- **FastAPI** - Modern, fast web framework
- **LangChain** - Framework for LLM applications
- **Google Gemini AI** - Google's language model
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM
- **PostgreSQL/MySQL** - Database
- **Redis** - Cache and in-memory storage
- **Uvicorn** - ASGI server
- **Python 3.x**

## 📦 Installation

⚠️ **This project cannot be installed or run** without the necessary private configurations:

```bash
# Install dependencies (won't work without configurations)
pip install -r requirements.txt

# Run (will fail without API keys)
python main.py
```

## 📁 Project Structure

```
MirAI-API_Agents/
├── app/
│   ├── mirai_agents/          # Specialized agents
│   │   ├── planner_agent.py   # Planning agent
│   │   ├── teacher_agent.py   # Teaching agent
│   │   ├── schema_agent.py    # Schema validation agent
│   │   ├── speaking_agent.py  # Language processing agent
│   │   └── guardrails.py      # Validations and controls
│   ├── routers/               # API endpoints
│   └── models/                # Data models
├── main.py                    # Main application
├── settings.py               # Settings
└── requirements.txt          # Dependencies
```

## 📄 License

This project does not have a specific license defined.

## 📞 Contact

For more information about this project, please contact through the appropriate channels.
