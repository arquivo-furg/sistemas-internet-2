import json
from flask import Flask, render_template

app = Flask(__name__)


# Carrega lista de sites bloqueados
def carregar_bloqueados():
    with open("blocked.json", "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados["bloqueados"]


# Carrega dicionário de palavrões e substituições
def carregar_palavroes():
    with open("words.json", "r", encoding="utf-8") as f:
        return json.load(f)


# Rota index: exibe uma página simples explicando o uso do proxy
# Mostra a lista de sites bloqueados e os palavrões filtrados
@app.route("/")
def index():
    bloqueados = carregar_bloqueados()
    palavroes = carregar_palavroes()
    return render_template("index.html", bloqueados=bloqueados, palavroes=palavroes)


if __name__ == "__main__":
    app.run(debug=True)
