import json
from datetime import datetime
from flask import Flask, render_template
from urllib.parse import urlparse

app = Flask(__name__)


# Define ações para o log
class Acoes:
    PERMITIDO = "permitido"
    BLOQUEADO = "bloqueado"
    FILTRADO = "filtrado"


# Carrega lista de sites bloqueados
def carregar_bloqueados():
    with open("blocked.json", "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados["bloqueados"]


# Carrega dicionário de palavrões e substituições
def carregar_palavroes():
    with open("words.json", "r", encoding="utf-8") as f:
        return json.load(f)


# Extrai o domínio da URL (ex: "facebook.com")
def extrair_dominio(url):
    # Garante que a URL comece com http:// ou https://
    if not url.startswith("http"):
        url = "http://" + url

    parsed = urlparse(url)
    return parsed.netloc


# Registra cada acesso no log
def registrar_log(dominio, acao):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"{agora} | {dominio} | {acao}\n"
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(linha)


# Rota index: exibe uma página simples explicando o uso do proxy
# Mostra a lista de sites bloqueados e os palavrões filtrados
@app.route("/")
def index():
    bloqueados = carregar_bloqueados()
    palavroes = carregar_palavroes()
    return render_template("index.html", bloqueados=bloqueados, palavroes=palavroes)


# Rota principal: captura qualquer URL passada após o endereço do proxy
@app.route("/<path:url>")
def proxy(url):
    dominio = extrair_dominio(url)
    bloqueados = carregar_bloqueados()

    # Verifica se o domínio está bloqueado
    if any(b in dominio for b in bloqueados):
        registrar_log(dominio, Acoes.BLOQUEADO)
        return f"<h1>O site {dominio} está bloqueado!</h1>", 403

    registrar_log(dominio, Acoes.PERMITIDO)
    return f"<h1>Você tentou acessar: {dominio}</h1>", 200


if __name__ == "__main__":
    app.run(debug=True)
