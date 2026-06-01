import json
import re
import requests
from datetime import datetime
from flask import Flask, request, Response, render_template, redirect
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Define ações para o log
PERMITIDO = "permitido"
BLOQUEADO = "bloqueado"
FILTRADO = "filtrado"


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
        json.dump(dados, f, indent=2)
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
        json.dump(dados, f, indent=2, ensure_ascii=False)
        f.truncate()


# Rota index: exibe uma página simples explicando o uso do proxy
# Mostra a lista de sites bloqueados e os palavrões filtrados
@app.route("/")
def index():
    acessar = request.args.get("acessar")
    if acessar:
        return redirect("/" + acessar)

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
        req_headers = {
            key: value
            for key, value in request.headers
            if key.lower() not in ["host", "accept-encoding"]
            # Impedir conflito de decodificação
        }
        res = requests.request(
            url=url,
            method=request.method,
            headers=req_headers,
            # allow_redirects=False,
        )
    except Exception:
        return (render_template("erro.html", dominio=dominio, codigo=502), 502)

    content = res.content
    status = res.status_code

    # Exclui headers que causam problemas de decodificação no navegador
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in res.headers.items()
        if name.lower() not in excluded_headers
    ]

    type = res.headers.get("Content-Type", "")

    # Verifica se o conteúdo é HTML antes de filtrar
    filtrado = False
    if "text/html" in type:
        palavroes = carregar_palavroes()

        html = filtrar_palavroes(res.text, palavroes)

        if html != res.text:
            content = html.encode("utf-8")
            filtrado = True

    # Insere a barra de navegação no HTML
    soup = BeautifulSoup(content, "html.parser")
    with open("templates/nav.html", "r", encoding="utf-8") as f:
        nav = BeautifulSoup(f.read(), "html.parser")
        nav.input["value"] = dominio
        soup.insert(0, nav)
        content = str(soup).encode("utf-8")

    registrar_log(dominio, FILTRADO if filtrado else PERMITIDO)
    return (
        Response(response=content, status=status, headers=headers, content_type=type),
        status,
    )


if __name__ == "__main__":
    app.run(debug=True)
