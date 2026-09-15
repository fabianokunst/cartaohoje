# -*- coding: utf-8 -*-
"""
Confere o SEO técnico de todas as páginas antes de publicar.

Por que existe
--------------
O erro mais caro de SEO é silencioso: um `canonical` apontando para uma URL
que não existe, um asset relativo que quebra dentro de subdiretório, uma
página indexável fora do sitemap. Nada disso aparece ao abrir o site no
navegador — só aparece semanas depois, no Search Console.

Este script falha em vez de deixar passar.

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
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://cartaohoje.com.br"

LIMITE_TITLE = 62        # acima disso o Google corta com reticências
LIMITE_DESC = 160

erros, avisos = [], []


def em_disco(url):
    """Mapeia uma URL do site para o arquivo que a serviria."""
    p = url.split("#")[0].split("?")[0]
    if not p.startswith("/"):
        return None
    p = p.lstrip("/")
    if p == "" or p.endswith("/"):
        return os.path.join(p, "index.html")
    return p


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
    os.chdir(RAIZ)
    paginas = ["index.html", "404.html"] + sorted(
        p.replace("\\", "/") for p in glob.glob("*/index.html"))

    sitemap = io.open("sitemap.xml", encoding="utf-8").read()
    no_sitemap = set(re.findall(r"<loc>([^<]+)</loc>", sitemap))

    for u in no_sitemap:
        alvo = em_disco(u.replace(SITE, ""))
        if alvo and not os.path.exists(alvo):
            erros.append("sitemap.xml: %s não existe em disco" % u)

    for pag in paginas:
        html = io.open(pag, encoding="utf-8").read()

        # --- links e assets internos apontam para arquivo que existe ------
        for attr, url in re.findall(r'(href|src)="(/[^"]*)"', html):
            alvo = em_disco(url)
            if alvo and not os.path.exists(alvo):
                erros.append('%s: %s="%s" → %s não existe' % (pag, attr, url, alvo))

        # --- nenhum link interno pode carregar .html ----------------------
        for m in re.findall(r'href="((?!http)[^"]*\.html[^"]*)"', html):
            erros.append("%s: link interno com .html: %s" % (pag, m))

        # --- asset relativo quebra quando a página vive em subdiretório ---
        for m in re.findall(r'(?:href|src|srcset)="(assets/[^"]*)"', html):
            erros.append("%s: asset relativo (use /assets/…): %s" % (pag, m))

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
            if not os.path.exists(rel):
                erros.append("%s: og:image não existe: %s" % (pag, rel))
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
            for u in re.findall(r'"(%s/[^"#]*)"' % re.escape(SITE), json.dumps(dados)):
                alvo = em_disco(u.replace(SITE, ""))
                if alvo and not os.path.exists(alvo):
                    erros.append("%s: JSON-LD aponta para %s (não existe)" % (pag, u))

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
    print("%d erro(s), %d aviso(s) — %d páginas conferidas"
          % (len(erros), len(avisos), len(paginas)))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
