# 🤖 Assistente Virtual InovaTech (LangChain + Gemini)

Este projeto implementa um **Agente de IA ReAct** (Reasoning + Acting) usando o framework **LangChain** e o modelo **Google Gemini**.  
O assistente é capaz de **raciocinar**, **escolher a melhor ferramenta** e **responder perguntas de forma autônoma**.

---

## ⚙️ Funcionalidades Principais

O agente possui **três ferramentas** integradas:

1.  **RAG interno (Retrieval-Augmented Generation)**  
   - Usa **FAISS** e **embeddings do Gemini (`text-embedding-004`)**  
   - Responde perguntas sobre a InovaTech Ltda.  
   - Fonte: `conhecimento.txt`

2.  **Busca na Web (DuckDuckGo)**  
   - Usa o pacote `duckduckgo-search` (ou Tavily/SerpAPI opcionalmente)  
   - Permite consultar informações **em tempo real**, como clima, notícias e eventos atuais.

3.  **Calculadora Personalizada**  
   - Implementada via `@tool` do LangChain  
   - Avalia expressões matemáticas simples (`+`, `-`, `*`, `/`, `**`, `%`, `//`).

---

## Tecnologias Utilizadas

- **LangChain** (`langchain`, `langchain-community`, `langchain-google-genai`)
- **Google Gemini** (via `google-generativeai`)
- **FAISS** para base vetorial em memória
- **DuckDuckGo Search** (API pública)
- **Python dotenv** para gestão de variáveis de ambiente

---

## 🚀 Como Executar

### 1. Clonar o repositório
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd assistente-inovatech
```

### 2. Criar e Ativar o Ambiente Virtual

```bash
# Criar o ambiente
python -m venv .venv

# Ativar o ambiente
# Windows (PowerShell/CMD):
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

### 3. Instalar as Dependências

As bibliotecas necessárias estão listadas no requirements.txt. Após entra no venv, execute:
```bash
pip install -r requirements.txt
```

### 4. Configurar API Key

Crie um arquivo `.env` na raiz do projeto e adicione sua chave de API do Google Gemini:
```env
GOOGLE_API_KEY=sua_chave_aqui
```

### 5. Executar o Assistente
Dentro do venv, execute:
```bash
python assistente.py
```

---
### Observações:
Erro na Busca Web (Rate Limit)

A ferramenta de busca_web utiliza a API pública e gratuita do DuckDuckGo. Esta API possui um limite de requisições (rate limit).

O que isso significa? Várias perguntas de busca na web em um curto período farão a ferramenta falhar temporariamente.

Você verá algo como:
Erro: 202 Ratelimit ou Busca web temporariamente indisponível.


Como resolver? Apenas aguarde alguns minutos e tente novamente.
****