import json
import re
import requests
from datetime import datetime
from flask import Flask, request, Response, render_template, redirect
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


# Substitui palavrões no HTML (case-insensitive)
def filtrar_palavroes(html, palavroes):
    for palavra, substituto in palavroes.items():
        html = re.sub(palavra, substituto, html, flags=re.IGNORECASE)
    return html


# Adiciona ou remove um site da lista de bloqueados
def adicionar_remover_url(url, remover):
    with open("blocked.json", "r+", encoding="utf-8") as f:
        dados = json.load(f)
        if remover:
            if url in dados["bloqueados"]:
                dados["bloqueados"].remove(url)
        else:
            if url not in dados["bloqueados"]:
                dados["bloqueados"].append(url)
        f.seek(0)
        json.dump(dados, f, indent=4)
        f.truncate()


# Adiciona ou remove um palavrão do dicionário
def adicionar_remover_palavra(palavra, substituto, remover):
    with open("words.json", "r+", encoding="utf-8") as f:
        dados = json.load(f)
        if remover:
            if palavra in dados:
                del dados[palavra]
        elif substituto:
            dados[palavra] = substituto
        f.seek(0)
        json.dump(dados, f, indent=4)
        f.truncate()


# Rota index: exibe uma página simples explicando o uso do proxy
# Mostra a lista de sites bloqueados e os palavrões filtrados
@app.route("/")
def index():
    url = request.args.get("url")
    palavra = request.args.get("palavra")
    substituto = request.args.get("substituto")
    remover = request.args.get("remover")

    if url:
        adicionar_remover_url(url, remover)
        return redirect("/")

    if palavra:
        adicionar_remover_palavra(palavra, substituto, remover)
        return redirect("/")

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

    # Faz a requisição ao site real
    try:
        res = requests.get(url)
    except Exception:
        registrar_log(dominio, ERRO)
        return (render_template("erro.html", dominio=dominio, codigo=502), 502)

    # Verifica se o conteúdo é HTML antes de filtrar
    type = res.headers.get("Content-Type", "")
    filtrado = False
    if "text/html" in type:
        palavroes = carregar_palavroes()

        html = filtrar_palavroes(res.text, palavroes)

        if html != res.text:
            filtrado = True

    registrar_log(dominio, FILTRADO if filtrado else PERMITIDO)
    return (Response(res.content, status=res.status_code, content_type=type), 200)


if __name__ == "__main__":
    app.run(debug=True)
