# Reference style

[Home](../index.md) > Reference > Style

**English** · [ไทย](../th/reference/_style.md)

How every page under `reference/` is written. Reference is **specification, not tutorial** — it states
what things are, not how to feel about them.

## Required page order

1. Breadcrumb: `[Home](../index.md) > Reference > <Name>`
2. `# <Name> Reference`
3. `**Module:** \`binance_th.<module>\`` and `**Available since:** 1.0.0`
4. A one-sentence description of the class/namespace.
5. `## Import` — the import line.
6. The class signature (constructor), if user-constructed.
7. `## Methods` — one `### <method>` per public method, each with: a signature code block, a
   **Parameters** table (Parameter / Type / Default / Description), **Returns**, **Raises** (if any),
   and one **Example**.
8. `## See Also` — em-dash-annotated cross-links.

## Style rules

- Exact signatures, copied from the source. Never guess a parameter or return type.
- Tables for anything enumerable (parameters, fields, error types).
- Direct language: "Returns X." "Raises `BinanceThAuthError` if the credentials are missing." Not "In
  this section we will…", "You can use this to…".
- Money types are `Decimal`. Mark methods that are **signed**, **api-key-only**, or **mutating**.
- Keep tutorial narrative in [guides](../guides/market-data.md); link to it, don't inline it.
