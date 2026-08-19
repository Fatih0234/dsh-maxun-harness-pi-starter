# Deterministic catalog fixture

Six products, two per page, ordinary `Previous`/`Next` pagination.

Start from project root:

```bash
./scripts/serve-fixtures.sh
```

Acceptance URL:

```text
http://127.0.0.1:4173/page1.html
```

Acceptance request:

> Scrape the products from this catalog. Get product name, price, rating, image URL, product URL and review count. Follow pagination and collect the first 5 products.

`expected-first-5.json` records normalized semantics. Resolve relative extracted URLs before comparing path components because Maxun may normalize `href`/`src` to absolute URLs.
