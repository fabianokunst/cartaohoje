# Cartão Hoje — protótipo do novo site

Protótipo estático da reformulação do site do Cartão Hoje. Sem WordPress, sem build,
sem dependências: HTML, CSS e ~60 linhas de JavaScript.

**Leia a [PROPOSTA.md](PROPOSTA.md)** — diagnóstico do site atual, stack recomendada,
direção de design, plano de SEO e próximos passos.

## Como abrir

Duplo clique em `index.html`. É isso.

Para servir por HTTP (recomendado se quiser testar caminhos absolutos):

```bash
python -m http.server 8000
# http://localhost:8000
```

## Páginas

| Arquivo | Página |
|---|---|
| `index.html` | Home |
| `perguntas-frequentes.html` | FAQ completo, com marcação `FAQPage` |
| `hoje-pay.html` | Hoje Pay, com marcação `HowTo` |
| `fale-conosco.html` | Canais de atendimento + formulário |
| `trabalhe-conosco.html` | Carreiras |

## Estrutura

```
assets/css/hoje.css     Design system inteiro — tokens, componentes, responsivo
assets/js/hoje.js       Menu mobile, header sticky, reveal, acordeão
assets/img/foto/        Fotos (Unsplash) em WebP + fallback JPEG
assets/img/marca/       Logos e arte oficiais da marca
```

## Editando

O CSS é organizado em 21 blocos numerados. As cores, espaçamentos, raios e sombras
estão todos em *custom properties* no bloco 1 (`:root`) — mudar a marca inteira é
mudar meia dúzia de valores ali.

Header e rodapé são idênticos nas cinco páginas. Como não há build, alterá-los exige
editar os cinco arquivos — limitação consciente do protótipo, resolvida na migração
para Astro (ver PROPOSTA.md, seção 2.1).

## Números

| | Site atual | Este protótipo |
|---|---|---|
| Peso da home | 1.074 KB | 337 KB |
| Requisições | 57 | 21 |
| Above the fold | ~880 KB | 68 KB |

## Pendências conhecidas

- Links das lojas de aplicativo e dos documentos jurídicos estão como `#`.
- Formulário do Fale Conosco não tem destino de envio.
- Logo `hoje` em SVG é uma vetorização do PNG — trocar pelo vetor oficial.
- Fonte Gilroy substituída por Plus Jakarta Sans (ver `CREDITOS.md`).
- Fotos são placeholders do Unsplash.
