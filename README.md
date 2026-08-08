# ProofBased

### Evidence-Based Decentralized Event Resolution

ProofBased is a decentralized event resolution primitive that determines whether a real-world event happened before or after a specified deadline using verifiable web evidence, evidence-aware reasoning, and decentralized consensus.

Instead of assuming that the absence of evidence means **NO**, ProofBased explicitly distinguishes between:

* **YES** — sufficient evidence confirms the event happened before the deadline.
* **NO** — sufficient evidence confirms the event happened after the deadline.
* **UNDETERMINED** — available evidence is insufficient, ambiguous, or only indicates a planned/scheduled event.

> **Absence of evidence is not evidence of NO.**

---

## The Problem

Smart contracts are deterministic, but many real-world questions cannot be answered from on-chain data alone.

For example:

> Did Protocol X launch its mainnet before June 30, 2026?

> Did Project Y distribute its promised airdrop before the deadline?

> Did Company Z complete the announced acquisition before a specific date?

The information needed to answer these questions often exists on the web:

* Official announcements
* Documentation
* Governance proposals
* Historical records
* Press releases
* Blockchain ecosystem websites
* News sources

Traditional smart contracts cannot directly interpret this information.

ProofBased provides a decentralized resolution layer between **web evidence and smart-contract state**.

---

## Core Concept

```text
                    Real World
                        │
                        ▼
                  Web Evidence
                        │
                        ▼
              Evidence Collection
                        │
                        ▼
                Evidence Analysis
                        │
                        ▼
              Event Verification
                        │
                        ▼
               Deadline Comparison
                        │
                        ▼
              Decentralized Consensus
                        │
                        ▼
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
         YES            NO      UNDETERMINED
```

ProofBased does not simply ask:

> "Can I find something about this event?"

It asks:

> "Is there sufficient evidence that proves the event occurred, and when did it occur relative to the deadline?"

---

# Resolution Logic

ProofBased follows a strict resolution model.

### 1. Insufficient Evidence

If the available sources cannot establish that the event occurred:

```text
→ UNDETERMINED
```

The system does not invent an answer.

---

### 2. Planned or Scheduled Event

A source may say:

```text
will launch
planned for
scheduled for
expected to
announced that it will
```

This does not prove that the event actually happened.

Therefore:

```text
PLANNED / SCHEDULED
        ↓
UNDETERMINED
```

---

### 3. Confirmed Event Before Deadline

If authoritative evidence confirms that the event occurred before the deadline:

```text
CONFIRMED EVENT
        +
EVENT_DATE < DEADLINE
        ↓
YES
```

---

### 4. Confirmed Event After Deadline

If authoritative evidence confirms that the event occurred after the deadline:

```text
CONFIRMED EVENT
        +
EVENT_DATE > DEADLINE
        ↓
NO
```

This is an important distinction.

**NO does not mean "we couldn't find evidence."**

NO requires positive evidence that the event occurred outside the required timeframe.

---

# V2 Verified Test Cases

The current V2 implementation has been tested against the four fundamental resolution states.

## Test 1 — Insufficient Evidence

When the available evidence cannot establish that the event occurred:

```text
Result:
UNDETERMINED
```

This demonstrates that ProofBased abstains when evidence is insufficient.

---

## Test 2 — Planned / Scheduled Event

When a source only describes an upcoming or scheduled event:

```text
Result:
UNDETERMINED
```

The system correctly distinguishes:

```text
ANNOUNCED
≠
CONFIRMED
```

A planned event is not treated as an event that has already happened.

---

## Test 3 — Confirmed Event Before Deadline

### Question

```text
Did the Dencun network upgrade successfully activate
on Ethereum mainnet before March 20, 2024?
```

### Deadline

```text
2024-03-20
```

### Evidence

Ethereum Foundation material confirms that the Dencun upgrade activated on Ethereum mainnet on:

```text
2024-03-13
```

Since:

```text
March 13 < March 20
```

the resolution is:

```text
YES
```

### Result

```json
{
  "decision": "YES",
  "event_date": "2024-03-13",
  "event_status": "CONFIRMED",
  "evidence_strength": "STRONG",
  "status": "RESOLVED"
}
```

---

## Test 4 — Confirmed Event After Deadline

### Question

```text
Did the Dencun network upgrade successfully activate
on Ethereum mainnet before March 1, 2024?
```

### Deadline

```text
2024-03-01
```

### Evidence

Authoritative Ethereum Foundation material confirms:

```text
Event date: March 13, 2024
```

Therefore:

```text
March 13 > March 1
```

### Result

```json
{
  "decision": "NO",
  "event_date": "2024-03-13",
  "event_status": "CONFIRMED",
  "evidence_strength": "STRONG",
  "confidence": 98,
  "status": "RESOLVED"
}
```

The reasoning correctly identifies **positive counter-evidence**:

```text
The event is confirmed to have occurred on
March 13, 2024.

March 13 is after the March 1, 2024 deadline.

Therefore: NO.
```

---

# Four-State Resolution Model

The core V2 behavior can be summarized as:

| Evidence State      | Event Timing    | Resolution     |
| ------------------- | --------------- | -------------- |
| Insufficient        | Unknown         | `UNDETERMINED` |
| Planned / Scheduled | Unknown         | `UNDETERMINED` |
| Confirmed           | Before deadline | `YES`          |
| Confirmed           | After deadline  | `NO`           |

This four-state model is the foundation of ProofBased.

---

# Evidence Strength

ProofBased evaluates evidence quality instead of treating every source equally.

Current evidence levels include:

```text
STRONG
MEDIUM
WEAK
INSUFFICIENT
```

A strong source can include:

* Official protocol documentation
* Official foundation announcements
* Official historical records
* Primary project documentation
* Direct on-chain or protocol records

The goal is to prioritize evidence that directly establishes **what happened and when it happened**.

---

# Why UNDETERMINED Matters

Many automated systems are forced into binary decisions:

```text
YES / NO
```

This creates a dangerous failure mode:

```text
No evidence found
       ↓
       NO
```

ProofBased avoids this.

Instead:

```text
No reliable evidence
       ↓
UNDETERMINED
```

This is particularly important for prediction markets, automation, governance, insurance, reputation systems, and other applications where an incorrect negative resolution can have financial consequences.

---

# Architecture

```text
┌──────────────────────────────┐
│          User Query          │
│                              │
│ Event + Deadline + Sources   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Evidence Collection     │
│                              │
│ Web pages / Documentation    │
│ Official sources / Records   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Evidence Analysis       │
│                              │
│ Event detection              │
│ Date extraction              │
│ Status classification        │
│ Evidence strength            │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Event Resolution       │
│                              │
│ Confirmed?                   │
│ Event date?                  │
│ Deadline comparison?         │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│    Decentralized Consensus   │
│                              │
│ Independent validators       │
│ Evidence-based resolution    │
└──────────────┬───────────────┘
               │
               ▼
        YES / NO / UNDETERMINED
```

---

# On-Chain Resolution

The resolution is ultimately represented on-chain.

The smart contract provides the deterministic state layer while evidence analysis provides the information required to resolve real-world events.

Current V2 deployment:

```text
0x1D...03ca
```

> Replace the shortened address above with the full V2 contract address before the final public release.

---

# Example Use Cases

ProofBased is designed to be generic.

### Protocol Launches

```text
Did Protocol X launch its mainnet before June 30?
```

### Airdrops

```text
Did Project X distribute the promised airdrop
before the stated deadline?
```

### Governance

```text
Was Proposal X executed before the governance deadline?
```

### Partnerships

```text
Did Company X officially complete the announced partnership
before date Y?
```

### Acquisitions

```text
Did Company X complete the acquisition of Company Y
before the specified date?
```

### Product Releases

```text
Did Project X release version 2.0 before the deadline?
```

### Compliance / Attestation

```text
Did organization X publish the required report
before the specified date?
```

---

# Source Reliability

One of the next major improvements is explicit source classification.

Future versions will classify sources as:

```text
PRIMARY
SECONDARY
UNKNOWN
```

For example:

```text
Official historical record
        ↓
PRIMARY

Official announcement
        ↓
PRIMARY

Established news organization
        ↓
SECONDARY

Unknown blog
        ↓
UNKNOWN
```

This enables more robust conflict resolution.

For example:

```text
Official source → Event confirmed
Random blog    → Event did not happen

                ↓

        PRIMARY > UNKNOWN

                ↓

           CONFIRMED
```

If evidence remains genuinely conflicting or insufficient:

```text
→ UNDETERMINED
```

---

# Evidence Provenance

Future versions will also preserve structured evidence provenance.

A resolution can be represented conceptually as:

```json
{
  "source": "...",
  "event_date": "2024-03-13",
  "event_status": "CONFIRMED",
  "evidence_strength": "STRONG",
  "evidence_summary": "...",
  "resolution": "NO"
}
```

This allows applications to answer:

> **Why was this event resolved this way?**

rather than exposing only:

```text
YES
```

or:

```text
NO
```

---

# Design Principles

## 1. Evidence First

A decision must be grounded in evidence.

## 2. No Forced Answers

When evidence is insufficient:

```text
UNDETERMINED
```

## 3. Planned ≠ Completed

Announcements and schedules do not prove execution.

## 4. NO Requires Positive Evidence

Failure to find evidence is not enough to resolve an event as NO.

## 5. Deadline Awareness

The actual event date must be compared against the specified deadline.

## 6. Provenance

Every resolution should be explainable through its underlying evidence.

## 7. Decentralization

Resolution should not depend on a single centralized oracle.

---

# Roadmap

### V2 — Completed

* [x] Evidence-based event resolution
* [x] Event date extraction
* [x] Confirmed event detection
* [x] Deadline comparison
* [x] YES resolution
* [x] NO resolution
* [x] UNDETERMINED resolution
* [x] Planned vs confirmed distinction
* [x] Evidence strength
* [x] Decentralized resolution flow

### V3 — Next

* [ ] Multi-source evidence aggregation
* [ ] Source reliability classification
* [ ] Primary vs secondary source weighting
* [ ] Conflict resolution
* [ ] Evidence provenance
* [ ] Evidence hashing
* [ ] Improved confidence scoring
* [ ] Expanded event schemas

### Future

* [ ] Permissionless event creation
* [ ] Reusable resolution API
* [ ] SDK for decentralized applications
* [ ] Prediction-market integrations
* [ ] Governance integrations
* [ ] Insurance / conditional-payment integrations
* [ ] Automated event monitoring

---

# Why ProofBased?

The web contains enormous amounts of information about events that smart contracts cannot directly interpret.

At the same time, AI systems can interpret web information but are not inherently trusted as deterministic sources of truth.

ProofBased combines:

```text
Web Evidence
      +
AI-Assisted Reasoning
      +
Evidence Validation
      +
Decentralized Consensus
      ↓
Deterministic On-Chain Resolution
```

The goal is not to make an AI "guess" what happened.

The goal is to create a system that can answer:

> **What happened?**

> **When did it happen?**

> **What evidence proves it?**

> **Did it happen before the deadline?**

> **Is the evidence strong enough to resolve the event?**

And when those questions cannot be answered reliably:

> **UNDETERMINED**

---

# Project Status

ProofBased is currently at the **V2 prototype stage**.

The four fundamental resolution scenarios have been validated:

```text
INSUFFICIENT EVIDENCE
        ↓
UNDETERMINED

PLANNED / SCHEDULED
        ↓
UNDETERMINED

CONFIRMED + BEFORE DEADLINE
        ↓
YES

CONFIRMED + AFTER DEADLINE
        ↓
NO
```

The next development stage focuses on making the evidence layer more robust through multi-source verification, source reliability, conflict resolution, and provenance.

---

# License

MIT License

Copyright (c) 2026 ProofBased

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, subject to the conditions of the MIT License.
