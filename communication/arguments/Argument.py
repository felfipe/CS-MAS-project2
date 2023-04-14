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
        val_and_prem = []
        for criterion_name in preferences.get_criterion_name_list():
            value = preferences.get_value(item, criterion_name)
            if value.value >= Value.GOOD.value:
                val_and_prem.append((value.value, CoupleValue(criterion_name, value)))

        # Sort from most important to least important
        val_and_prem.sort(key=lambda vp: vp[0], reverse=True)

        # Return only the premises
        return [vp[1] for vp in val_and_prem]

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

        val_and_prem = []
        for criterion_name in preferences.get_criterion_name_list():
            value = preferences.get_value(item, criterion_name)
            if value.value <= Value.BAD.value:
                val_and_prem.append((value.value, CoupleValue(criterion_name, value)))

        # Sort from most important to least important
        val_and_prem.sort(key=lambda vp: vp[0], reverse=False)

        # Return only the premises
        return [vp[1] for vp in val_and_prem]


if __name__ == "__main__":
    """Testing the Argument class."""
    from ..preferences.CriterionName import CriterionName  # noqa
    from ..preferences.CriterionValue import CriterionValue  # noqa
    from ..preferences.Item import Item  # noqa
    from ..preferences.Preferences import Preferences  # noqa
    from ..preferences.Value import Value  # noqa
    from .CoupleValue import CoupleValue  # noqa

    agent_pref = Preferences()
    agent_pref.set_criterion_name_list(
        [
            CriterionName.PRODUCTION_COST,
            CriterionName.ENVIRONMENT_IMPACT,
            CriterionName.CONSUMPTION,
            CriterionName.DURABILITY,
            CriterionName.NOISE,
        ]
    )

    diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.PRODUCTION_COST, Value.VERY_GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.CONSUMPTION, Value.GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.DURABILITY, Value.VERY_GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.ENVIRONMENT_IMPACT, Value.BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.NOISE, Value.VERY_BAD)
    )

    supporting_premises = Argument.get_supporting_premises(diesel_engine, agent_pref)
    supporting_premises_names = [p.criterion_name for p in supporting_premises]
    assert supporting_premises_names == [
        CriterionName.PRODUCTION_COST,
        CriterionName.DURABILITY,
        CriterionName.CONSUMPTION,
    ]
    attacking_premises = Argument.get_attacking_premises(diesel_engine, agent_pref)
    attacking_premises_names = [p.criterion_name for p in attacking_premises]
    assert attacking_premises_names == [
        CriterionName.NOISE,
        CriterionName.ENVIRONMENT_IMPACT,
    ]
