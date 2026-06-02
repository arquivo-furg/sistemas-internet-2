# 🌐 Web Proxy com Controle de Conteúdo

Projeto de Sistemas para Internet II.  
Implementa um proxy HTTP simples com bloqueio de sites e filtro de palavrões usando **Python + Flask**.

## 👨‍💻 Desenvolvido por

- Alex Santos (@Alexsander-oml)
- Pedro Machado (@pedromchd)

## 📋 O que o projeto faz

- Funciona como um **proxy web**: você acessa sites através dele
- **Bloqueia** sites listados em `blocked.json`
- **Filtra palavrões** do HTML usando `words.json`
- **Registra** todos os acessos em `log.txt`

## 🗂️ Estrutura do projeto

```
proxy/
├── templates/
│   ├── bloqueado.html  → página de bloqueio personalizada
│   ├── erro.html       → página com outros erros do sistema
│   ├── inicio.html     → página inicial do proxy
│   └── nav.html        → componente de navegação do proxy
├── app.py              → código principal do servidor
├── blocked.json        → lista de sites bloqueados
├── log.txt             → registro de acessos
├── README.md           → este arquivo
├── requirements.txt    → dependências Python
└── words.json          → palavrões e suas substituições
```

## ✅ Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

## 🚀 Como instalar e executar

### 1. Clone ou copie a pasta do projeto

```bash
cd proxy
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute o servidor

```bash
python app.py
```

O servidor inicia em: `http://localhost:5000`

## 🧪 Como usar e testar

Abra o navegador e acesse URLs no seguinte formato:

```
http://localhost:5000/http://example.com
```

### Exemplos de teste

| Acesso                                       | Resultado esperado                             |
| -------------------------------------------- | ---------------------------------------------- |
| `http://localhost:5000/http://example.com`   | Site carregado normalmente                     |
| `http://localhost:5000/http://facebook.com`  | Página de bloqueio                             |
| `http://localhost:5000/http://instagram.com` | Página de bloqueio                             |
| `http://localhost:5000/http://globo.com`     | Site carregado (palavrões filtrados se houver) |

## 📄 Arquivos JSON

### `blocked.json`

Lista de domínios que serão bloqueados pelo proxy.

```json
{
  "bloqueados": ["facebook.com", "instagram.com"]
}
```

Para bloquear um novo site, basta adicionar o domínio na lista.

### `words.json`

Dicionário de palavrões e suas substituições. A busca é **case-insensitive** (não diferencia maiúsculas de minúsculas).

```json
{
  "burro": "bobão",
  "idiota": "bobalhão"
}
```

Para adicionar uma nova substituição, insira uma nova entrada no formato `"palavra": "substituto"`.

## ⚙️ Como funciona (resumo)

1. O usuário acessa `http://localhost:5000/http://site.com`
2. O Flask captura a URL após `/`
3. O proxy verifica se o domínio está em `blocked.json`
   - **Se estiver:** retorna uma página de bloqueio (sem fazer requisição)
   - **Se não estiver:** faz a requisição ao site real com `requests`
4. Se o conteúdo for HTML, aplica o filtro de palavrões de `words.json`
5. Registra o acesso em `log.txt` com timestamp e ação
6. Retorna o conteúdo ao navegador

## ⚠️ Limitações do projeto

- **JavaScript dinâmico:** sites que carregam conteúdo via JavaScript não serão filtrados (o filtro age apenas no HTML inicial).
- **Imagens e recursos externos:** recursos (CSS, imagens) que o browser carrega diretamente do site original não passam pelo proxy.

## 📝 Exemplo do log.txt

```
2026-05-28 20:10 | example.com | permitido
2026-05-28 20:11 | facebook.com | bloqueado
2026-05-28 20:12 | algumsite.com | filtrado
```
