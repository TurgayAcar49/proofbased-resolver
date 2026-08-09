import json


SOURCE_1 = "https://example.com/source-1"
SOURCE_2 = "https://example.com/source-2"


def setup_web_mocks(direct_vm):
    direct_vm.mock_web(
        r"example\.com/source-1",
        {
            "status": 200,
            "body": "Authoritative event evidence."
        },
    )

    direct_vm.mock_web(
        r"example\.com/source-2",
        {
            "status": 200,
            "body": "Secondary event evidence."
        },
    )


def setup_llm_mock(direct_vm, result):
    direct_vm.mock_llm(
        r".*",
        json.dumps(result),
    )


def resolve_contract(
    direct_vm,
    direct_deploy,
    llm_result,
):
    setup_web_mocks(direct_vm)
    setup_llm_mock(direct_vm, llm_result)

    contract = direct_deploy(
        "contracts/ProofBasedResolverV2.py"
    )

    contract.resolve(
        "Did the event happen before the deadline?",
        "2024-03-20",
        SOURCE_1,
        SOURCE_2,
    )

    return contract.get_result()


def test_initial_state(direct_deploy):
    contract = direct_deploy(
        "contracts/ProofBasedResolverV2.py"
    )

    result = contract.get_result()

    assert result["decision"] == "PENDING"
    assert result["event_status"] == "UNKNOWN"
    assert result["evidence_strength"] == "NONE"
    assert result["confidence"] == 0
    assert result["status"] == "PENDING"


def test_insufficient_evidence_returns_undetermined(
    direct_vm,
    direct_deploy,
):
    result = resolve_contract(
        direct_vm,
        direct_deploy,
        {
            "decision": "UNDETERMINED",
            "event_date": "UNKNOWN",
            "event_status": "UNKNOWN",
            "evidence_strength": "NONE",
            "confidence": 20,
            "evidence": "The supplied sources do not establish that the event occurred.",
            "reasoning": "There is insufficient evidence to determine whether the event happened before the deadline.",
        },
    )

    assert result["decision"] == "UNDETERMINED"
    assert result["event_status"] == "UNKNOWN"
    assert result["event_date"] == "UNKNOWN"
    assert result["status"] == "RESOLVED"


def test_planned_event_returns_undetermined(
    direct_vm,
    direct_deploy,
):
    result = resolve_contract(
        direct_vm,
        direct_deploy,
        {
            "decision": "UNDETERMINED",
            "event_date": "UNKNOWN",
            "event_status": "NOT_CONFIRMED",
            "evidence_strength": "WEAK",
            "confidence": 30,
            "evidence": "The sources describe a planned or scheduled event but do not confirm completion.",
            "reasoning": "A planned or scheduled event is not proof that the event actually happened.",
        },
    )

    assert result["decision"] == "UNDETERMINED"
    assert result["event_status"] == "NOT_CONFIRMED"
    assert result["event_date"] == "UNKNOWN"
    assert result["status"] == "RESOLVED"


def test_confirmed_event_before_deadline_returns_yes(
    direct_vm,
    direct_deploy,
):
    result = resolve_contract(
        direct_vm,
        direct_deploy,
        {
            "decision": "YES",
            "event_date": "2024-03-13",
            "event_status": "CONFIRMED",
            "evidence_strength": "STRONG",
            "confidence": 98,
            "evidence": "The supplied evidence confirms that the event occurred on 2024-03-13.",
            "reasoning": "The confirmed event date is before the 2024-03-20 deadline.",
        },
    )

    assert result["decision"] == "YES"
    assert result["event_status"] == "CONFIRMED"
    assert result["event_date"] == "2024-03-13"
    assert result["evidence_strength"] == "STRONG"
    assert result["status"] == "RESOLVED"


def test_confirmed_event_after_deadline_returns_no(
    direct_vm,
    direct_deploy,
):
    result = resolve_contract(
        direct_vm,
        direct_deploy,
        {
            "decision": "NO",
            "event_date": "2024-03-25",
            "event_status": "CONFIRMED",
            "evidence_strength": "STRONG",
            "confidence": 98,
            "evidence": "The supplied evidence confirms that the event occurred on 2024-03-25.",
            "reasoning": "The confirmed event date is after the 2024-03-20 deadline.",
        },
    )

    assert result["decision"] == "NO"
    assert result["event_status"] == "CONFIRMED"
    assert result["event_date"] == "2024-03-25"
    assert result["evidence_strength"] == "STRONG"
    assert result["status"] == "RESOLVED"
