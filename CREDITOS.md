# Créditos das imagens

## Fotografias — Unsplash

Todas sob a [Unsplash License](https://unsplash.com/license): uso gratuito, comercial inclusive,
sem necessidade de atribuição (creditamos por cortesia).

| Arquivo | Fotógrafo | Origem |
|---|---|---|
| `foto/hero.*` | Nolan Manning | https://unsplash.com/photos/Ll9YOG20UFI |
| `foto/aproximacao.*` | Towfiqu barbhuiya | https://unsplash.com/photos/HNPrWOH2Z8U |
| `foto/casa.*` | Pipcke | https://unsplash.com/photos/SZ-DsEZxzlg |
| `foto/bem-estar.*` | Susan Wilkinson | https://unsplash.com/photos/gSOdp7YlgNQ |
| `foto/iphone.*` | Dennis Brendel | https://unsplash.com/photos/YLNMXzXk8zs |
| `foto/herval.*` | Abstral Official | https://unsplash.com/photos/Jf8jKl6WNIg |
| `foto/hoje-pay.*` | Jakub Żerdzicki | https://unsplash.com/photos/08TJqR3mSrE |

Todas foram recortadas e convertidas para WebP (qualidade 76) com fallback JPEG progressivo.

> **Atenção:** são placeholders para o protótipo. Antes do go-live, avaliar substituição por
> banco de imagens licenciado ou produção fotográfica própria, com pessoas que representem
> o público do Cartão Hoje.

## Imagem de produto

| Arquivo | O que é |
|---|---|
| `foto/iphone-17.png`, `foto/iphone-17.webp` | Foto de produto do iPhone 17 (prata, laranja e azul), PNG com fundo transparente, fornecida pelo cliente. Usada no hero da página Hoje Pay e na seção Hoje Pay da home. O WebP (63 KB) é a versão servida; o PNG (209 KB) é fallback e está quantizado em 256 cores, com leve granulação nos degradês. **Imagem de produto Apple — confirmar o direito de uso com a Apple/iPlace antes da publicação.** |

## Imagem de produto

| Arquivo | O que é |
|---|---|
| `foto/iphone-17.png`, `.webp` | Render oficial do iPhone 17 (PNG com transparência), fornecido pelo cliente. Base da página Hoje Pay — hero e seção do Hoje Pay na home. **Imagem de produto da Apple: confirmar com jurídico/marca o direito de uso antes da publicação.** |
| `foto/hoje-pay-og.jpg` | Derivada da anterior, composta sobre o creme da marca em 1200 × 630 para `og:image` (redes sociais não respeitam transparência). |

> A arte de origem já vem **cortada na base** — só o aparelho prata mostra a curva inferior. Por isso ela é
> posicionada encostando na borda da seção (`.prod-art--bleed`), e não flutuando com sombra.

## Captura de tela

| Arquivo | O que é |
|---|---|
| `foto/hojepay-formas-de-compra.png` | Print da tela \“Formas de compra\” do site da iPlace, fornecido no documento `atividades/site_cartao_hoje.docx`. Usado no passo 6 da página Hoje Pay. **É um print de baixa resolução com valores de exemplo — substituir por arte produzida antes do go-live.** |

## Ativos de marca

Extraídos do site atual (`cartaohoje.com.br`) e de propriedade do Grupo Herval / HS Financeira:

| Arquivo | O que é |
|---|---|
| `marca/logo-hoje.png` | Logo original (116 × 68 px) |
| `marca/logo-hoje.svg` | Vetorização feita a partir do PNG para este protótipo — **substituir pelo SVG oficial** |
| `marca/app-cartao.webp` | Arte do cartão + app |
| `marca/taqi.png`, `voulevar.png`, `iplace.png`, `volis.png` | Logos dos parceiros (versões brancas, para fundo escuro) |
| `marca/grupo-herval.png`, `hs-financeira.png` | Logos institucionais |
| `marca/appstore.png`, `googleplay.png` | Selos das lojas de aplicativo |
| `bancos/bradesco.svg`, `bancodobrasil.svg`, `btg.svg` | Logos dos bancos elegíveis do Hoje Pay, nas cores oficiais. Fornecidos pelo cliente. Usados na seção "Cartões aceitos" da página Hoje Pay — conferir com jurídico/marca as regras de uso de cada marca antes da publicação. |

A arte do cartão no hero da home é um **SVG desenhado do zero** (`index.html`), reproduzindo o
cartão físico. Deve ser conferida com o time de marca antes da publicação.

## Tipografia

- **Protótipo:** [Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans) — SIL Open Font License, gratuita.
- **Produção:** Gilroy (Radomir Tinkov), fonte da marca — requer licença web e self-host.
