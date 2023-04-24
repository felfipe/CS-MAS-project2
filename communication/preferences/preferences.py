#!/usr/bin/env python3

import math
import os
import random
from typing import List, Dict, Optional

import pandas as pd

from .criterion_name import CriterionName
from .criterion_value import CriterionValue
from .item import Item
from .values import Value


class Preferences:
    """Preferences class.
    This class implements the preferences of an agent.

    attr:
        criterion_name_list: the list of criterion name (ordered by importance)
        criterion_value_list: the list of criterion value
    """

    def __init__(self) -> None:
        """Creates a new Preferences object."""
        self.__criterion_name_list: List[CriterionName] = []
        self.__criterion_value_list: List[CriterionValue] = []

    @staticmethod
    def generate_random(items: Dict[str, Item], rand: Optional[random.Random]=None):
        if rand is None:
            rand = random.Random()

        # Generate a random criterion name list
        p = Preferences()
        criterion_name_list = list(CriterionName)
        rand.shuffle(criterion_name_list)
        p.set_criterion_name_list(criterion_name_list)

        # Generate a random value for each criterion
        for item in items.values():
            for criterion_name in CriterionName:
                # Random value for each item and criterion
                value = rand.choice(list(Value))
                p.add_criterion_value(CriterionValue(item, criterion_name, value))

        return p

    @staticmethod
    def load(dir_path: str, items: Dict[str, Item]):
        p = Preferences()
        p.read_criteria_from_csv(os.path.join(dir_path, "criteria.csv"))
        p.read_values_from_csv(os.path.join(dir_path, "values.csv"), items)
        return p

    def read_criteria_from_csv(self, filepath: str):
        data = pd.read_csv(filepath)

        # Sort by rank (top rank == 0)
        data.sort_values("rank", ascending=True, inplace=True)

        # Convert from str to CriterionName
        criterion_name_list = []
        for c in data["criterion_name"]:
            criterion_name_list.append(CriterionName[c])

        # Set criteria
        self.set_criterion_name_list(criterion_name_list)

    def read_values_from_csv(self, filepath: str, items: Dict[str, Item]):
        data = pd.read_csv(filepath)

        # Create any items which are missing in the items dictionary
        for item_name in data["item"].unique():
            if item_name not in items:
                items[item_name] = Item(item_name, "No description.")

        # Go through each row and add the corresponding criterion value
        for _, row in data.iterrows():
            # Parse this row's data
            item = items[row["item"]]
            criterion_name = CriterionName[row["criterion_name"]]
            value = Value[row["value"]]

            # Add it to the preferences
            self.add_criterion_value(CriterionValue(item, criterion_name, value))

        return items

    def get_criterion_name_list(self):
        """Returns the list of criterion name."""
        return self.__criterion_name_list

    def get_criterion_value_list(self) -> List[CriterionValue]:
        """Returns the list of criterion value."""
        return self.__criterion_value_list

    def set_criterion_name_list(self, criterion_name_list: List[CriterionName]):
        """Sets the list of criterion name."""
        self.__criterion_name_list = criterion_name_list

    def add_criterion_value(self, criterion_value: CriterionValue) -> None:
        """Adds a criterion value in the list."""
        self.__criterion_value_list.append(criterion_value)

    def get_value(self, item: Item, criterion_name: CriterionName) -> Value:
        """Gets the value for a given item and a given criterion name."""
        for value in self.__criterion_value_list:
            if (
                value.get_item() == item
                and value.get_criterion_name() == criterion_name
            ):
                return value.get_value()
        msg = f"No value found for {item=} {criterion_name=}"
        raise ValueError(msg)

    def is_preferred_criterion(
        self, criterion_name_1: CriterionName, criterion_name_2: CriterionName
    ) -> bool:
        """Returns if a criterion 1 is preferred to the criterion 2."""
        for criterion_name in self.__criterion_name_list:
            if criterion_name == criterion_name_1:
                return True
            if criterion_name == criterion_name_2:
                return False
        msg = f"Criteria not found: {criterion_name_1, criterion_name_2}"
        raise ValueError(msg)

    def is_preferred_item(self, item_1: Item, item_2: Item) -> bool:
        """Returns if the item 1 is preferred to the item 2."""
        return item_1.get_score(self) > item_2.get_score(self)

    def most_preferred(self, item: Dict[str, Item], rand: Optional[random.Random]=None) -> Item:
        """Returns the most preferred item from a list."""
        if rand is None:
            rand = random.Random()

        # compute scores to each item and filter only the best scores
        scores = [(item.get_score(self), item) for item in item.values()]
        max_score = max(scores, key=lambda x: x[0])[0]
        best_scores = [item for item in scores if item[0] == max_score]

        # select randomly among the best scores
        selected_item = rand.choice(best_scores)[1]

        return selected_item

    def is_item_among_top_10_percent(self, item: Item, items: Dict[str, Item], x : Optional[int] = 0.1) -> bool:
        """
        Return whether a given item is among the top 10 percent of the preferred items.
        Optionally, it is possible to pass x as parameter to change the percentage.

        :return: a boolean, True means that the item is among the favourite ones
        """
        item_list = list(items.values())

        # take the ceil of the resulting division
        k_top10 = math.ceil(x * len(item_list))
        item_list.sort(key=lambda item: item.get_score(self), reverse=True)

        if item in item_list[:k_top10]:
            return True

        return False


if __name__ == "__main__":
    """Testing the Preferences class."""
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
        CriterionValue(diesel_engine, CriterionName.ENVIRONMENT_IMPACT, Value.VERY_BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.NOISE, Value.VERY_BAD)
    )

    electric_engine = Item("Electric Engine", "A very quiet engine")
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.PRODUCTION_COST, Value.BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.CONSUMPTION, Value.VERY_BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.DURABILITY, Value.GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(
            electric_engine, CriterionName.ENVIRONMENT_IMPACT, Value.VERY_GOOD
        )
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.NOISE, Value.VERY_GOOD)
    )

    """test list of preferences"""
    print(diesel_engine)
    print(electric_engine)
    print(diesel_engine.get_value(agent_pref, CriterionName.PRODUCTION_COST))
    print(
        agent_pref.is_preferred_criterion(
            CriterionName.CONSUMPTION, CriterionName.NOISE
        )
    )
    print(
        "Electric Engine > Diesel Engine : {}".format(
            agent_pref.is_preferred_item(electric_engine, diesel_engine)
        )
    )
    print(
        "Diesel Engine > Electric Engine : {}".format(
            agent_pref.is_preferred_item(diesel_engine, electric_engine)
        )
    )
    print(
        "Electric Engine (for agent 1) = {}".format(
            electric_engine.get_score(agent_pref)
        )
    )
    print(f"Diesel Engine (for agent 1) = {diesel_engine.get_score(agent_pref)}")
    print(
        "Most preferred item is : {}".format(
            agent_pref.most_preferred([diesel_engine, electric_engine]).get_name()
        )
    )

    print(
        "Diesel is in top 10 percent : {}".format(
            agent_pref.is_item_among_top_10_percent(
                diesel_engine, [diesel_engine, electric_engine]
            )
        )
    )

    # Test reading preferences from csv for agent 1
    items = []
    p = Preferences.load("data/agent_1", items)
    assert p.get_criterion_name_list() == [
        CriterionName.PRODUCTION_COST,  # c1
        CriterionName.ENVIRONMENT_IMPACT,  # c4
        CriterionName.CONSUMPTION,  # c2
        CriterionName.DURABILITY,  # c3
        CriterionName.NOISE,  # c5
    ]
    assert len(items) == 2, "Missing items should be added"
    assert {i.get_name() for i in items} == {
        "ICED",
        "E",
    }, "The correct items should be added"
    # Ensure ICED is the first item for the remainder of the tests
    if items[0].get_name() == "E":
        items.reverse()
    assert p.get_value(items[0], CriterionName.CONSUMPTION) == Value.GOOD
    assert p.get_value(items[1], CriterionName.ENVIRONMENT_IMPACT) == Value.VERY_GOOD

    # Test reading preferences from csv for agent 2
    old_items = items.copy()
    p = Preferences.load("data/agent_2", items)
    assert p.get_criterion_name_list() == [
        CriterionName.ENVIRONMENT_IMPACT,  # c4
        CriterionName.NOISE,  # c5
        CriterionName.PRODUCTION_COST,  # c1
        CriterionName.CONSUMPTION,  # c2
        CriterionName.DURABILITY,  # c3
    ]
    assert items == old_items, "Existing items should not be replaced"
    assert p.get_value(items[0], CriterionName.CONSUMPTION) == Value.BAD
    assert p.get_value(items[1], CriterionName.ENVIRONMENT_IMPACT) == Value.VERY_GOOD

    print("read_value_from_csv OK")
