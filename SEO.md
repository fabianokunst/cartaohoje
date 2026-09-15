# SEO e legibilidade por LLMs

Como o site está montado para ser encontrado — por buscador e por modelo de
linguagem — e o que ainda depende de decisão de vocês.

---

## 1. O problema que existia

O protótipo já tinha uma base boa: JSON-LD em todas as páginas, `canonical`,
Open Graph, sitemap. Mas três coisas o teriam machucado no dia do go-live.

**O `canonical` apontava para URLs que os arquivos não tinham.**
`perguntas-frequentes.html` declarava ser `/perguntas-frequentes/`. Publicado
como estava, o Google receberia um `canonical` para um endereço que devolve 404
— e o sinal mais forte que existe para dizer "esta é a URL oficial" viraria
ruído. Pior em `/hojepay/`: a página apontava para a URL **antiga** do
WordPress, não para a nova prevista na PROPOSTA.

**A imagem de compartilhamento era vertical.** `og:image` apontava para
`hero.jpg`, 900×1125. WhatsApp, LinkedIn e X esperam 1200×630 — uma imagem
vertical é cortada no meio ou rebaixada a miniatura. Todo link compartilhado do
site chegaria torto. Cinco das sete páginas não tinham `og:image` nenhuma.

**O `sameAs` declarava perfis falsos.** O JSON-LD dizia que os perfis sociais da
marca eram `https://www.instagram.com/`, `https://www.youtube.com/` e
`https://www.facebook.com/` — os sites, não as contas. Isso não é um campo vazio:
é uma afirmação errada sobre a identidade da empresa, no exato lugar onde o
Google monta o Knowledge Panel. Os perfis reais estavam no rodapé o tempo todo.

---

## 2. URLs

Cada página virou um diretório com `index.html` dentro:

```
hoje-pay/index.html            →  cartaohoje.com.br/hoje-pay/
perguntas-frequentes/index.html →  cartaohoje.com.br/perguntas-frequentes/
```

Isso faz as URLs limpas funcionarem **nativamente em qualquer host** — Apache,
nginx, Netlify, Vercel, Cloudflare Pages, GitHub Pages, S3 — sem uma linha de
regra de reescrita. Regra de reescrita é coisa que quebra na migração de host e
ninguém percebe; diretório é diretório em todo lugar.

O custo: os caminhos viraram absolutos (`/assets/…`), então o site precisa ser
servido por HTTP. Abrir por duplo clique não navega mais. É a troca certa —
`python -m http.server 8000` resolve o desenvolvimento local.

`canonical`, `og:url`, sitemap, JSON-LD e todos os links internos foram alinhados
a esses endereços. O `tools/checar-seo.py` falha se algum sair de sincronia.

---

## 3. Dados estruturados

Toda página carrega um grafo JSON-LD completo e autocontido — o Google lê cada
página isoladamente, então referenciar um `@id` definido em outra não resolve.

| Nó | Onde | O que carrega |
|---|---|---|
| `Organization` | todas | Razão social, **CNPJ**, endereço, telefones com horário de atendimento, perfis sociais reais, vínculo com o Grupo Herval |
| `WebSite` | todas | Identidade do site, idioma, publisher |
| `CreditCard` + `FinancialProduct` | todas | O produto: bandeira, mensalidade, prazos, e mais 13 atributos em `additionalProperty` |
| `WebPage` | todas | Título, descrição, imagem, data, trilha — específico de cada página |
| `BreadcrumbList` | todas | Trilha de navegação |
| `MobileApplication` | home, `/baixar-o-app/` | O app, com os links reais da App Store e do Google Play |
| `FAQPage` | `/perguntas-frequentes/` | As 23 perguntas |
| `HowTo` | `/hoje-pay/` | Os 6 passos da compra na iPlace |
| `ContactPage` | `/fale-conosco/` | Canais de atendimento |

Três decisões que valem explicar:

**O `FAQPage` saiu da home.** As 8 perguntas da home são um subconjunto das 23 da
página de FAQ. Marcar o mesmo conteúdo como `FAQPage` em duas URLs é
duplicação — o próprio Google desaconselha. A home continua com o acordeão
visível e o link para o FAQ completo.

**As 23 perguntas são extraídas do HTML, não escritas à mão.** O
`tools/gerar-llms.py` lê os `<details>` da página. Antes, o JSON-LD era uma cópia
manual do texto visível — duas fontes da verdade que divergem no primeiro dia em
que alguém corrige uma resposta e esquece do JSON.

**`annualPercentageRate: null` saiu.** Campo nulo em JSON-LD não é "campo vazio",
é um campo declarado sem valor. Se a taxa for publicada um dia, entra com o valor
real ou não entra.

Uma ressalva honesta: o Google **restringiu os rich results de `FAQPage` em
agosto de 2023** a sites de governo e saúde, e **aposentou os de `HowTo`**. O
ganho de aparência na busca é hoje próximo de zero. A marcação continua valendo
por outro motivo — é o que motores de IA leem para responder sobre o produto, e
é o que sustenta o Knowledge Panel da empresa.

---

## 4. Compartilhamento

Foram gerados sete cards de Open Graph em 1200×630 (`assets/img/og/`), um por
página, com a marca, a foto da página e a cor do sistema. Toda página declara
`og:image` com `width`, `height`, `type` e `alt`, além do bloco completo de
Twitter Card — que antes só existia na home.

Os cards são gerados por `tools/gerar-og.py` — foto à direita esmaecendo no
creme, marca e texto à esquerda, faixa coral no rodapé, cores tiradas dos tokens
do `hoje.css`. Página nova é uma linha a mais no fim do script.

Uma ressalva: o script compõe com a **Segoe UI do sistema**, não com a Plus
Jakarta Sans, que não está instalada localmente. A diferença é discreta num card
social, mas quando a fonte da marca for hospedada (seção 6) vale apontar as duas
linhas de `ImageFont.truetype` para ela e regerar.

---

## 5. Rastreabilidade por LLMs

Um modelo de linguagem não "vê" a página: ele recebe HTML e tenta achar o
conteúdo no meio de `<div>`, SVG inline, CSS e menu repetido. Quatro medidas,
da mais para a menos importante:

### 5.1 `llms.txt` e `llms-full.txt`

A convenção [llmstxt.org](https://llmstxt.org) define dois arquivos na raiz:

- **`/llms.txt`** — o mapa curado. Abre com a ficha do produto em texto direto
  (bandeira, mensalidade, prazos, exigências, canais de atendimento), depois
  lista cada página e cada PDF com uma descrição. É o arquivo que responde "o
  que é o Cartão Hoje" sem que o modelo precise ler o site inteiro.
- **`/llms-full.txt`** — o conteúdo íntegro das 7 páginas em Markdown, 35 KB,
  incluindo as 23 perguntas e respostas.

O `llms-full.txt` é **gerado a partir do HTML**, nunca escrito à mão. Se a página
mudar e ninguém rodar `tools/gerar-llms.py`, a divergência aparece no diff — não
em silêncio.

### 5.2 `robots.txt`

Os robôs de IA estão liberados **nominalmente**, não por omissão: ClaudeBot,
GPTBot, OAI-SearchBot, PerplexityBot, Google-Extended, Applebot-Extended, CCBot,
meta-externalagent e outros.

Isso importa por um detalhe da especificação: um robô que encontra um grupo com
o próprio nome **ignora o grupo `*` inteiro**. Por isso as exclusões dos
artefatos internos (`/design-system/`, `/_probe.html`, `/chamado/`) aparecem
repetidas nos dois grupos. Sem essa repetição, liberar um robô nominalmente
abriria para ele justamente o que o grupo genérico bloqueia.

> Se o Jurídico quiser depois separar motores de resposta (que citam a fonte e
> mandam tráfego) dos robôs de treinamento em massa, a mudança é mover `CCBot`,
> `Bytespider` e `meta-externalagent` para um grupo próprio com `Disallow: /`.

### 5.3 Dados estruturados

O JSON-LD da seção 3 é a fonte mais confiável que um modelo tem: não depende de
interpretar layout. Os 13 `additionalProperty` do cartão existem exatamente para
isso — "Mensalidade: R$ 12,90", "Renda mínima: 1 salário mínimo" são pares
nome/valor inequívocos, não frases a interpretar.

### 5.4 O HTML já ajudava

Duas coisas que o protótipo acertou antes e que valem preservar: **nenhum
conteúdo depende de JavaScript** (o FAQ usa `<details>` nativo, com as respostas
no HTML mesmo fechadas), e o `baixar-o-app` **nunca redireciona robôs** — sem
isso, todo crawler indexaria a App Store no lugar da página.

---

## 6. Desempenho — o que falta

`hoje.css` e `hoje.js` são leves e o HTML é estático. O maior custo de LCP que
sobra é externo: **a fonte vem do Google Fonts**, o que custa duas conexões
(`fonts.googleapis.com` e `fonts.gstatic.com`) e uma folha de estilo bloqueante
antes de qualquer texto aparecer.

Plus Jakarta Sans é licenciada em **OFL — hospedar por conta própria é permitido
e é a correção certa**:

1. Baixar os pesos em uso (400, 500, 600, 700, 800) em `woff2`;
2. Colocar em `assets/fonts/` e declarar `@font-face` com `font-display: swap`;
3. Trocar as três linhas do `<head>` por um `<link rel="preload" as="font" …>`;
4. Remover os dois `preconnect`.

Elimina duas conexões de terceiro e tira o Google Fonts do caminho crítico.
Não foi feito aqui porque exige baixar os arquivos da fonte.

Pendente também: `/assets/` precisa de `Cache-Control` longo — está pronto em
`deploy/`, mas depende de aplicar a configuração do host.

---

## 7. Onde está o ganho real

A base técnica está resolvida. Ela **não** traz cliente novo sozinha — ela
garante que o conteúdo seja indexado corretamente. O site hoje disputa
basicamente a busca pela própria marca.

Isso continua valendo, e é o item mais valioso desta lista inteira (detalhado na
[PROPOSTA.md](PROPOSTA.md), seção 4.2):

| Intenção de busca | Página a criar |
|---|---|
| "cartão de crédito sem conta em banco" | Página de produto aprofundada |
| "cartão de crédito para negativado" | Página de elegibilidade, honesta sobre a análise |
| "cartão de crédito anuidade barata" | Página de tarifas e custos |
| "como pedir cartão de crédito pelo celular" | Guia passo a passo |
| "cartão taQi / volis / iPlace" | Uma página por parceiro |

Uma página por dúvida de alto volume, além do FAQ agregado. Cada uma vira porta
de entrada — e cada uma entra no `llms.txt` como um item a mais que um modelo
pode citar.

---

## 8. Antes de publicar

**Bloqueadores**

- [ ] **Confirmar CNPJ e endereço** usados no JSON-LD: `07.512.441/0001-11`,
      BR-116 nº 7070, Sala 14, Dois Irmãos (RS). Foram extraídos do rascunho da
      política de privacidade. Errado, contamina a identidade da empresa no Google.
- [ ] **Decidir sobre a política de privacidade.** A página é uma minuta com
      blocos "a confirmar" visíveis e está marcada como indexável. Instituição
      financeira publicando rascunho de política de privacidade é risco de
      compliance, não de SEO. Ou o Jurídico fecha o texto, ou a página sai do
      `sitemap.xml` e ganha `noindex` até fechar.
- [ ] **Levantar as URLs do site atual** no Search Console antes de desligá-lo, e
      escrever um 301 para cada uma. Só `/hojepay/` é conhecida hoje. Redirecionar
      tudo para a home em massa é tratado como *soft 404*.
- [ ] Aplicar a configuração do host (`deploy/LEIA-ME.md`): host canônico, 404,
      charset dos `.txt`, cache.
- [ ] Remover `_probe.html`, `chamado/` e `Guide e logo/` do que sobe a produção.

**Primeiro dia**

- [ ] Registrar no Google Search Console e no Bing Webmaster Tools; enviar o sitemap
      nos dois.
- [ ] Rodar `python tools/checar-seo.py` — precisa sair com 0 erro.
- [ ] Testar uma URL de cada tipo no [Rich Results Test](https://search.google.com/test/rich-results)
      e no [Schema Markup Validator](https://validator.schema.org/).
- [ ] Testar o compartilhamento no WhatsApp, no LinkedIn e no X.
- [ ] Lighthouse em `/` e `/perguntas-frequentes/`.

**Depois**

- [ ] Self-host da fonte (seção 6).
- [ ] Páginas de conteúdo da seção 7.
- [ ] Analytics. A PROPOSTA sugere Plausible ou GA4 — decidir antes, porque
      qualquer rastreamento muda a política de privacidade e pode exigir banner
      de consentimento.

---

## 9. Manutenção

```bash
python tools/checar-seo.py    # antes de todo deploy; sai com código 1 se achar erro
python tools/gerar-llms.py    # sempre que o texto de uma página mudar
```

Ao editar conteúdo, três coisas precisam andar juntas e é fácil esquecer uma:
o texto visível, o `<lastmod>` no `sitemap.xml` e o `llms-full.txt`. O
`gerar-llms.py` cuida do terceiro; o `checar-seo.py` pega o resto.
