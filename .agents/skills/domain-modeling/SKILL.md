---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the _active_ discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely _reading_ `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only after the user approves the concrete file change. If no `CONTEXT.md` or `docs/adr/` exists, first propose the path and content outline; create it only after approval.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### 深掘りする衝突を選ぶ

同じ語が異なる意味を持ち、その差が次のいずれかを変えるときは、用語表、具体例、未確認事項で深掘りする。

1. データ属性または所有者
2. 状態遷移
3. 外部APIまたは他コンテキストとの境界
4. 業務上の判断

これらを変えない名称揺れは、推奨表記と避ける表記を提案して終了できる。名称だけの変更で、追加のADRや無関係な質問を増やさない。

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Propose CONTEXT.md updates, then apply after approval

When a term is resolved, prepare the exact `CONTEXT.md` addition and show its path, affected terms, and any renamed terminology. Do not create or edit a file until the user explicitly approves that change. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If all three are true, propose the ADR path, number, title, and decision summary. Create it only after explicit user approval. If any condition is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

名称変更だけ、または未決定の移行方式だけではADRを作らない。移行方式が用語の意味・データ境界・トレードオフに影響する場合は、決定済みの事実と未確認事項を分けて質問または調査計画を示す。
