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
        self.items = [Item("ICED", "A super cool diesel engine"), Item("E", "A very quiet engine")]

        self.agent_1 = self._create_agent("Alice", prefs_agent_1)
        self.agent_2 = self._create_agent("Bob", prefs_agent_2)

        self.running = True

    def _create_agent(self, name: str, prefs_path: Optional[str]):
        # Load or generate the preferences depending on if the prefs_path is set
        if prefs_path is None:
            prefs = Preferences.generate_random(self.items)
        else:
            prefs = Preferences.load(prefs_path, self.items)

        # Create the agent and add it to the scheduler
        agent = ArgumentAgent(self.next_id(), self, name, prefs)
        self.scheduler.add(agent)

        return agent

    def step(self):
        self.__messages_service.dispatch_messages()
        self.scheduler.step()

    def run_steps(self, steps : int = 5):
        for _ in range(steps):
            self.step()

class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent"""

    def __init__(
        self, unique_id: int, model: ArgumentModel, name: str, preferences: Preferences
    ):
        super().__init__(unique_id, model, name)
        self.init_prop = False
        self.preferences = preferences

    def step(self):
        super().step()
        if(self.get_name() == "Alice"):
            if(self.init_prop == False):
                self.init_prop = True
                self.send_message(
                    Message(self.get_name(), None, MessagePerformative.PROPOSE, self.model.items[0])
                )
            else:
                messages = self.get_new_messages()
                if(len(messages) > 0):
                    print(*messages, sep='\n')

            return

        if(self.get_name() == "Bob"):
            messages = self.get_new_messages()
            if(len(messages) > 0):
                print(*messages, sep='\n')

            for msg in messages:
                if(msg.get_performative() == MessagePerformative.PROPOSE):
                    proposed_item = msg.get_content()
                    if(self.preferences.is_item_among_top_10_percent(proposed_item, self.model.items)):
                        self.send_message(
                            Message(self.get_name(), msg.get_exp(), MessagePerformative.ACCEPT, proposed_item)
                        )
                    else:
                        self.send_message(
                            Message(self.get_name(), msg.get_exp(), MessagePerformative.ASK_WHY, proposed_item)
                        )

    def get_preferences(self):
        return self.preferences


if __name__ == "__main__":
    argument_model = ArgumentModel(
        prefs_agent_1="data/agent_1", prefs_agent_2="data/agent_2"
    )
    argument_model.run_steps()
    