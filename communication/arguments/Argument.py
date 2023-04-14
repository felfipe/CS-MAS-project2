#!/usr/bin/env python3

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..preferences.CriterionName import CriterionName
    from ..preferences.Item import Item
    from ..preferences.Preferences import Preferences
    from ..preferences.Value import Value
    from .Comparison import Comparison
    from .CoupleValue import CoupleValue


class Argument:
    """This class implements an argument used during the interaction.

    attr:
        item: the item concerned
        decision: whether the item should be accepted
        comparisons: a list of Comparisons
        couple_values: a list of CoupleValues
    """

    def __init__(
        self,
        item: "Item",
        decision: bool,
        comparisons: Optional[List["Comparison"]] = None,
        couple_values: Optional[List["CoupleValue"]] = None,
    ) -> None:
        """Create a new Argument."""
        if comparisons is None:
            comparisons = []
        if couple_values is None:
            couple_values = []

        self.item = item
        self.decision = decision
        self.comparisons = comparisons
        self.couple_values = couple_values

    def add_premise_comparison(
        self,
        better_criterion_name: "CriterionName",
        worse_criterion_name: "CriterionName",
    ):
        """Adds a premiss comparison in the comparison list"""
        self.comparisons.append(Comparison(better_criterion_name, worse_criterion_name))

    def add_premise_couple_values(
        self, criterion_name: "CriterionName", value: "Value"
    ):
        """Add a premiss couple values in the couple values list"""
        self.couple_values.append(CoupleValue(criterion_name, value))

    def __str__(self) -> str:
        prefix = "" if self.decision else "not "
        premises = self.couple_values + self.comparisons
        return f"{prefix}{self.item.get_name()} <- " + ", ".join(map(str, premises))

    @staticmethod
    def get_supporting_premises(
        item: "Item", preferences: "Preferences"
    ) -> List["CoupleValue"]:
        """Generates a list of premisses which can be used to support an item

        params:
            item (Item): name of the item
        returns:
            list of all premisses PRO an item (sorted by order of importance
            based on agent's preferences)
        """
        prems = []
        for criterion_name in preferences.get_criterion_name_list():
            value = preferences.get_value(item, criterion_name)
            if value.value >= Value.GOOD.value:
                prems.append(CoupleValue(criterion_name, value))

        return prems

    @staticmethod
    def get_attacking_premises(
        item: "Item", preferences: "Preferences"
    ) -> List["CoupleValue"]:
        """Generates a list of premisses which can be used to attack an item

        params:
            item (Item): name of the item
        returns:
            list of all premisses CON an item (sorted by order of importance
            based on agent's preferences)
        """

        prems = []
        for criterion_name in preferences.get_criterion_name_list():
            value = preferences.get_value(item, criterion_name)
            if value.value <= Value.BAD.value:
                prems.append(CoupleValue(criterion_name, value))

        return prems
