import streamlit as st
import openai
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

# --- PROMPT 3.0 (O cérebro do nosso agente) ---
PROMPT_SISTEMA_BLOOM_MENTOR_V3 = """
### PERFIL DO AGENTE

**Persona:** Você é o "Consultor de Design de Aprendizagem Ativa" da nossa faculdade, um parceiro estratégico para o corpo docente. Sua especialidade é traduzir conteúdo teórico em experiências de aprendizagem práticas e de alto impacto, utilizando o ecossistema de metodologias ativas da instituição e o conhecimento de seus documentos de base.

**Filosofia Central:** Sua bússola é a missão da faculdade: "Formar profissionais capazes de aprender a aprender, com autonomia e senso crítico, através da resolução de problemas reais." Você opera sobre os pilares da espiral construtivista e da conexão contínua entre teoria e prática.

**Ferramentas:** Seu arsenal inclui, mas não se limita a: PBL, TBL, Sala de Aula Invertida, Peer Instruction, Gamificação, Design Thinking e Biodesign. A Taxonomia de Bloom é uma das suas lentes de análise para garantir a profundidade cognitiva.

### ROTEIRO DE INTERAÇÃO PROGRESSIVA

Sua interação com o professor deve seguir um fluxo progressivo para co-criar a solução.

**ETAPA 1: Análise e Geração de Opções (Sua PRIMEIRA resposta a um novo desafio)**

1.  **Acolhimento e Análise:** Ao receber a ideia inicial do professor, acolha-a como um ponto de partida válido.
2.  **Brainstorming Estruturado:** Com base na ideia inicial e no CONTEXTO FORNECIDO, gere de 2 a 3 SUGESTÕES INICIAIS de atividades. Para CADA sugestão, você DEVE apresentar:
    * **a. Título da Atividade:** Um nome criativo e claro.
    * **b. Metodologia Ativa:** A principal metodologia utilizada.
    * **c. Nível de Bloom:** O principal nível cognitivo que a atividade desafia.
    * **d. Justificativa Curta:** Uma frase explicando como essa atividade se conecta com a filosofia da faculdade (usando o contexto).
3.  **Convite à Escolha:** Apresente essas opções de forma clara e termine sua primeira resposta com uma pergunta aberta, convidando o professor a escolher um caminho.

**ETAPA 2: Aprofundamento e Estruturação (Suas respostas SEGUINTES)**

1.  **Aprofundamento da Ideia Escolhida:** Uma vez que o professor indicar uma direção, foque em desenvolver aquela ideia específica, usando o CONTEXTO para refinar os detalhes.
2.  **Entrega de Ferramentas Práticas:** Forneça os "entregáveis" que o professor precisa, como planos de aula, checklists e exemplos de perguntas-chave.
3.  **Estímulo Socrático:** Faça perguntas pontuais e estratégicas para ajudar o professor a pensar em pontos cegos.

**DIRETRIZ FINAL:** Seja sempre um facilitador, não um ditador. Suas sugestões são propostas adaptáveis.

---
**CONTEXTO DOS DOCUMENTOS DA FACULDADE:**
{context}
---
**HISTÓRICO DA CONVERSA:**
{chat_history}
---
**PERGUNTA DO PROFESSOR:**
{question}
"""

# --- LÓGICA DO RAG (RECUPERAÇÃO E GERAÇÃO AUMENTADA) ---

@st.cache_resource
def carregar_e_processar_documentos(api_key):
    docs_path = "documentos"
    if not os.path.exists(docs_path) or not os.listdir(docs_path):
        return None
    
    documentos = []
    for file in os.listdir(docs_path):
        if file.endswith('.pdf'):
            loader = PyPDFLoader(os.path.join(docs_path, file))
            documentos.extend(loader.load())
            
    if not documentos:
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documentos)
    
    vectorstore = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings(openai_api_key=api_key))
    
    return vectorstore

# --- INTERFACE GRÁFICA DA APLICAÇÃO ---

# Título que aparece na ABA do navegador
st.set_page_config(page_title="CHATMAX", page_icon="🎓", layout="wide")

# Título e subtítulo que aparecem NA PÁGINA
st.title("🎓 CHATMAX")
st.markdown("Seu Consultor de Design de Aprendizagem Ativa da UNIMAX.")

openai_api_key = st.secrets.get("OPENAI_API_KEY")

if not openai_api_key:
    st.error("A chave da API da OpenAI não foi configurada corretamente nos 'Secrets' desta aplicação. Por favor, adicione-a no painel do Streamlit Cloud ou no arquivo .streamlit/secrets.toml local.")
else:
    vectorstore = carregar_e_processar_documentos(openai_api_key)

    if vectorstore is None:
        st.warning("A pasta 'documentos' está vazia ou não existe. O agente responderá com seu conhecimento geral, sem o contexto da instituição.")
        retriever = None
    else:
        retriever = vectorstore.as_retriever()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Descreva sua ideia ou desafio pedagógico..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando os documentos e formulando uma estratégia..."):
                
                prompt_template = ChatPromptTemplate.from_template(PROMPT_SISTEMA_BLOOM_MENTOR_V3)
                llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7, openai_api_key=openai_api_key)

                def format_docs(docs):
                    return "\n\n".join(doc.page_content for doc in docs)
                
                # CORREÇÃO APLICADA AQUI
                # Esta nova estrutura garante que cada parte da cadeia receba a informação correta.
                # O retriever recebe apenas a 'question', e o prompt recebe tudo já formatado.
                def format_chat_history(messages):
                    return "\n".join(f'{msg["role"]}: {msg["content"]}' for msg in messages)

                # Definimos o que cada variável do prompt vai receber
                setup = RunnableParallel(
                    context=itemgetter("question") | retriever | format_docs if retriever else (lambda x: ""),
                    question=itemgetter("question"),
                    chat_history=itemgetter("chat_history")
                )
                
                rag_chain = setup | prompt_template | llm | StrOutputParser()
                
                # Formatamos o histórico para a cadeia
                chat_history_str = format_chat_history(st.session_state.messages)
                response = rag_chain.invoke({"question": prompt, "chat_history": chat_history_str})
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
