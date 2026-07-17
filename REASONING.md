# Reasoning

## Knowledge structure

Two stores, one for each kind of knowledge structure. Research is claims in prose, so what matters is meaning: seven documents embedded once and retrieved by cosine similarity. The catalogue is rows with typed fields, so what matters is exactness — a product matches when the searched term appears anywhere in its name, ingredients, or tags. Neither store reasons. Retrieval is exposed as tools; the model decides whether and how often to call them, chaining calls where each input builds on the last. The links between facts are never stored; the model finds them at answer time — low ferritin leads to iron research, which notes vitamin C aids absorption, so it searches for a product with both, visible in the trace.

I rejected a knowledge graph: its edges must be extracted from the prose up front, which is error-prone and freezes it to the links already drawn, and adding a source means re-extracting entities where here it is one embedding. A graph is more reliable for links it holds, but only at a scale where extraction cost is already the bottleneck.

## Context assembly

Every turn's prompt is the system prompt, the full profile as a data block, and the conversation so far. I include the whole profile each time — at seven fields, selection is premature; the real selectivity is behavioural, the model ignoring the irrelevant journalling field. Retrieved evidence is different: it enters only through tool results and is dropped after the turn that fetched it, so each answer grounds on evidence fetched fresh that turn, not lingering context. One rule underpins this: profile and retrieved text are data, not instructions, so neither a customer's typed goal nor a poisoned source can rewrite the rules.

## Safety

Safety works in three layers. The corpus is the first fence: wellness-grade sources only, so a grounded answer cannot prescribe. Routing is the second — out-of-lane questions (medications, interactions, dosing, diagnosis) are declined and sent to a professional. The third is framing: "may support," never "will fix." Price never reaches the model — the CLI adds it after — so ranking is evidence and fit alone, and a profile field shapes advice only where evidence links it (sex → ferritin ranges), never by demographic. It catches obvious out-of-lane questions but misses what it can't see: no drug-interaction check (iron with thyroid medication is routed out, not answered), and a grounded-or-general label that is the model's own. The one structural guarantee: any recommended product must trace back to a search.

## What was left out

I scoped out everything that measures answer quality or hardens the system for production, keeping only what demonstrates reasoning: no LLM-judge evaluation, fairness sweeps, retrieval metrics, MCP server, learned reranker, or persistence. The tests confirm behaviour — retrieving when it should, routing unsafe questions, degrading on a miss — not that advice is good. That would need an evaluation harness: the clearest gap, and the first thing I'd add with another hour.

## The uncertain decision

The call I'm least sure about: how the system judges whether a search helped — good enough, or too thin. A fixed score threshold is testable but can't separate "on-topic but unhelpful" from relevant; a model judgment catches that but is hard to test. So I fused them: each result gets a coarse band (high/medium/low) from its score, which the model weighs in deciding whether to re-search or degrade, answering what it can otherwise. The band is cheap and testable; the model's judgment covers what it can't. The cost: the cutoffs are tuned to this corpus and embedding model, and would need retuning at scale.