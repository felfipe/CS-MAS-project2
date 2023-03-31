from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent"""

    def __init__(
        self, unique_id: int, model: Model, name: str, preferences: Preferences
    ):
        super().__init__(unique_id, model, name)
        self.preferences = preferences

    def step(self):
        super().step()

    def get_preferences(self):
        return self.preferences


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model"""

    def __init__(self):
        self.scheduler = RandomActivation(self)
        self.__messages_service = MessageService(self.scheduler)

        self.diesel_engine = Item("ICED", "A super cool diesel engine")
        self.electric_engine = Item("E", "A very quiet engine")
        items = [self.diesel_engine, self.electric_engine]

        self.agent_1 = ArgumentAgent(
            self.next_id(), self, "Alice", Preferences.generate_random(items)
        )
        self.scheduler.add(self.agent_1)

        self.agent_2 = ArgumentAgent(
            self.next_id(), self, "Bob", Preferences.generate_random(items)
        )
        self.scheduler.add(self.agent_2)

        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.scheduler.step()


if __name__ == "__main__":
    argument_model = ArgumentModel()

    # To be completed 
