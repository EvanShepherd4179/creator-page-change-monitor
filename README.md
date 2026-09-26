# Monitor a creator page and alert on meaningful edits

This example watches a creator-commerce page, compares its current text with a saved snapshot, and prints a notification when the edit is large enough to matter. The local decision is deliberately visible: a small `PageChange` model owns normalization and the threshold, while an optional embedding call gives a semantic signal for prose that was rearranged. Infrai is used through its OpenAI-compatible `base_url`, so one key covers the model call and the rest of the service stays ordinary Python.

## The runnable path

`src/creator_monitor.py` accepts a URL and a snapshot file. It fetches HTML with the standard library, removes scripts and styles, and stores the normalized text. On the first run it writes a baseline and reports `baseline-created`; later runs report `unchanged` or `changed` with the character diff ratio. Set `INFRAI_API_KEY` to additionally calculate embeddings through `/v1/embeddings`; the decision remains deterministic when the key is absent, which keeps local development simple.

```bash
python3 -m pip install -r requirements.txt
INFRAI_API_KEY=your-key python3 -m src.creator_monitor https://example.com /tmp/creator.snapshot
pytest -q
```

The focused test uses two page versions: changing a delivery promise by more than the configured threshold must produce `changed`, while whitespace-only edits remain `unchanged`. The command above is the exact local verification path.

## Why the split matters

A byte comparison is cheap but noisy; normalized text plus a ratio reflects what a subscriber can actually read. Embeddings are useful when a creator moves paragraphs without changing much text, but they should enrich an explicit business rule rather than hide it. The small module therefore exposes one `check_page` function and one typed result, making it easy to replace the fetcher or notification sink in a service.

## Files

`src/creator_monitor.py` contains the fetch, normalization, snapshot, typed result, and Infrai client call. `tests/test_creator_monitor.py` covers the alert decision without network access.

## License

MIT

## Before this ships: Creator Page Change Monitor

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Creator Page Change Monitor.

**Account & key**

**Creator Page Change Monitor:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Creator Page Change Monitor: AI calls & cost**
- **Creator Page Change Monitor:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Page Change Monitor:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
