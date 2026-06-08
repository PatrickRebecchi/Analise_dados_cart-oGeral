import os
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

def carregar_dados():
    return pd.read_csv("ClientesBanco.csv", encoding="latin1")

def gerar_graficos(df):
    pasta_static = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(pasta_static, exist_ok=True)
    for f in os.listdir(pasta_static):
        if f.startswith("grafico_") and f.endswith(".png"):
            os.remove(os.path.join(pasta_static, f))
    timestamp = int(time.time())
    graficos = {}

    sexo_counts = df["Sexo"].value_counts()
    sexo_pct = (sexo_counts / sexo_counts.sum() * 100).round(1)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(sexo_counts, labels=sexo_counts.index, autopct='%1.1f%%', startangle=90)
    ax.set_title("Clientes por Sexo")
    caminho_sexo = os.path.join(pasta_static, f"grafico_sexo_{timestamp}.png")
    fig.savefig(caminho_sexo, bbox_inches='tight', dpi=120)
    plt.close(fig)
    graficos['sexo'] = f"/static/grafico_sexo_{timestamp}.png"
    graficos['sexo_dados'] = {k: f"{v} ({sexo_pct[k]}%)" for k, v in sexo_counts.items()}

    cat_counts = df["Categoria Cartão"].value_counts()
    cat_pct = (cat_counts / cat_counts.sum() * 100).round(1)
    fig, ax = plt.subplots(figsize=(5, 4))
    cat_counts.plot(kind='bar', ax=ax, color=['#0d6efd', '#ffc107', '#198754', '#dc3545'], width=0.6)
    ax.set_title("Clientes por Categoria")
    ax.set_xlabel("Categoria")
    ax.set_ylabel("Quantidade")
    plt.xticks(rotation=0)
    caminho_cat = os.path.join(pasta_static, f"grafico_categoria_{timestamp}.png")
    fig.savefig(caminho_cat, bbox_inches='tight', dpi=120)
    plt.close(fig)
    graficos['categoria'] = f"/static/grafico_categoria_{timestamp}.png"
    graficos['categoria_dados'] = {k: f"{v} ({cat_pct[k]}%)" for k, v in cat_counts.items()}

    sit_counts = df["Categoria"].value_counts()
    sit_pct = (sit_counts / sit_counts.sum() * 100).round(1)
    fig, ax = plt.subplots(figsize=(5, 4))
    sit_counts.plot(kind='bar', ax=ax, color=['#198754', '#dc3545'], width=0.4)
    ax.set_title("Clientes por Situação")
    ax.set_xlabel("Situação")
    ax.set_ylabel("Quantidade")
    plt.xticks(rotation=0)
    caminho_sit = os.path.join(pasta_static, f"grafico_situacao_{timestamp}.png")
    fig.savefig(caminho_sit, bbox_inches='tight', dpi=120)
    plt.close(fig)
    graficos['situacao'] = f"/static/grafico_situacao_{timestamp}.png"
    graficos['situacao_dados'] = {k: f"{v} ({sit_pct[k]}%)" for k, v in sit_counts.items()}

    return graficos

@app.route("/todosClientes")
def todosClientes():
    df = carregar_dados()
    lista = df.to_dict(orient="records")
    colunas = df.columns.tolist()
    total = len(lista)
    return render_template("clientes.html", colunas=colunas, lista=lista, total=total)

@app.route("/")
def home():
    return redirect(url_for("dashboard"))

@app.route("/categoria_cartao")
def categoria_cartao():
    df = carregar_dados()
    df_categoria = df["Categoria Cartão"].value_counts().reset_index()
    df_categoria.columns = ["Categoria Cartão", "Quantidade"]
    tabela_html = df_categoria.to_html(index=False, classes="table table-striped table-hover")
    return render_template("categoria_cartao.html", tabela_html=tabela_html)

@app.route("/sexo")
def sexo():
    df = carregar_dados()
    df_sexo = df["Sexo"].value_counts().reset_index()
    df_sexo.columns = ["Sexo", "Quantidade"]
    tabela_html = df_sexo.to_html(index=False, classes="table table-striped table-hover")
    return render_template("sexo.html", tabela_html=tabela_html)

@app.route("/situacao")
def situacao():
    df = carregar_dados()
    df_situacao = df["Categoria"].value_counts().reset_index()
    df_situacao.columns = ["Situação", "Quantidade"]
    tabela_html = df_situacao.to_html(index=False, classes="table table-striped table-hover")
    return render_template("situacao.html", tabela_html=tabela_html)

@app.route("/filtro")
def filtro():
    df = carregar_dados()
    sexos = sorted(df["Sexo"].dropna().unique().tolist())
    categorias = sorted(df["Categoria Cartão"].dropna().unique().tolist())
    return render_template("filtro.html", sexos=sexos, categorias=categorias)

@app.route("/clientes_por_sexo_categoria")
def clientes_por_sexo_categoria():
    df = carregar_dados()
    sexo = request.args.get("sexo")
    categoria = request.args.get("categoria")
    df_filtrado = df[(df["Sexo"] == sexo) & (df["Categoria Cartão"] == categoria)]
    lista = df_filtrado.to_dict(orient="records")
    colunas = df_filtrado.columns.tolist()
    total = len(lista)
    return render_template("lista_clientes.html", colunas=colunas, lista=lista, total=total, sexo=sexo, categoria=categoria)

@app.route("/dashboard")
def dashboard():
    df = carregar_dados()
    sexos = sorted(df["Sexo"].dropna().unique().tolist())
    categorias = sorted(df["Categoria Cartão"].dropna().unique().tolist())
    
    sexo = request.args.get("sexo", "")
    categoria = request.args.get("categoria", "")
    
    df_filtrado = df.copy()
    if sexo:
        df_filtrado = df_filtrado[df_filtrado["Sexo"] == sexo]
    if categoria:
        df_filtrado = df_filtrado[df_filtrado["Categoria Cartão"] == categoria]
    total = len(df_filtrado)
    
    graficos = gerar_graficos(df)
    
    return render_template("index.html",
                           sexos=sexos, categorias=categorias,
                           total=total, sexo=sexo, categoria=categoria,
                           clientes_sexo=df["Sexo"].value_counts().to_dict(),
                           clientes_categoria=df["Categoria Cartão"].value_counts().to_dict(),
                           clientes_situacao=df["Categoria"].value_counts().to_dict(),
                           cruzado=df.groupby(["Sexo", "Categoria Cartão"]).size().unstack(fill_value=0).to_dict(),
                           graficos=graficos)

if __name__ == "__main__":
    app.run(debug=True)
