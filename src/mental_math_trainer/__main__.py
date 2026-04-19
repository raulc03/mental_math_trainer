from collections import deque
import random
import time
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Digits, Input, Label, Footer


class Operation:
    def __init__(self, kind_numbers: str = "2_2", kind_operation: str = "+"):
        length_numbers = tuple(map(lambda x: int(x), kind_numbers.split("_")))
        self.first = self._generate_rand_num(length_numbers[0])
        self.second = self._generate_rand_num(length_numbers[1])
        self.kind_op = kind_operation

    def _generate_rand_num(self, length: int):
        min_base = 10 ** (length - 1)
        max_base = 10 ** (length) - 1
        return random.randint(min_base, max_base)

    def get_answer(self) -> int | float:
        match self.kind_op:
            case "+":
                return self.first + self.second
            case "-":
                return self.first - self.second
            case "*":
                return self.first * self.second
            case "/":
                return self.first / self.second
            case _:
                return self.first + self.second

    def __str__(self) -> str:
        return f"{self.first} {self.kind_op} {self.second}"

    def isOk(self, other: int | float) -> bool:
        return other == self.get_answer()


class Timer(Digits):
    start_time = time.monotonic()
    elapsed = reactive(0.0)

    def on_mount(self, _: events.Mount) -> None:
        self.update_timer = self.set_interval(1 / 60, self.update_elapsed, pause=True)

    def update_elapsed(self):
        self.elapsed = time.monotonic() - self.start_time

    def watch_elapsed(self, elapsed: float) -> None:
        minutes, seconds = divmod(elapsed, 60)
        self.update(f"{minutes:02.0f}:{seconds:02.0f}")

    def start(self):
        self.start_time = time.monotonic()
        self.update_timer.resume()

    def reset(self):
        self.start_time = time.monotonic()
        self.update_timer.reset()
        self.update_timer.pause()


def format_operations(
    numbers: tuple[int | float, int | float], operation: str = "+"
) -> str:
    return f"{numbers[0]} {operation} {numbers[1]}"


class Addition(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen"),
        ("ctrl+s", "start_test", "Start Test"),
        ("ctrl+r", "reset_test", "Reset Test"),
    ]
    CSS_PATH = "addition.tcss"
    started = reactive(False)
    tests = [(random.randint(10, 99), random.randint(10, 99)) for _ in range(5)]

    def watch_started(self, started: bool) -> None:
        ans_input = self.query_exactly_one("#answer_input")
        if started:
            ans_input.display = True
            ans_input.focus()
        else:
            ans_input.display = False

    def compose(self) -> ComposeResult:
        yield Container(
            Timer("00:00", id="timer"),
            Horizontal(
                Digits("--", classes="operations", id="prev_ope"),
                Digits(
                    format_operations(self.tests[0]), classes="operations", id="main"
                ),
                Digits("--", classes="operations", id="next_ope"),
                classes="operations_container",
            ),
            Input(placeholder="Enter the answer", id="answer_input", type="number"),
            classes="container",
        )
        yield Footer()

    def action_reset_test(self) -> None:
        self.query_one("#timer", Timer).reset()
        self.started = False

    def action_start_test(self) -> None:
        self.started = True
        self.query_one("#timer", Timer).start()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "answer_input":
            if event.input.value == sum(map(lambda x: int(x), self.curr_test)):
                self.curr_test = next(self.tests)


class MyApp(App):
    SCREENS = {"addition": Addition}
    BINDINGS = [("b", "push_screen('addition')", "Addition")]
    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Mental Math Trainer")


if __name__ == "__main__":
    app = MyApp()
    app.run()
