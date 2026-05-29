import json
import requests
from datetime import datetime
from flask import Flask, Response, render_template
from urllib.parse import urlparse

# Define ações para o log
PERMITIDO = "permitido"
BLOQUEADO = "bloqueado"
FILTRADO = "filtrado"
ERRO = "erro ao acessar"


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


# Extrai o domínio da URL (ex: "facebook.com")
def extrair_dominio(url):
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
    # Garante que a URL comece com http:// ou https://
    if not url.startswith("http"):
        url = "http://" + url

    dominio = extrair_dominio(url)
    bloqueados = carregar_bloqueados()

    # Verifica se o domínio está bloqueado
    if any(b in dominio for b in bloqueados):
        registrar_log(dominio, BLOQUEADO)
        return (render_template("bloqueado.html", dominio=dominio), 403)

    res = requests.get(url)
    type = res.headers.get("Content-Type", "")

    registrar_log(dominio, PERMITIDO)
    return (Response(res.content, status=res.status_code, content_type=type), 200)


if __name__ == "__main__":
    app.run(debug=True)
