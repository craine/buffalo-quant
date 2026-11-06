# buffalo-quant

Buffalo Quant Desk: Bills and Sabres analytics with a graded, public prediction Ledger.
Live site: https://buffaloquant.com (Cloudflare Pages serves `site/`).

```
pip install -r requirements.txt
make all        # ingest -> clean -> test -> report -> site
python3 -m src.ledger.log_card   # log an approved card (before kickoff only)
```

See CLAUDE.md for rules, architecture and conventions.

## Cloudflare Pages settings
- Production branch: `main`
- Build command: *(none)*
- Build output directory: `site`
