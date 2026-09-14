# Cartão Hoje — proposta de reformulação do site

**Versão:** protótipo inicial para discussão · setembro/2026
**Escopo desta entrega:** protótipo navegável de 5 páginas, fora do WordPress, com a identidade atual da marca.

---

## 1. Diagnóstico do site atual

Medições feitas em `https://cartaohoje.com.br/` (home, transferência já comprimida):

| Item | Hoje | Protótipo | Variação |
|---|---|---|---|
| Peso total da home | **1.074 KB** | **337 KB** | −69% |
| Requisições | **57** | **21** | −63% |
| CSS | 24 arquivos, 413 KB | 1 arquivo, 6 KB gzip | −98% |
| JavaScript | 16 arquivos, 347 KB | 1 arquivo, 1 KB gzip | −99% |
| HTML | 119 KB | 9 KB gzip | −92% |
| Above the fold | ~880 KB antes da 1ª imagem | **68 KB** | −92% |

Stack atual: WordPress + tema Hello Elementor + Elementor + Contact Form 7 + SVG Support.
O peso vem quase todo do construtor visual, não do conteúdo.

**Outros pontos observados**

- **Títulos genéricos.** `<title>Home - Cartão Hoje</title>` não disputa nenhuma busca. O mesmo vale para as internas.
- **Sem dados estruturados.** Nenhum JSON-LD. O FAQ existente — que é o melhor conteúdo do site — não está marcado como `FAQPage` e por isso não aparece como resultado rico no Google.
- **Conteúdo raso fora do FAQ.** A home tem poucas centenas de palavras e nenhuma página explica o produto em profundidade (prazos, tarifas, como funciona a análise).
- **Imagens não otimizadas.** PNGs onde caberia WebP/SVG; logo principal disponível apenas em 116 × 68 px.
- **Fonte da marca (Gilroy) carregada via CSS do tema**, sem `font-display` nem pré-carregamento.
- **Apenas 5 páginas indexáveis**, sem blog, sem páginas de comparação ou de intenção de busca.

Nada disso é culpa de má execução — é o custo natural de manter um site institucional dentro de um page builder.

---

## 2. O que estou propondo

### 2.1 Stack

**Site estático, sem WordPress.** O conteúdo do Cartão Hoje muda pouco (produto, tarifas, FAQ, canais de atendimento). Não há razão para pagar o custo de um CMS em cada visita.

- **Recomendado para produção: [Astro](https://astro.build).** Gera HTML estático puro, envia **zero JavaScript por padrão**, tem suporte nativo a otimização de imagem, sitemap e coleções de conteúdo (útil se um dia entrar um blog). Componentização real — header e footer em um único lugar.
- **Hospedagem:** Cloudflare Pages, Vercel ou Netlify. Deploy por Git, HTTPS e CDN global inclusos, custo próximo de zero.
- **Este protótipo** foi escrito em **HTML + CSS + ~60 linhas de JS**, sem build, justamente para vocês abrirem e avaliarem sem instalar nada. A migração para Astro é mecânica: o CSS e o HTML vêm inteiros.

**Por que não Next.js/React:** um site institucional de 5–10 páginas não precisa de runtime de framework. Seria mais peso, mais build e mais superfície de manutenção para o mesmo resultado.

### 2.2 Como o conteúdo seria editado

Três caminhos possíveis, em ordem de esforço:

1. **Markdown no repositório** — o time de marketing edita pelo GitHub (interface web), o site reconstrói sozinho. Custo zero.
2. **CMS headless com painel visual** — Decap CMS (grátis, roda junto com o site) ou Sanity/Contentful. Painel parecido com o WordPress, sem o peso dele no site.
3. **Manter WordPress só como back-office** (headless), consumindo a API REST no build.

Minha recomendação para o volume de conteúdo de vocês: **opção 1 ou 2**.

---

## 3. Direção de design

Mantive integralmente a identidade atual — a mudança é de **execução**, não de marca.

### Paleta (extraída do site atual)

| Token | Valor | Uso |
|---|---|---|
| Coral da marca | `#EB9C6B` | logo, detalhes, ícones, CTA sobre fundo escuro |
| Coral escurecido | `#B5652C` | coral em texto sobre fundo claro (contraste AA) |
| Charcoal | `#2F2D2A` | seções escuras, rodapé, botão primário |
| Creme | `#FAF7F1` / `#F2EBE1` | fundo das páginas e seções alternadas |
| Verde | `#2E9E5B` | apenas WhatsApp |

O creme veio do próprio cartão físico. O site atual usa branco puro em quase tudo e reserva o creme para nada — trocar a base por creme já muda a temperatura da página inteira.

### Tipografia

A marca usa **Gilroy** (Radomir Tinkov), que é licenciada. O protótipo usa **Plus Jakarta Sans** (Google Fonts, gratuita) como substituta — mesma família geométrica, proporções muito próximas.
Em produção: self-host da Gilroy licenciada, em WOFF2, com `font-display: swap` e preload.

### Princípios aplicados

- **Respiro.** Seções com 72–132 px de espaçamento vertical, títulos grandes, largura de leitura limitada a ~56 caracteres.
- **Alternância clara/escura.** Creme → creme escurecido → charcoal cria ritmo e destaca o app e os parceiros.
- **Motivo dos arcos.** As curvas finas do cartão físico viram elemento gráfico do site (hero e faixas de CTA).
- **Cartão em SVG**, não em foto: nítido em qualquer tela, ~2 KB, e sempre atualizado com a arte real.
- **Sombras quentes e discretas** em vez de sombras cinzas — mantém o tom premium.

### Acessibilidade

- Contraste AA em todo texto (o coral puro nunca é usado como texto sobre creme).
- Navegação completa por teclado, `:focus-visible` visível, *skip link*.
- FAQ em `<details>/<summary>` nativo — funciona sem JavaScript e é lido por leitores de tela.
- `prefers-reduced-motion` respeitado: animações desligam.
- Todas as imagens com `alt` descritivo e `width`/`height` (sem *layout shift*).

---

## 4. Plano de SEO

### 4.1 Base técnica (já no protótipo)

- `<title>` e `<meta description>` únicos e orientados a busca em cada página.
- `canonical`, Open Graph e Twitter Card.
- **JSON-LD**: `Organization`, `WebSite`, `CreditCard` (produto financeiro), `FAQPage`, `HowTo` (Hoje Pay), `ContactPage`, `BreadcrumbList`.
- `sitemap.xml` e `robots.txt`.
- Hierarquia de headings correta, um `<h1>` por página.
- WebP com fallback JPEG, `loading="lazy"` abaixo da dobra, `fetchpriority="high"` na imagem do hero.
- HTML semântico: `<main>`, `<nav aria-label>`, `<article>`, trilha de navegação.

O ganho mais imediato é o **`FAQPage` na página de perguntas frequentes**: 23 perguntas marcadas, elegíveis a resultado rico.

### 4.2 Conteúdo — onde está a oportunidade real

O site hoje disputa basicamente a busca pela própria marca. As buscas que trazem cliente novo são outras:

| Intenção | Página a criar |
|---|---|
| "cartão de crédito sem conta em banco" | Página de produto aprofundada |
| "cartão de crédito para negativado / com renda baixa" | Página de elegibilidade, honesta sobre a análise |
| "cartão de crédito anuidade barata" | Página de tarifas e custos |
| "como pedir cartão de crédito pelo celular" | Guia passo a passo |
| "cartão taQi / cartão volis / cartão iPlace" | Uma página por parceiro |
| Dúvidas de uso ("como desbloquear", "segunda via fatura") | Já cobertas pelo FAQ — falta marcação e páginas individuais |

Sugestão: **uma página por dúvida de alto volume**, além do FAQ agregado. Cada uma vira porta de entrada.

### 4.3 Métricas-alvo

- Lighthouse ≥ 95 em Performance, Acessibilidade, Boas Práticas e SEO.
- LCP < 1,2 s em 4G; CLS 0; INP < 200 ms.
- Google Search Console e um analytics leve (Plausible ou GA4) configurados desde o primeiro dia.

---

## 5. Arquitetura de informação proposta

```
/                        Home
/cartao-hoje/            O cartão: benefícios, limites, como funciona   [nova]
/como-pedir/             Passo a passo + elegibilidade                  [nova]
/tarifas/                Custos, mensalidade, contratos                 [nova]
/parceiros/              taQi · volis · iPlace · voulevar               [nova]
  /parceiros/taqi/       …uma por parceiro                             [nova]
/hoje-pay/               Carteira digital
/app/                    Página do aplicativo                           [nova]
/perguntas-frequentes/   FAQ completo (FAQPage)
/fale-conosco/           Canais + formulário
/trabalhe-conosco/       Carreiras
/juridico/…              Contrato, tarifas, termos, privacidade
```

Redirecionamentos 301 do que existe hoje (`/hojepay/` → `/hoje-pay/` etc.) entram junto com o go-live.

---

## 6. O que está neste protótipo

| Página | Estado |
|---|---|
| `index.html` | Completa — hero, benefícios, como pedir, parceiros, Hoje Pay, app, transparência, FAQ, atendimento, Grupo Herval |
| `perguntas-frequentes.html` | Completa — 23 perguntas do site atual, agrupadas, com `FAQPage` |
| `hoje-pay.html` | Completa — passo a passo em 6 etapas com `HowTo` |
| `fale-conosco.html` | Completa — 4 canais + formulário (sem back-end) |
| `trabalhe-conosco.html` | Estrutura pronta, conteúdo a definir com o RH |

**Como abrir:** dê duplo clique em `index.html`. Não precisa de servidor nem de instalação.

### Conteúdo

Todo o texto veio do site atual, reescrito para ficar mais direto. Nada foi inventado: telefones, horários, valor da mensalidade (R$ 12,90), regras de elegibilidade e o passo a passo do Hoje Pay são os que estão publicados hoje. O conteúdo do Hoje Pay já incorpora a revisão pedida em `atividades/site_cartao_hoje.docx` (bancos elegíveis Bradesco, Banco do Brasil e BTG Pactual; novos textos de hero, passos 4 a 6 e CTA; correção da etapa pós-compra).

### Imagens

Fotos gratuitas do Unsplash, como combinado — ver `CREDITOS.md`. São **placeholders**: a versão final deveria usar banco de imagens próprio ou produção fotográfica, com pessoas que representem o público do cartão.
Os logos (hoje, taQi, volis, iPlace, voulevar, Grupo Herval, HS Financeira) e a imagem do cartão + app são os oficiais, extraídos do site atual.

---

## 7. Pontos a decidir com vocês

1. **Fonte Gilroy** — vocês têm a licença web? Se sim, preciso dos arquivos WOFF2.
2. **Logo em vetor** — o único arquivo disponível é um PNG de 116 px. Vetorizei para o protótipo, mas o SVG original da marca dará um resultado melhor.
3. **Onde o app é baixado** — os links das lojas estão como `#`. Preciso das URLs reais (e das IDs, se formos medir conversão).
4. **Documentos jurídicos** — contrato, tarifas e termos de uso: PDFs atuais ou páginas HTML? Páginas HTML indexam melhor.
5. **Formulário do Fale Conosco** — para onde envia? (e-mail, CRM, HubSpot?)
6. **Fotografia** — seguimos com banco de imagens ou vale produzir um ensaio próprio?
7. **CMS** — qual das três opções da seção 2.2?
8. **Analytics e pixels** — quais ferramentas precisam continuar?

---

## 8. Próximos passos sugeridos

| Fase | Entrega | Prazo estimado |
|---|---|---|
| 1 | Revisão deste protótipo e decisões da seção 7 | — |
| 2 | Migração para Astro + componentização + CMS | 1 semana |
| 3 | Páginas novas de SEO (seção 4.2) | 1–2 semanas |
| 4 | Formulário, analytics, integrações | 3 dias |
| 5 | QA (dispositivos, acessibilidade, Lighthouse), redirects 301 | 3 dias |
| 6 | Go-live + monitoramento no Search Console | 1 dia |

Os prazos são estimativas para conversa, não compromisso — dependem do volume de conteúdo novo e das aprovações.

---

## 9. Estrutura de arquivos

```
Cartao-Hoje/
├── index.html                     Home
├── perguntas-frequentes.html      FAQ (FAQPage)
├── hoje-pay.html                  Hoje Pay (HowTo)
├── fale-conosco.html              Atendimento + formulário
├── trabalhe-conosco.html          Carreiras
├── robots.txt
├── sitemap.xml
├── assets/
│   ├── css/hoje.css               Design system completo (21 KB)
│   ├── js/hoje.js                 Menu, header, reveal, acordeão (3 KB)
│   └── img/
│       ├── foto/                  Fotos Unsplash em WebP + JPEG
│       └── marca/                 Logos e arte oficiais
├── PROPOSTA.md                    Este documento
└── CREDITOS.md                    Créditos das fotos
```
