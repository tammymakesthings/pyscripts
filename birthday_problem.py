#!/usr/pkg/bin/python3

from random import randint
from typing import Optional, Tuple
from argparse import ArgumentParser
import time
from colorama import Fore, Back, Style, init as color_init


#: The number of people in each group
NUM_PEOPLE: int = 30

#: The number of trials we'll perform
NUM_TRIALS: int = 100000


class BirthdayProblem:
    _num_people: int
    _num_trials: int
    _successful_trials: int
    _detailed_results: list[int]

    def __init__(
        self,
        num_people: Optional[int] = None,
        num_trials: Optional[int] = None,
    ):
        self._num_people = num_people or NUM_PEOPLE
        self._num_trials = num_trials or NUM_TRIALS
        self.reset_experiment()

    @property
    def num_people(self) -> int:
        return self._num_people

    @num_people.setter
    def num_people(self, new_value: int) -> None:
        if not (isinstance(new_value, int) and new_value > 0):
            raise ValueError("num_people must be a positive integer")
        self._num_people = new_value

    @property
    def num_trials(self) -> int:
        return self._num_trials

    @num_trials.setter
    def num_trials(self, new_value: int) -> None:
        if not (isinstance(new_value, int) and new_value > 0):
            raise ValueError("num_trials must be a positive integer")
        self._num_trials = new_value

    @property
    def successful_trials(self) -> int:
        return self._successful_trials

    @property
    def detailed_results(self) -> list[int]:
        return self._detailed_results

    @property
    def percent_matching(self) -> float:
        if self.num_trials > 0:
            return (self.successful_trials / self.num_trials) * 100
        return

    @property
    def delta_percent(self) -> float:
        if self.successful_trials < 0:
            return 0.00
        np, ep = self.expected_matches
        ep = ep * 100
        return abs(((self.percent_matching - ep) / ep) * 100)

    @property
    def expected_matches(self) -> Tuple[int, float]:
        """
        Get the number of expected matches given the number of people.

         Returns:
            Tuple[int, float]: The number of people in the expected match
                group, and the percent of matches in that group.
        """

        # We could calculate this, but we'll just use a precomputed list
        EXPECTED_MATCHES: dict[int, float] = {
            1: 0.00,
            5: 0.027,
            10: 0.117,
            20: 0.411,
            23: 0.507,
            30: 0.706,
            40: 0.891,
            50: 0.970,
            60: 0.994,
            70: 0.999,
            75: 0.9997,
            100: 0.9999997,
        }
        np: int = 0
        ep: float = 0.0

        # There's probably a more efficient way to do this, but this will
        # work.
        for k in EXPECTED_MATCHES:
            if self.num_people < k:
                return (np, ep)
            np = k
            ep = EXPECTED_MATCHES[k]
        return (np, ep)

    def reset_experiment(self) -> None:
        self._successful_trials = 0
        self._detailed_results = []

    def generate_birthdays(self) -> list[int]:
        """
        Generate a list of birthdays for a set of people.

        Returns:
            list[int]: The list of birthdays for the group.
        """
        return [randint(1, 366) for _ in range(1, self.num_people + 1)]

    def matching_birthdays(self, bdays: list[int]) -> bool:
        """
        Determine if a list of birthdays contains one or more match.

        Parameters:
            bdays (list[int]): True if the list of birthdays contains at
                least one matching birthday.
        """
        return len(set(bdays)) != len(bdays)

    def delta_expr(self, delta: float, delta_threshold: float) -> str:
        """
        Summarize how close our results are to the expected.

        Parameters:
            delta (float): How far our result is from the expected.
            delta_threshold: (float): How close we want to be

        Returns:
            string: The summary message to print out.
        """
        delta_expr: str

        if delta < delta_threshold:
            delta_expr = f"{Fore.CYAN}Boom! Nailed it.{Fore.RESET}"
        elif delta < (2 * delta_threshold):
            delta_expr = f"{Fore.CYAN}That's pretty darned good.{Fore.RESET}"
        else:
            delta_expr = f"{Fore.CYAN}Not too bad.{Fore.RESET}"

        return f"We're within {Fore.CYAN}{delta:.3f}%{Fore.RESET} of the expected result. {delta_expr}"

    def run_experiment(
        self,
        gather_detailed_results: Optional[bool] = True,
        delta_threshold: Optional[float] = 0.2,
        enable_output: Optional[bool] = False,
        enable_progress_messages: Optional[bool] = True,
        terminal_width: Optional[int] = 80,
    ) -> None:

        if enable_output:
            color_init(autoreset=True)
            print(f"{Fore.GREEN}{'*' * terminal_width}")
            print(
                f"{Fore.GREEN}* {'BIRTHDAY PROBLEM IN PYTHON '.center(terminal_width - 4)} *"
            )
            print(
                f"{Fore.GREEN}* {'10/21/2025 - Tammy Cravit - tammy@tammymakesthings.com '.center(terminal_width - 4)} *"
            )
            print(
                f"{Fore.GREEN}* {'https://en.wikipedia.org/wiki/Birthday_problem'.center(terminal_width - 4)} *"
            )
            print(f"{Fore.GREEN}{'*' * terminal_width}")
            print("")
            print(
                    f"We'll run {Fore.CYAN}{self.num_trials:,d}{Fore.RESET} trials of {Fore.CYAN}{self.num_people}{Fore.RESET} people."
            )
        if enable_progress_messages:
            print("")
            print("Running the experiment - please wait...", flush=True)

        start_time = time.time()

        progress_len = 0

        batch_size = self.num_trials / 10
        for i in range(self.num_trials + 1):
            birthdays = self.generate_birthdays()
            if gather_detailed_results:
                self._detailed_results.append(birthdays)
            if self.matching_birthdays(birthdays):
                self._successful_trials = self._successful_trials + 1
            if enable_progress_messages and ((i % batch_size) == 0):
                progress_str = f"{i:,d}"
                print(f"{Fore.MAGENTA}{progress_str}{Fore.RESET}...", end="", flush=True)
                progress_len = progress_len + len(progress_str) + 3
                if progress_len >= (terminal_width-4):
                    print("")
                    progress_len=0


        end_time = time.time()

        if enable_progress_messages:
            print("")
            print(f"Done.")
            print("", flush=True)

        if any([enable_progress_messages, enable_output]):
            exec_time = end_time - start_time
            time_per_hundy = (exec_time / self.num_trials) * 100000

            print(
                f"Completed in {Fore.CYAN}{exec_time:.4f}{Fore.RESET} seconds. [{Fore.CYAN}{time_per_hundy:.4f}{Fore.RESET} sec/100k]"
            )
            print("")
            print(
                    f"In {Fore.CYAN}{self.num_trials:,d}{Fore.RESET} trials, {Fore.CYAN}{self.successful_trials:,d}{Fore.RESET} groups had at least one matching birthday."
            )
            print(
                f"That's {Fore.CYAN}{self.percent_matching:.3f}%{Fore.RESET} of the time."
            )
            print("")

        np, ep = self.expected_matches
        ep = ep * 100

        if any([enable_progress_messages, enable_output]):
            print(
                f"In a population of {Fore.CYAN}{np}{Fore.RESET} people, we'd expect this result {Fore.CYAN}{ep:.3f}%{Fore.RESET} of the time."
            )
            print(self.delta_expr(self.delta_percent, delta_threshold))
            print("")


if __name__ == "__main__":
    ap = ArgumentParser(
        prog="BirthdayProblem",
        description="Birthday problem simulation in Python",
        epilog="See <https://en.wikipedia.org/wiki/Birthday_problem> for more.",
    )
    ap.add_argument(
        "-p",
        "--num_people",
        default=NUM_PEOPLE,
        help="the number of people in each group",
        metavar="PEOPLE",
        type=int,
    )
    ap.add_argument(
        "-t",
        "--num-trials",
        default=NUM_TRIALS,
        help="the number of trials",
        metavar="TRIALS",
        type=int,
    )
    ap.add_argument(
        "-v",
        "--verbose",
        help="enable more verbose output",
        action="store_true",
    )
    ap.add_argument(
        "-d",
        "--detailed-results",
        help="save the individual results as well as the summary",
        action="store_true",
    )
    ap.add_argument(
        "-l",
        "--delta-threshold",
        help="the delta threshold in percentage",
        default=0.2,
        type=float,
    )
    ap.add_argument(
        "-w",
        "--terminal-width",
        default=80,
        help="the width of the terminal for output formatting (must be at least 59)",
        metavar="WIDTH",
        type=int,
    )
    ap.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress output (not really useful from the CLI)",
        default=False,
    )

    args = ap.parse_args()

    experiment = BirthdayProblem(
        num_people=args.num_people,
        num_trials=args.num_trials,
    )

    experiment.run_experiment(
        gather_detailed_results=args.detailed_results or False,
        delta_threshold=args.delta_threshold or 0.2,
        enable_output=(not args.quiet),
        enable_progress_messages=args.verbose or False,
        terminal_width=max(args.terminal_width, 59) or 80,
    )
