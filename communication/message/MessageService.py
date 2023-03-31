#!/usr/bin/env python3


from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent.CommunicatingAgent import CommunicatingAgent
    from mesa.time import BaseScheduler
from .Message import Message


class MessageService:
    """MessageService class.

    Class implementing the message service used to dispatch messages
    between communicating agents.

    Not intended to be created more than once: it's a singleton.

    attr:
        scheduler: the scheduler of the sma (Scheduler)
        messages_to_proceed: the list of message to proceed mailbox of the agent (list)
    """
    __instance: Optional["MessageService"] = None

    @staticmethod
    def get_instance() -> "MessageService":
        """Static access method."""
        assert MessageService.__instance is not None
        return MessageService.__instance

    def __init__(
        self, scheduler: "BaseScheduler", instant_delivery: bool = True
    ) -> None:
        """Create a new MessageService object."""
        if MessageService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            MessageService.__instance = self
            self.__scheduler = scheduler
            self.__instant_delivery = instant_delivery
            self.__messages_to_proceed = []

    def set_instant_delivery(self, instant_delivery: bool) -> None:
        """Set the instant delivery parameter."""
        self.__instant_delivery = instant_delivery

    def send_message(self, message: "Message") -> None:
        """Dispatch message if instant delivery active, otherwise add to proceed list"""
        if self.__instant_delivery:
            self.dispatch_message(message)
        else:
            self.__messages_to_proceed.append(message)

    def dispatch_message(self, message: "Message") -> None:
        """Dispatch the message to the right agent."""

        if(message.get_dest() == None):
            for agent in self.__scheduler.agents:
                agent: "CommunicatingAgent"
                if agent.get_name() == message.get_exp():
                    continue
                new_message = Message(message.get_exp(), agent.get_name(), message.get_performative(), message.get_content())
                agent.receive_message(new_message)
        else:
            self.find_agent_from_name(message.get_dest()).receive_message(message)

    def dispatch_messages(self) -> None:
        """Proceed each message received by the message service."""
        if len(self.__messages_to_proceed) > 0:
            for message in self.__messages_to_proceed:
                self.dispatch_message(message)

        self.__messages_to_proceed.clear()

    def find_agent_from_name(self, agent_name) -> "CommunicatingAgent":
        """Return the agent according to the agent name given."""
        for agent in self.__scheduler.agents:  # type: ignore
            agent: "CommunicatingAgent"
            if agent.get_name() == agent_name:
                return agent
        raise ValueError(f"No such agent: {agent_name}")
