# import time
import json
# import matplotlib.pyplot as plt
import mip
# import networkx as nx
import numpy as np

# start = time.time()


# Reads a .json instance and returns it in a dictionary
def load_instance(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


# Reads a .txt result and returns it
def load_result(filename):
    with open(filename, 'r') as f:
        res = f.read()
    return float(res)


instNum = 10

instance = load_instance(".\\Instances\\instance_{}.json".format(instNum))
if instNum < 5:
    given_result = load_result(".\\Results\\instance_{}.txt".format(instNum))

model = mip.Model(sense="MAXIMIZE", solver_name="CBC")

I = range(instance["n"])

M = instance["M"]  # M is max energy production
Q = instance["Q"]  # Energy produced for ton (kWh / ton)
a = instance["a"]  # % of dry matter
b = instance["b"]  # Revenue (Euros / kWh)
c = instance["c"]  # Availability (ton)
kmax = instance["kmax"]  # Max % of dry matter
kmin = instance["kmin"]  # Min % of dry matter
n = instance["n"]  # Number of farms
p = instance["p"]  # Number of plants
ps = instance["points"]  # Coordinates of farms (x, y)
points = np.array([np.array(ps[i]) for i in I])

u = [model.add_var(name="is_plant", var_type=mip.BINARY) for i in I]
v = [[model.add_var(name="selling_to", var_type=mip.BINARY) for i in I] for j in I]
w = [[model.add_var(name="material_amount", var_type=mip.CONTINUOUS, lb=0.0) for i in I] for j in I]

model.add_constr(mip.xsum(u[i] for i in range(len(u))) == p)

for i in I:
    for j in I:
        model.add_constr(v[i][j] <= u[j])

for i in I:
    model.add_constr(mip.xsum(v[i][j] for j in I) <= 1)

for i in I:
    for j in I:
        model.add_constr(w[i][j] <= c[i] * v[i][j])

for i in I:
    model.add_constr(mip.xsum(w[j][i] * a[j] for j in I) >= mip.xsum(w[j][i] * kmin for j in I))
    model.add_constr(mip.xsum(w[j][i] * a[j] for j in I) <= mip.xsum(w[j][i] * kmax for j in I))

for i in I:
    model.add_constr(mip.xsum(w[j][i] for j in I) * Q <= M)


def fast_distance_matrix(x):
    xy = x @ x.T
    x2 = xy.diagonal()[:, np.newaxis]
    return np.abs(x2 + x2.T - 2. * xy) ** 0.5


distances = fast_distance_matrix(points)
model.objective = mip.maximize(
    mip.xsum(w[i][j] * Q * b for i in I for j in I) - mip.xsum(distances[i][j] * v[i][j] for i in I for j in I))

model.optimize()
result = model.objective_value

gap = 100 * (result - given_result) / given_result

print("\n\n\nREVENUE: {}".format(result))
print("EXPECTED: {}".format(given_result))
print("[!] GAP: {}\n\n\n".format(gap))
