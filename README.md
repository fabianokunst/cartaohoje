# Cartão Hoje — protótipo do novo site

Protótipo estático da reformulação do site do Cartão Hoje. Sem WordPress, sem build,
sem dependências: HTML, CSS e ~60 linhas de JavaScript.

- **[PROPOSTA.md](PROPOSTA.md)** — diagnóstico do site atual, stack recomendada, direção
  de design e próximos passos.
- **[SEO.md](SEO.md)** — como o SEO e a legibilidade por LLMs estão montados, e o que
  ainda falta antes do go-live.

## Como abrir

O site usa URLs limpas (`/hoje-pay/`) e caminhos absolutos (`/assets/…`), então precisa
ser servido por HTTP. Abrir o `index.html` por duplo clique mostra a home, mas os links
e as imagens não resolvem.

```bash
python -m http.server 8000
# http://localhost:8000
```

## Páginas

| URL | Arquivo | Página |
|---|---|---|
| `/` | `index.html` | Home |
| `/perguntas-frequentes/` | `perguntas-frequentes/index.html` | FAQ completo, com marcação `FAQPage` |
| `/hoje-pay/` | `hoje-pay/index.html` | Hoje Pay, com marcação `HowTo` |
| `/fale-conosco/` | `fale-conosco/index.html` | Canais de atendimento + formulário |
| `/trabalhe-conosco/` | `trabalhe-conosco/index.html` | Carreiras |
| `/baixar-o-app/` | `baixar-o-app/index.html` | **Download do app** — escolha manual no desktop, redirecionamento automático no celular |
| `/404.html` | `404.html` | Página de erro, com os caminhos mais procurados |
| `/design-system/` | `design-system/index.html` | **Design system documentado** — marca, cor, tipografia, componentes (`noindex`) |

Cada página vive em seu próprio diretório como `index.html`. É o que faz a URL limpa
funcionar em qualquer host — Apache, nginx, Netlify, Vercel, S3 — sem uma única regra
de reescrita.

## Página de download

`/baixar-o-app/` resolve um endereço único para material impresso, QR em loja e
atendimento. No desktop mostra as duas lojas e o QR; no celular detecta a plataforma e
manda direto para a App Store ou o Google Play.

O conteúdo completo **sempre** está no HTML. O redirecionamento é só uma sobreposição
por cima, que some sozinha em 3,5 s se a loja não abrir. Detecção errada, JS desligado,
webview que engole o link — em todos os casos o usuário cai na página de escolha, nunca
em uma tela branca.

- **Para desligar o redirecionamento**, troque `REDIRECIONAR` para `false` no script do
  `<head>`. A página de escolha continua funcionando igual.
- **`?ver=tudo`** abre a página sem redirecionar — para QA e para compartilhar o link.
- Buscadores, geradores de preview e Lighthouse nunca são redirecionados.
- O QR (`assets/img/marca/qr-baixar-o-app.svg`) é estático, ECC nível Q, e foi conferido
  por decodificação até 164 px. Se a URL mudar, ele precisa ser gerado de novo.

## Estrutura

```
assets/css/hoje.css     Design system inteiro — tokens, componentes, responsivo
assets/js/hoje.js       Menu mobile, header sticky, reveal, acordeão
assets/img/foto/        Fotos (Unsplash) em WebP + fallback JPEG
assets/img/og/          Cards de Open Graph, 1200×630, um por página
assets/img/marca/       Arte de marca, favicons e ícones de app
assets/img/marca/logo/  Logos oficiais em SVG — 10 variantes + 3 símbolos isolados
deploy/                 Configuração por host: redirects, 404, charset, cache
tools/                  Scripts de manutenção (ver abaixo)
Guide e logo/           PDFs de origem: sistema de marca e arquivo de logos

robots.txt              Liberação explícita de buscadores e robôs de IA
sitemap.xml             URLs canônicas
llms.txt                Mapa do site para modelos de linguagem
llms-full.txt           Conteúdo integral do site em Markdown
site.webmanifest        Nome, cores e ícones para a tela inicial do celular
```

Os SVGs de `assets/img/marca/logo/` foram extraídos dos vetores originais do
`Guide e logo/Logos HojePay.pdf` — são as curvas do arquivo da agência, não um redesenho.

## Ferramentas

Nenhuma é obrigatória para o site rodar — ele continua sendo HTML estático. São
utilitários de manutenção, sem dependências além da biblioteca padrão:

```bash
python tools/checar-seo.py    # confere links, canonicals, sitemap, JSON-LD, OG
python tools/gerar-llms.py    # regenera llms.txt e llms-full.txt a partir do HTML
python tools/gerar-og.py      # regenera os cards de compartilhamento (requer Pillow)
```

**Rode os dois antes de publicar.** O `checar-seo.py` sai com código 1 se achar erro,
então serve como passo de CI.

## Editando

O CSS é organizado em 24 blocos numerados. As cores, espaçamentos, raios e sombras
estão todos em *custom properties* no bloco 1 (`:root`) — mudar a marca inteira é
mudar meia dúzia de valores ali.

Abra **[`design-system/`](design-system/index.html)** antes de mexer em qualquer coisa:
ele carrega o mesmo `hoje.css` e mostra cada token e componente renderizado, com as
regras de uso e a tabela de contraste verificada.

Header e rodapé são idênticos nas sete páginas. Como não há build, alterá-los exige
editar os sete arquivos — limitação consciente do protótipo, resolvida na migração
para Astro (ver PROPOSTA.md, seção 2.1).

Ao mexer no texto de uma página, rode `tools/gerar-llms.py` para que `llms-full.txt`
não fique defasado.

## Números

| | Site atual | Este protótipo |
|---|---|---|
| Peso da home | 1.074 KB | 337 KB |
| Requisições | 57 | 21 |
| Above the fold | ~880 KB | 68 KB |

## Pendências conhecidas

- Links dos documentos jurídicos apontam para os PDFs; confirmar se são as versões
  vigentes.
- Formulário do Fale Conosco não tem destino de envio.
- Fonte Gilroy substituída por Plus Jakarta Sans — falta licença web (ver `CREDITOS.md`).
  Enquanto vier do Google Fonts, é o maior custo de LCP do site (ver `SEO.md`).
- Faltam regras de co-branding com iPlace, taQi e voulevar.
- Ideal receber os arquivos mestres da agência para conferir a extração dos vetores.
- Fotos são placeholders do Unsplash. As imagens de aparelhos Apple em `/hoje-pay/`
  são material de imprensa da Apple — confirmar direito de uso antes de publicar.
- `_probe.html` e `chamado/` são artefatos internos: não devem subir para produção.
- Pendências de SEO e conteúdo: ver a última seção do [SEO.md](SEO.md).
