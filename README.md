## Group Members
*Mario Cela*

*Giovanni Baccichet*

*Luca Cassenti*

## Biogas plants location

An association of $n$ farmers wants to open $p$ plants to produce energy from biogas. 
Each plant will be opened at a farm of a member of the association and will be powered with corn chopping purchased from the farm itself or from other neighboring farms.

Each farm $i$ can provide at most $c_i$ tons of corn chopping, with a percentage of dry matter $a_i$. As you may know, dry matter is the key component of corn chopping used for biogas production. In order to maintain the quality of produced energy, each plant must burn a mixture of corn chopping with a percentage of dry matter between $k_{min}$ and $k_{max}$. 

At most one plant can be located in each farm, and every farm can sell its corn chopping to one and only one plant.

Each farm $i$ is located at coordinates $x_i$ and $y_i$, representing respectively its latitude and longitude, and the cost of moving corn chopping from a farm $i$ to a farm $j$ is proportional to the euclidean distance between the two farms (it does not depend on the actual quantity moved, since the trucks used for this transportations are sufficiently big). 

Under such conditions, every plant produces $Q$ kWh of energy per ton of corn chopping burned. The energy produced by each plant will be fed into the national electricity system, at a unitary price of $b$ (€/kWh). Moreover, due to state regulations, each plant must not produce more than $M$ kWh of energy.

You must locate $p$ plants among the available farms and assign the farms that will supply each plant, with the goal of maximizing the total revenues of the association.

## Solution
The Python programming language is used to solve the problem. In particular, we used the MIP solver from the homonym package.

In the first part of the notebook there is the modelization, with the definition of variables, constraints and objective function.

In the second part there is the code that follows the path shown by the model. 

One of the main difficulties of the problem is to keep all the runtimes under 10 minutes.
To do that, we used an heuristic. Considering that transportation costs are way less than the profits, we modified the objective function, removing the
calculation of costs. Furthermore, we decided to locate plants on farms that have the greater amounts of corn chopping. In this way, the optimization problem is reduced in finding the edges that must be activated for the transportation in order to maximize tons of material burnt.

Solutions are suboptimal, but it is an approach that is usually seen also in real problems: sacrificing optimality to reduce computing times of the machine.

It follows an example of the optimization result.

In particular, red nodes are the one in which it is located a plant, green nodes ar just farms. Edges represent a transportation edge between the two nodes.

![Drag Racing](/src/Images/download.png)

You can find the Jupyter Notebook [here](GiovanniBaccichet_LucaCassenti_MarioCela.ipynb).

If you want just the Python script, you can find it [here](/src/main.py).
