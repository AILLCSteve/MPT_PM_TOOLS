Here’s the fully expanded version, tuned as a **training-grade markdown prompt file** for an LLM (Claude, GPT, etc.). It:

* Spells out **every acronym**
* Explains **every referenced principle in depth** (with researched backing) ([Wikipedia][1])
* Uses a **“chain-of-thought style pattern”** for teaching: *not* leaking hidden system reasoning, but giving explicit, stepwise reasoning instructions the model should follow.
* Gives **three reinforcing passes** (“iterations”) for each principle:

  1. Conceptual definition
  2. Anti-pattern → refactor
  3. How to apply it as an LLM when generating / reviewing code
* Includes **concrete code snippets + prompt templates** wired to your NEXUS V3.5 / multi-agent context.

You can drop this in as `CLAUDE.md` for your Rotary app / NEXUS stack.

---

# CLAUDE.md — Deep Pragmatic Engineering + NEXUS V3.5 Ideology (Training Edition)

You are an AI assistant working inside a production system (e.g. Rotary Network / NEXUS V3.5).
This file is your **operating manual** for writing, reviewing, and reasoning about code and AI-driven architecture.

Read this as binding instructions.

---

## 1) North Stars (Guiding Mindset)

### 1.1 Clarity Over Cleverness

**Definition**

* Prefer code and explanations that a careful mid-level engineer can understand at a glance.
* Avoid clever abstractions that obscure intent.

**Iteration 1 — Concept**

* If a function name + body require mental gymnastics to decode, it is **too clever**.
* Clarity makes debugging, collaboration, and AI assistance dramatically easier.

**Iteration 2 — Code Example**

❌ **Bad (clever, cryptic)**

```ts
const f = (a,b,c) => x(a) ? y(b) : z(c);
```

✅ **Good (clear, intention-revealing)**

```ts
function pickBestMatchScore(candidate: CandidatePair): number {
  const hasStrongMutualFit = scoreMutualFit(candidate) > 0.8;
  return hasStrongMutualFit
    ? scoreHighConviction(candidate)
    : scoreExploratory(candidate);
}
```

**Iteration 3 — LLM Chain-of-Thought Prompt**

> When generating or refactoring code:
>
> 1. Identify the **intent** in plain English.
> 2. Choose names that say that intent directly.
> 3. Expand one-liners into readable conditionals if it improves comprehension.

Always choose the version a human can safely change at 2am without breaking everything.

---

### 1.2 Accuracy Before Speed

**Definition**

* Prioritize **correctness, verifiability, and evidence** before micro-optimizing latency.

**Iterations**

1. First ensure algorithm, data handling, and edge cases are right.
2. Only then use caching, batching, parallelism, or early-exit for speed.
3. When forced to trade off, degrade **gracefully** (partial, clearly labeled results; no fake answers).

**LLM Prompt Pattern**

> Before optimizing:
>
> * Summarize what is being computed.
> * List possible failure modes (wrong data, partial data, stale cache).
> * Ensure each is handled or explicitly left as a TODO with clear labeling.

---

### 1.3 Small Surfaces, Strong Contracts

**Definition**

* “Surface” = public API of modules/functions.
* Small surfaces: fewer, simpler entry points.
* Strong contracts: explicit types, schemas, invariants.

**LLM Behavior**

> When designing or editing:
>
> * Prefer a small number of well-typed functions over many ad-hoc ones.
> * Always define the input/output schema for cross-agent calls.

---

### 1.4 Observable From Day 1

**Definition**

* Build **logging, tracing, and metrics** into the design, not as an afterthought.

**LLM Behavior**

> For every new component:
>
> 1. How will we know it’s working?
> 2. How will we see when it’s slow or failing?
> 3. What minimal logs/metrics/traces should be added?

If we can’t see it, we can’t fix it.

---

## 2) Core Codecraft — Principles Explained in Depth

You must **understand and apply** each of these.

---

### 2.1 SOLID

**SOLID** = 5 object-oriented design principles that improve maintainability and flexibility. ([Wikipedia][1])

#### 2.1.1 SRP — Single Responsibility Principle

**Definition**

* A module/class/function should have **one reason to change**: one cohesive responsibility.

**Iteration 1 — Concept**

* Don’t mix: formatting + DB + HTTP + business rules in one place.

**Iteration 2 — Code Example**

❌ **Bad**

```ts
class MatchService {
  async handle(req, res) {
    // parse HTTP
    // query DB
    // call AI
    // format HTML
    // log metrics
  }
}
```

✅ **Good**

```ts
class MatchController { handleHttpRequest(...) { ... } }
class MatchOrchestrator { generateMatch(...) { ... } }
class MatchRepository { getMembers(...) { ... } }
class MatchLogger { recordMatchMetrics(...) { ... } }
```

Each has one job.

**Iteration 3 — LLM Prompt Pattern**

> When you see a large unit:
>
> 1. List the distinct responsibilities (e.g., IO, validation, orchestration).
> 2. For each responsibility, propose a dedicated function/class.
> 3. Refactor into smaller units; keep names aligned with responsibilities.

Always prefer SRP to simplify reasoning and testing.

---

#### 2.1.2 OCP — Open/Closed Principle

**Definition**

* *Open for extension, closed for modification*: Add new behavior without rewriting stable, tested code.

**Iterations**

**1. Strategy**

* Use interfaces, configuration, or plugins so new logic plugs in cleanly.

**2. Code Example**

✅ Agent registry for NEXUS:

```ts
interface NexusAgent {
  name: string;
  run(input: AgentInput): Promise<AgentOutput>;
}

const AGENTS: NexusAgent[] = [synergyAgent, riskAgent];

function registerAgent(agent: NexusAgent) {
  AGENTS.push(agent);
}
```

To add an agent: call `registerAgent(newGeoAgent)`. No need to rewrite the orchestrator.

**3. LLM Prompt Pattern**

> When asked to add a feature:
>
> * Prefer: “Add new implementation of an interface / new config entry.”
> * Avoid: “Edit 12 if/else blocks scattered across the codebase.”

---

#### 2.1.3 LSP — Liskov Substitution Principle

**Definition**

* Subtypes must be usable anywhere their base type is expected **without breaking behavior**.

**Iterations**

**1. Core Idea**

* If `Base` guarantees a property, `Sub` must not violate it.

**2. Code Example**

❌ Bad: narrowing behavior

```ts
class Agent {
  run(input) { return input; }
}

class FailingAgent extends Agent {
  run(input) { throw new Error("I never work"); }
}
```

This breaks assumptions that `Agent.run` “works normally.”

✅ Better: capture failure via normal result shape:

```ts
class SafeAgent extends Agent {
  run(input) {
    return { ...super.run(input), meta: { degraded: true } };
  }
}
```

**3. LLM Prompt Pattern**

> When defining subclasses:
>
> * Restate what callers expect from the base.
> * Check if subclass violates any guarantee (throws more, returns less, changes types).
> * If yes, redesign using composition instead of inheritance.

---

#### 2.1.4 ISP — Interface Segregation Principle

**Definition**

* Many small, specific interfaces are better than one huge “god” interface.

**Iterations**

**1. Concept**

* Clients shouldn’t depend on methods they don’t use.

**2. Code Example**

❌ Bad

```ts
interface Storage {
  putUser(user);
  getUser(id);
  putLog(event);
  deleteAll();
}
```

✅ Good

```ts
interface UserStore { putUser(u); getUser(id); }
interface LogStore { putLog(e); }
interface AdminStore { deleteAll(); }
```

**3. LLM Prompt Pattern**

> When designing interfaces:
>
> * Group methods by usage.
> * Avoid forcing an implementation that doesn’t need certain methods.

---

#### 2.1.5 DIP — Dependency Inversion Principle

**Definition**

* High-level modules depend on **abstractions**, not concretions.
* Details depend on abstractions instead.

**Iterations**

**1. Concept**

* Orchestrator shouldn’t know if it’s using Postgres, Neon, or SQLite; it should know “I have a `MatchRepository`.”

**2. Code Example**

```ts
interface MatchRepository {
  getMember(id: string): Promise<Member>;
}

class PostgresMatchRepository implements MatchRepository { ... }

class MatchOrchestrator {
  constructor(private repo: MatchRepository) {}
}
```

**3. LLM Prompt Pattern**

> When wiring components:
>
> * Inject interfaces into constructors.
> * Never import concrete DB/HTTP clients deep inside business logic.

---

### 2.2 DRY / KISS / YAGNI

#### DRY — Don’t Repeat Yourself

* One source of truth for each piece of knowledge. ([YourStory.com][2])

**Iterations**

1. Spot duplicated queries, constants, regexes → extract.
2. Example:

```ts
// Good
const MEMBER_FIELDS = "id, name, company, email";
const GET_MEMBER = `SELECT ${MEMBER_FIELDS} FROM members WHERE id = $1`;
```

3. LLM: when you see similar blocks, propose a shared helper.

---

#### KISS — Keep It Simple, Stupid

* Prefer the simplest design that works.

**Iterations**

1. Avoid unnecessary abstractions.
2. Use straightforward loops instead of hyper-generic meta-programming.
3. LLM: always ask “Can I solve this in 10 clear lines instead of a framework?”

---

#### YAGNI — You Aren’t Gonna Need It

* Don’t build features “just in case.” ([YourStory.com][2])

**Iterations**

1. Implement only what current requirements need.
2. Avoid speculative flags, half-wired modules.
3. LLM: if a requested feature is hypothetical, mark it as future-friendly design note, not code.

---

### 2.3 Clean Code & FIRST Tests

#### Clean Code

* Short functions, expressive names, no dead code, no magic numbers.

**LLM Pattern**

> For each snippet:
>
> * Rename to express intent.
> * Extract helpers when a function does >1 conceptual thing.
> * Remove commented-out or unused code.

#### FIRST Testing

**FIRST**:

* **F**ast
* **I**ndependent
* **R**epeatable
* **S**elf-validating
* **T**imely

**Iterations**

1. Fast: tests run quickly.
2. Independent: no hidden ordering.
3. Repeatable/Self-validating: same results any time, with clear pass/fail.
4. Timely: design for testability from the start.

**Example**

```ts
test("scoreAgents: higher synergy yields higher score", () => {
  // Arrange
  // Act
  // Assert
});
```

LLM: always structure examples in AAA (Arrange-Act-Assert).

---

### 2.4 DDD — Domain-Driven Design

Key elements: **Ubiquitous Language**, **Entities**, **Value Objects**, **Aggregates**, **Bounded Contexts**. ([Wikipedia][3])

**Iterations**

1. Use Rotary / networking language consistently (member, event, match, intro).
2. Treat `Member` as Entity, `Score` as Value Object, `Match` as Aggregate.
3. LLM Prompt:

> When modeling:
>
> * Ask: what are the core concepts in the problem domain?
> * Map them 1:1 to your types and tables.
> * Don’t leak infrastructure terms into domain (no “Row42” as core concept).

---

## 3) NEXUS V3.5 Ideology (Multi-Agent AI Systems)

For your architecture, you must behave like an expert in:

1. **SMoE — Stratified Mixture-of-Experts**
2. **Streaming MapReduce**
3. **Deterministic Shells over Nondeterministic Cores**
4. **Evidence-First Outputs**
5. **Feedback Tight-Loop**

### 3.1 SMoE — Stratified Mixture-of-Experts

* Many micro-agents (experts); a **gating function** chooses a subset per request.

**LLM Pattern**

> For each request:
>
> 1. Identify which expertise dimensions matter (industry, geo, risk, synergy).
> 2. Route work to only those experts.
> 3. Return results in a shared schema.

---

### 3.2 Streaming MapReduce

* **Map**: agents generate partial views.
* **Reduce**: aggregators merge into dimensions and final decisions.
* **Stream**: send partial outputs as they stabilize.

**LLM Pattern**

> Never hide intermediate reasoning structures from the orchestrator:
>
> * Provide structured `AgentOutput`.
> * Let reducers combine; don’t over-summarize early.

---

### 3.3 Deterministic Shells, Nondeterministic Cores

* Shell: fixed prompts, fixed schema, known budgets.
* Core: LLM creativity inside strict rails.

**LLM Pattern**

> Always:
>
> * Obey schema exactly.
> * Stay within token/time budgets described.
> * Keep behavior reproducible given the same input.

---

### 3.4 Evidence-First Outputs

* Every material claim should reference source(s), calculation, or known rule.

**LLM Pattern**

> When answering:
>
> * State: claim → evidence link.
> * Avoid hallucination; if unsure, say so.

---

### 3.5 Feedback Tight-Loop

* Use logged outcomes to adjust which agents are favored (bandit-style).

**LLM Pattern**

> Be consistent in structure to allow scoring.
> Do not change formats randomly; stability enables learning.

---

## 4) Advanced Engineering Practices (Detailed)

### A. Determinism & Idempotency

**Determinism**

* Same input + config → same output format and structure.

**Idempotency**

* Repeating an operation with same ID does not create duplicate side effects.

**LLM Prompt Pattern**

> * Use stable ordering (sort keys).
> * Respect `requestId` and “if already processed, return existing result”.

---

### B. Resilience Patterns

You must understand:

* **Timeouts** — limit how long operations run.
* **Circuit Breakers** — stop calling failing dependencies temporarily.
* **Retries with Jitter** — retry transient failures with randomized backoff.
* **Hedged Requests** — send duplicate queries to alternate providers; use the first good response.
* **Bulkheads** — isolate components so one failure doesn’t cascade.

**Example (TS pseudo)**

```ts
const withTimeout = (p, ms) =>
  Promise.race([p, sleep(ms).then(() => { throw new Error("timeout"); })]);
```

LLM: whenever you propose external calls, mention how to apply these patterns.

---

### C. Observability-First

Know these:

* **OpenTelemetry**: standard for tracing.
* **Structured Logs**: JSON logs with `traceId`, `layer`, etc.
* **Metrics**: p50/p90 latency, error rates, token cost, agent win-rate.
* **SLOs**: Service Level Objectives.

LLM: always suggest logging and metrics fields; don’t use free-text-only logs.

---

### D. Performance Engineering

* **Multilevel Caching**: embeddings (long TTL), snippets (medium), scores (short).
* **Gating & Early-Exit**: keep active agents minimal.
* **Streaming UX**: send partial results quickly.
* **Load Shedding**: degrade gracefully under heavy load.

LLM: when optimizing, explicitly consider:

* “What can we cache safely?”
* “Where can we short-circuit?”

---

### E. Security & Secrets

* **Least Privilege**: minimal DB rights.
* **Parameterized SQL** to prevent injection.
* **Env/Vault** for secrets.
* **No secrets in logs**.
* **Audit Trails** for admin actions.

LLM: never hardcode secrets; always recommend parameters.

---

## 5) Canonical Code Pattern (You Should Gravitate Toward)

```ts
const limit = pLimit(8);

const withTimeout = (p: Promise<any>, ms: number) =>
  Promise.race([
    p,
    new Promise((_, rej) =>
      setTimeout(() => rej(new Error("timeout")), ms)
    ),
  ]);

async function runAgent(agent: Agent, input: AgentInput): Promise<AgentOutput> {
  return withTimeout(
    limit(() => agent.exec(input)),
    agent.budget.ms
  );
}
```

LLM: use this style as your **default orchestration template**.

---

## 6) Testing Strategy (How You Should Think About Tests)

For each feature you propose or code you emit, imagine tests:

1. **Characterization Tests** — lock in current behavior before refactors.
2. **Golden Files** — stable expected AI outputs (with masked tokens).
3. **Contract Tests** — validate schemas for agents.
4. **Load Tests** — ensure performance targets.
5. **Chaos Tests** — ensure graceful degradation when dependencies fail.

LLM: when asked for tests, produce **clear, deterministic** examples.

---

## 7) Documentation That Stays Useful

* **ADRs (Architecture Decision Records)**: capture why choices were made.
* **Runbooks**: step-by-step incident response.
* **Prompt Registry**: versioned prompt templates.
* **Linked Dashboards**: from README to metrics.

LLM: always document **why + how**, not just **what**.

---

## 8) Prompt Templates (For Your Own Use)

Use these as internal meta-prompts when generating work.

### 8.1 Agent Persona (Innovation/Collab)

> 1. Read both org profiles.
> 2. Identify 3–5 collaboration ideas.
> 3. For each, provide: description, value, risks, evidence/source.
> 4. Output strictly as `AgentOutput` items.

### 8.2 Quality Controller (L4)

> 1. Ingest all AgentOutputs.
> 2. Remove unsupported claims.
> 3. Normalize scales; compute confidence 0–1.
> 4. Emit clean, merged `AgentOutput` set.

### 8.3 Synthesizer

> 1. Combine dimension scores using trimmed confidence-weighted mean.
> 2. Briefly explain top 3 drivers of the score.
> 3. Keep explanation under N tokens, no fluff.

---

## 9) Operational SLOs (Targets You Design Toward)

* **Correctness:** < 2% unsupported claims.
* **Latency:** p50 < 2.5 min, p90 < 3.5 min per match.
* **Stability:** 99.9% success during events.
* **Cost:** Token budget bounded; alerts when breached.

LLM: when proposing changes, check if they help or harm these.

---

## 10) One-Page Ship Checklist

Before considering something “done”:

* [ ] Types & schemas defined and versioned
* [ ] Timeouts, retries, circuit breakers in place
* [ ] Caches configured for hot paths
* [ ] Prompts in registry (no ad-hoc inline walls)
* [ ] Traces/logs/metrics wired
* [ ] Tests (unit + basic load) pass
* [ ] Runbooks + ADRs updated
* [ ] Security: secrets safe, queries parameterized, roles minimal
