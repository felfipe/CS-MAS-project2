#!/usr/bin/env python3

from typing import List, Optional

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

    @staticmethod
    def parse(raw: str, items: dict[str, Item]) -> "Argument":
        """Parses a string representation of an argument

        Args:
            raw (str): the string representation of the argument

        Returns:
            Argument: the parsed argument
        """
        raw_conclusion, raw_premises = raw.split("<-")

        # Parse the conclusion
        # Format: "not" ITEM | ITEM
        conclusion_parts = raw_conclusion.split(maxsplit=1)
        if len(conclusion_parts) == 1:
            item_name = conclusion_parts[0]
            decision = True
        elif len(conclusion_parts) == 2 and conclusion_parts[0].lower() == "not":
            item_name = conclusion_parts[-1]
            decision = False
        else:
            msg = f'Invalid conclusion "{raw_conclusion}" in argument "{raw}"'
            raise ValueError(msg)
        item = items[item_name.strip()]

        # Parse the premises
        # Format: NAME=VALUE | NAME>NAME
        comparisons = []
        couple_values = []
        for premise in raw_premises.split(","):
            if "=" in premise:
                name, value = premise.split("=")
                couple_values.append(
                    CoupleValue(
                        criterion_name=CriterionName[name.strip()],
                        value=Value[value.strip()],
                    )
                )
            elif ">" in premise:
                name1, name2 = premise.split(">")
                comparisons.append(
                    Comparison(
                        better_criterion_name=CriterionName[name1.strip()],
                        worse_criterion_name=CriterionName[name2.strip()],
                    )
                )
            else:
                msg = f'Invalid premise "{premise}" in argument "{raw}"'
                raise ValueError(msg)

        return Argument(item, decision, comparisons, couple_values)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Argument):
            return NotImplemented

        return (
            self.item == other.item
            and self.decision == other.decision
            and self.comparisons == other.comparisons
            and self.couple_values == other.couple_values
        )


if __name__ == "__main__":
    """Testing the Argument class."""
    from ..preferences.CriterionValue import CriterionValue

    agent_pref = Preferences()
    agent_pref.set_criterion_name_list(
        [
            CriterionName.DURABILITY,
            CriterionName.ENVIRONMENT_IMPACT,
            CriterionName.CONSUMPTION,
            CriterionName.PRODUCTION_COST,
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
        CriterionName.DURABILITY,
        CriterionName.CONSUMPTION,
        CriterionName.PRODUCTION_COST,
    ]
    attacking_premises = Argument.get_attacking_premises(diesel_engine, agent_pref)
    attacking_premises_names = [p.criterion_name for p in attacking_premises]
    assert attacking_premises_names == [
        CriterionName.ENVIRONMENT_IMPACT,
        CriterionName.NOISE,
    ]

    argument = Argument(
        diesel_engine,
        decision=False,
        comparisons=[
            Comparison(CriterionName.CONSUMPTION, CriterionName.DURABILITY),
            Comparison(CriterionName.ENVIRONMENT_IMPACT, CriterionName.PRODUCTION_COST),
        ],
        couple_values=[CoupleValue(CriterionName.DURABILITY, Value.GOOD)],
    )
    parsed_argument = Argument.parse(
        str(argument), {diesel_engine.get_name(): diesel_engine}
    )
    assert parsed_argument == argument
