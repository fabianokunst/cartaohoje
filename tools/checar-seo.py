# -*- coding: utf-8 -*-
"""
Confere o SEO técnico de todas as páginas antes de publicar.

Por que existe
--------------
O erro mais caro de SEO é silencioso: um `canonical` apontando para uma URL
que não existe, um link que não chega a arquivo nenhum, uma página indexável
fora do sitemap. Nada disso aparece ao abrir o site no navegador — só aparece
semanas depois, no Search Console.

Este script falha em vez de deixar passar.

Links e assets
--------------
Os caminhos são relativos à própria página (`../assets/…`,
`../hoje-pay/index.html`): é o que deixa o site abrir direto da pasta no
Windows e no GitHub Pages, que o serve dentro de /cartaohoje/. Cada
href/src/srcset é resolvido a partir do arquivo da página e precisa chegar a
um arquivo com o mesmo nome, letra por letra — o Windows abre `Foto.JPG`
quando o arquivo é `foto.jpg`; publicado, dá 404.

Como rodar
----------
    python tools/checar-seo.py

Sai com código 1 se houver erro, para poder virar passo de CI. Sem
dependências além do Pillow, usado só para conferir o tamanho das imagens de
Open Graph (se não estiver instalado, essa checagem é pulada).
"""
import glob
import io
import json
import os
import posixpath
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://cartaohoje.com.br"

LIMITE_TITLE = 62        # acima disso o Google corta com reticências
LIMITE_DESC = 160

# Atributos que carregam o caminho de um arquivo. Os de srcset trazem uma
# lista ("a.webp 1x, b.webp 2x"); os outros, um caminho só.
ATRIB_URL = {"href", "src", "poster", "xlink:href"}
ATRIB_SRCSET = {"srcset", "imagesrcset"}

# Um candidato do srcset: a URL e, depois dela, vírgula ou descritores ("1x",
# "400w") até a próxima vírgula. Como no navegador, só a vírgula depois da URL
# separa candidatos — um data:…;base64,… não é cortado no meio.
CANDIDATO_SRCSET = re.compile(r"([^\s,]\S*?)(?:,+(?=\s|$)|(?=\s|$)[^,]*)")

erros, avisos = [], []


class Links(HTMLParser):
    """Junta (linha, atributo, URL) de cada href/src/srcset da página.
    Parser, e não regex, para não pegar URL de comentário nem de <script>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.achados = []

    def handle_starttag(self, tag, attrs):
        linha = self.getpos()[0]
        for nome, valor in attrs:
            if not valor:
                continue
            if nome in ATRIB_SRCSET:
                urls = CANDIDATO_SRCSET.findall(valor)
            elif nome in ATRIB_URL:
                urls = [valor.strip()]
            else:
                continue
            self.achados += [(linha, nome, u) for u in urls]


def em_disco(url):
    """Mapeia o caminho de uma URL pública do site ("/hoje-pay/") para o
    arquivo que a serviria, relativo à raiz."""
    p = unquote(url.split("#")[0].split("?")[0])
    if not p.startswith("/"):
        return None
    p = p.lstrip("/")
    if p == "" or p.endswith("/"):
        p += "index.html"
    return posixpath.normpath(p)


_pastas = {}


def no_disco(caminho):
    """O caminho (relativo à raiz, com /) com a caixa de letras que ele tem no
    disco — ou None, se não existe."""
    pasta, real = RAIZ, []
    for parte in caminho.split("/"):
        if pasta not in _pastas:
            _pastas[pasta] = os.listdir(pasta) if os.path.isdir(pasta) else []
        if parte not in _pastas[pasta]:
            outra_caixa = [n for n in _pastas[pasta] if n.lower() == parte.lower()]
            if not outra_caixa:
                return None
            parte = outra_caixa[0]
        real.append(parte)
        pasta = os.path.join(pasta, parte)
    return "/".join(real)


def falta(caminho):
    """Por que o arquivo não seria servido — ou None, se seria. O Windows não
    diferencia maiúsculas de minúsculas; o GitHub Pages e os hosts de
    deploy/, sim."""
    real = no_disco(caminho)
    if real is None:
        return "%s não existe" % caminho
    if real != caminho:
        return ("%s só existe como %s (no Windows abre; publicado, dá 404)"
                % (caminho, real))
    return None


def tamanho_imagem(caminho):
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        return Image.open(caminho).size
    except Exception:
        return None


def main():
    # Com a saída redirecionada, o Python no Windows escreve em cp1252: um
    # caractere fora dela (num título, numa URL) derrubaria o relatório no
    # meio. Melhor sair como "?".
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    os.chdir(RAIZ)
    paginas = ["index.html", "404.html"] + sorted(
        p.replace("\\", "/") for p in glob.glob("*/index.html"))

    sitemap = io.open("sitemap.xml", encoding="utf-8").read()
    no_sitemap = set(re.findall(r"<loc>([^<]+)</loc>", sitemap))

    for u in sorted(no_sitemap):
        alvo = em_disco(u.replace(SITE, ""))
        motivo = alvo and falta(alvo)
        if motivo:
            erros.append("sitemap.xml: %s — %s" % (u, motivo))

    n_links = 0
    for pag in paginas:
        html = io.open(pag, encoding="utf-8").read()

        # --- links e assets internos chegam a um arquivo que existe -------
        # Relativos à pasta da própria página. A 404 mora na raiz, como a
        # home: o "hoje-pay/index.html" dela vale a partir da raiz.
        links = Links()
        links.feed(html)
        links.close()
        pasta = posixpath.dirname(pag)
        for linha, attr, url in links.achados:
            onde = '%s:%d: %s="%s"' % (pag, linha, attr, url)
            if re.match(r"(?i)file:|[a-z]:[\\/]", url):
                erros.append("%s — aponta para o disco deste computador" % onde)
                continue
            if url.startswith("//") or re.match(r"(?i)[a-z][a-z0-9+.-]*:", url):
                continue                    # http(s):, mailto:, tel:, data:…
            caminho = unquote(url.split("#")[0].split("?")[0])
            if not caminho:
                continue                    # "#âncora", "?ver=tudo": a própria página
            n_links += 1
            if caminho.startswith("/"):
                erros.append("%s — caminho absoluto: quebra no GitHub Pages "
                             "(/cartaohoje/) e aberto direto do Windows; "
                             "use relativo" % onde)
                continue
            alvo = posixpath.normpath(posixpath.join(pasta, caminho))
            if alvo == ".." or alvo.startswith("../"):
                erros.append("%s — sai da raiz do site" % onde)
            elif os.path.isdir(alvo):
                erros.append("%s — aponta para uma pasta: aberto direto do "
                             "Windows, não abre a página (use …/index.html)" % onde)
            else:
                motivo = falta(alvo)
                if motivo:
                    erros.append("%s — %s" % (onde, motivo))

        # A 404 e as páginas noindex não precisam de canonical, OG ou sitemap.
        if pag == "404.html" or "noindex" in html:
            continue

        esperado = SITE + "/" + ("" if pag == "index.html"
                                 else os.path.dirname(pag) + "/")

        # --- canonical aponta para a própria página -----------------------
        can = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        if not can:
            erros.append("%s: sem canonical" % pag)
        elif can.group(1) != esperado:
            erros.append("%s: canonical %s, esperado %s" % (pag, can.group(1), esperado))

        # --- página indexável precisa estar no sitemap --------------------
        if esperado not in no_sitemap:
            erros.append("%s: indexável mas fora do sitemap.xml" % pag)

        # --- og:image existe e tem a proporção que as redes esperam -------
        og = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if not og:
            erros.append("%s: sem og:image" % pag)
        else:
            rel = og.group(1).replace(SITE + "/", "")
            motivo = falta(rel)
            if motivo:
                erros.append("%s: og:image %s" % (pag, motivo))
            else:
                tam = tamanho_imagem(rel)
                if tam and tam != (1200, 630):
                    erros.append("%s: og:image %dx%d, esperado 1200x630 — "
                                 "fora disso o preview é cortado" % (pag, tam[0], tam[1]))

        # --- exatamente um <h1> -------------------------------------------
        n = len(re.findall(r"<h1[\s>]", html))
        if n != 1:
            erros.append("%s: %d <h1>, esperado 1" % (pag, n))

        # --- title e description dentro do que o Google mostra ------------
        t = re.search(r"<title>(.*?)</title>", html, re.S)
        d = re.search(r'<meta name="description" content="([^"]*)"', html)
        if not t:
            erros.append("%s: sem <title>" % pag)
        elif len(t.group(1)) > LIMITE_TITLE:
            avisos.append("%s: title com %d caracteres (>%d corta): %s"
                          % (pag, len(t.group(1)), LIMITE_TITLE, t.group(1)))
        if not d:
            erros.append("%s: sem meta description" % pag)
        elif len(d.group(1)) > LIMITE_DESC:
            avisos.append("%s: description com %d caracteres (>%d corta)"
                          % (pag, len(d.group(1)), LIMITE_DESC))

        # --- JSON-LD é válido e não aponta para URL inexistente -----------
        blocos = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                            html, re.S)
        if not blocos:
            erros.append("%s: sem JSON-LD" % pag)
        for bloco in blocos:
            try:
                dados = json.loads(bloco)
            except Exception as e:
                erros.append("%s: JSON-LD inválido: %s" % (pag, e))
                continue
            # ensure_ascii=False: com o padrão, "ç" vira ç e a URL não
            # bate com o nome do arquivo.
            for u in re.findall(r'"(%s/[^"#]*)"' % re.escape(SITE),
                                json.dumps(dados, ensure_ascii=False)):
                alvo = em_disco(u.replace(SITE, ""))
                motivo = alvo and falta(alvo)
                if motivo:
                    erros.append("%s: JSON-LD aponta para %s — %s" % (pag, u, motivo))

    # --- arquivos de raiz que o site inteiro depende ----------------------
    for f in ["robots.txt", "sitemap.xml", "llms.txt", "llms-full.txt",
              "404.html", "site.webmanifest"]:
        if not os.path.exists(f):
            erros.append("falta o arquivo de raiz: %s" % f)

    largura = 74
    print("=" * largura)
    for e in erros:
        print("ERRO   " + e)
    for a in avisos:
        print("AVISO  " + a)
    print("=" * largura)
    print("%d erro(s), %d aviso(s) — %d páginas e %d links internos conferidos"
          % (len(erros), len(avisos), len(paginas), n_links))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
