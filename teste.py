import pandas as pd
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

def carregar_dados():
    return pd.read_csv("ClientesBanco.csv", encoding="latin1")

@app.route("/")
def clientes():
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
    
    return render_template("index.html",
                           sexos=sexos, categorias=categorias,
                           total=total, sexo=sexo, categoria=categoria,
                           clientes_sexo=df["Sexo"].value_counts().to_dict(),
                           clientes_categoria=df["Categoria Cartão"].value_counts().to_dict(),
                           clientes_situacao=df["Categoria"].value_counts().to_dict(),
                           cruzado=df.groupby(["Sexo", "Categoria Cartão"]).size().unstack(fill_value=0).to_dict())

if __name__ == "__main__":
    app.run(debug=True)
