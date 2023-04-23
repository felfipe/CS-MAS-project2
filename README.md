# Argumentation-based Dialogue for choosing a car engine

This is a implementation of a an argumentation model with 2 agents arguing between types of car engines. Each engine has five properties : cost, consumption, durability, environmental impact and degree of Noise. Each agent has a list of properties preferences.


#### Implementation aspects

All of the model's behaviors were implemented in accordance with the instructions from the course, except for certain aspects listed bellow:

- The funtion ```is_item_among_top_10_percent()``` identifies whether an item is among an agent's top 10% preferred items. To ensure that at least one item is returned when there are fewer than 10 items in total, we take in consideration the ceiling of the number of items divided by 10.

- If there is no more valid argument, the agent will try to propose another item with a probability of p, otherwise the agent will be convinced by the argument and accept the item. The new proposed item will be the best item (from agent's point of view) not yet proposed by the agent.