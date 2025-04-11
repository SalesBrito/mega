import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import requests
from io import StringIO

st.set_page_config(page_title="MegaMaster 2025", layout="wide")

NUMEROS_MEGA = list(range(1, 61))

def baixar_resultados():
    url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Mega-Sena"
    try:
        response = requests.get(url)
        if response.ok:
            df = pd.read_html(StringIO(response.text))[0]
            df = df.dropna(subset=["Dezenas Sorteadas (1ª dezena)"])
            return df
        else:
            st.error("Erro ao baixar resultados.")
            return None
    except Exception as e:
        st.error(f"Erro: {e}")
        return None

def numeros_em_sequencia(jogo):
    for i in range(len(jogo) - 2):
        if jogo[i+1] == jogo[i]+1 and jogo[i+2] == jogo[i]+2:
            return True
    return False

def gerar_jogo(filtros=True, excluir=[]):
    while True:
        jogo = sorted(random.sample(NUMEROS_MEGA, 6))
        if filtros:
            pares = sum(1 for n in jogo if n % 2 == 0)
            if 2 <= pares <= 4 and not numeros_em_sequencia(jogo) and not any(n in excluir for n in jogo):
                return jogo
        else:
            return jogo

def gerar_varios_jogos(qtd, filtros=True, excluir=[]):
    return [gerar_jogo(filtros, excluir) for _ in range(qtd)]

def analisar_frequencia(df):
    dezenas = []
    for i in range(1, 7):
        dezenas.extend(df[f"Dezenas Sorteadas ({i}ª dezena)"].astype(int).tolist())
    contagem = Counter(dezenas)
    mais_comuns = contagem.most_common(10)
    return contagem, mais_comuns

def simular_apostas(n_apostas, jogo_real=None):
    if not jogo_real:
        jogo_real = sorted(random.sample(NUMEROS_MEGA, 6))
    acertos = {4: 0, 5: 0, 6: 0}
    for _ in range(n_apostas):
        jogo = gerar_jogo()
        qnt = len(set(jogo_real) & set(jogo))
        if qnt in acertos:
            acertos[qnt] += 1
    ganho = (acertos[4]*300) + (acertos[5]*15000) + (acertos[6]*3000000)
    gasto = n_apostas * 5
    return acertos, ganho, gasto, jogo_real

def app():
    st.title("MegaMaster 2025")
    menu = st.sidebar.radio("Navegação", ["Gerar Jogos", "Análise de Frequência", "Simular Apostas", "Bolão"])

    if menu == "Gerar Jogos":
        qtd = st.slider("Quantos jogos deseja gerar?", 1, 20, 5)
        if st.button("Gerar jogos"):
            jogos = gerar_varios_jogos(qtd)
            for i, jogo in enumerate(jogos, 1):
                st.write(f"Jogo {i}: {jogo}")

    elif menu == "Análise de Frequência":
        st.subheader("Analisando sorteios anteriores")
        df = baixar_resultados()
        if df is not None:
            contagem, mais_comuns = analisar_frequencia(df)
            st.write("Top 10 mais sorteados:")
            st.write(pd.DataFrame(mais_comuns, columns=["Dezena", "Frequência"]))

            fig, ax = plt.subplots(figsize=(12, 5))
            ax.bar(contagem.keys(), contagem.values(), color='blue')
            ax.set_title("Frequência dos Números da Mega-Sena")
            ax.set_xlabel("Dezenas")
            ax.set_ylabel("Frequência")
            st.pyplot(fig)
        else:
            st.error("Erro ao carregar dados da Caixa.")

    elif menu == "Simular Apostas":
        st.subheader("Simulador de apostas")
        n = st.number_input("Número de apostas para simular", min_value=1, max_value=100000, value=1000)
        if st.button("Simular"):
            acertos, ganho, gasto, sorteado = simular_apostas(n)
            st.write(f"Jogo sorteado: {sorteado}")
            st.write(f"Quadras: {acertos[4]} | Quinas: {acertos[5]} | Senas: {acertos[6]}")
            st.success(f"Gasto: R$ {gasto} | Ganho estimado: R$ {ganho}")
            st.info(f"Lucro/Prejuízo: R$ {ganho - gasto}")

    elif menu == "Bolão":
        st.subheader("Gerador de bolão")
        valor = st.number_input("Valor total disponível (R$)", min_value=5.0, step=5.0)
        if st.button("Gerar bolão"):
            n_jogos = int(valor // 5)
            jogos = gerar_varios_jogos(n_jogos)
            for i, jogo in enumerate(jogos, 1):
                st.write(f"Jogo {i}: {jogo}")

if __name__ == "__main__":
    app()
