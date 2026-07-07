# Groq 413 Payload Too Large Fix

## Problem

Groq mode was selected and the token meter still showed `0`, but the sidebar revealed the real issue:

```text
413 Client Error: Payload Too Large for url: https://api.groq.com/openai/v1/chat/completions
```

That means Groq rejected the request before returning a completion or token-usage metadata. The token meter was not the root problem; the Groq prompt was too large.

## Fix

Updated `frontend/dashboard.py` so the Groq narrative rewrite no longer sends the full nested dashboard/committee object.

The app now builds a small Groq context containing only the important facts:

- selected department and supply item
- forecast demand
- total stock / usable stock / true shortage gap
- packing quantity and priority
- Stage 3 transfer/supplier/substitute summary
- Stage 4 finance summary
- Stage 5 command-center priority/decision
- short local committee baseline text

## Added helpers

```python
_compact_for_groq(...)
_build_tiny_groq_context(...)
_json_compact_limited(...)
```

## Safety controls

Optional `.env` controls:

```text
MEDPACK_GROQ_CONTEXT_MAX_CHARS=6500
MEDPACK_GROQ_MAX_TOKENS=650
```

Lower `MEDPACK_GROQ_CONTEXT_MAX_CHARS` if Groq still rejects the payload on your machine.

## Expected behavior

After this fix:

1. Select Remote LLM Mode.
2. Choose Groq.
3. Run MedPack Committee Decision.
4. Groq should receive a compact prompt instead of the huge full state.
5. If Groq succeeds, the token meter should show non-zero tokens.
6. If Groq still fails, the sidebar should show a clear failure reason.

