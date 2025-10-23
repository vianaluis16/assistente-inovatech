import os
from dotenv import load_dotenv

print("Inicializando Assistente Virtual InovaTech...")

# 1. Ambiente
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERRO: GOOGLE_API_KEY não encontrada no arquivo .env")
    raise SystemExit(1)
print("Ambiente configurado!")

# 2. Imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    from langchain_community.tools import DuckDuckGoSearchRun
    from langchain_community.document_loaders import TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain.tools import Tool
    from langchain.tools.retriever import create_retriever_tool
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.prompts import PromptTemplate
    from langchain_core.tools import tool
except Exception as e:
    print(f"Erro de importação: {e}")
    raise SystemExit(1)





# 3. LLM Gemini

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0
    )
    print("LLM configurada")
except Exception as e:
    print(f" Erro LLM: {e}")
    raise SystemExit(1)

# 4) RAG — carregar conhecimento, gerar embeddings, FAISS, retriever

print("Montando base RAG...")

try:
    if not os.path.exists("conhecimento.txt"):
        raise FileNotFoundError("Arquivo conhecimento.txt não encontrado na raiz do projeto")
    docs = TextLoader("conhecimento.txt", encoding="utf-8").load()

    #chunkar os textos

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, chunk_overlap=80, separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vectordb = FAISS.from_documents(chunks, embedding=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    rag_tool = create_retriever_tool(
        retriever,
        name="base_conhecimento_inovatech",
        description=(
            "Use para responder perguntas internas sobre a InovaTech Ltda.: fundadores, sede, missão, cultura, produtos (Sistema Omega, Data Insights), números citados no arquivo conhecimento.txt."
        ),
    )
    print("Base RAG pronta")
except Exception as e:
    print(f"Erro ao montar RAG: {e}")
    raise SystemExit(1)

# 5. Busca web (informação externa / tempo real) - DuckDUckGo search tool

print("Adicionando busca web...")


def busca_web_corrigida(query: str) -> str:
    """Busca na web com tratamento de erro melhorado"""
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                return "\n".join([f"- {r['body']}" for r in results])
            else:
                return "Nenhum resultado encontrado na busca."
    except Exception as e:
        return f"Busca web temporariamente indisponível. Erro: {str(e)}"


busca_web = Tool(
    name="busca_web",
    description="Buscador na internet para fatos externos/atuais (clima, notícias, eventos recentes, dados que NÃO estejam no conhecimento interno).",
    func=busca_web_corrigida
)

# 6. Calculadora (@tool)
import ast
import operator as op

ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
}

def _eval_node(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Constante inválida")
    if isinstance(node, ast.BinOp):
        if type(node.op) not in ALLOWED_OPS:
            raise ValueError("Operação não permitida")
        return ALLOWED_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in ALLOWED_OPS:
            raise ValueError("Operação unária não permitida")
        return ALLOWED_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Expressão inválida")

@tool("calculadora", return_direct=False)
def calculadora(expressao: str) -> str:
    """Calculadora para operações simples: +, -, *, /, //, %, ** e parênteses."""
    try:
        tree = ast.parse(expressao, mode="eval")
        resultado = _eval_node(tree.body)
        #return f"{expressao} = {resultado}"
        return str(resultado)
    except ZeroDivisionError:
        return "Erro: divisão por zero."
    except Exception as e:
        return f"Erro no cálculo: {e}"

# 7. Coleção de ferramentas

tools = [rag_tool, busca_web, calculadora]
print("Ferramentas: RAG, Busca Web, Calculadora")

# 8. Prompt do agente (o mais claro possível sobre quando usar cada ferramenta)

from langchain.prompts import PromptTemplate

prompt_template = """Você é o Assistente Virtual Inteligente da InovaTech Ltda.

Você tem acesso às seguintes ferramentas:

{tools}

Use o seguinte formato de raciocínio (ReAct):

Question: a pergunta que você deve responder
Thought: você deve sempre pensar sobre o que fazer
Action: a ação a tomar, deve ser uma de [{tool_names}]
Action Input: a entrada para a ação
Observation: o resultado da ação
... (este ciclo Thought/Action/Action Input/Observation pode se repetir N vezes)
Thought: Agora eu sei a resposta final
Final Answer: a resposta final para a pergunta original

REGRAS IMPORTANTES:
- Use "base_conhecimento_inovatech" para perguntas sobre a InovaTech (fundadores, produtos Sistema Omega e Data Insights, missão, sede, cultura)
- Use "busca_web" para informações externas (clima, notícias, eventos atuais)
- Use "calculadora" para operações matemáticas
- Sempre responda em português brasileiro de forma clara e completa

Comece!

Question: {input}
Thought: {agent_scratchpad}"""

prompt = PromptTemplate.from_template(prompt_template)

# 9. Cria agente + executor
try:
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt) #injetar os passos do agente
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=4,
        return_intermediate_steps=False,
        early_stopping_method="generate",
    )
    print("Agente criado!")
except Exception as e:
    print(f"Erro ao criar agente: {e}")
    raise SystemExit(1)

# 10) CLI
print("\n" + "=" * 60)
print("ASSISTENTE VIRTUAL INOVATECH - PRONTO!")
print("=" * 60)
print("Digite 'sair' para encerrar")
print("\n Exemplos:")
print(" • Quem fundou a InovaTech?")
print(" • Qual a temperatura em São Paulo agora?")
print(" • Quanto é 25 * 4?")
print(" • Quais são os produtos da empresa?")
print("=" * 60)

while True:
    try:
        pergunta = input("\nPergunte alguma coisa: ").strip()
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("Até logo!")
            break
        if not pergunta:
            continue

        print("\nProcessando...")
        resposta = executor.invoke({"input": pergunta})

        print(f"\nAssistente: {resposta.get('output', resposta)}")

    except KeyboardInterrupt:
        print("\n\nPrograma interrompido.")
        break
    except Exception as e:
        print(f"\nErro: {e}")
        print("Tente novamente.")
