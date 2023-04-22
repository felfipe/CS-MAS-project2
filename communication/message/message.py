#!/usr/bin/env python3

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .message_performative import MessagePerformative

BROADCAST = None


class Message:
    """Message class.
    Class implementing the message object which is exchanged between agents through
    a message service during communication.

    attr:
        from_agent: the sender of the message (id)
        to_agent: the receiver of the message (id). If null, broadcast.
        message_performative: the performative of the message
        content: the content of the message
    """

    def __init__(
        self,
        from_agent: str,
        to_agent: Optional[str],
        message_performative: "MessagePerformative",
        content: str,
    ):
        """Create a new message."""
        self.__from_agent = from_agent
        self.__to_agent = to_agent
        self.__message_performative = message_performative
        self.__content = content

    def __str__(self):
        """Return Message as a String."""
        return (
            "From "
            + str(self.__from_agent)
            + " to "
            + str(self.__to_agent)
            + " ("
            + str(self.__message_performative)
            + ") "
            + str(self.__content)
        )

    def get_exp(self) -> str:
        """Return the sender of the message."""
        return self.__from_agent

    def get_dest(self) -> Optional[str]:
        """Return the receiver of the message."""
        return self.__to_agent

    def get_performative(self) -> "MessagePerformative":
        """Return the performative of the message."""
        return self.__message_performative

    def get_content(self) -> str:
        """Return the content of the message."""
        return self.__content
