# Argumentation-based Dialogue for choosing a car engine

This is a implementation of a an argumentation model with 2 agents arguing between types of car engines. Each engine has five properties : cost, consumption, durability, environmental impact and degree of Noise. Each agent has a list of properties preferences.


## To install and run

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```pip install -r requirements.txt```

To run:

```python3 pw_argumentation.py```

## Implementation aspects

All of the model's behaviors were implemented in accordance with the instructions from the course, except for certain aspects listed bellow:

- The constructor of the model allows for the option of passing a CSV file path that contains the preferences of each agent and items in the format found in the ```data``` folder. If no file is passed, then the preferences and items will be randomly generated. The ```number_items``` parameter specifies the number of engines to be created. If it is not None, the preferences of each agent will also be randomly selected.

- the parameter ```FIRST_AGENT``` $\in$ ```{"Alice", "Bob"}``` specifies the name of the agent that will initiate the conversation.

- The funtion ```is_item_among_top_10_percent()``` identifies whether an item is among an agent's top 10% preferred items. To ensure that at least one item is returned when there are fewer than 10 items in total, we take in consideration the ceiling of the number of items divided by 10.

- We introduced a parameter ```TOP_K``` indicating to ```is_item_among_top_10_percent()``` the percentage of items to consider.

- If there is no more valid argument, the agent will try to propose another item with a probability of ```PROB_ACCEPT_ARGUMENT``` (a parameter we introduced), otherwise the agent will be convinced by the argument and accept the item. The new proposed item will be the best item (from agent's point of view) not yet proposed by the agent.



## Example of arguments generated

```
From Alice to Bob (PROPOSE) Engine8
From Bob to Alice (ASK_WHY) Engine8
From Alice to Bob (ARGUE)     Engine8 <- DURABILITY=GOOD
From Bob to Alice (ARGUE) not Engine8 <- CONSUMPTION=VERY_BAD, CONSUMPTION>DURABILITY
From Alice to Bob (ARGUE)     Engine8 <- DURABILITY=GOOD, DURABILITY>CONSUMPTION
From Bob to Alice (PROPOSE) Engine5
From Alice to Bob (ASK_WHY) Engine5
From Bob to Alice (ARGUE)     Engine5 <- CONSUMPTION=VERY_GOOD
From Alice to Bob (ARGUE) not Engine5 <- DURABILITY=BAD, DURABILITY>CONSUMPTION
From Bob to Alice (ARGUE)     Engine5 <- CONSUMPTION=VERY_GOOD, CONSUMPTION>DURABILITY
From Alice to Bob (PROPOSE) Engine7
From Bob to Alice (ASK_WHY) Engine7
From Alice to Bob (ARGUE)     Engine7 <- CONSUMPTION=VERY_GOOD
From Bob to Alice (ARGUE) not Engine7 <- CONSUMPTION=VERY_BAD
From Alice to Bob (PROPOSE) Engine8
From Bob to Alice (ASK_WHY) Engine8
From Alice to Bob (ARGUE)     Engine8 <- DURABILITY=GOOD
From Bob to Alice (PROPOSE) Engine4
From Alice to Bob (ASK_WHY) Engine4
From Bob to Alice (ARGUE)     Engine4 <- CONSUMPTION=VERY_GOOD
From Alice to Bob (ARGUE)     Engine7 <- PRODUCTION_COST=VERY_GOOD
From Bob to Alice (ARGUE) not Engine7 <- CONSUMPTION=VERY_BAD, CONSUMPTION>PRODUCTION_COST
From Alice to Bob (PROPOSE) Engine8
From Bob to Alice (ASK_WHY) Engine8
From Alice to Bob (ARGUE)     Engine8 <- DURABILITY=GOOD
From Bob to Alice (PROPOSE) Engine6
From Alice to Bob (ASK_WHY) Engine6
From Bob to Alice (ARGUE)     Engine6 <- CONSUMPTION=VERY_GOOD
From Alice to Bob (ARGUE) not Engine6 <- CONSUMPTION=BAD
From Bob to Alice (PROPOSE) Engine5
From Alice to Bob (ASK_WHY) Engine5
From Bob to Alice (ARGUE)     Engine5 <- CONSUMPTION=VERY_GOOD
From Alice to Bob (ACCEPT) Engine5
From Bob to Alice (COMMIT) Engine5
From Alice to Bob (COMMIT) Engine5
Done. Chosen product: Engine5 (No description)
```