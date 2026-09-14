# -*- coding: utf-8 -*-
"""
Gera os cards de Open Graph (1200x630) — a imagem que aparece quando alguem
compartilha uma pagina no WhatsApp, no LinkedIn ou no X.

Por que 1200x630
----------------
E a proporcao que todas as redes recortam sem cortar nada. Uma imagem vertical
(era o caso: og:image apontava para hero.jpg, 900x1125) e cortada no meio ou
rebaixada a miniatura — o link chega torto em todo lugar.

Layout: foto a direita esmaecendo no creme, marca e texto a esquerda, faixa
coral no rodape. As cores saem dos tokens do hoje.css.

Como rodar
----------
    python tools/gerar-og.py

Requer Pillow (pip install pillow). Rode quando o texto de um card mudar, ou
quando entrar pagina nova — e entao acrescente a chamada card() no final.

A fonte usada aqui e a Segoe UI do sistema, nao a Plus Jakarta Sans do site:
a fonte da marca nao esta instalada localmente. Trocar e mudar as duas linhas
de ImageFont.truetype abaixo.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, "assets", "img", "og")
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630
CREAM   = (247, 245, 242)
INK     = (47, 45, 42)
CORAL   = (225, 146, 107)
CORALINK= (167, 93, 57)
MUTED   = (95, 91, 85)

F = r"C:\Windows\Fonts"
bold = lambda s: ImageFont.truetype(os.path.join(F, "segoeuib.ttf"), s)
reg  = lambda s: ImageFont.truetype(os.path.join(F, "segoeui.ttf"), s)

PAD, COL = 76, 700          # respiro e largura da coluna de texto


def cover(path, box):
    """Recorta a foto preenchendo a caixa, sem distorcer."""
    im = Image.open(path).convert("RGB")
    bw, bh = box
    r = max(bw / im.width, bh / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, t = (im.width - bw) // 2, (im.height - bh) // 2
    return im.crop((l, t, l + bw, t + bh))


def tracked(d, xy, text, font, fill, track):
    """PIL nao tem entrelinhamento: desenha caractere a caractere."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track
    return x


def wrap(d, text, font, width):
    linhas, atual = [], ""
    for p in text.split():
        teste = (atual + " " + p).strip()
        if d.textlength(teste, font=font) <= width:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def card(nome, eyebrow, titulo, foto=None, sub="cartaohoje.com.br"):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    if foto:
        pw = W - COL + 120                       # a foto invade um pouco a coluna
        img.paste(cover(foto, (pw, H)), (W - pw, 0))
        # degrade do creme por cima da borda esquerda da foto, para o texto respirar
        grad = Image.new("L", (300, 1))
        for i in range(300):
            grad.putpixel((i, 0), int(255 * (1 - i / 300) ** 1.5))
        mask = grad.resize((300, H))
        img.paste(Image.new("RGB", (300, H), CREAM), (W - pw, 0), mask)

    # marca
    logo = Image.open(os.path.join(BASE, "assets", "img", "marca", "logo-hoje.png")).convert("RGBA")
    lh = 58
    logo = logo.resize((round(logo.width * lh / logo.height), lh), Image.LANCZOS)
    img.paste(logo, (PAD, PAD), logo)

    largura = COL - PAD - 40

    # titulo: diminui ate caber em 3 linhas
    for size in (62, 56, 50, 45, 40, 36):
        ft = bold(size)
        linhas = wrap(d, titulo, ft, largura)
        if len(linhas) <= 3:
            break
    lead = round(size * 1.14)
    alturaT = lead * len(linhas)

    fe = bold(21)
    y = (H - alturaT) // 2 + 12
    tracked(d, (PAD, y - 54), eyebrow.upper(), fe, CORALINK, 2.2)
    for ln in linhas:
        d.text((PAD, y), ln, font=ft, fill=INK)
        y += lead

    d.rectangle([PAD, y + 26, PAD + 64, y + 31], fill=CORAL)
    d.text((PAD, y + 52), sub, font=reg(22), fill=MUTED)
    d.rectangle([0, H - 9, W, H], fill=CORAL)

    p = os.path.join(OUT, nome)
    img.save(p, "JPEG", quality=88, optimize=True, progressive=True)
    print(nome, os.path.getsize(p) // 1024, "KB")


FOTO = os.path.join(BASE, "assets", "img", "foto")
card("home.jpg", "Cartão de crédito Visa internacional", "O amanhã começa hoje",
     os.path.join(FOTO, "hero.jpg"))
card("perguntas-frequentes.jpg", "Ajuda", "Perguntas frequentes sobre o Cartão Hoje",
     os.path.join(FOTO, "aproximacao.jpg"))
card("fale-conosco.jpg", "Atendimento", "Fale com a gente",
     os.path.join(FOTO, "bem-estar.jpg"))
card("trabalhe-conosco.jpg", "Carreiras", "Trabalhe conosco na HS Financeira",
     os.path.join(FOTO, "herval.jpg"))
card("baixar-o-app.jpg", "Aplicativo", "Baixe o app do Cartão Hoje",
     os.path.join(FOTO, "hero.jpg"))
card("politica-de-privacidade.jpg", "Documento", "Política de Privacidade")
card("hoje-pay.jpg", "Carteira digital", "Hoje Pay: sua compra na iPlace",
     os.path.join(FOTO, "hoje-pay.jpg"))
