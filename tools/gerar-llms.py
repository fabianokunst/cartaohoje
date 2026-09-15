# -*- coding: utf-8 -*-
"""
Gera /llms.txt e /llms-full.txt a partir do HTML das páginas.

Por que existe
--------------
Modelos de linguagem leem melhor Markdown do que HTML: sem <div>, sem SVG
inline, sem CSS, sem menu repetido em toda página. A convenção llms.txt
(llmstxt.org) resolve isso com dois arquivos na raiz:

  /llms.txt        mapa curado do site — o que existe e onde
  /llms-full.txt   o conteúdo inteiro, já em Markdown

O conteúdo é EXTRAÍDO do HTML, nunca escrito à mão. Assim os dois arquivos não
podem divergir do site: se a página mudar e ninguém rodar este script, a
divergência aparece no diff — não em silêncio.

Como rodar
----------
    python tools/gerar-llms.py

Sem dependências: só a biblioteca padrão. Rode sempre que o texto de uma
página mudar, e confira o diff antes de publicar.
"""
import io
import os
import re
from html.parser import HTMLParser

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://cartaohoje.com.br"

# Ordem importa: é a ordem em que o conteúdo aparece no llms-full.txt.
PAGINAS = [
    ("/",                         "index.html",                          "Home"),
    ("/baixar-o-app/",            "baixar-o-app/index.html",             "Baixar o app"),
    ("/hoje-pay/",                "hoje-pay/index.html",                 "Hoje Pay"),
    ("/perguntas-frequentes/",    "perguntas-frequentes/index.html",     "Perguntas frequentes"),
    ("/fale-conosco/",            "fale-conosco/index.html",             "Fale conosco"),
    ("/trabalhe-conosco/",        "trabalhe-conosco/index.html",         "Trabalhe conosco"),
    ("/politica-de-privacidade/", "politica-de-privacidade/index.html",  "Política de Privacidade"),
]

IGNORAR = {"script", "style", "svg", "noscript", "template"}
BLOCOS = {"p", "div", "section", "article", "header", "footer", "h1", "h2", "h3",
          "h4", "h5", "h6", "li", "tr", "summary", "details", "figcaption", "dd", "dt"}

# Elementos sem tag de fechamento. Tratá-los como par abre/fecha desequilibra
# qualquer contador — foi o que, antes, fazia o <source> de um <picture> deixar
# o parser mudo até o fim do arquivo.
VAZIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
          "meta", "param", "source", "track", "wbr"}

# O título da página já é o "#" do documento: o conteúdo desce um nível.
TITULOS = {"h1": "##", "h2": "###", "h3": "####", "h4": "#####",
           "h5": "######", "h6": "######"}

# Elementos inline vizinhos costumam vir sem espaço no HTML — <b>24x</b><span>
# parcelas</span> viraria "24xparcelas". Fecha-se cada um com um espaço; a
# normalização depois colapsa o excesso e cola de volta a pontuação.
INLINE = {"a", "abbr", "b", "code", "em", "i", "small", "span", "strong"}


class ParaMarkdown(HTMLParser):
    """Converte o <main> de uma página em Markdown legível."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.saida = []          # linhas prontas
        self.buf = []            # texto da linha em construção
        self.pilha = []          # tags abertas
        self.mudo = 0            # profundidade dentro de tag ignorada
        self.no_main = False
        self.prefixo = None      # marcador da linha atual ("- ", "### ", ...)
        self.href = None
        self.texto_link = []

    # ------------------------------------------------------------- utilidades
    def _emit(self, s):
        """Marcação inline dentro de um link pertence ao rótulo, não à linha."""
        (self.texto_link if self.href is not None else self.buf).append(s)

    def _flush(self):
        txt = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        pref = self.prefixo
        self.prefixo = None
        if not txt:
            return
        self.saida.append((pref or "") + txt)

    def _abs(self, url):
        if url.startswith("/"):
            return SITE + url
        return url

    # ------------------------------------------------------------- handlers
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)

        if tag == "main":
            self.no_main = True
            return
        if not self.no_main:
            return

        if tag in IGNORAR:
            if tag not in VAZIOS:
                self.mudo += 1
            return
        if self.mudo:
            return

        # A trilha de navegação é redundante em texto corrido.
        if tag == "nav" and "crumbs" in a.get("class", ""):
            self.mudo += 1
            self.pilha.append("nav-crumbs")
            return

        if tag in BLOCOS:
            self._flush()

        if tag in TITULOS:
            self.prefixo = TITULOS[tag] + " "
        elif tag == "summary":
            # No FAQ o <summary> é a pergunta.
            self.prefixo = "### "
        elif tag == "li":
            self.prefixo = "- "
        elif tag == "a":
            self.href = a.get("href")
            self.texto_link = []
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("_")
        elif tag == "br":
            self._emit(" ")
        elif tag == "img":
            alt = a.get("alt", "").strip()
            if alt:
                self._emit("[imagem: %s] " % alt)

        if tag not in VAZIOS:
            self.pilha.append(tag)

    def handle_endtag(self, tag):
        if tag == "main":
            self._flush()
            self.no_main = False
            return
        if not self.no_main:
            return

        if tag in IGNORAR:
            if tag not in VAZIOS:
                self.mudo = max(0, self.mudo - 1)
            return
        if tag == "nav" and self.pilha and self.pilha[-1] == "nav-crumbs":
            self.pilha.pop()
            self.mudo = max(0, self.mudo - 1)
            return
        if self.mudo:
            return

        if tag == "a" and self.href:
            rotulo = re.sub(r"\s+", " ", "".join(self.texto_link)).strip()
            destino = self._abs(self.href)
            # Âncoras internas e telefones viram texto puro: link não ajuda quem lê.
            if rotulo and not destino.startswith(("#", "tel:")):
                self.buf.append("[%s](%s)" % (rotulo, destino))
            else:
                self.buf.append(rotulo)
            self.href = None
            self.texto_link = []
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("_")

        if tag in INLINE:
            self._emit(" ")

        if tag in BLOCOS:
            self._flush()

        if tag in self.pilha:
            for i in range(len(self.pilha) - 1, -1, -1):
                if self.pilha[i] == tag:
                    del self.pilha[i]
                    break

    def handle_data(self, dados):
        if not self.no_main or self.mudo:
            return
        if self.href is not None:
            self.texto_link.append(dados)
        else:
            self.buf.append(dados)


def markdown_da_pagina(caminho):
    html = io.open(os.path.join(RAIZ, caminho), encoding="utf-8").read()
    p = ParaMarkdown()
    p.feed(html)
    p._flush()

    linhas, anterior = [], None
    for ln in p.saida:
        ln = re.sub(r"\*\*\s*\*\*", "", ln).strip()
        ln = re.sub(r"\s+([,.;:!?])", r"\1", ln)
        if not ln or ln == anterior:
            continue
        # Um título vazio de conteúdo não agrega nada.
        if re.fullmatch(r"#{1,6}\s*", ln):
            continue
        linhas.append(ln)
        anterior = ln

    # Uma linha em branco entre blocos, duas antes de título.
    saida = []
    for ln in linhas:
        if saida:
            saida.append("" if not ln.startswith("#") else "")
        saida.append(ln)
    return "\n".join(saida)


# --------------------------------------------------------------------- llms.txt
CABECALHO = """# Cartão Hoje

> Cartão de crédito Visa internacional emitido pela HS Financeira S.A. (CNPJ
> 07.512.441/0001-11), a instituição financeira do Grupo Herval. É solicitado
> pelo aplicativo "Hoje — Cartão e HojePay", com resposta da análise de crédito
> em poucos minutos e sem necessidade de abrir conta em banco.

Ficha do produto:

- Bandeira: Visa, internacional (aceito no Brasil e no exterior)
- Mensalidade: R$ 12,90
- Prazo para pagar: até 40 dias
- Parcelamento: até 24x iguais
- Pagamento por aproximação: sim
- Cartão virtual pelo app: sim
- Conta em banco: não é necessária
- Idade mínima: 18 anos
- Renda mínima: 1 salário mínimo
- Documento exigido: RG emitido há até 10 anos, ou CNH válida (frente e verso).
  Comprovante de endereço e de renda são opcionais.
- Prazo da análise: poucos minutos, no próprio app
- Após uma recusa: nova solicitação em 90 dias
- Onde se pede: somente pelo aplicativo, para iPhone e Android

Atendimento:

- Central 24 horas: 3003 6680 (capitais) / 0800 400 6680 (demais localidades)
- Serviço de Atendimento ao Cliente: 4020 2202 / 0800 602 2202 —
  segunda a sexta 8h às 20h, sábado 8h às 18h
- WhatsApp: (51) 4042 1377 — segunda a sexta 8h às 20h, sábado 8h às 18h
- Ouvidoria: 0800 648 7070

Aviso: crédito sujeito a análise e aprovação. As condições completas e
definitivas estão no contrato e na tabela de tarifas, listados abaixo.

## Páginas
"""

DESCRICOES = {
    "/": "O cartão: benefícios, os três passos para pedir, lojas parceiras do Grupo Herval, custos e as dúvidas mais frequentes.",
    "/baixar-o-app/": "Download do aplicativo Hoje para iPhone (App Store) e Android (Google Play). É por ele que o cartão é solicitado e gerenciado.",
    "/hoje-pay/": "Hoje Pay, a carteira digital dentro do app: passo a passo para comprar aparelhos Apple na iPlace usando um cartão Bradesco, Banco do Brasil ou BTG Pactual.",
    "/perguntas-frequentes/": "23 perguntas e respostas sobre solicitação, documentos, análise de crédito, bandeira, mensalidade, desbloqueio, segunda via, fatura e contestação de compras.",
    "/fale-conosco/": "Todos os canais de atendimento com telefones, horários e formulário de contato.",
    "/trabalhe-conosco/": "Carreiras na HS Financeira. As vagas são publicadas no portal do Grupo Herval.",
    "/politica-de-privacidade/": "Como a HS Financeira trata dados pessoais e como exercer os direitos previstos na LGPD.",
}

DOCUMENTOS = [
    ("/assets/docs/clausulas-gerais-do-contrato.pdf", "Cláusulas gerais do contrato",
     "Regras de uso, encargos, limites e cancelamento."),
    ("/assets/docs/tarifas-cartao-hoje.pdf", "Tabela de tarifas",
     "Valor de cada tarifa e quando ela se aplica."),
    ("/assets/docs/proposta-de-adesao-ao-cartao.pdf", "Proposta de adesão",
     "Formulário assinado no pedido, com as características da operação."),
    ("/assets/docs/termos-de-uso-do-app.pdf", "Termos de uso do app",
     "Condições de uso do aplicativo Hoje."),
    ("/assets/docs/termo-de-adesao-hojepay-plus.pdf", "Termo de adesão do Hoje Pay PLUS",
     "Condições específicas da carteira digital."),
]


def escrever_llms():
    l = [CABECALHO]
    for url, _, nome in PAGINAS:
        l.append("- [%s](%s%s): %s" % (nome, SITE, url, DESCRICOES[url]))

    l.append("\n## Documentos oficiais (PDF)\n")
    for url, nome, desc in DOCUMENTOS:
        l.append("- [%s](%s%s): %s" % (nome, SITE, url, desc))

    l.append("\n## Opcional\n")
    l.append("- [Conteúdo integral do site em Markdown](%s/llms-full.txt): "
             "todas as páginas acima em um único arquivo." % SITE)
    l.append("- [Sitemap XML](%s/sitemap.xml): lista canônica de URLs." % SITE)

    texto = "\n".join(l) + "\n"
    io.open(os.path.join(RAIZ, "llms.txt"), "w", encoding="utf-8", newline="\n").write(texto)
    return texto


def escrever_llms_full():
    partes = [
        "# Cartão Hoje — conteúdo integral do site",
        "",
        "Todas as páginas de %s em Markdown, extraídas do HTML publicado." % SITE,
        "Gerado por tools/gerar-llms.py. Não edite este arquivo à mão.",
        "",
    ]
    for url, caminho, nome in PAGINAS:
        partes += ["", "=" * 78, "", "# %s" % nome, "", "URL: %s%s" % (SITE, url), "",
                   markdown_da_pagina(caminho), ""]
    texto = "\n".join(partes).rstrip() + "\n"
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    io.open(os.path.join(RAIZ, "llms-full.txt"), "w", encoding="utf-8", newline="\n").write(texto)
    return texto


if __name__ == "__main__":
    a = escrever_llms()
    b = escrever_llms_full()
    print("llms.txt       %6d bytes" % len(a.encode("utf-8")))
    print("llms-full.txt  %6d bytes" % len(b.encode("utf-8")))
