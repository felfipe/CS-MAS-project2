#!/usr/bin/env python3

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..preferences.CriterionName import CriterionName
    from ..preferences.Value import Value


class CoupleValue:
    """This class implements a couple value used in argument object.

    attr:
        criterion_name: the criterion
        value: the criterion's value
    """

    def __init__(self, criterion_name: "CriterionName", value: "Value") -> None:
        """Create a new Comparison."""
        self.criterion_name = criterion_name
        self.value = value

    def __str__(self) -> str:
        return self.criterion_name.name + "=" + self.value.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoupleValue):
            return NotImplemented
        return self.criterion_name == other.criterion_name and self.value == other.value
