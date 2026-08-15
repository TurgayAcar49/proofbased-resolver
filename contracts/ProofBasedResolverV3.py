# {"Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6"}

from genlayer import *
import typing


class ProofBasedResolverV3(gl.Contract):

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

        if self.status == "RESOLVED":
            raise gl.vm.UserError("ALREADY_RESOLVED")

        def leader_fn():

            # -------------------------------------------------
            # 1. FETCH WEB EVIDENCE
            # -------------------------------------------------

            MAX_SOURCE_CHARS = 40000

            def fetch_source(url: str) -> str:
                response = gl.nondet.web.get(url)
                return response.body.decode("utf-8")

            def compact_source(content: str) -> str:
                if len(content) <= MAX_SOURCE_CHARS:
                    return content

                head = 24000
                tail = 16000

                return (
                    content[:head]
                    + "\n\n[... MIDDLE OF SOURCE OMITTED ...]\n\n"
                    + content[-tail:]
                )

            content_1 = fetch_source(source_1)
            content_2 = fetch_source(source_2)

            content_1 = compact_source(content_1)
            content_2 = compact_source(content_2)

            # -------------------------------------------------
            # 2. EVIDENCE-BASED RESOLUTION
            # -------------------------------------------------

            prompt = f"""
You are an evidence-based decentralized event resolver.

Your task is to determine whether the real-world event described in the
QUESTION actually occurred before the DEADLINE.

You are NOT allowed to guess.

You must base the decision ONLY on the supplied source contents.

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
CORE PRINCIPLE
===========================================================

Distinguish carefully between:

1. A plan, announcement, proposal, roadmap, schedule, or expectation.
2. An event that was actually completed, activated, launched, deployed,
   finalized, or went live.

An announcement alone is NOT proof that an event occurred.

However, an announcement page may contain historical or later text
confirming that the event subsequently happened.

Therefore, you must examine the ENTIRE supplied source content and look
for explicit evidence of actual completion.


===========================================================
EVIDENCE HIERARCHY
===========================================================

STRONG evidence includes explicit statements such as:

- the event occurred on a specific date
- the event was activated on a specific date
- the event went live on a specific date
- the event launched on a specific date
- the event was successfully completed on a specific date
- a historical record explicitly records the event as having occurred
- a first-party source explicitly states that the event is already live,
  active, completed, or deployed

MODERATE evidence may be used when:

- multiple supplied sources independently confirm the same completed event
- a first-party source clearly describes the event as completed and provides
  a date, even if the wording is not exactly "launched" or "activated"

WEAK evidence includes:

- announcements without completion confirmation
- plans
- proposals
- roadmaps
- schedules
- expected dates
- future tense statements
- "will launch"
- "will activate"
- "is scheduled for"
- "is expected to"
- "plans to"
- "target date"
- "upcoming"

Weak evidence alone MUST NOT produce YES.


===========================================================
DATE EXTRACTION
===========================================================

You must identify the actual EVENT DATE, not merely the publication date
of an article.

Do NOT confuse:

- article publication date
- article update date
- announcement date
- scheduled date

with:

- actual event date

The event date must come from explicit evidence in the supplied sources.

If a source says that an event occurred on a particular date, use that date.

If a source gives both a planned date and a later confirmation that the event
actually occurred, use the actual occurrence date.

Do not invent, estimate, or infer a date.

Return:

"event_date": "YYYY-MM-DD"

only when the actual event date is sufficiently established.

Otherwise return:

"event_date": "UNKNOWN"


===========================================================
TEMPORAL DECISION
===========================================================

The question asks whether the event happened BEFORE the DEADLINE.

YES requires:

1. Positive evidence that the event actually happened.
2. A sufficiently established actual event date.
3. The actual event date is strictly earlier than the DEADLINE.

NO requires:

1. Positive evidence that the event actually happened after the DEADLINE,
   OR
2. Explicit evidence that establishes the event did not happen before the
   DEADLINE.

UNDETERMINED is required when:

- the event is only planned or scheduled
- the sources do not establish that the event actually occurred
- the actual event date cannot be established
- the supplied sources contain unresolved contradictory evidence
- the evidence is otherwise insufficient

IMPORTANT:

Do NOT return UNDETERMINED merely because the page is titled an
"announcement" or because the source was originally published before the
event.

Read the complete supplied content and determine whether that same source
contains explicit historical confirmation of the event.


===========================================================
SOURCE COMPARISON
===========================================================

Evaluate both sources independently.

For each source, determine internally:

- Does it contain evidence of actual occurrence?
- What date does it associate with the actual occurrence?
- Is that date an event date or merely a publication/scheduled date?
- Is the source first-party or authoritative?
- Does another supplied source confirm or contradict it?

Prefer authoritative first-party evidence when available.

If both sources confirm the same actual event and date, confidence should
generally be higher.

If one source contains only a plan but another authoritative source explicitly
confirms completion, use the completion evidence.


===========================================================
DO NOT USE PRIOR KNOWLEDGE
===========================================================

You MUST NOT rely on facts you remember from outside the supplied sources.

Even if you personally know that an event happened, that knowledge is irrelevant.

The decision must be reproducible from the supplied source contents alone.


===========================================================
IMPORTANT DENCUN-TYPE CASE
===========================================================

A source may be an announcement published before the actual event.

That does NOT automatically make the evidence insufficient.

If the supplied content explicitly states that the upgrade/event later
activated, launched, went live, or was completed, that statement is evidence
of actual occurrence.

In such a case:

- identify the actual occurrence date
- ignore the article publication date as the event date
- compare the actual occurrence date with the DEADLINE

Do not hardcode any particular event or date.


===========================================================
OUTPUT
===========================================================

Return ONLY one valid JSON object.

Do not use markdown.

Do not add commentary outside the JSON.

Required fields:

{{
    "decision": "YES | NO | UNDETERMINED",
    "event_date": "YYYY-MM-DD or UNKNOWN",
    "event_status": "CONFIRMED | NOT_CONFIRMED | UNKNOWN",
    "evidence_strength": "STRONG | MODERATE | WEAK | NONE",
    "confidence": 0,
    "evidence": "Short quote-free summary of the strongest evidence actually found",
    "reasoning": "Explain exactly why the evidence supports YES, NO, or UNDETERMINED"
}}

OUTPUT RULES:

- decision MUST be exactly YES, NO, or UNDETERMINED.
- event_status MUST be exactly CONFIRMED, NOT_CONFIRMED, or UNKNOWN.
- evidence_strength MUST be exactly STRONG, MODERATE, WEAK, or NONE.
- confidence MUST be an integer from 0 to 100.
- event_date MUST be YYYY-MM-DD or UNKNOWN.
- evidence MUST summarize actual evidence found in the supplied sources.
- reasoning MUST explain the temporal comparison with the DEADLINE.
- Do not invent facts.
- Do not use prior knowledge.
- Do not include markdown.
- Do not add extra JSON fields.
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
            # 4. DATE VALIDATION
            # -------------------------------------------------

            def is_valid_iso_date(value: str) -> bool:
                if len(value) != 10:
                    return False

                if (
                    value[4] != "-"
                    or value[7] != "-"
                ):
                    return False

                year_text = value[0:4]
                month_text = value[5:7]
                day_text = value[8:10]

                if not (
                    year_text.isdigit()
                    and month_text.isdigit()
                    and day_text.isdigit()
                ):
                    return False

                year = int(year_text)
                month = int(month_text)
                day = int(day_text)

                if year < 1:
                    return False

                if month < 1 or month > 12:
                    return False

                days_in_month = [
                    31,
                    29,
                    31,
                    30,
                    31,
                    30,
                    31,
                    31,
                    30,
                    31,
                    30,
                    31,
                ]

                if day < 1 or day > days_in_month[month - 1]:
                    return False

                if month == 2 and day == 29:
                    if (
                        year % 4 != 0
                        or (
                            year % 100 == 0
                            and year % 400 != 0
                        )
                    ):
                        return False

                return True

            if not is_valid_iso_date(deadline):
                raise gl.vm.UserError(
                    "INVALID_DEADLINE"
                )

            if event_date != "UNKNOWN":
                if not is_valid_iso_date(event_date):
                    raise gl.vm.UserError(
                        "INVALID_EVENT_DATE"
                    )

            # -------------------------------------------------
            # 5. INTERNAL CONSISTENCY RULES
            # -------------------------------------------------

            # YES requires confirmed event + sufficient evidence
            # + actual event date strictly before deadline.

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
            # missing, contradictory, or the date cannot be established.

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

            # Validator independently fetches the same sources
            # and independently evaluates the evidence.

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
            # Event status must agree.
            # -------------------------------------------------

            if (
                leader_data["event_status"]
                != validator_result["event_status"]
            ):
                return False

            # -------------------------------------------------
            # Evidence strength may differ by one level.
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

            if abs(
                leader_strength - validator_strength
            ) > 1:
                return False

            # -------------------------------------------------
            # Event-date consistency.
            # -------------------------------------------------

            leader_event_date = leader_data["event_date"]
            validator_event_date = validator_result["event_date"]

            # If both independently establish a date, require
            # the same actual date.

            if (
                leader_event_date != "UNKNOWN"
                and validator_event_date != "UNKNOWN"
            ):
                if leader_event_date != validator_event_date:
                    return False

            # For YES, both must establish an actual event date.

            if leader_data["decision"] == "YES":

                if leader_event_date == "UNKNOWN":
                    return False

                if validator_event_date == "UNKNOWN":
                    return False

                if leader_event_date >= deadline:
                    return False

                if validator_event_date >= deadline:
                    return False

            # For NO, both must establish an actual event date.

            if leader_data["decision"] == "NO":

                if leader_event_date == "UNKNOWN":
                    return False

                if validator_event_date == "UNKNOWN":
                    return False

                if leader_event_date <= deadline:
                    return False

                if validator_event_date <= deadline:
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
