from llm_validator import utils

def test_extract_balance_stub():
    result = utils.extract_balance("Balance $100")
    assert isinstance(result, list)