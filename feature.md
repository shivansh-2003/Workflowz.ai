# Workflowz.ai — Core Features

## Overview

Workflowz.ai is a project management platform that helps teams organize, track, and manage projects, tasks, and team members. Its **core feature** is an **agentic AI system** that turns project descriptions into realistic, team-aware work plans—architecture-first, human-in-the-loop, with explicit approval before any persistence.

**Core philosophy:**
1. Architecture-first, not task-first
2. People-aware planning (team size and capability are first-class inputs)
3. Human-in-the-loop is mandatory
4. Explainability over automation
5. Never invent capability or certainty

**Pipeline:**
```
Project Created
   → Input Ingestion Agent
   → Architecture Context Agent
   → Clarification / Question Agent (Human-in-loop)
   → Constraint-Aware Task Decomposition Agent
   → Role → Task Matching Agent
   → Validation & Risk Agent
   → Human Approval Agent (UI)
   → Persist Tasks & Assignments
```

---

## Features

### Authentication & Authorization
- JWT-based authentication with OAuth2 password flow
- Secure password hashing using bcrypt
- Token-based session management

### Role-Based Access Control (RBAC)
- **Superuser:** Full access to the platform. Can create users, manage all organizations, and access superuser-only endpoints.
- **Organization Head:** Can manage projects and tasks within their organization. Required for creating projects, adding team members, and approving AI-generated plans.
- **Member:** Can view and update tasks assigned to them. Scoped to their organization.
- **Team position:** Within a team, members have a position (`head` or `member`), which affects task assignment and workload visibility.
- Permissions are enforced at the API layer; each role sees only the data they are authorized to access.

### Multi-Tenancy
- Organization-scoped data isolation
- Each organization operates independently
- Superuser can manage multiple organizations

### Project Management
- Create and manage projects within organizations
- Automatic project progress calculation (0–100%)
- Project descriptions and metadata
- Created-by tracking

### Task Management
- Create, update, and delete tasks
- Assign tasks to team members
- Set priorities (high, medium, low)
- Set deadlines and track completion status
- Task filtering and organization

### Team Management
- Add/remove team members
- Assign roles (head/member)
- Track member designations
- View team composition

### User Interface
- Modern Streamlit-based web interface
- Responsive design
- Real-time updates
- Intuitive navigation

---

## Functionalities (AI Agents)

### 1. Input Ingestion Agent
- **Role:** Requirement comprehension and normalization  
- **Functionality:** Parse text/markdown, extract architectural signals, measure confidence, preserve user structure. Outputs structured context (project_goal, primary_users, core_domains, constraints, assumptions, confidence). Blocks downstream agents if confidence is too low. Never hallucinates or simplifies meaning.

### 2. Architecture Context Agent
- **Role:** System classification and invariant detection  
- **Functionality:** Classify system type, identify primary patterns and required subsystems, state assumptions, identify architectural risk zones. Outputs system_class, primary_patterns, required_subsystems, assumptions, confidence. No tech stack decisions, task creation, or direct user interaction.

### 3. Clarification / Question Agent (Human-in-the-loop)
- **Role:** Ambiguity resolver and implementation gatekeeper  
- **Functionality:** Compare assumptions vs evidence, quantify implementation risk, ask minimum necessary questions (MCQ: single/multiple/boolean), group questions logically. Uses risk budget (not fixed question count); stops when residual risk ≤ threshold. Only agent allowed to ask the user questions. Never asks tech preference or “nice to know” questions.

### 4. Constraint-Aware Task Decomposition Agent
- **Role:** Generate realistic work plans  
- **Functionality:** Uses project context, architecture context, and team capability model. Generates tasks that match team capabilities, are safely simplified, or explicitly marked blocked. Strategies: task compression, escalation to head, explicit blocking. No task may exist unless at least one team member can realistically execute it.

### 5. Role → Task Matching Agent
- **Role:** Feasibility validator and workload balancer  
- **Functionality:** Confirm role compatibility, balance workload, flag overloads and mismatches, suggest scope reduction or escalation. Never forces assignment or hides capability gaps.

### 6. Validation & Risk Agent
- **Role:** Independent AI auditor  
- **Functionality:** Validates architectural completeness, task feasibility, capability gaps, load imbalance, security and workflow invariants. Outputs risk_score, risk_level, top_risks. No task creation, assignment, or user interaction.

### 7. Human Approval Agent (UI)
- **Role:** Trust bridge and final authority  
- **Functionality:** User can review architecture summary, edit tasks, reassign tasks, remove tasks, approve or reject plan. Nothing is written to the database without explicit human approval.

---

### Cross-Cutting

- **Explainability:** Every task answers why it exists, why the assignee, and what assumption it depends on.
- **Confidence & assumptions:** Every agent outputs confidence; assumptions are visible and revisitable.
- **No silent failure:** If the AI cannot proceed safely, it stops, explains why, and asks for help.
- **Auditability:** Original input, agent outputs, assumptions, and user approvals are stored.

---

*Overview, features, and functionalities for Workflowz.ai.*
