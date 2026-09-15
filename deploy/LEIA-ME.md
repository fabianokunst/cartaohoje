# Configuração de publicação

As páginas estão em diretórios (`hoje-pay/index.html`), então **as URLs limpas
funcionam sozinhas em qualquer host** — Apache, nginx, Netlify, Vercel,
Cloudflare Pages, GitHub Pages, S3 + CloudFront. Não há regra de reescrita
para escrever.

O que ainda depende de configuração é o que nenhum arquivo estático resolve:

| Item | Por que é obrigatório |
|---|---|
| **301 de `/hojepay/` → `/hoje-pay/`** | A URL antiga tem histórico no Google. Sem o 301, a autoridade dela é jogada fora e ainda sobra um 404 indexado. |
| **Host canônico** (`https://cartaohoje.com.br`) | `www`, `http` e apex servindo o mesmo conteúdo = três cópias do site para o Google. O canonical avisa, o 301 resolve. |
| **`404.html` na resposta 404** | Sem isso o host devolve uma página de erro genérica — ou pior, um 200 com conteúdo de erro (*soft 404*), que o Google indexa. |
| **`charset=utf-8` nos `.txt`** | `llms.txt` e `llms-full.txt` têm acento. Servidos como ASCII, viram lixo. |
| **Cache longo em `/assets/`** | Nomes de arquivo são estáveis; sem cache, cada visita rebaixa o LCP. |

## Qual arquivo usar

Copie **apenas um** para a raiz do site publicado:

| Host | Arquivo | Onde vai |
|---|---|---|
| Apache / cPanel / hospedagem compartilhada | `apache.htaccess` | raiz, renomeado para `.htaccess` |
| Netlify | `netlify_redirects` → `_redirects` e `netlify.toml` | raiz |
| Vercel | `vercel.json` | raiz |
| nginx | `nginx.conf` | incluído no `server {}` (não vai na raiz do site) |
| Cloudflare Pages | `netlify_redirects` → `_redirects` | raiz (mesma sintaxe) |

## Antes de publicar

1. **Levante as URLs reais do site atual** antes de desligá-lo: Search Console →
   *Páginas* → exportar, e o `sitemap.xml` do WordPress. Só `/hojepay/` é
   conhecida hoje; toda URL antiga com tráfego ou link externo precisa do
   próprio 301. Redirecione para a página **equivalente**, nunca em massa para
   a home — o Google trata redirect em massa para a raiz como *soft 404*.
2. Publique com o `robots.txt` deste repositório, não com o do WordPress.
3. Registre a propriedade no **Google Search Console** e no **Bing Webmaster
   Tools** e envie `https://cartaohoje.com.br/sitemap.xml` nos dois.
4. Depois do go-live, confira em produção:
   - `curl -I https://www.cartaohoje.com.br/` devolve `301` para o apex
   - `curl -I https://cartaohoje.com.br/hojepay/` devolve `301` para `/hoje-pay/`
   - `curl -I https://cartaohoje.com.br/nao-existe/` devolve `404`
   - `curl -I https://cartaohoje.com.br/llms.txt` traz `charset=utf-8`
