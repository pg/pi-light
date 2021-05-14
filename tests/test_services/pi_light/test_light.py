import testslide
from testslide import TestCase
from testslide.matchers import Any

from app.services.pi_light import fake_board, rule_manager
from app.services.pi_light.color import Color
from app.services.pi_light.light import Light
from app.services.pi_light.mode import Mode
from app.services.pi_light.state import State


class TestLight(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.mock_board = testslide.StrictMock(fake_board.Board)
        self.mock_constructor(fake_board, "Board").for_call().to_return_value(
            self.mock_board
        )
        self.mock_rule_manager = testslide.StrictMock(rule_manager.RuleManager)
        self.mock_constructor(rule_manager, "RuleManager").for_call().to_return_value(
            self.mock_rule_manager
        )
        self.light = Light()

    def test_state(self) -> None:
        self.mock_callable(self.light, "state").to_return_values(
            [State.RUNNING, State.STOPPED]
        )
        self.mock_callable(self.mock_board, "fill").for_call(Any()).to_return_value(
            None
        ).and_assert_called_once()
        self.light.run()

    def test_default_mode(self) -> None:
        self.mock_callable(self.light, "state").to_return_values(
            [State.RUNNING, State.STOPPED]
        )
        self.mock_callable(self.mock_board, "fill").for_call(Any()).to_return_value(
            None
        ).and_assert_called_once()
        self.light.run()

    def test_rainbow_mode(self) -> None:
        self.mock_callable(self.light, "state").to_return_values(
            [State.RUNNING, State.STOPPED]
        )
        self.mock_callable(self.light, "mode").to_return_value(Mode.RAINBOW)
        self.mock_callable(self.mock_board, "fill").for_call(Any()).to_return_value(
            None
        ).and_assert_not_called()
        self.mock_callable(self.mock_board, "rainbow_step").for_call().to_return_value(
            None
        ).and_assert_called_once()
        self.light.run()

    def test_rules_mode(self) -> None:
        self.mock_callable(self.light, "state").to_return_values(
            [State.RUNNING, State.STOPPED]
        )
        self.mock_callable(self.light, "mode").to_return_value(Mode.RULES)
        expected_color = Color()
        self.mock_callable(
            self.mock_rule_manager, "current_color"
        ).for_call().to_return_value(expected_color).and_assert_called_once()
        self.mock_callable(self.mock_board, "fill").for_call(
            expected_color
        ).to_return_value(None).and_assert_called_once()
        self.light.run()
