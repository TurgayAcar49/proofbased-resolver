# ProofBased

### Evidence-Based Decentralized Event Resolution

ProofBased is a decentralized event resolution primitive that determines whether a real-world event happened before or after a specified deadline using web evidence, evidence-aware reasoning, and decentralized consensus.

Instead of assuming that the absence of evidence means **NO**, ProofBased explicitly distinguishes between:

- **YES** — sufficient evidence confirms the event happened before the deadline.
- **NO** — sufficient evidence confirms the event happened after the deadline.
- **UNDETERMINED** — available evidence is insufficient, ambiguous, or only indicates a planned or scheduled event.

> **Absence of evidence is not evidence of NO.**

---

## The Problem

Smart contracts are deterministic, but many real-world questions cannot be answered from on-chain data alone.

For example:

> Did Protocol X launch its mainnet before June 30?

> Did Project Y distribute its promised airdrop before the deadline?

> Did Company Z complete the announced acquisition before a specific date?

The information needed to answer these questions often exists on the web:

- Official announcements
- Documentation
- Governance proposals
- Historical records
- Press releases
- Protocol websites
- News sources

Traditional smart contracts cannot directly interpret this information.

ProofBased provides a decentralized resolution layer between **web evidence and smart-contract state**.

---

## How It Works

~~~
                     Real World
                          |
                          v
                    Web Evidence
                          |
                          v
                  Evidence Collection
                          |
                          v
                   Evidence Analysis
                          |
                          v
                   Event Verification
                          |
                          v
                   Deadline Comparison
                          |
                          v
                 Decentralized Consensus
                          |
                          v
              +-----------+-----------+
              |           |           |
              v           v           v
             YES          NO     UNDETERMINED
~~~

ProofBased does not simply ask:

> "Can I find something about this event?"

It asks:

> "Is there sufficient evidence that proves the event occurred, and when did it occur relative to the deadline?"

---

## Resolution Logic

### 1. Insufficient Evidence

If the available evidence cannot establish that the event occurred:

~~~
UNDETERMINED
~~~

The system does not invent an answer.

### 2. Planned or Scheduled Event

A source may say:

~~~
will launch
planned for
scheduled for
expected to
announced that it will
~~~

This does not prove that the event actually happened.

Therefore:

~~~
PLANNED / SCHEDULED
        |
        v
UNDETERMINED
~~~

A planned event is not treated as a completed event.

### 3. Confirmed Event Before Deadline

If authoritative evidence confirms that the event occurred before the deadline:

~~~
CONFIRMED EVENT
      +
EVENT_DATE < DEADLINE
      |
      v
YES
~~~

### 4. Confirmed Event After Deadline

If authoritative evidence confirms that the event occurred after the deadline:

~~~
CONFIRMED EVENT
      +
EVENT_DATE > DEADLINE
      |
      v
NO
~~~

**NO does not mean "we couldn't find evidence."**

NO requires positive evidence that the event occurred outside the required timeframe.

---

## V2 Verified Test Cases

The current V2 implementation has been tested against the four fundamental resolution states.

### Test 1 — Insufficient Evidence

When the available evidence cannot establish that the event occurred:

~~~
Result:
UNDETERMINED
~~~

This demonstrates that ProofBased abstains when evidence is insufficient.

### Test 2 — Planned / Scheduled Event

When a source only describes an upcoming or scheduled event:

~~~
Result:
UNDETERMINED
~~~

The system correctly distinguishes:

~~~
ANNOUNCED
   !=
CONFIRMED
~~~

### Test 3 — Confirmed Event Before Deadline

#### Question

~~~
Did the Dencun network upgrade successfully activate
on Ethereum mainnet before March 20, 2024?
~~~

#### Deadline

~~~
2024-03-20
~~~

#### Evidence

Ethereum Foundation material confirms that the Dencun upgrade activated on Ethereum mainnet on:

~~~
2024-03-13
~~~

Since:

~~~
March 13 < March 20
~~~

the resolution is:

~~~
YES
~~~

#### Result

~~~json
{
  "decision": "YES",
  "event_date": "2024-03-13",
  "event_status": "CONFIRMED",
  "evidence_strength": "STRONG",
  "status": "RESOLVED"
}
~~~

### Test 4 — Confirmed Event After Deadline

#### Question

~~~
Did the Dencun network upgrade successfully activate
on Ethereum mainnet before March 1, 2024?
~~~

#### Deadline

~~~
2024-03-01
~~~

#### Evidence

Authoritative Ethereum Foundation material confirms:

~~~
Event date: March 13, 2024
~~~

Therefore:

~~~
March 13 > March 1
~~~

#### Result

~~~json
{
  "decision": "NO",
  "event_date": "2024-03-13",
  "event_status": "CONFIRMED",
  "evidence_strength": "STRONG",
  "confidence": 98,
  "status": "RESOLVED"
}
~~~

The reasoning correctly identifies positive counter-evidence:

~~~
The event is confirmed to have occurred on March 13, 2024.

March 13 is after the March 1, 2024 deadline.

Therefore: NO.
~~~

---

## Four-State Resolution Model

| Evidence State | Event Timing | Resolution |
|---|---|---|
| Insufficient | Unknown | **`UNDETERMINED`** |
| Planned / Scheduled | Unknown | **`UNDETERMINED`** |
| Confirmed | Before deadline | **`YES`** |
| Confirmed | After deadline | **`NO`** |

This four-state model is the foundation of ProofBased.

---

## On-Chain Deployment

ProofBased V3 is deployed on GenLayer at:

~~~
0xBB107edE20B3bB3B0c6f0d90D579e2e3209b9D0A
~~~

The V3 implementation has been tested through finalized resolution transactions covering:

~~~
Insufficient evidence
        |
        v
UNDETERMINED

Planned / scheduled event
        |
        v
UNDETERMINED

Confirmed event before deadline
        |
        v
YES

Confirmed event after deadline
        |
        v
NO
~~~

The resolution transactions were finalized using the **Normal (Full Consensus)** execution mode.

---

## Evidence Strength

ProofBased evaluates evidence quality instead of treating every source equally.

Current evidence levels include:

~~~
STRONG
MEDIUM
WEAK
INSUFFICIENT
~~~

Strong evidence can include:

- Official protocol documentation
- Official foundation announcements
- Official historical records
- Primary project documentation
- Direct protocol records

The goal is to prioritize evidence that directly establishes **what happened and when it happened**.

---

## Why UNDETERMINED Matters

Many automated systems are forced into binary decisions:

~~~
YES / NO
~~~

This creates a dangerous failure mode:

~~~
No evidence found
       |
       v
NO
~~~

ProofBased avoids this.

Instead:

~~~
No reliable evidence
       |
       v
UNDETERMINED
~~~

This is particularly important for prediction markets, automation, governance, insurance, reputation systems, and other applications where an incorrect negative resolution can have financial consequences.

---

## Architecture

~~~
+------------------------------+
|          User Query          |
|                              |
| Event + Deadline + Sources   |
+---------------+--------------+
                |
                v
+------------------------------+
|      Evidence Collection     |
|                              |
| Web pages / Documentation    |
| Official sources / Records   |
+---------------+--------------+
                |
                v
+------------------------------+
|      Evidence Analysis       |
|                              |
| Event detection              |
| Date extraction              |
| Status classification        |
| Evidence strength            |
+---------------+--------------+
                |
                v
+------------------------------+
|       Event Resolution       |
|                              |
| Confirmed?                   |
| Event date?                  |
| Deadline comparison?         |
+---------------+--------------+
                |
                v
+------------------------------+
|    Decentralized Consensus   |
|                              |
| Independent validators       |
| Evidence-based resolution    |
+---------------+--------------+
                |
                v
        YES / NO / UNDETERMINED
~~~

---

## Example Use Cases

### Protocol Launches

~~~
Did Protocol X launch its mainnet before June 30?
~~~

### Airdrops

~~~
Did Project X distribute the promised airdrop
before the stated deadline?
~~~

### Governance

~~~
Was Proposal X executed before the governance deadline?
~~~

### Partnerships

~~~
Did Company X officially complete the announced partnership
before date Y?
~~~

### Acquisitions

~~~
Did Company X complete the acquisition of Company Y
before the specified date?
~~~

### Product Releases

~~~
Did Project X release version 2.0 before the deadline?
~~~

### Compliance / Attestation

~~~
Did organization X publish the required report
before the specified date?
~~~

---

## Source Reliability

One of the next major improvements is explicit source classification.

Future versions will classify sources as:

~~~
PRIMARY
SECONDARY
UNKNOWN
~~~

For example:

~~~
Official historical record
        |
        v
PRIMARY

Official announcement
        |
        v
PRIMARY

Established news organization
        |
        v
SECONDARY

Unknown blog
        |
        v
UNKNOWN
~~~

This enables more robust conflict resolution.

For example:

~~~
Official source -> Event confirmed
Random blog     -> Event did not happen

        |
        v

PRIMARY > UNKNOWN

        |
        v

CONFIRMED
~~~

If evidence remains genuinely conflicting or insufficient:

~~~
UNDETERMINED
~~~

---

## Evidence Provenance

Future versions will preserve structured evidence provenance.

A resolution can be represented conceptually as:

~~~json
{
  "source": "...",
  "event_date": "2024-03-13",
  "event_status": "CONFIRMED",
  "evidence_strength": "STRONG",
  "evidence_summary": "...",
  "resolution": "NO"
}
~~~

This allows applications to answer:

> **Why was this event resolved this way?**

rather than exposing only:

~~~
YES
~~~

or:

~~~
NO
~~~

---

## Design Principles

### 1. Evidence First

A decision must be grounded in evidence.

### 2. No Forced Answers

When evidence is insufficient:

~~~
UNDETERMINED
~~~

### 3. Planned != Completed

Announcements and schedules do not prove execution.

### 4. NO Requires Positive Evidence

Failure to find evidence is not enough to resolve an event as NO.

### 5. Deadline Awareness

The actual event date must be compared against the specified deadline.

### 6. Provenance

Every resolution should be explainable through its underlying evidence.

### 7. Decentralization

Resolution should not depend on a single centralized oracle.

---

## Roadmap

### V2 — Completed

- Evidence-based event resolution
- Event date extraction
- Confirmed event detection
- Deadline comparison
- YES resolution
- NO resolution
- UNDETERMINED resolution
- Planned vs confirmed distinction
- Evidence strength
- Decentralized resolution flow
- Finalized V2 test transactions

### V3 — Next

- Multi-source evidence aggregation
- Source reliability classification
- Primary vs secondary source weighting
- Conflict resolution
- Evidence provenance
- Evidence hashing
- Improved confidence scoring
- Expanded event schemas

### Future

- Permissionless event creation
- Reusable resolution API
- SDK for decentralized applications
- Prediction-market integrations
- Governance integrations
- Insurance / conditional-payment integrations
- Automated event monitoring

---

## Why ProofBased?

The web contains enormous amounts of information about events that smart contracts cannot directly interpret.

AI systems can interpret web information, but AI alone should not be treated as an unquestionable source of truth.

ProofBased combines:

~~~
Web Evidence
      +
AI-Assisted Reasoning
      +
Evidence Validation
      +
Decentralized Consensus
      |
      v
On-Chain Event Resolution
~~~

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

## Project Status

ProofBased is currently at the **V2 prototype stage**.

The four fundamental resolution scenarios have been validated through finalized transactions:

~~~
INSUFFICIENT EVIDENCE
        |
        v
UNDETERMINED

PLANNED / SCHEDULED
        |
        v
UNDETERMINED

CONFIRMED + BEFORE DEADLINE
        |
        v
YES

CONFIRMED + AFTER DEADLINE
        |
        v
NO
~~~

The next development stage focuses on making the evidence layer more robust through multi-source verification, source reliability, conflict resolution, and provenance.

---

## License

MIT License

Copyright (c) 2026 ProofBased

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, subject to the conditions of the MIT License.
