---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

## Start by classifying decisions

At the start of each round, classify each unsettled decision as one of the following:

1. **Critical**: hard to reverse, or a wrong choice has a large failure impact.
2. **Blocking**: not yet decided, and deciding it later would change the next decision.
3. **Assumption**: low impact and safe to proceed with when stated explicitly.

Only Critical and Blocking decisions belong on the **frontier**. Record Assumptions with their reason and proceed; do not turn a name-only or other low-impact choice into repeated questions. Reclassify a decision if new evidence changes its impact or dependency.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), investigate it with the available read-only tools; don't ask the user for anything you could look up yourself. An investigation is an unsettled prerequisite, so only its downstream questions wait; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait. Do not silently decide an unresolved Critical or Blocking decision.

The session is done when every Critical and Blocking decision is settled, remaining Assumptions are stated, and the user confirms the shared understanding. Do not act on the result until that confirmation.
