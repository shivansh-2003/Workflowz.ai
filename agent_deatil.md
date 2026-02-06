

# Workflowz.ai – Final Agentic AI Architecture (Locked)

## Core Design Philosophy (Non-Negotiable)

1. **Architecture-first, not task-first**
2. **People-aware planning** (team size & capability are first-class inputs)
3. **Human-in-the-loop is mandatory**
4. **Explainability > automation**
5. **Never invent capability or certainty**

---

## Agent Stack Overview

```
Project Created
   ↓
Input Ingestion Agent
   ↓
Architecture Context Agent
   ↓
Clarification / Question Agent (Human-in-loop)
   ↓
Constraint-Aware Task Decomposition Agent
   ↓
Role → Task Matching Agent
   ↓
Validation & Risk Agent
   ↓
Human Approval Agent (UI)
   ↓
Persist Tasks & Assignments
```

Each agent has **one responsibility** and **clear boundaries**.

---

# 1️⃣ Input Ingestion Agent

**Role:** Requirement comprehension & normalization
**Persona:** Senior solutions architect reading a PRD

### Core Expertise

* Requirement analysis
* Markdown & technical doc comprehension
* Ambiguity detection
* Information preservation

### Responsibilities

* Parse text / markdown
* Extract architectural signals
* Measure confidence of understanding
* Preserve high-quality user structure (never degrade)

### Output (Stable Core Schema)

```json
{
  "project_goal": "",
  "primary_users": [],
  "core_domains": [],
  "constraints": [],
  "assumptions": [],
  "confidence": 0.0
}
```

### Hard Rules

* Never hallucinate
* Never simplify meaning
* Block downstream agents if confidence too low

---

# 2️⃣ Architecture Context Agent

**Role:** System classification & invariant detection
**Persona:** System architect (not solution designer)

### Core Expertise

* Architectural pattern recognition
* System typing
* Invariant identification
* Risk framing

### Responsibilities

* Classify system type
* Identify mandatory subsystems
* State assumptions explicitly
* Identify architectural risk zones

### Output

```json
{
  "system_class": "",
  "primary_patterns": [],
  "required_subsystems": [],
  "assumptions": [],
  "confidence": 0.0
}
```

### Hard Rules

* No tech stack decisions
* No task creation
* No user interaction

---

# 3️⃣ Clarification / Question Agent

**Role:** Ambiguity resolver & implementation gatekeeper
**Persona:** Senior software engineer
**Human-in-the-loop:** ✅ **Yes (only agent allowed to talk to user)**

### Core Expertise

* Risk-based questioning
* Implementation realism
* Constraint clarification

### Responsibilities

* Compare assumptions vs evidence
* Quantify implementation risk
* Ask **minimum necessary questions**
* Group questions logically

### Question Strategy

* No fixed number of questions
* Uses **risk budget**, not question count
* Stops when residual risk ≤ threshold

### Hard Rules

* Never ask tech preference questions
* Never ask “nice to know” questions
* Every question must reduce irreversible risk

---

# 4️⃣ Constraint-Aware Task Decomposition Agent

**Role:** Generate *realistic* work plans
**Persona:** Engineering manager

### Inputs

* Project context
* Architecture context
* **Team capability model** (critical)

### Core Expertise

* Task decomposition
* Scope shaping
* Capability adaptation

### Responsibilities

* Generate tasks that:

  * Match team capabilities **or**
  * Are safely simplified **or**
  * Are explicitly marked blocked
* Group tasks into logical domains/epics

### Allowed Strategies

1. Task compression (simplify)
2. Task escalation (assign to head)
3. Explicit blocking (honest limitation)

### Hard Rule

> **No task may exist unless at least one team member can realistically execute it.**

---

# 5️⃣ Role → Task Matching Agent

**Role:** Feasibility validator & workload balancer
**Persona:** Technical project lead

### Core Expertise

* Capability validation
* Load balancing
* Risk detection

### Responsibilities

* Confirm role compatibility
* Balance workload
* Flag overloads & mismatches
* Suggest scope reduction or escalation

### Hard Rules

* Never “force” assignment
* Never hide capability gaps

---

# 6️⃣ Validation & Risk Agent (Locked)

**Role:** Independent AI auditor
**Persona:** Risk & compliance reviewer

### Validations Performed

* Architectural completeness
* Task feasibility
* Capability gaps
* Load imbalance
* Security & workflow invariants

### Output

```json
{
  "risk_score": 0-100,
  "risk_level": "low|medium|high",
  "top_risks": []
}
```

### Hard Rules

* No task creation
* No assignment
* No user interaction

---

# 7️⃣ Human Approval Agent (UI Layer) (Locked)

**Role:** Trust bridge & final authority
**Persona:** Organization Head

### User Can

* Review architecture summary
* Edit tasks
* Reassign tasks
* Remove tasks
* Approve or reject plan

### Absolute Rule

> **Nothing is written to DB without explicit human approval.**

---

# Cross-Cutting System Rules (Global)

## 1️⃣ Explainability

Every task must answer:

* Why this task exists
* Why this assignee
* What assumption it depends on

---

## 2️⃣ Confidence & Assumptions Are First-Class Data

* Every agent outputs confidence
* Assumptions are visible and revisitable

---

## 3️⃣ No Silent Failure

If AI cannot proceed safely:

* It stops
* It explains why
* It asks for help

---

## 4️⃣ Auditability

Store:

* Original input
* Agent outputs
* Assumptions
* User approvals

---

# Why This Architecture Works

✔ Respects real teams
✔ Scales from 2-person startups to orgs
✔ Avoids hallucinated work
✔ Builds trust through transparency
✔ Modular but not naïve

This is **not a chatbot workflow**.
This is a **decision-support system with AI agents**.

---

## Final Verdict

You’ve designed:

* A **production-grade agentic AI system**
* With correct human control points
* With realistic organizational awareness
* Without over-automation

This is **exactly how Workflowz.ai should differentiate itself**.

If you want next, we can:

* Turn this into a **formal system design doc**
* Define **agent APIs & contracts**
* Design **state machines for orchestration**
* Or map this 1:1 to your FastAPI backend

Just tell me the next move.



Perfect closing step 👍
This is exactly what you want before freezing the design.

Below is a **clean, cumulative list of every major question you raised for each agent — and the final, agreed solution**.
Think of this as the **design decision log** for Workflowz.ai’s AI system.

---

# Workflowz.ai – Agent-wise Questions & Final Solutions

This section answers:

> *“What problems did we identify per agent, and what design decisions did we lock in?”*

---

## 1️⃣ Input Ingestion Agent

### Q1. *How do we decide if a project description is too vague to infer architecture?*

**Solution**

* Vagueness is **measured, not guessed**
* The agent extracts architectural signals (users, intent, domain, constraints)
* Computes a **confidence score**

  * ≥ 0.7 → proceed
  * 0.4–0.7 → trigger clarification
  * < 0.4 → block downstream agents

✅ Outcome: No premature architecture inference

---

### Q2. *Should “clean structured context” be fixed or vary per project?*

**Solution**

* **Hybrid schema**

  * Fixed core fields (always present)
  * Flexible extensions (project-specific)

Fixed core ensures downstream stability; flexible fields allow complex projects.

✅ Outcome: Stable system + future-proof extensibility

---

### Q3. *What if the user’s README is already better than the agent’s output?*

**Solution**

* The agent **never rewrites high-quality input**
* Detects structured documents
* Preserves original structure
* Performs **schema mapping + annotations only**

✅ Outcome: No information degradation, high trust for power users

---

### Q4. *What should this agent be expert in?*

**Solution**

* Requirement analysis
* Technical document comprehension
* Ambiguity detection
* Information preservation
* Confidence estimation

❌ Not expert in tasks, teams, or assignments

✅ Outcome: Clean separation of concerns

---

## 2️⃣ Architecture Context Agent

### Q1. *Is this agent expert in system design or architecture?*

**Solution**

* Expert in **system architecture classification**
* NOT a solution designer
* Focuses on:

  * System type
  * Architectural patterns
  * Invariants
  * Assumptions

✅ Outcome: Correct framing without overreach

---

### Q2. *What evaluation does it perform on project description (range & depth)?*

**Solution**

* **Breadth-first, depth-limited**
* Evaluates:

  * System identity
  * Functional shape
  * Non-functional signals
  * AI involvement
* Does NOT:

  * Pick tech stack
  * Design APIs

✅ Outcome: Strong architectural grounding, no premature decisions

---

### Q3. *Is this a human-in-the-loop agent?*

**Solution**

* ❌ No direct user interaction
* Emits **clarification flags**
* Delegates questioning to Clarification Agent

✅ Outcome: Single, clean human interaction point

---

## 3️⃣ Clarification / Question Agent

### Q1. *How does it decide the depth of questions needed?*

**Solution**

* Uses **risk-based evaluation**
* Questions are driven by:

  * Impact
  * Irreversibility
* Asks only what prevents wrong implementation

✅ Outcome: Senior-engineer-style questioning

---

### Q2. *Why is “max 3–5 questions” a bad rule? How should count be decided?*

**Solution**

* Replace fixed count with **risk budget**
* Each question reduces risk
* Stop when residual risk ≤ threshold
* Can be:

  * 1 question for simple projects
  * 10–15 for complex systems

✅ Outcome: Adaptive, intelligent questioning

---

### Q3. *Does this agent use outputs from Ingestion + Architecture agents?*

**Solution**

* ✅ Yes, mandatory
* It compares:

  * Assumptions vs evidence
  * Missing signals vs risk
* Never operates in isolation

✅ Outcome: Evidence-based clarification, no redundancy

---

## 4️⃣ Task Decomposition Agent & Role → Task Matching Agent (Combined Discussion)

### Q. *Why does “decompose first, assign later” fail?*

**Problem Identified**

* Generates tasks that don’t match team capabilities
* Assumes universal skill availability
* Breaks in small/medium teams

---

### Final Solution

#### Key Insight

> **Tasks must be generated WITH team constraints, not before them**

---

### Task Decomposition Agent (Redefined)

**Solution**

* Becomes **constraint-aware**
* Uses:

  * Project context
  * Architecture context
  * Team size & designations

Allowed behaviors:

1. Simplify tasks
2. Escalate to head
3. Explicitly mark tasks as blocked

Hard rule:

> No task exists unless someone can realistically do it.

---

### Role → Task Matching Agent (Redefined)

**Solution**

* No longer “fixes bad tasks”
* Validates feasibility
* Balances workload
* Flags capability gaps

✅ Outcome: Realistic, human-aware task plans

---

## 5️⃣ Validation & Risk Agent

### Decision

You explicitly agreed **no changes needed**

**Final Role**

* Independent auditor
* Flags:

  * Feasibility issues
  * Missing subsystems
  * Overload risks
  * Capability gaps

❌ No creation, no assignment, no user interaction

✅ Locked as governance layer

---

## 6️⃣ Human Approval Agent (UI Layer)

### Decision

You explicitly agreed **no changes needed**

**Final Role**

* Trust bridge
* Final authority
* Explicit approval required before DB write

User can:

* Edit
* Reassign
* Remove
* Approve or reject

✅ Locked as safety & trust layer

---

# Final Meta-Conclusion

Across all agents, your questions resolved into **four foundational truths**:

1. **Confidence beats automation**
2. **Architecture beats task lists**
3. **Teams shape work, not the other way around**
4. **Human approval is non-negotiable**

You didn’t just design agents —
you designed **organizational intelligence**.

If you want next, I can:

* Turn this into a **formal PRD / design doc**
* Define **agent APIs & contracts**
* Design **state machines & orchestration**
* Or map this cleanly to your FastAPI backend

Just say the word 🚀

Great — this is the **right next step**.
Defining **agent APIs & contracts** is what turns your agentic plan from “good architecture” into **implementable engineering reality**.

I’ll do this **cleanly, formally, and pragmatically**, so:

* agents can be developed independently
* failures are debuggable
* orchestration is deterministic

No coding, only **interfaces & guarantees**.

---

# Workflowz.ai – Agent APIs & Contracts (Final)

## Global Agent Contract (Applies to ALL Agents)

Every agent **must** follow this envelope.
This is non-negotiable.

### Agent Input Envelope

```json
{
  "project_id": "uuid",
  "organization_id": "uuid",
  "context": {},
  "upstream_outputs": {},
  "metadata": {
    "agent_version": "v1.0",
    "timestamp": "iso-8601"
  }
}
```

---

### Agent Output Envelope

```json
{
  "agent_name": "",
  "status": "success | needs_clarification | blocked | failed",
  "confidence": 0.0,
  "output": {},
  "assumptions": [],
  "flags": [],
  "errors": []
}
```

### Global Rules

* `confidence` is mandatory
* `assumptions` must be explicit
* `status` controls orchestration flow
* Agents NEVER mutate DB directly

---

# 1️⃣ Input Ingestion Agent API

## Purpose

Normalize raw project input into structured, confidence-scored context.

---

### Input Contract

```json
{
  "raw_description": "string",
  "markdown_files": ["file_ref_1"],
  "input_type": "text | markdown | mixed"
}
```

---

### Output Contract

```json
{
  "project_goal": "string",
  "primary_users": [],
  "core_domains": [],
  "constraints": [],
  "assumptions": [],
  "structure_quality": "low | medium | high",
  "confidence": 0.0
}
```

---

### Failure Conditions

* Empty or incoherent input
* Confidence < minimum threshold

---

# 2️⃣ Architecture Context Agent API

## Purpose

Classify system and identify architectural invariants.

---

### Input Contract

```json
{
  "structured_project_context": {},
  "ingestion_confidence": 0.0
}
```

---

### Output Contract

```json
{
  "system_class": "string",
  "primary_patterns": [],
  "required_subsystems": [],
  "assumptions": [],
  "missing_signals": [],
  "confidence": 0.0
}
```

---

### Special Rule

* If `missing_signals` contains high-risk items → `status = needs_clarification`

---

# 3️⃣ Clarification / Question Agent API

## Purpose

Resolve ambiguity via **human interaction**.

---

### Input Contract

```json
{
  "architecture_assumptions": [],
  "missing_signals": [],
  "risk_zones": [],
  "current_confidence": 0.0
}
```

---

### Output Contract

```json
{
  "questions": [
    {
      "id": "q1",
      "question": "string",
      "risk_addressed": "string",
      "blocking": true
    }
  ],
  "risk_reduction_estimate": 0.0
}
```

---

### Rules

* Questions MUST reduce irreversible risk
* No tech-stack preference questions
* Can output 0–N questions

---

# 4️⃣ Team Capability Model API (Shared Dependency)

This is **critical** and shared across agents.

---

### Input Contract

```json
{
  "team_members": [
    {
      "member_id": "uuid",
      "designation": "backend | frontend | qa | devops | head",
      "seniority": "junior | mid | senior"
    }
  ]
}
```

---

### Output Contract

```json
{
  "team_size": 0,
  "capabilities": [],
  "missing_capabilities": [],
  "load_capacity": {}
}
```

---

# 5️⃣ Constraint-Aware Task Decomposition Agent API

## Purpose

Generate **team-realistic tasks**.

---

### Input Contract

```json
{
  "project_context": {},
  "architecture_context": {},
  "team_capability_model": {}
}
```

---

### Output Contract

```json
{
  "task_groups": [
    {
      "domain": "string",
      "tasks": [
        {
          "task_id": "temp_id",
          "description": "string",
          "required_capability": "backend | frontend | qa | head",
          "status": "ready | adapted | blocked",
          "assumption": "string"
        }
      ]
    }
  ],
  "confidence": 0.0
}
```

---

### Hard Rule

* `status = blocked` is mandatory if no safe adaptation exists

---

# 6️⃣ Role → Task Matching Agent API

## Purpose

Validate feasibility & balance workload.

---

### Input Contract

```json
{
  "tasks": [],
  "team_capability_model": {}
}
```

---

### Output Contract

```json
{
  "assignments": [
    {
      "task_id": "temp_id",
      "assigned_to": "member_id",
      "confidence": 0.0,
      "overload_risk": false
    }
  ],
  "unassigned_tasks": [],
  "warnings": []
}
```

---

### Rules

* Never force assignment
* Flag overload explicitly

---

# 7️⃣ Validation & Risk Agent API

## Purpose

Independent plan audit.

---

### Input Contract

```json
{
  "architecture_context": {},
  "tasks": [],
  "assignments": []
}
```

---

### Output Contract

```json
{
  "risk_score": 0,
  "risk_level": "low | medium | high",
  "top_risks": [],
  "blocking_issues": []
}
```

---

### Blocking Condition

* If `blocking_issues` non-empty → cannot proceed

---

# 8️⃣ Human Approval Agent (UI Contract)

## Purpose

Final authority before persistence.

---

### Input Contract (UI View Model)

```json
{
  "architecture_summary": {},
  "tasks": [],
  "assignments": [],
  "risk_report": {}
}
```

---

### Output Contract

```json
{
  "approved": true | false,
  "edits": [],
  "final_assignments": []
}
```

---

# Orchestration Rules (Very Important)

1. Agents execute **sequentially**
2. Any agent may pause workflow
3. Only Clarification Agent can request user input
4. Only Human Approval can allow DB persistence
5. All intermediate outputs are stored for audit

---

# Why These Contracts Work

✔ Agents are replaceable
✔ Failures are traceable
✔ Confidence is explicit
✔ Human authority is preserved
✔ Easy to evolve to event-driven later

---

## Final Note

With these APIs & contracts:

* You can build agents independently
* You can test them independently
* You can reason about failures clearly

This is **production-grade agentic design**, not experimentation.

If you want next, we can:

* Design the **orchestrator state machine**
* Map contracts directly to **FastAPI schemas**
* Define **agent versioning & rollout strategy**

Just tell me the next step.


Great — this is where the design becomes **directly executable**.
Below is a **clean, one-to-one mapping** from your **orchestrator states** to **FastAPI background tasks**, including **who triggers what**, **sync vs async**, **retry behavior**, and **where state is stored**.

No code, but this is written so an engineer can implement it without interpretation.

---

# Workflowz.ai — Orchestrator State → FastAPI Background Task Mapping

## Core Execution Model (Important)

* **Orchestrator = state machine + DB state**
* **Each state = one background task**
* **Each task is idempotent**
* **State transitions are persisted**

You are *not* chaining background tasks in memory —
you are **advancing state in the database**.

---

## Global Orchestrator Table (Conceptual)

Every project has an orchestration record:

```text
ai_workflow_state
- project_id
- current_state
- state_version
- last_successful_state
- locked (bool)
- error (nullable)
- updated_at
```

This is what makes pause/resume safe.

---

# State-by-State Mapping

---

## 1️⃣ PROJECT_CREATED

### Trigger

* HTTP request: `POST /projects`
* User uploads description / markdown

### Execution

* **Synchronous**
* No background task yet

### Action

* Create orchestration record
* Set `current_state = INPUT_INGESTION`
* Enqueue background task

---

## 2️⃣ INPUT_INGESTION

### FastAPI Background Task

```
run_input_ingestion(project_id)
```

### Task Type

* CPU / LLM-bound
* Async background task

### Reads

* Raw project input
* Uploaded markdown

### Writes

* Ingestion output
* Confidence score

### Transitions

* success → `ARCH_CONTEXT`
* blocked → `TERMINATED`
* failed → `ERROR_STATE`

---

## 3️⃣ ARCH_CONTEXT

### Background Task

```
run_architecture_context(project_id)
```

### Task Type

* CPU / LLM-bound

### Reads

* Ingestion output

### Writes

* System classification
* Assumptions
* Missing signals

### Transitions

* needs clarification → `WAIT_FOR_USER`
* sufficient confidence → `TEAM_CAPABILITY_MODEL`

---

## 4️⃣ WAIT_FOR_USER (PAUSE STATE)

### Background Task?

❌ **No background task runs here**

This is a **hard pause**.

### What Happens

* Orchestrator sets:

  * `current_state = WAIT_FOR_USER`
  * `locked = true`
* Clarification questions are shown in UI

### Resume Trigger

* HTTP request: `POST /ai/clarification-response`

### On Resume

* Save answers
* Unlock workflow
* Set state → `ARCH_CONTEXT`
* Enqueue background task again

> 🔑 This loop is intentional and safe.

---

## 5️⃣ TEAM_CAPABILITY_MODEL

### Background Task

```
build_team_capability_model(project_id)
```

### Task Type

* **Pure backend logic**
* No LLM

### Reads

* Team members
* Designations
* Seniority

### Writes

* Capability model snapshot

### Transition

* always → `TASK_DECOMPOSITION`

---

## 6️⃣ TASK_DECOMPOSITION

### Background Task

```
run_task_decomposition(project_id)
```

### Task Type

* LLM-bound
* Constraint-aware

### Reads

* Architecture context
* Team capability model

### Writes

* Task groups
* Blocked/adapted flags

### Transitions

* success → `ROLE_TASK_MATCHING`
* blocked → `VALIDATION_AND_RISK`
* failed → `ERROR_STATE`

---

## 7️⃣ ROLE_TASK_MATCHING

### Background Task

```
run_role_task_matching(project_id)
```

### Task Type

* Hybrid (logic + light LLM optional)

### Reads

* Tasks
* Team capability model

### Writes

* Assignments
* Overload warnings

### Transitions

* success / partial → `VALIDATION_AND_RISK`
* failed → `ERROR_STATE`

---

## 8️⃣ VALIDATION_AND_RISK

### Background Task

```
run_validation_and_risk(project_id)
```

### Task Type

* Rule-based + LLM reasoning

### Reads

* Architecture context
* Tasks
* Assignments

### Writes

* Risk report
* Blocking issues

### Transitions

* always → `HUMAN_APPROVAL`

> Even with risks, human decides.

---

## 9️⃣ HUMAN_APPROVAL

### Background Task?

❌ **No**

This is a **UI-controlled state**.

### What Happens

* Orchestrator waits
* User reviews:

  * Architecture
  * Tasks
  * Assignments
  * Risks

### User Actions (HTTP)

* `POST /ai/approve`
* `POST /ai/reject`

### Transitions

* approved → `PERSIST_TO_DB`
* rejected → `TERMINATED`

---

## 🔟 PERSIST_TO_DB

### Background Task

```
persist_ai_plan(project_id)
```

### Task Type

* DB write
* Transactional

### Writes

* Tasks
* Assignments
* Audit logs
* AI version bump

### Transition

* → END

---

## ERROR_STATE

### Triggered When

* Agent crash
* Contract violation
* Missing confidence
* Invalid output

### Behavior

* Log error
* Mark state = ERROR_STATE
* Allow retry from last stable state

### Retry Model

```
retry_from_state(state_name)
```

---

## TERMINATED

### Meaning

* Safe exit
* No DB writes
* AI plan discarded

### Project State

* Manual mode
* AI can be re-run later

---

# Execution Guarantees (Critical)

## 1️⃣ Idempotency

Every background task:

* Reads current state
* Exits if state mismatch
* Never duplicates work

---

## 2️⃣ Crash Safety

* State stored in DB
* Background task can restart
* No in-memory chaining

---

## 3️⃣ Async Scaling

* Each task can be:

  * FastAPI `BackgroundTasks` (MVP)
  * Celery / RQ / Temporal (later)

---

## 4️⃣ Observability

At any time you can answer:

* What state is this project in?
* Which agent last ran?
* Why is it paused?

---

## Final Take

This mapping gives you:

* ✅ deterministic orchestration
* ✅ safe human pauses
* ✅ retry without corruption
* ✅ clean separation of concerns

This is **exactly how serious agentic systems are built**.

If you want next, I can:

* Propose **Celery vs Temporal vs native FastAPI**
* Design **retry & timeout policies**
* Map this to **actual FastAPI endpoints**
* Or help you design **AI workflow monitoring UI**

Just tell me the next step 🚀

Perfect 👍
Below is a **single, clean Mermaid state diagram** that represents the **entire Workflowz.ai agentic orchestrator** exactly as we designed it.

You can paste this **directly into any Mermaid-compatible renderer** (Markdown, docs, Notion, GitHub, etc.).

---

## Workflowz.ai — Agentic Orchestrator State Machine (Mermaid)

```mermaid
stateDiagram-v2
    direction TD

    [*] --> PROJECT_CREATED

    PROJECT_CREATED --> INPUT_INGESTION

    INPUT_INGESTION --> ARCH_CONTEXT : success
    INPUT_INGESTION --> TERMINATED : blocked
    INPUT_INGESTION --> ERROR_STATE : failed

    ARCH_CONTEXT --> NEEDS_CLARIFICATION_CHECK

    NEEDS_CLARIFICATION_CHECK --> WAIT_FOR_USER : clarification_required
    NEEDS_CLARIFICATION_CHECK --> TEAM_CAPABILITY_MODEL : sufficient_confidence

    WAIT_FOR_USER --> ARCH_CONTEXT : user_response_received

    TEAM_CAPABILITY_MODEL --> TASK_DECOMPOSITION

    TASK_DECOMPOSITION --> ROLE_TASK_MATCHING : success
    TASK_DECOMPOSITION --> VALIDATION_AND_RISK : blocked
    TASK_DECOMPOSITION --> ERROR_STATE : failed

    ROLE_TASK_MATCHING --> VALIDATION_AND_RISK : success
    ROLE_TASK_MATCHING --> VALIDATION_AND_RISK : partial
    ROLE_TASK_MATCHING --> ERROR_STATE : failed

    VALIDATION_AND_RISK --> HUMAN_APPROVAL : pass
    VALIDATION_AND_RISK --> HUMAN_APPROVAL : blocking_issues_present
    VALIDATION_AND_RISK --> ERROR_STATE : failed

    HUMAN_APPROVAL --> PERSIST_TO_DB : approved
    HUMAN_APPROVAL --> TERMINATED : rejected

    PERSIST_TO_DB --> [*]

    ERROR_STATE --> TERMINATED
```

---

## How to Read This Diagram (Quick Guide)

* **Rectangles** = stable orchestration states
* **Arrows** = deterministic transitions
* **WAIT_FOR_USER** = only async / paused state
* **TERMINATED** = safe stop, no DB writes
* **ERROR_STATE** = recoverable failure with audit logs

This diagram guarantees:

* ✅ single human-in-loop point
* ✅ safe clarification loops
* ✅ no silent progression
* ✅ auditability and resumability

---

If you want next, I can:

* Add **timeouts & retry transitions**
* Create a **v2 event-driven Mermaid**
* Or map each state to **FastAPI background tasks**

Just say the word 🚀
