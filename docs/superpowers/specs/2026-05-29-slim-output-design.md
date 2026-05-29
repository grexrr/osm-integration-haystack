# Slim Output Mode for OSMFetcher

**Date:** 2026-05-29
**Issue:** #3
**Status:** Approved for implementation

---

## Problem

When `OSMFetcher` is used as a `ComponentTool` inside a Haystack Agent, the full
document list (with rich OSM metadata including `tags`, `tags_norm`, addresses, etc.)
is serialised as a tool message and forwarded to the LLM verbatim. For dense urban
areas (300–1000 m radius, common tags like `amenity`/`tourism`/`leisure`), this
produces 900–1300 Documents whose total token count easily exceeds 128k tokens,
causing OpenAI API errors.

The same query works fine in a pipeline (`OSMFetcher → PromptBuilder → Generator`)
because the prompt template selects only a small subset of fields. Agents have no
equivalent filter.

---

## Decision

Add `slim_output: bool = False` to `OSMFetcher`. When `True`, every document is
compressed to its essential fields before the token budget is applied. Default is
`False` to preserve existing behaviour.

---

## Interface

```python
OSMFetcher(
    slim_output: bool = False,  # new parameter
    max_token: int = 12000,     # unchanged
    # ... all other existing parameters unchanged
)
```

Output type remains `List[Document]` — compatible with pipelines, Agents, and
`ComponentTool` without changes to call sites.

---

## Implementation

### New module-level constant (`osm_fetcher.py`)

```python
_SLIM_META_FIELDS = {"name", "category", "lat", "lon", "distance_m", "address"}
```

### New method: `_slim_documents`

Mutates documents in place, keeping only `_SLIM_META_FIELDS` in meta and
truncating content to 300 characters.

```python
def _slim_documents(self, documents: List[Document]) -> List[Document]:
    for doc in documents:
        doc.meta = {k: v for k, v in doc.meta.items() if k in _SLIM_META_FIELDS}
        if len(doc.content) > 300:
            doc.content = doc.content[:300]
    return documents
```

### Updated tail of `_fetch_by_radius`

```python
documents.sort(key=lambda d: d.meta.get("distance_m", float("inf")))

if self.slim_output:
    documents = self._slim_documents(documents)
if self.max_token:
    documents = self._apply_token_budget(documents)

return documents
```

### Interaction with `_apply_token_budget`

When `slim_output=True`, `tags` and `tags_norm` are already stripped and content
is already truncated before `_apply_token_budget` runs. Phase 1 of the budget
method (which strips those same fields) becomes a no-op. Only phase 2 (dropping
farthest documents) can still fire if the slim documents collectively exceed
`max_token`.

---

## Testing

Three new unit tests added to `TestOSMFetcherTokenBudget` in
`tests/test_osm_fetcher.py`. All tests use constructed `Document` objects —
no network calls.

| Test | Verifies |
|------|----------|
| `test_slim_output_keeps_only_essential_fields` | Only `_SLIM_META_FIELDS` keys survive in meta |
| `test_slim_output_truncates_long_content` | Content > 300 chars is truncated |
| `test_slim_output_false_leaves_meta_unchanged` | Default behaviour: meta untouched |

---

## Backwards Compatibility

`slim_output` defaults to `False`. All existing usage of `OSMFetcher` is unaffected.
