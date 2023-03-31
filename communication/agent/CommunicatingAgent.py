#!/usr/bin/env python3

from typing import List
from mesa import Agent, Model

from ..mailbox.Mailbox import Mailbox
from ..message.MessageService import MessageService
from ..message.Message import Message
from ..message.MessagePerformative import MessagePerformative


class CommunicatingAgent(Agent):
    """CommunicatingAgent class.
    Class implementing communicating agent in a generalized manner.

    Not intended to be used on its own, but to inherit its methods to multiple
    other agents.

    attr:
        name: The name of the agent (str)
        mailbox: The mailbox of the agent (Mailbox)
        message_service: The message service used to send and receive message
            (MessageService)
    """

    def __init__(self, unique_id: int, model: Model, name: str) -> None:
        """Create a new communicating agent."""
        super().__init__(unique_id, model)
        self.__name = name
        self.__mailbox = Mailbox()
        self.__messages_service = MessageService.get_instance()

    def step(self) -> None:
        """The step methods of the agent called by the scheduler at each time tick."""
        super().step()

    def get_name(self) -> str:
        """Return the name of the communicating agent."""
        return self.__name

    def receive_message(self, message: Message) -> None:
        """Receive a message and store it in the mailbox.

        Called by the MessageService object."""
        self.__mailbox.receive_messages(message)

    def send_message(self, message: Message) -> None:
        """Send message through the MessageService object."""
        self.__messages_service.send_message(message)

    def get_new_messages(self) -> List[Message]:
        """Return all the unread messages."""
        return self.__mailbox.get_new_messages()

    def get_messages(self) -> List[Message]:
        """Return all the received messages."""
        return self.__mailbox.get_messages()

    def get_messages_from_performative(
        self, performative: MessagePerformative
    ) -> List[Message]:
        """Return a list of messages which have the same performative."""
        return self.__mailbox.get_messages_from_performative(performative)

    def get_messages_from_exp(self, exp: str) -> List[Message]:
        """Return a list of messages which have the same sender."""
        return self.__mailbox.get_messages_from_exp(exp)
