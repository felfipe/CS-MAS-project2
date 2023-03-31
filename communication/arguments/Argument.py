#!/usr/bin/env python3

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..preferences.CriterionName import CriterionName
    from ..preferences.Item import Item
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
