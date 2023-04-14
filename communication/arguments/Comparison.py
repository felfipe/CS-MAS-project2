#!/usr/bin/env python3

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..preferences.CriterionName import CriterionName


class Comparison:
    """This class implements a comparison object used in argument object.

    attr:
        better_criterion_name: a criterion better than worst_criterion_name
        worse_criterion_name: a criterion worse than best_criterion_name
    """

    def __init__(
        self,
        better_criterion_name: "CriterionName",
        worse_criterion_name: "CriterionName",
    ) -> None:
        """Create a new Comparison."""
        self.better_criterion_name = better_criterion_name
        self.worse_criterion_name = worse_criterion_name

    def __str__(self) -> str:
        return self.better_criterion_name.name + ">" + self.worse_criterion_name.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Comparison):
            return NotImplemented
        return (
            self.better_criterion_name == other.better_criterion_name
            and self.worse_criterion_name == other.worse_criterion_name
        )
