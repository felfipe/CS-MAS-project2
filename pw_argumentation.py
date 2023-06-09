import argparse
from typing import List, Optional

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.communicating_agent import CommunicatingAgent
from communication.arguments.argument import Argument
from communication.arguments.comparison import Comparison
from communication.arguments.equality import Equality
from communication.message.message import Message
from communication.message.message_performative import MessagePerformative
from communication.message.message_service import MessageService
from communication.preferences.item import Item
from communication.preferences.preferences import Preferences
from communication.preferences.values import Value


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model"""

    def __init__(
        self,
        prefs_agent_1: Optional[str] = None,
        prefs_agent_2: Optional[str] = None,
        number_items: Optional[int] = None,
        prob_accept_argument: float = 0.2,
        first_agent: str = "Alice",
        top_k: float = 0.1,
    ):
        super().__init__()
        self.scheduler = RandomActivation(self)
        self.__messages_service = MessageService(self.scheduler)

        # Probability to accept an argument
        self.prob_accept_argument = prob_accept_argument
        # Percent of items to consider in top-k
        self.top_k = top_k
        # # First agent to send a message
        self.first_agent = first_agent

        if number_items is not None:
            self.items = {
                f"Engine{str(i)}": Item(f"Engine{str(i)}", "No description")
                for i in range(number_items)
            }
            if prefs_agent_1 is not None or prefs_agent_2 is not None:
                print(
                    "Warning: ignoring preference csv files because number_items was specified"
                )
                prefs_agent_1 = None
                prefs_agent_2 = None
        else:
            self.items = {
                "ICED": Item("ICED", "A super cool diesel engine"),
                "E": Item("E", "A very quiet engine"),
            }

        self.agent_1 = self._create_agent("Alice", prefs_agent_1)
        self.agent_2 = self._create_agent("Bob", prefs_agent_2)

        self.running = True

    def _create_agent(self, name: str, prefs_path: Optional[str]):
        # Load or generate the preferences depending on if the prefs_path is set
        if prefs_path is None:
            prefs = Preferences.generate_random(self.items, rand=self.random)
        else:
            prefs = Preferences.load(prefs_path, self.items)
            print(f"Loading agent {name} from {prefs_path}")

        # Create the agent and add it to the scheduler
        initial_agent = name == self.first_agent
        agent = ArgumentAgent(self.next_id(), self, name, prefs, initial_agent)
        self.scheduler.add(agent)

        return agent

    def step(self):
        self.__messages_service.dispatch_messages()
        self.scheduler.step()

    def run_steps(self, steps: int = 5):
        for _ in range(steps):
            self.step()
            if (
                self.agent_1.commited_item is not None
                and self.agent_2.commited_item is not None
            ):
                assert (
                    self.agent_1.commited_item == self.agent_2.commited_item is not None
                )
                print("Done. Chosen product:", self.agent_1.commited_item)
                return
        print("Simulation not finished, max steps reached")


class ExtendedArgument:
    argument: Argument
    counterarguments: List[Argument]

    def __init__(self, argument: Argument, counterarguments: List[Argument]):
        self.argument = argument
        self.counterarguments = counterarguments

    @staticmethod
    def attackble(argument: Argument, prefs: Preferences) -> "ExtendedArgument":
        if argument.decision:
            premises = Argument.get_attacking_premises(argument.item, prefs)
        else:
            premises = Argument.get_supporting_premises(argument.item, prefs)
        arg_eq = argument.equalities[0]
        arg_criterion = arg_eq.criterion_name
        criteria = prefs.get_criterion_name_list()
        counter = []

        if argument.comparisons:
            arg_cmp = argument.comparisons[0]
            if criteria.index(arg_cmp.better_criterion_name) > criteria.index(
                arg_cmp.worse_criterion_name
            ):
                counter.append(
                    Argument(
                        argument.item,
                        not argument.decision,
                        comparisons=[
                            Comparison(
                                arg_cmp.worse_criterion_name,
                                arg_cmp.better_criterion_name,
                            )
                        ],
                        equalities=[
                            Equality(
                                arg_cmp.worse_criterion_name,
                                prefs.get_value(
                                    argument.item, arg_cmp.worse_criterion_name
                                ),
                            )
                        ],
                    )
                )

        other_val = arg_eq.value.value
        self_val = prefs.get_value(argument.item, arg_eq.criterion_name).value
        if (other_val < 2 and self_val > 2) or (other_val > 2 and self_val < 2):
            counter.append(
                Argument(
                    argument.item,
                    not argument.decision,
                    equalities=[Equality(arg_criterion, Value(self_val))],
                )
            )

        for p in premises:
            if criteria.index(p.criterion_name) >= criteria.index(arg_criterion):
                break
            counter.append(
                Argument(
                    argument.item,
                    not argument.decision,
                    comparisons=[Comparison(p.criterion_name, arg_criterion)],
                    equalities=[p],
                )
            )
        return ExtendedArgument(argument, counter[::-1])

    @staticmethod
    def not_attackble(argument: Argument) -> "ExtendedArgument":
        return ExtendedArgument(argument, [])

    @staticmethod
    def base(args: List[Argument]):
        return ExtendedArgument(Argument(Item("", ""), True), args)


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent"""

    model: ArgumentModel
    accepted_items: List[Item]
    commited_item: Optional[Item]
    arguments: List[ExtendedArgument]
    used_arguments: List[Argument]
    received_items: List[Item]

    def __init__(
        self,
        unique_id: int,
        model: ArgumentModel,
        name: str,
        preferences: Preferences,
        initial_agent: bool,
    ):
        super().__init__(unique_id, model, name)
        self.preferences = preferences
        self.items = self.model.items.copy()

        self.initial_agent = initial_agent
        self.accepted_items = []
        self.received_items = []
        self.commited_item = None
        self.arguments = []
        self.used_arguments = []

    def step(self):
        super().step()

        messages = self.get_new_messages()
        if len(messages) > 0:
            print(*messages, sep="\n")

        if self.initial_agent and not self.accepted_items:
            item = self.preferences.most_preferred(self.items, rand=self.random)
            self.accepted_items.append(item)
            self.send_message(
                Message(
                    self.get_name(),
                    None,
                    MessagePerformative.PROPOSE,
                    item.get_name(),
                )
            )
            return

        for msg in messages:
            if msg.get_performative() == MessagePerformative.PROPOSE:
                received_proposition = self.items[msg.get_content()]
                if self.preferences.is_item_among_top_10_percent(
                    received_proposition, self.items, self.model.top_k
                ):
                    self.accepted_items.append(received_proposition)
                    self.send_message(
                        Message(
                            self.get_name(),
                            msg.get_exp(),
                            MessagePerformative.ACCEPT,
                            received_proposition.get_name(),
                        )
                    )
                else:
                    self.received_items.append(received_proposition)
                    self.send_message(
                        Message(
                            self.get_name(),
                            msg.get_exp(),
                            MessagePerformative.ASK_WHY,
                            received_proposition.get_name(),
                        )
                    )
            elif (
                msg.get_performative() == MessagePerformative.ACCEPT
                and self.items[msg.get_content()] in self.accepted_items
            ):
                self.send_message(
                    Message(
                        self.get_name(),
                        None,
                        MessagePerformative.COMMIT,
                        msg.get_content(),
                    )
                )
                self.commited_item = self.items[msg.get_content()]

            elif msg.get_performative() == MessagePerformative.COMMIT:
                item_name = msg.get_content()
                item = self.items[item_name]
                if item in self.accepted_items:
                    del self.items[item_name]
                    if self.commited_item is None:
                        self.send_message(
                            Message(
                                self.get_name(),
                                None,
                                MessagePerformative.COMMIT,
                                item_name,
                            )
                        )
                        self.commited_item = item
            elif msg.get_performative() == MessagePerformative.ASK_WHY:
                self.send_message(
                    Message(
                        self.get_name(),
                        None,
                        MessagePerformative.ARGUE,
                        str(self.support_proposal(self.items[msg.get_content()])),
                    )
                )
            elif msg.get_performative() == MessagePerformative.ARGUE:
                argument = Argument.parse(msg.get_content(), self.items)
                counter = self.process_argument(argument)
                if (
                    argument.item not in self.accepted_items
                    and argument.item not in self.received_items
                ):
                    self.received_items.append(argument.item)
                if counter is None:
                    if argument.decision:
                        # No possible counter argument to refuse the item
                        # If possible, propose a product.
                        # Otherwise, accept the current one.
                        if self.random.random() < self.model.prob_accept_argument:
                            self.send_message(
                                Message(
                                    self.get_name(),
                                    None,
                                    MessagePerformative.ACCEPT,
                                    argument.item.get_name(),
                                )
                            )
                            self.accepted_items.append(argument.item)
                        else:
                            remaining_items = {
                                item.get_name(): item
                                for item in self.items.values()
                                if item not in self.accepted_items
                            }
                            item = self.preferences.most_preferred(remaining_items)
                            self.send_message(
                                Message(
                                    self.get_name(),
                                    None,
                                    MessagePerformative.PROPOSE,
                                    item.get_name(),
                                )
                            )
                            self.accepted_items.append(item)
                    else:
                        # No possible counter argument to accept the item,
                        # so propose another one
                        item = self.preferences.most_preferred(self.items)
                        if (
                            item in self.accepted_items
                            and argument.item in self.received_items
                        ):
                            self.send_message(
                                Message(
                                    self.get_name(),
                                    msg.get_exp(),
                                    MessagePerformative.ACCEPT,
                                    item.get_name(),
                                )
                            )
                        else:
                            self.accepted_items.append(item)
                            self.send_message(
                                Message(
                                    self.get_name(),
                                    None,
                                    MessagePerformative.PROPOSE,
                                    item.get_name(),
                                )
                            )
                else:
                    self.send_message(
                        Message(
                            self.get_name(),
                            None,
                            MessagePerformative.ARGUE,
                            str(counter),
                        )
                    )

    def get_preferences(self) -> Preferences:
        return self.preferences

    def support_proposal(self, item: Item) -> Argument:
        """Used when the agent receives "ASK_WHY" after having proposed an item

        params:
            item (str): name of the item which was proposed
        returns:
            Argument - the strongest supportive argument
        """
        premises = Argument.get_supporting_premises(item, self.preferences)
        args = [Argument(item, decision=True, equalities=[p]) for p in premises]

        # We return the strongest argument, but store the others for the future
        self.arguments.append(ExtendedArgument.base(args))
        return args[0]

    def process_argument(self, argument: Argument) -> Optional[Argument]:
        # If the other agent wants the same thing as us, just accept it
        our_decision = self.preferences.is_item_among_top_10_percent(
            argument.item, self.items, self.model.top_k
        )
        if our_decision == argument.decision:
            return None

        self.arguments.append(ExtendedArgument.attackble(argument, self.preferences))
        for ea in self.arguments[:-1]:
            if ea.argument in self.arguments[-1].counterarguments:
                self.arguments[-1].counterarguments.remove(ea.argument)

        while self.arguments:
            # If the last two arguments are opposite (e.g. "c1 is good" and "c1 is bad")
            # remove both of them
            if len(self.arguments) >= 2 and Argument.is_opposite(
                self.arguments[-1].argument, self.arguments[-2].argument
            ):
                self.arguments.pop()
                self.arguments.pop()
                continue

            last = self.arguments[-1]
            while last.counterarguments:
                counter = last.counterarguments.pop()
                if counter not in self.used_arguments:
                    self.used_arguments.append(counter)
                    self.arguments.append(ExtendedArgument.not_attackble(counter))
                    if len(self.arguments) >= 2 and Argument.is_opposite(
                        self.arguments[-1].argument, self.arguments[-2].argument
                    ):
                        self.arguments.pop()
                        self.arguments.pop()
                    return counter
            if len(self.arguments) >= 2:
                self.arguments.pop()
                self.arguments.pop()
            else:
                break

        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--preset",
        "-p",
        action="store_true",
        help=(
            "Uses the same agent preferences and values as defined in the project's"
            "description, and the two example engines (ICED and E). "
            "Otherwise, randomly generated products will be used."
        ),
    )
    parser.add_argument(
        "--number-items",
        "-n",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Run with N randomly generated items. "
            "Default: 10 (unless --preset is specified)."
        ),
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=1000,
        help="Maximum number of steps per simulation. Default: 1000",
    )
    parser.add_argument(
        "--prob-accept-argument",
        type=float,
        default=0.2,
        metavar="PROB",
        help=(
            "The probability that an agent will accept an item if they lose"
            "the argument. Otherwise, if possible, they will suggest an alternative"
            "item. Default: 0.2"
        ),
    )
    parser.add_argument(
        "--first-agent",
        choices=["Alice", "Bob"],
        default="Alice",
        help="The agent who makes the first proposal. Default: Alice",
    )
    parser.add_argument(
        "--top-k",
        "-k",
        metavar="K",
        type=float,
        default=0.1,
        help=
            "The percentage of best items which are acceptable for an agent. "
            "Default: 0.1"
        ,
    )
    args = parser.parse_args()

    prefs_agent_1 = None
    prefs_agent_2 = None
    if args.preset:
        if args.number_items not in (None, 2):
            print(
                f"Warning: --preset always uses two items (ICED and E). "
                f"Ignoring argument --number-items={args.number_items}."
            )
        prefs_agent_1 = "data/agent_1"
        prefs_agent_2 = "data/agent_2"
        args.number_items = None
    elif args.number_items is None:
        args.number_items = 10

    argument_model = ArgumentModel(
        prefs_agent_1=prefs_agent_1,
        prefs_agent_2=prefs_agent_2,
        number_items=args.number_items,
        prob_accept_argument=args.prob_accept_argument,
        first_agent=args.first_agent,
        top_k=args.top_k,
    )
    argument_model.run_steps(args.max_steps)


if __name__ == "__main__":
    main()
