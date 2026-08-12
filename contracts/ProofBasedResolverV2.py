# {"Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6"}

from genlayer import *
import typing


class ProofBasedResolverV2(gl.Contract):

    question: str
    deadline: str

    source_1: str
    source_2: str

    decision: str
    event_date: str
    event_status: str
    evidence_strength: str

    confidence: u8
    evidence: str
    reasoning: str

    status: str

    def __init__(self):
        self.question = ""
        self.deadline = ""

        self.source_1 = ""
        self.source_2 = ""

        self.decision = "PENDING"
        self.event_date = ""
        self.event_status = "UNKNOWN"
        self.evidence_strength = "NONE"

        self.confidence = 0
        self.evidence = ""
        self.reasoning = ""

        self.status = "PENDING"

    @gl.public.write
    def resolve(
        self,
        question: str,
        deadline: str,
        source_1: str,
        source_2: str,
    ) -> typing.Any:

        def leader_fn():

            # -------------------------------------------------
            # 1. FETCH WEB EVIDENCE
            # -------------------------------------------------

            response_1 = gl.nondet.web.get(source_1)
            response_2 = gl.nondet.web.get(source_2)

            content_1 = response_1.body.decode("utf-8")[:14000]
            content_2 = response_2.body.decode("utf-8")[:14000]

            # -------------------------------------------------
            # 2. EVIDENCE-BASED RESOLUTION
            # -------------------------------------------------

            prompt = f"""
You are an evidence-based decentralized event resolver.

Your job is NOT to guess the answer.

You must determine whether the event described in the
QUESTION actually happened before the DEADLINE.

QUESTION:
{question}

DEADLINE:
{deadline}

SOURCE 1:
URL: {source_1}

CONTENT:
{content_1}

SOURCE 2:
URL: {source_2}

CONTENT:
{content_2}

===========================================================
STRICT EVIDENCE RULES
===========================================================

RULE 1:
Use ONLY information contained in the supplied sources.

RULE 2:
Do not use your prior knowledge.

RULE 3:
Do not treat an announcement, plan, roadmap, schedule,
expectation, or prediction as proof that an event actually
happened.

Examples of WEAK evidence:

- "will launch"
- "is scheduled to launch"
- "expected to launch"
- "plans to launch"
- "will activate"
- "is planned for"

These statements do NOT prove that the event happened.

RULE 4:
For YES, there must be positive evidence that the event
actually happened BEFORE the deadline.

Acceptable examples include:

- "launched on March 13"
- "activated on March 13"
- "went live on March 13"
- an authoritative historical record showing the event
  occurred on a specific date

RULE 5:
For NO, absence of evidence is NOT enough.

You may return NO only if the supplied evidence positively
shows that the event happened AFTER the deadline, OR
explicitly shows that the event did not happen before the
deadline.

RULE 6:
If the sources only show planning, scheduling, announcements,
or insufficient evidence, return UNDETERMINED.

RULE 7:
If sources contradict each other and the contradiction cannot
be resolved using authoritative evidence, return
UNDETERMINED.

RULE 8:
Dates must come from the supplied evidence.

RULE 9:
Do not invent or infer an event date.

RULE 10:
Prefer authoritative first-party sources over secondary
sources when assessing evidence quality.

===========================================================
DECISION LOGIC
===========================================================

YES:

The event is positively confirmed as having happened before
the deadline.

NO:

The event is positively confirmed as having happened after
the deadline, or the evidence explicitly establishes that it
did not happen before the deadline.

UNDETERMINED:

Evidence is insufficient, only describes plans/schedules,
contains unresolved contradictions, or does not establish
whether the event happened before the deadline.

===========================================================
OUTPUT
===========================================================

Return ONLY a JSON object.

Required fields:

{{
    "decision": "YES | NO | UNDETERMINED",

    "event_date": "YYYY-MM-DD or UNKNOWN",

    "event_status": "CONFIRMED | NOT_CONFIRMED | UNKNOWN",

    "evidence_strength": "STRONG | MODERATE | WEAK | NONE",

    "confidence": 0,

    "evidence": "Short quote-free summary of the strongest
                  evidence actually found",

    "reasoning": "Explain exactly why the evidence supports
                  YES, NO, or UNDETERMINED"
}}

IMPORTANT:

confidence MUST be an integer from 0 to 100.

Do NOT put markdown around the JSON.

Do NOT add extra fields.

Do NOT use prior knowledge.
"""

            result = gl.nondet.exec_prompt(
                prompt,
                response_format="json"
            )

            # -------------------------------------------------
            # 3. BASIC RESPONSE VALIDATION
            # -------------------------------------------------

            if not isinstance(result, dict):
                raise gl.vm.UserError(
                    "INVALID_LLM_RESPONSE"
                )

            decision = result.get("decision")
            event_date = result.get("event_date")
            event_status = result.get("event_status")
            evidence_strength = result.get("evidence_strength")
            confidence = result.get("confidence")
            evidence = result.get("evidence")
            reasoning = result.get("reasoning")

            if decision not in [
                "YES",
                "NO",
                "UNDETERMINED"
            ]:
                raise gl.vm.UserError(
                    "INVALID_DECISION"
                )

            if event_status not in [
                "CONFIRMED",
                "NOT_CONFIRMED",
                "UNKNOWN"
            ]:
                raise gl.vm.UserError(
                    "INVALID_EVENT_STATUS"
                )

            if evidence_strength not in [
                "STRONG",
                "MODERATE",
                "WEAK",
                "NONE"
            ]:
                raise gl.vm.UserError(
                    "INVALID_EVIDENCE_STRENGTH"
                )

            if not isinstance(confidence, int):
                raise gl.vm.UserError(
                    "INVALID_CONFIDENCE"
                )

            if confidence < 0 or confidence > 100:
                raise gl.vm.UserError(
                    "INVALID_CONFIDENCE"
                )

            if not isinstance(event_date, str):
                raise gl.vm.UserError(
                    "INVALID_EVENT_DATE"
                )

            if not isinstance(evidence, str):
                raise gl.vm.UserError(
                    "INVALID_EVIDENCE"
                )

            if not isinstance(reasoning, str):
                raise gl.vm.UserError(
                    "INVALID_REASONING"
                )

            # -------------------------------------------------
            # 4. INTERNAL CONSISTENCY RULES
            # -------------------------------------------------
    
            # YES requires confirmed event + actual evidence.
            if decision == "YES":
    
                if event_status != "CONFIRMED":
                    raise gl.vm.UserError(
                        "YES_REQUIRES_CONFIRMED_EVENT"
                    )
    
                if evidence_strength not in [
                    "STRONG",
                    "MODERATE"
                ]:
                    raise gl.vm.UserError(
                        "YES_REQUIRES_SUFFICIENT_EVIDENCE"
                    )
    
                if event_date == "UNKNOWN":
                    raise gl.vm.UserError(
                        "YES_REQUIRES_EVENT_DATE"
                    )
    
                if event_date >= deadline:
                    raise gl.vm.UserError(
                        "YES_EVENT_NOT_BEFORE_DEADLINE"
                    )
    
            # NO requires confirmed event after deadline.
            if decision == "NO":
    
                if event_status != "CONFIRMED":
                    raise gl.vm.UserError(
                        "NO_REQUIRES_CONFIRMED_EVENT"
                    )
    
                if evidence_strength not in [
                    "STRONG",
                    "MODERATE"
                ]:
                    raise gl.vm.UserError(
                        "NO_REQUIRES_SUFFICIENT_EVIDENCE"
                    )
    
                if event_date == "UNKNOWN":
                    raise gl.vm.UserError(
                        "NO_REQUIRES_EVENT_DATE"
                    )
    
                if event_date <= deadline:
                    raise gl.vm.UserError(
                        "NO_EVENT_NOT_AFTER_DEADLINE"
                    )
    
            # UNDETERMINED is allowed when evidence is weak,
            # missing, or contradictory.
    
            return {
                "decision": decision,
                "event_date": event_date,
                "event_status": event_status,
                "evidence_strength": evidence_strength,
                "confidence": confidence,
                "evidence": evidence,
                "reasoning": reasoning,
            }

        # -----------------------------------------------------
        # VALIDATOR
        # -----------------------------------------------------

        def validator_fn(leader_result) -> bool:

            if not isinstance(
                leader_result,
                gl.vm.Return
            ):
                return False

            leader_data = leader_result.calldata

            # Independently fetch and evaluate the evidence.
            validator_result = leader_fn()

            # -------------------------------------------------
            # Core decision must agree.
            # -------------------------------------------------

            if (
                leader_data["decision"]
                != validator_result["decision"]
            ):
                return False

            # -------------------------------------------------
            # Event status must also agree.
            # -------------------------------------------------

            if (
                leader_data["event_status"]
                != validator_result["event_status"]
            ):
                return False

            # -------------------------------------------------
            # Evidence strength should not contradict.
            # -------------------------------------------------

            strength_order = {
                "NONE": 0,
                "WEAK": 1,
                "MODERATE": 2,
                "STRONG": 3,
            }

            leader_strength = strength_order.get(
                leader_data["evidence_strength"],
                -1
            )

            validator_strength = strength_order.get(
                validator_result["evidence_strength"],
                -1
            )

            if leader_strength < 0:
                return False

            if validator_strength < 0:
                return False

            # Allow one level of difference because independent
            # LLMs may rate evidence slightly differently.
            if abs(
                leader_strength - validator_strength
            ) > 1:
                return False

            # -------------------------------------------------
            # For YES, both must have an actual event date.
            # -------------------------------------------------

            if leader_data["decision"] == "YES":

                if leader_data["event_date"] == "UNKNOWN":
                    return False

                if validator_result["event_date"] == "UNKNOWN":
                    return False

            return True

        # -----------------------------------------------------
        # CONSENSUS
        # -----------------------------------------------------

        result = gl.vm.run_nondet_unsafe(
            leader_fn,
            validator_fn
        )

        # -----------------------------------------------------
        # DETERMINISTIC STORAGE
        # -----------------------------------------------------

        self.question = question
        self.deadline = deadline

        self.source_1 = source_1
        self.source_2 = source_2

        self.decision = result["decision"]
        self.event_date = result["event_date"]
        self.event_status = result["event_status"]

        self.evidence_strength = result[
            "evidence_strength"
        ]

        self.confidence = result["confidence"]
        self.evidence = result["evidence"]
        self.reasoning = result["reasoning"]

        self.status = "RESOLVED"

    @gl.public.view
    def get_result(self) -> typing.Any:

        return {
            "question": self.question,
            "deadline": self.deadline,

            "source_1": self.source_1,
            "source_2": self.source_2,

            "decision": self.decision,

            "event_date": self.event_date,
            "event_status": self.event_status,
            "evidence_strength": self.evidence_strength,

            "confidence": self.confidence,
            "evidence": self.evidence,
            "reasoning": self.reasoning,

            "status": self.status,
        }
