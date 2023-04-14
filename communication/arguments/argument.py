#!/usr/bin/env python3

from typing import List, Optional

from ..preferences.criterion_name import CriterionName
from ..preferences.item import Item
from ..preferences.preferences import Preferences
from ..preferences.values import Value
from .comparison import Comparison
from .equality import Equality


class Argument:
    """This class implements an argument used during the interaction.

    attr:
        item: the item concerned
        decision: whether the item should be accepted
        comparisons: a list of Comparison's
        equalities: a list of Equality's
    """

    def __init__(
        self,
        item: "Item",
        decision: bool,
        comparisons: Optional[List["Comparison"]] = None,
        equalities: Optional[List["Equality"]] = None,
    ) -> None:
        """Create a new Argument."""
        if comparisons is None:
            comparisons = []
        if equalities is None:
            equalities = []

        self.item = item
        self.decision = decision
        self.comparisons = comparisons
        self.equalities = equalities

    def add_premise_comparison(
        self,
        better_criterion_name: "CriterionName",
        worse_criterion_name: "CriterionName",
    ):
        """Adds a comparison premise in the comparison list"""
        self.comparisons.append(Comparison(better_criterion_name, worse_criterion_name))

    def add_premise_equality(self, criterion_name: "CriterionName", value: "Value"):
        """Adds an equality premise in the equalities list"""
        self.equalities.append(Equality(criterion_name, value))

    def __str__(self) -> str:
        prefix = "" if self.decision else "not "
        premises = self.equalities + self.comparisons
        return f"{prefix}{self.item.get_name()} <- " + ", ".join(map(str, premises))

    @staticmethod
    def get_supporting_premises(
        item: "Item", preferences: "Preferences"
    ) -> List["Equality"]:
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
                prems.append(Equality(criterion_name, value))

        return prems

    @staticmethod
    def get_attacking_premises(
        item: "Item", preferences: "Preferences"
    ) -> List["Equality"]:
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
                prems.append(Equality(criterion_name, value))

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
        equalities = []
        for premise in raw_premises.split(","):
            if "=" in premise:
                name, value = premise.split("=")
                equalities.append(
                    Equality(
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

        return Argument(item, decision, comparisons, equalities)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Argument):
            return NotImplemented

        return (
            self.item == other.item
            and self.decision == other.decision
            and self.comparisons == other.comparisons
            and self.equalities == other.equalities
        )


if __name__ == "__main__":
    """Testing the Argument class."""
    from ..preferences.criterion_value import CriterionValue

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

    assert Argument.get_supporting_premises(diesel_engine, agent_pref) == [
        Equality(CriterionName.DURABILITY, Value.VERY_GOOD),
        Equality(CriterionName.CONSUMPTION, Value.GOOD),
        Equality(CriterionName.PRODUCTION_COST, Value.VERY_GOOD),
    ]
    assert Argument.get_attacking_premises(diesel_engine, agent_pref) == [
        Equality(CriterionName.ENVIRONMENT_IMPACT, Value.BAD),
        Equality(CriterionName.NOISE, Value.VERY_BAD),
    ]

    argument = Argument(
        diesel_engine,
        decision=False,
        comparisons=[
            Comparison(CriterionName.CONSUMPTION, CriterionName.DURABILITY),
            Comparison(CriterionName.ENVIRONMENT_IMPACT, CriterionName.PRODUCTION_COST),
        ],
        equalities=[Equality(CriterionName.DURABILITY, Value.GOOD)],
    )
    parsed_argument = Argument.parse(
        str(argument), {diesel_engine.get_name(): diesel_engine}
    )
    assert parsed_argument == argument
