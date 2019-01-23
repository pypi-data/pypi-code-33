import pytest
from clustaar.schemas.models import CustomerSatisfactionAction, CustomerSatisfactionChoice, \
    StepTarget
from tests.utils import MAPPER


@pytest.fixture
def action():
    return CustomerSatisfactionAction(
        message="Are you satisfied ?",
        choices=[
            CustomerSatisfactionChoice(
                kind="positive",
                target=StepTarget(step_id="a1" * 12, name="a step"),
                matching_intent_id="b1" * 12,
                label="yes"
            ),
            CustomerSatisfactionChoice(
                kind="negative",
                target=StepTarget(step_id="a2" * 12, name="a step"),
                matching_intent_id="b2" * 12,
                label="no"
            )
        ]
    )


@pytest.fixture
def data():
    return {
        "type": "customer_satisfaction_action",
        "message": "Are you satisfied ?",
        "choices": [
            {
                "type": "customer_satisfaction_choice",
                "kind": "positive",
                "label": "yes",
                "matchingIntentID": "b1" * 12,
                "target": {
                    "type": "step",
                    "id": "a1" * 12,
                    "name": "a step"
                }
            },
            {
                "type": "customer_satisfaction_choice",
                "kind": "negative",
                "matchingIntentID": "b2" * 12,
                "label": "no",
                "target": {
                    "type": "step",
                    "id": "a2" * 12,
                    "name": "a step"
                }
            }
        ]
    }


class TestDump(object):
    def test_returns_a_dict(self, data, action):
        result = MAPPER.dump(action, "customer_satisfaction_action")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "customer_satisfaction_action")
        assert isinstance(result, CustomerSatisfactionAction)
        assert result.message == "Are you satisfied ?"
        assert len(result.choices) == 2

        choice1, choice2 = result.choices
        assert choice1.kind == "positive"
        assert choice1.target.step_id == "a1" * 12
        assert choice1.matching_intent_id == "b1" * 12
        assert choice1.label == "yes"

        assert choice2.kind == "negative"
        assert choice2.target.step_id == "a2" * 12
        assert choice2.matching_intent_id == "b2" * 12
        assert choice2.label == "no"
