# Worked Example — one bullet, start to finish

A fully fictional candidate, to show the process end-to-end. **All names, numbers, and facts here
are invented for illustration** — the point is the *method*, not the content.

## The candidate (synthetic)
A backend engineer, ~2 years in, who spent the last year as an early engineer at a small startup
building an internal **RAG support assistant** that deflects customer-support tickets. Lane target:
AI / Agent Engineer at seed–Series-A startups.

## Step A — deep-read essence (NOT a bullet yet)
From reading the repo + design doc, the honest essence:

> Built a retrieval-augmented support bot over the company's help-center + past tickets. The hard part
> wasn't the LLM call — it was retrieval quality: naive vector search returned near-duplicates and the
> bot hallucinated policy. Added a reranker + a "no confident answer → escalate to human" abstention
> gate, and an offline eval set of 300 real tickets scored by an LLM-judge. Deflection went from ~18%
> to ~41% of tickets; the abstention gate cut wrong-answer complaints to near zero. Runs on GPT-4.1-mini,
> ~\$30/month. Solo build over ~4 months, now handling ~2,000 tickets/month in production.

Note the real, checkable numbers (18%→41%, 300-ticket eval set, ~2,000/mo, $30/mo) and the genuine
differentiator (abstention gate + eval discipline, not "used RAG").

## Step B — the writer+critic loop on the lead bullet

**mustKeep:** deflection 18%→41% · abstention/escalation gate · offline eval (LLM-judge, 300 tickets)
**leadVerbs:** Built / Shipped / Cut · **charLimit:** ~100 visible

### Round 1 — writer draft (weak)
> *Utilized RAG with a reranker and vector search using GPT-4.1-mini to build a robust, seamless
> support bot that improved deflection by 50%.*

**Critic:**
- `present`: [within char limit, names a model]
- `missing`: [no eval mention, no abstention gate, "50%" doesn't match essence]
- `violations`: [leads with the stack ("Utilized RAG…"), BANNED words "utilized/robust/seamless",
  round number "50%" with no baseline, **fabricated metric** (essence says 18%→41%, not 50%),
  buried impact]
- `score`: **1** — *"Rewrite: lead with the deflection outcome as a baseline→new pair; drop the
  stack from the front and the banned adjectives; restore the true numbers; add the eval + gate,
  which are the real differentiators."*

### Round 2 — writer draft (better, not there)
> *Built an internal support assistant that raised ticket deflection to 41\%, using a reranker and an
> escalation gate, evaluated on 300 tickets.*

**Critic:**
- `present`: [dual-legible: deflection outcome up front · abstention gate · eval present · no banned words]
- `missing`: [baseline for the metric — "to 41%" without "from 18%" is one-sided/unfalsifiable]
- `violations`: [eval named but not credited to a method (LLM-judge)]
- `score`: **3** — *"Add the baseline (18\%$\to$41\%) so the number is two-sided; name the eval method
  (LLM-judge) so it reads as real discipline, not a buzzword. Watch the char count."*

### Round 3 — writer draft (ship-ready)
> *Built an internal RAG support assistant that lifted ticket deflection \textbf{18\%$\to$41\%}
> (\textbf{$\sim$2K tickets/mo}) via a reranker + human-escalation gate, validated on a 300-ticket
> LLM-judge eval.*

**Critic:**
- `present`: [two-sided metric with baseline · scale (2K/mo) · abstention gate · eval + its method ·
  dual-legible (deflection outcome front, mechanism tail) · no banned words · defensible against the essence]
- `missing`: []
- `violations`: []
- `score`: **4** → **approved (in code, because score ≥ PASS).**

## Step C — the AI-tell set review (after the loop)
Suppose all three of the candidate's bullets came back as:
> *Built … 18%→41% … via …* / *Designed … 3× faster … via …* / *Cut … 60% … via …*

Every bullet is the identical `Verb … Δnumber … via mechanism` shape and length. No single bullet is
wrong — but **as a set** the uniform cadence is the AI-tell a same-model critic can't see. Fix by hand:
vary one bullet's structure (lead with the problem instead of the metric; change the length), e.g.
> *When naive vector search kept surfacing near-duplicate policy, added a reranker + abstention gate —
> dropping wrong-answer complaints to near zero across $\sim$2K tickets/mo.*

## The takeaways this example encodes
- The critic's **negative criteria** caught the fabricated "50%", the stack-first lead, and the banned
  words — a purely positive rubric would have rubber-stamped the fluent-but-wrong Round-1 draft.
- **Dual-legibility** = the deflection outcome (any screener grasps it) leads; the reranker/gate/eval
  (engineer credibility) trail.
- **Odd true numbers** (18%→41%, 300, 2K) over clean round ones — more defensible AND less AI-tell.
- The loop got it *structurally* right; the **human still owns integrity** (only the human knew "50%"
  was invented) and the **cross-bullet cadence review** (the tell no single-bullet critic sees).
