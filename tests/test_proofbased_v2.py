def test_proofbased_v2_contract_structure(direct_deploy):
    contract = direct_deploy(
        "contracts/ProofBasedResolverV2.py"
    )

    result = contract.get_result()

    assert result["decision"] == "PENDING"
    assert result["event_status"] == "UNKNOWN"
    assert result["evidence_strength"] == "NONE"
    assert result["confidence"] == 0
    assert result["status"] == "PENDING"
