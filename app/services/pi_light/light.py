import time

from app.core.config import Settings
from app.core.settings import get_settings
from app.services.pi_light import rule_manager
from app.services.pi_light.color import Color
from app.services.pi_light.mode import Mode
from app.services.pi_light.state import State

if get_settings().environment == "prod":
    import app.services.pi_light.board as board
else:
    import app.services.pi_light.fake_board as board  # type: ignore


class Light:
    _board: board.Board
    _state: State
    _mode: Mode
    color: Color
    rule_manager: rule_manager.RuleManager

    def __init__(self):
        self._board = board.Board()
        self._state = State.RUNNING
        self._mode = Mode.DEFAULT
        self.color = Color()
        self.rule_manager = rule_manager.RuleManager()

    def state(self):
        return self._state

    def mode(self):
        return self._mode

    def run(self, settings: Settings = get_settings()) -> None:
        while self.state() == State.RUNNING:
            if self.mode() == Mode.RAINBOW:
                self._board.rainbow_step()
                time.sleep(0.01)
                continue
            if self.mode() == Mode.RULES:
                self.color = self.rule_manager.current_color()
            self._board.fill(self.color)
            time.sleep(settings.sleep_ms / 1000)
