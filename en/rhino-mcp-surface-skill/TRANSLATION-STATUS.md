# Translation Status

> These files are the **1.2.0 Chinese updates**, copied so both language trees stay
> structurally identical. They are **not yet translated**.
>
> Until translation lands, **read the Chinese originals** — the content is identical.

## Status

| File | 1.2.0 update | Translation |
|---|---|---|
| `SKILL.md` | Yes | ⏳ pending |
| `references/03-construction.md` | Yes | ⏳ pending |
| `references/04-continuity-and-validation.md` | Yes | ⏳ pending |
| `references/05-mcp-execution.md` | Yes | ⏳ pending |
| `references/07-diagnosis.md` | Yes | ⏳ pending |
| `references/10-parameters-and-recipes.md` | Rewritten | ⏳ pending |
| `references/11-consumer-electronics.md` | Yes | ⏳ pending |
| `references/13-construction-discipline.md` | **New file** | ⏳ pending |
| `VALIDATION.md` / `CHANGELOG.md` | Yes | ⏳ pending |

Everything else in `en/` remains translated from 1.1.0.

## Why this file exists

The 1.1.0 release shipped two language trees with identical file lists.
Without this note, a reader of `en/` would find Chinese text under an English
path and assume the skill was broken.

Keeping the structure aligned means a translator can work file-by-file
against `../references/` without restructuring anything.

## Translation notes for whoever picks this up

1. **Keep the structure.** The 1.1.0 English rewrites were written independently
   rather than translated sentence-by-sentence. Keep that freedom.
2. **Preserve the conditional framing.** Numeric values now carry
   *source / applicability / failure signal*. The conditional wording is the point —
   do not flatten "教材案例, not a standard" into a bare number.
3. **Do not translate the ⛔/⚠️ markers** — they carry meaning:
   `⛔` = doing this breaks something irreversible, `⚠️` = verify first.
4. **Command and option names stay verbatim**: `MatchSrf`, `BlendSrf`,
   `Same height shapes`, `SpanCount`, `Deformable`, `Refine match`.
5. **`Class-A` keeps its适用范围 warning** — it is an automotive-household
   standard, not a general one.