from typing import Optional, List
from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value
from communication.arguments.CoupleValue import CoupleValue
from communication.arguments.Comparison import Comparison
from communication.arguments.Argument import Argument


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

    def get_supporting_premises(self, item: "Item") -> List["CoupleValue"]:
        """Generates a list of premisses which can be used to support an item

        params:
            item (Item): name of the item
        returns:
            list of all premisses PRO an item (sorted by order of importance
            based on agent's preferences)
        """
        prems = []
        for criterion_name in self.preferences.get_criterion_name_list():
            value = self.preferences.get_value(item, criterion_name)
            if value.value >= Value.GOOD.value:
                prems.append(CoupleValue(criterion_name, value))

        return prems

    def get_attacking_premises(self, item: "Item") -> List["CoupleValue"]:
        """Generates a list of premisses which can be used to attack an item

        params:
            item (Item): name of the item
        returns:
            list of all premisses CON an item (sorted by order of importance
            based on agent's preferences)
        """

        prems = []
        for criterion_name in self.preferences.get_criterion_name_list():
            value = self.preferences.get_value(item, criterion_name)
            if value.value <= Value.BAD.value:
                prems.append(CoupleValue(criterion_name, value))

        return prems

    def support_proposal(self, item: Item) -> Argument:
        """Used when the agent receives "ASK_WHY" after having proposed an item

        params:
            item (str): name of the item which was proposed
        returns:
            string - the strongest supportive argument
        """
        premises = self.get_supporting_premises(item)
        return Argument(item, decision=True, couple_values=[premises[0]])


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model"""

    def __init__(
        self, prefs_agent_1: Optional[str] = None, prefs_agent_2: Optional[str] = None
    ):
        super().__init__()
        self.scheduler = RandomActivation(self)
        self.__messages_service = MessageService(self.scheduler)
        self.diesel_engine = Item("ICED", "A super cool diesel engine")
        self.electric_engine = Item("E", "A very quiet engine")

        self.agent_1 = self._create_agent("Alice", prefs_agent_1)
        self.agent_2 = self._create_agent("Bob", prefs_agent_2)

        self.running = True

    def _create_agent(self, name: str, prefs_path: Optional[str]):
        # Load or generate the preferences depending on if the prefs_path is set
        items = [self.diesel_engine, self.electric_engine]
        if prefs_path is None:
            prefs = Preferences.generate_random(items)
        else:
            prefs = Preferences.load(prefs_path, items)

        # Create the agent and add it to the scheduler
        agent = ArgumentAgent(self.next_id(), self, name, prefs)
        self.scheduler.add(agent)

        return agent

    def step(self):
        self.__messages_service.dispatch_messages()
        self.scheduler.step()


if __name__ == "__main__":
    argument_model = ArgumentModel(
        prefs_agent_1="data/agent_1", prefs_agent_2="data/agent_2"
    )

    # To be completed 
    argument_model.agent_1.send_message(
        Message(argument_model.agent_1.get_name(), argument_model.agent_2.get_name(), MessagePerformative.PROPOSE, argument_model.diesel_engine)
        )

    print(*argument_model.agent_2.get_new_messages(), sep='\n')
    
    argument_model.step()
    argument_model.agent_2.send_message(
        Message(argument_model.agent_2.get_name(), argument_model.agent_1.get_name(), MessagePerformative.ACCEPT, argument_model.diesel_engine)
        )
    
    print(*argument_model.agent_1.get_new_messages(), sep='\n')

 

