---
name: falsify-me
description: Critically examine and constructively improve claims, conversations, project plans, designs, and code snippets. Use for explicit critical requests, including Japanese requests such as 「批判的に検討して改善して」「このコードを批判的に改善して」「案内文を批判的に見て改善して」, and requests to falsify, stress-test, or find failure conditions. These requests qualify even when short or similar to editing or debugging. Exclude explanation, proofreading, debugging, routine review, and brainstorming when no explicit critical intent is expressed.
---

# Falsify Me

Find the few material challenges that could change a conclusion or decision, then help improve it. Understand the target before trying to defeat it. Match the user's language.

## Select the mode

Infer the primary mode from the goal, not merely the file type; use a secondary mode only where useful. Read its reference before evaluating:

- Conversation, argument, analysis, or rewrite: [discourse](references/discourse.md).
- Early project, feasibility, design, or plan: [project](references/project.md).
- Implementation behavior or proposed code improvement: [code](references/code.md).

For consequential risks, pharmaceutical quality, uncertain acceptance, or detailed control/review decisions, also read [risk management](references/risk-management.md). Keep low-impact discussions brief; do not require a formal table.

## Understand and challenge

1. State the target and scope. Separate relevant claims, assumptions, evidence, and decisions. Distinguish factual assertions from purposes, values, and preferences. Split multiple material claims rather than compressing them into an easier claim to attack. Ask only when ambiguity would change the judgment; disclose interpretive assumptions.
2. Pursue challenges only if they could materially change correctness, interpretation, safety, decisions, architecture, or outcomes. Try concrete counterexamples, necessary-assumption failure, boundaries, alternative explanations, disconfirming evidence, and internal contradictions. Prefer one strong challenge over many weak objections.
3. Try to defeat each criticism: can the original claim survive under its stated scope and existing controls? Withdraw objections resolved by available information. Do not invent problems for balance or adversarial appearance.
4. For each remaining material challenge, show its evidence and consequence. Use sources, file/line references, inputs, premises, or observed output where available. Mark **Observed** for directly evidenced observations, **Derived** for consequences that follow from stated premises, and **Hypothesis** for plausible but unverified mechanisms. A read source is evidence of what it says, not proof that its substantive assertion is true. Never call an unexecuted example reproduced.
5. Propose the smallest justified revision, limitation, experiment, or control. Preserve the user's purpose and values. If nothing needs changing, say so. Re-examine the revision once for the original failure and new material risks, then expose unresolved issues and the next verification rather than looping indefinitely.

## Judge each material claim

| Result | Apply when |
| --- | --- |
| FAILS | An established material counterexample, contradiction, or evidence conflict defeats this claim as stated, even if a narrower or repaired proposal is viable. |
| INCONCLUSIVE | Essential evidence is missing and prevents judgment, with no established defeat of this claim. Name the minimum additional evidence. |
| REVISE | Evidence justifies revision or clarification, but defeat of the stated claim has not been established; explain the exact change and basis. |
| SURVIVES | Relevant examination found no material falsifier in the tested scope. State limits; this is not proof or safety assurance. |

A defeated claim remains FAILS even when another claim lacks evidence. Give separate verdicts rather than hiding this under an aggregate INCONCLUSIVE. Judge the original claim separately from the proposed improvement and its verification status. A hypothetical failure alone does not establish FAILS. For an improvement, report the actual verification performed and its scope in plain language (for example, untested, statically examined, or execution-checked); do not reuse the original-claim verdict as a verification label.

## Improve with risk in view

Use ICH Q9(R1) as the risk-management foundation: scientific knowledge and patient protection for pharmaceutical quality; clearly identified adaptation for general topics. The reference distinguishes source principles from this skill's design. Regulations, SOPs, and expert judgment retain their roles.

For material risks, connect failure conditions to affected people/goals, potential harm, likelihood and severity, current controls, evidence and uncertainty. Unknown is not low risk. Do not invent probabilities, scores, RPNs, or acceptance thresholds. Detectability is used only when appropriate to the selected method.

Connect proposed controls to effectiveness checks, new risks, estimated residual risk, the responsible decision maker and available acceptance criteria, necessary communication, and review triggers. Label unimplemented controls and predicted residual risk accordingly. Distinguish **claim verdict**, **improvement verification**, and **risk acceptance**. SURVIVES does not establish acceptable risk. Missing acceptance criteria or decisions remain unresolved; do not make unassigned acceptance decisions. Cite documented acceptance and its decision maker separately from your recommendation.

## Deliver a useful response

Be compact. Even in a short response, state the exact verdict token (SURVIVES, REVISE, FAILS, or INCONCLUSIVE) for each material claim; do not replace it with prose alone. Use the mode's output as needed:

- Target, scope, and material claim verdicts.
- Strongest challenges, evidence status, and why they matter; or none found.
- What remains sound and the minimum revision/rewrite/experiment/fix, when warranted.
- Re-examination of the revision and its actual verification status.
- Material residual risk, acceptance state, review triggers, and minimum next action.

Keep these distinctions even when collapsing them into a few paragraphs. Suggest stopping or changing direction if the original objective cannot reasonably be met. A critical-review request does not itself authorize changes to files or external systems. Follow the user's authorized scope for edits and execution. Self-review is not independent QA and does not replace formal Owner decisions or workflow state transitions.
