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

# --- FUNÇÃO DE CHAMADA À API DA OPENAI (A mesma que testamos) ---
def chamar_bloom_mentor(api_key, atividade_do_professor):
    try:
        openai.api_key = api_key
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA_BLOOM_MENTOR},
                {"role": "user", "content": atividade_do_professor}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except openai.AuthenticationError:
        return "Erro de Autenticação: A chave da API da OpenAI fornecida não é válida. Verifique a chave e tente novamente."
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"

# --- INTERFACE GRÁFICA DA APLICAÇÃO (STREAMLIT) ---

# Configuração da página
st.set_page_config(page_title="BloomMentor", page_icon="🎓", layout="wide")

# Título e descrição
st.title("🎓 BloomMentor: Seu Arquiteto Pedagógico")
st.markdown("Insira a descrição de uma atividade, objetivo de aprendizagem ou desafio pedagógico, e receba uma análise crítica e construtiva para elevar sua prática.")

# Colunas para organizar a interface
col1, col2 = st.columns(2)

with col1:
    # Área para inserir a chave da API
    st.subheader("1. Configuração")
    api_key_input = st.text_input(
        "Insira sua chave da API da OpenAI aqui:",
        type="password",
        placeholder="sk-...",
        help="Sua chave é necessária para processar a solicitação e não é armazenada. Obtenha em platform.openai.com"
    )

    # Área para o input do professor
    st.subheader("2. Descreva sua Ideia ou Desafio")
    user_input = st.text_area(
        "Cole aqui sua ideia para a atividade:",
        height=250,
        placeholder="Ex: 'Para minha aula de história, pensei em pedir aos alunos para fazerem um resumo sobre a Revolução Francesa.'"
    )

    # Botão para gerar a análise
    if st.button("Analisar com BloomMentor", type="primary"):
        if not api_key_input:
            st.error("Por favor, insira sua chave da API da OpenAI para continuar.")
        elif not user_input:
            st.error("Por favor, descreva sua ideia ou desafio no campo de texto.")
        else:
            # Mostra uma mensagem de "carregando" enquanto processa
            with st.spinner("O Arquiteto Pedagógico está analisando seu projeto..."):
                # Armazena a resposta na sessão do usuário
                st.session_state.resposta_agente = chamar_bloom_mentor(api_key_input, user_input)

with col2:
    # Área para exibir a resposta
    st.subheader("3. Análise e Sugestões do Mentor")
    if 'resposta_agente' in st.session_state:
        st.markdown(st.session_state.resposta_agente)
    else:
        st.info("A análise do seu projeto aparecerá aqui.")