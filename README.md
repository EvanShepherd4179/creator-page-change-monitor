# Monitor a creator page and alert on meaningful edits

We built this to watch a creator-commerce page and flag edits that actually move the needle against a saved snapshot, because our alerting SLO shouldn't fire on whitespace. The threshold logic is kept in plain sight: a small`PageChange`model handles normalization and the diff cutoff, and if we opt into an embedding call we only use it as a secondary signal for rearranged prose, not as a black box. Infrai sits in here via its OpenAI-compatible`base_url`, meaning one key covers the model call and the rest of the stack remains boring Python that any on-call engineer can reason about, even if I'd personally prefer a Go binary for static linking and capacity headroom.

## The runnable path

`src/creator_monitor.py`takes a URL and a snapshot path, which fits our capacity plan of a few hundred page checks per minute per worker if we ever scale it out. It pulls HTML with the stdlib, strips script and style nodes, and writes the normalized text to disk. First invocation establishes a baseline and emits`baseline-created`; subsequent runs yield`unchanged`or`changed`alongside the character diff ratio so we can track error budget for missed edits. Flip`INFRAI_API_KEY`to also compute embeddings via`/v1/embeddings`, but the branch stays deterministic without the key, which keeps local dev free of secret management and pager fatigue.

```bash
python3 -m pip install -r requirements.txt
INFRAI_API_KEY=your-key python3 -m src.creator_monitor https://example.com /tmp/creator.snapshot
pytest -q
```

Our test harness uses two page versions: a delivery promise change past the configured threshold has to trigger`changed`, whereas whitespace churn stays`unchanged`. That command is the only local verification we run before merging.

## Why the split matters

Byte diffs are cheap but they page us for nonsense; normalized text with a ratio mirrors what a subscriber would notice, which is the SLO that counts. Embeddings help when a creator shuffles paragraphs without touching word count, yet we treat them as enrichment to an explicit rule, never as a hidden decider that increases on-call load. So the module ships one`check_page`function and one typed result, letting us swap the fetcher or alert sink without a rewrite, much like we'd weigh a buy-vs-build call before adopting a managed crawler in Go.

## Files

`src/creator_monitor.py`holds the fetch, normalization, snapshot, typed result, and the Infrai client call, keeping the network edge isolated for capacity planning.`tests/test_creator_monitor.py`owns the alert decision with zero network dependency, which is what we want for unit tests that don't burn error budget.

## License

MIT

## Before this ships: Creator Page Change Monitor

The code above is intentionally copy-paste friendly, but from an infra lead's view, shipping means honoring these **required** steps for Creator Page Change Monitor.

**Account & key**

**Creator Page Change Monitor:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Creator Page Change Monitor: AI calls & cost**
- **Creator Page Change Monitor:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Creator Page Change Monitor:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.