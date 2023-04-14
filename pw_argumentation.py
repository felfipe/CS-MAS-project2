from typing import Optional
from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.message.Message import Message, BROADCAST
from communication.message.MessagePerformative import MessagePerformative
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model"""

    def __init__(
        self, prefs_agent_1: Optional[str] = None, prefs_agent_2: Optional[str] = None
    ):
        super().__init__()
        self.scheduler = RandomActivation(self)
        self.__messages_service = MessageService(self.scheduler)
        self.items = [
            Item("ICED", "A super cool diesel engine"),
            Item("E", "A very quiet engine"),
        ]

        self.agent_1 = self._create_agent("Alice", prefs_agent_1, True)
        self.agent_2 = self._create_agent("Bob", prefs_agent_2, False)

        self.running = True

    def _create_agent(self, name: str, prefs_path: Optional[str], initial_agent : bool):
        # Load or generate the preferences depending on if the prefs_path is set
        if prefs_path is None:
            prefs = Preferences.generate_random(self.items)
        else:
            prefs = Preferences.load(prefs_path, self.items)

        # Create the agent and add it to the scheduler
        agent = ArgumentAgent(self.next_id(), self, name, prefs, initial_agent)
        self.scheduler.add(agent)

        return agent

    def step(self):
        self.__messages_service.dispatch_messages()
        self.scheduler.step()

    def run_steps(self, steps: int = 5):
        for _ in range(steps):
            self.step()


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent"""

    model: ArgumentModel

    def __init__(
        self,
        unique_id: int,
        model: ArgumentModel,
        name: str,
        preferences: Preferences,
        initial_agent: bool
    ):
        super().__init__(unique_id, model, name)
        self.preferences = preferences
        self.items = self.model.items.copy()

        self.initial_agent = initial_agent
        self.proposed_item = self.items[1]

        self.has_committed = False
        self.has_proposed = False

    def step(self):
        super().step()

        messages = self.get_new_messages()
        if len(messages) > 0:
            print(*messages, sep="\n")

        if self.initial_agent and not self.has_proposed:
            self.has_proposed = True
            self.send_message(
                Message(
                    self.get_name(),
                    None,
                    MessagePerformative.PROPOSE,
                    self.proposed_item,
                )
            )
            return

        for msg in messages:

            if msg.get_performative() == MessagePerformative.PROPOSE:
                    self.received_proposition = msg.get_content()
                    if self.preferences.is_item_among_top_10_percent(
                        self.received_proposition, self.items
                    ):
                        self.send_message(
                            Message(
                                self.get_name(),
                                msg.get_exp(),
                                MessagePerformative.ACCEPT,
                                self.received_proposition,
                            )
                        )
                    else:
                        self.send_message(
                            Message(
                                self.get_name(),
                                msg.get_exp(),
                                MessagePerformative.ASK_WHY,
                                self.received_proposition,
                            )
                        )
            elif (
                msg.get_performative() == MessagePerformative.ACCEPT
                and msg.get_content() == self.proposed_item
            ):
                self.send_message(
                    Message(
                        self.get_name(),
                        None,
                        MessagePerformative.COMMIT,
                        self.proposed_item,
                    )
                )
                self.has_committed = True
                
            elif (
                msg.get_performative() == MessagePerformative.COMMIT
            ):
                if(msg.get_content() == self.proposed_item and self.has_committed):
                    self.items.remove(self.proposed_item)
                elif(msg.get_content() == self.received_proposition):
                    self.items.remove(self.received_proposition)
                    self.send_message(
                        Message(
                            self.get_name(),
                            None,
                            MessagePerformative.COMMIT,
                            self.received_proposition,
                        )
                    )
                    self.has_committed = True
            else:
                self.send_message(
                    Message(self.get_name(), None, MessagePerformative.ARGUE, None)
                )

            return

    def get_preferences(self):
        return self.preferences


if __name__ == "__main__":
    argument_model = ArgumentModel(
        prefs_agent_1="data/agent_1", prefs_agent_2="data/agent_2"
    )
    argument_model.run_steps()
