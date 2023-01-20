import os
import mip
import time
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import json

# Reads a .json instance and returns it in a dictionary
def load_instance(filename):
  with open(filename, 'r') as f:
    data = json.load(f)
  return data

# Reads a .txt result and returns it
def load_result(filename):
  with open(filename, 'r') as f:
      result = f.read()
  return float(result)

# SUPPORT FUNCTIONS

# This function computes the distances between all pairs of points
def distance_matrix(points_matrix):
  return [[np.linalg.norm(i - j) for i in points_matrix] for j in points_matrix]

# This functions is a text visualizer for the solution
def print_result(optimal_result, v, u, w, farm_indexes, corn_availability):
    
  print(f"Cost: {optimal_result:.2f} M euro")

  print("Plants:")
  for plant in farm_indexes:
    if u[plant].x > 1e-7:
      print(f"{plant:3d} --> {u[plant].x:7.3f}; farms: ", end='')
      for farm in farm_indexes:
        if v[farm][plant].x > 1e-7:
          print(f"{farm} ({w[farm][plant].x:.2f}/{corn_availability[farm]:.2f}); ", end='')
      print('')

def solve(instance):

  # Start timer for evaluation
  start_time = time.time()

  # Model Initialization
  model = mip.Model(sense="MAXIMIZE", solver_name="CBC")

  # Sets
  farm_indexes = range(instance["n"])

  # Parameters
  max_energy_production = instance["M"]  # M is max energy production
  energy_per_ton = instance["Q"]  # Energy produced for ton (kWh / ton)
  dry_matter_array = np.array(instance["a"])  # % of dry matter
  revenue_per_kwh = instance["b"]  # Revenue (Euros / kWh)
  corn_availability = np.array(instance["c"])  # Availability (ton)
  dry_matter_max = instance["kmax"]  # Max % of dry matter
  dry_matter_min = instance["kmin"]  # Min % of dry matter
  number_of_farms = instance["n"]  # Number of farms
  number_of_plants = instance["p"]  # Number of plants
  coordinates = instance["points"]  # Coordinates of farms (x, y)
  points = np.array([np.array(coordinates[index]) for index in farm_indexes])

  # Variables
  u = np.array([model.add_var(name="is_plant", var_type=mip.BINARY) for farm in farm_indexes])  # Represents if plant exists in farm i
  v = np.array([np.array([model.add_var(name="selling_to", var_type=mip.BINARY) for farm in farm_indexes]) for plant in farm_indexes])  # Represents if farm i sells to plant j
  w = np.array([np.array([model.add_var(name="material_amount", var_type=mip.CONTINUOUS, lb=0.0) for farm in farm_indexes]) for plant in farm_indexes])  # Represents quantity farm i sells to plant j
  
  # Heuristic
  # Since in the given instances revenues are way higher than costs, it is possible to choose in advance all the plants, in fact even the worst positioning
  # still grants an almost optimal result. Thus we decided to proceed following this idea.
  # We decided to choose our plants based on the corn available, as a plant with more corn should require less corn from other farms, thus reducing costs
  # Following this heurisitic results in the constraint on the number of plants being already satisfied, thus we won't include it

  heuristic_plants = sorted([farm for farm in farm_indexes], key=lambda farm: abs(corn_availability[farm] - max(corn_availability))/max(corn_availability))[::-1][:number_of_plants]

  for farm in farm_indexes:
    if farm in heuristic_plants:
      model.add_constr(u[farm] == 1)
    else:
      model.add_constr(u[farm] == 0)

  # Constraints

  # 1) Redudant

  # 2) When the corn chopping is moved from a farm it must be sent to one and only one plant
  for farm in farm_indexes:
    model.add_constr(mip.xsum(v[farm]) <= 1)

  # 3) We can move the corn chopping if and only if the corresponding farm is selling to a specific plant
  for farm in farm_indexes:
    for plant in farm_indexes:
        model.add_constr(w[farm][plant] <= corn_availability[farm] * v[farm][plant])

  # 4) The corn chopping that each plant burns must have a percentage amount of dry matter within a specified range
  for plant in farm_indexes:
    model.add_constr(mip.xsum(np.multiply(w[:, plant], dry_matter_array)) >= mip.xsum(w[:, plant]) * dry_matter_min)
    model.add_constr(mip.xsum(np.multiply(w[:, plant], dry_matter_array)) <= mip.xsum(w[:, plant]) * dry_matter_max)

  # 5) Due to state regulations, we have a limit on the energy produced by each plant. This constraint is introduced for each plant
  for plant in farm_indexes:
    model.add_constr(mip.xsum(w[farm][plant] for farm in farm_indexes) * energy_per_ton <= max_energy_production)

  # 6) When the corn chopping is moved from a farm to another farm, the receiving farm must be a plant:
  for farm in farm_indexes:
    for plant in farm_indexes:
        model.add_constr(v[farm][plant] <= u[plant])

  # Optimization
  # We decided to only focus on the optimization of the revenue and not the minimization of the distances due to what we
  # mentioned above. This only marginally changes the results and only worsen it, thus it's still a feasible solution.

  model.objective = mip.maximize(mip.xsum(w.flatten()))  # Maximize the revenue
  status = model.optimize()

  # Calculate the effective result, now including the cost due to distances
  distances = np.array(distance_matrix(points))
  v_optimized = np.array([np.array([v[farm][plant].x for plant in farm_indexes]) for farm in farm_indexes])
  result = model.objective_value * energy_per_ton * revenue_per_kwh - sum(np.multiply(np.array(distances), v_optimized).flatten())

  # End timer for evaluation
  end_time = time.time()
  execution_time = end_time - start_time

  # Data visualization
  G = nx.Graph()

  for farm in farm_indexes:
    G.add_node(farm, pos=points[farm])

  pos=nx.get_node_attributes(G,'pos')

  color_map = []

  for plant in farm_indexes:
    if u[plant].x == 1:
      color_map.append('#e76f51' )
    else:
      color_map.append('#2a9d8f')

  for farm in farm_indexes:
    for plant in farm_indexes:
      if v[farm][plant].x == 1:
        G.add_edge(farm, plant, label=w[farm][plant].x)

  plt.figure(1, figsize=(25,15))
  nx.draw_networkx(G, font_size=11, pos=pos, node_color=color_map, node_size=1500, alpha=0.90)
  nx.draw_networkx_edge_labels(G,pos,edge_labels=nx.get_edge_attributes(G,'label'), font_color='#f08080')
  plt.show()

  print_result(result, v, u, w, farm_indexes, corn_availability)

  # Return result
  return result


inst = load_instance("./Instances/instance_5.json")
res = load_result("./Results/instance_1.txt")

obj = solve(inst)

gap = 100 * (obj - res) / res

print("\n\n\n")
print("result: {}".format(obj))
print("expected: {}".format(res))
print("gap: {}".format(gap))
