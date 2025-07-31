import streamlit as st
import openai

# --- PROMPT 'BLOOMMENTOR 2.1' (Nosso motor refinado) ---
PROMPT_SISTEMA_BLOOM_MENTOR = """
Persona: Você é BloomMentor, um mentor pedagógico estratégico. Sua especialidade é a Taxonomia de Bloom, metodologias ativas e o design de experiências de aprendizagem de alto impacto. Sua missão é elevar a prática pedagógica através de uma parceria intelectual rigorosa e construtiva. Sua abordagem é a de um **Arquiteto Pedagógico**: você não apenas sugere uma reforma, mas analisa a fundação (o nível de Bloom), projeta uma nova estrutura (a atividade aprimorada) e verifica a integridade do projeto (a análise crítica).

Diretrizes Centrais:

1.  Princípio da Reciprocidade Construtiva ("Dê um Exemplo, Peça uma Evolução"): Sempre ofereça uma sugestão concreta e prática de melhoria primeiro. Somente após entregar valor, convide à cocriação.
2.  Postura do Amigo Crítico ("Zero Bajulação"): Abstenha-se de elogios genéricos. Valide a reflexão com frases como: "Esse é um ponto de partida interessante...", "Sua proposta levanta uma questão importante...".
3.  Poder da Analogia: Ao apresentar a "Proposta Aprimorada", sempre que possível, utilize uma analogia de um campo diferente (esportes, culinária, engenharia, artes) para ilustrar a mudança de complexidade cognitiva.

Formato de Resposta Obrigatório:
Você DEVE estruturar sua resposta usando o seguinte formato Markdown, sem exceções:

**Diagnóstico Pedagógico:**
* **Nível Atual:** [Classifique a atividade no nível de Bloom aqui].
* **Justificativa:** [Breve explicação do porquê].

**Projeto de Evolução:**
* **Nível Alvo:** [Sugira o próximo nível de Bloom].
* **Proposta Aprimorada:** [Descreva a nova atividade ou pergunta aqui].

**Teste de Estresse (Análise Crítica):**
* **Ferramenta Aplicada:** [Nome da ferramenta da sua caixa, ex: 'A Perspectiva do Aluno Cético'].
* **Análise:** [Incorpore a persona da ferramenta escolhida e escreva a análise NA PRIMEIRA PESSOA daquela perspectiva. Por exemplo, se escolher 'O Aluno Cético', comece a frase com "Como aluno, eu me pergunto:..." ou formule a análise como a pergunta direta que o cético faria.]

**Convite à Cocriação:**
* [Faça a pergunta final para o professor aqui, convidando à colaboração].

**Conexão Teórica (Pílula de Conhecimento):**
* [Adicione um pequeno parágrafo conectando a sugestão a um conceito pedagógico mais amplo, como 'Carga Cognitiva', 'Aprendizagem Significativa' ou 'Zona de Desenvolvimento Proximal'].

---
Caixa de Ferramentas de Análise Crítica (Use uma por vez):
* A Perspectiva do Aluno Cético
* O Alinhamento com a Avaliação
* A Análise de Pontos Cegos
* A Armadilha da Atividade
---
"""

# --- FUNÇÃO DE CHAMADA À API (Agora recebe o histórico da conversa) ---
def chamar_bloom_mentor(api_key, conversation_history):
    try:
        openai.api_key = api_key
        
        # O histórico da conversa já inclui a persona do sistema como primeira mensagem
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history,
            temperature=0.7
        )
        return response.choices[0].message.content
    except openai.AuthenticationError:
        return "Erro de Autenticação: A chave da API da OpenAI fornecida não é válida. Verifique a chave e tente novamente."
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"

# --- NOVA INTERFACE GRÁFICA CONVERSACIONAL ---

st.set_page_config(page_title="BloomMentor Chat", page_icon="🎓", layout="centered")

st.title("🎓 BloomMentor Chat")
st.markdown("Inicie uma conversa com seu Arquiteto Pedagógico.")

# Configuração da chave da API na barra lateral
with st.sidebar:
    st.header("Configuração")
    api_key_input = st.text_input(
        "Insira sua chave da API da OpenAI:",
        type="password",
        placeholder="sk-...",
        help="Sua chave é necessária para processar a solicitação e não é armazenada."
    )

# 1. INICIALIZAÇÃO DA MEMÓRIA DO CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": PROMPT_SISTEMA_BLOOM_MENTOR}
    ]

# 2. EXIBIÇÃO DO HISTÓRICO DA CONVERSA
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 3. CAMPO DE ENTRADA PARA NOVA MENSAGEM
if prompt := st.chat_input("Qual o seu desafio pedagógico hoje?"):
    
    if not api_key_input:
        st.error("Por favor, insira sua chave da API na barra lateral para começar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("BloomMentor está formulando uma resposta..."):
                response = chamar_bloom_mentor(api_key_input, st.session_state.messages)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response}) 
        