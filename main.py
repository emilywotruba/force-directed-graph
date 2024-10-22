import tkinter
import random
import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Node:
    coords: Tuple[int, int]
    velocity: Tuple[float, float]
    canvas_id: int

@dataclass
class Line:
    node_from: int
    node_to: int
    canvas_id: int

adj_matrix = []

fname = "example_in/input1.txt"

def graph_input(nodes, edges, lists=[]):
    adj_matrix = []

    for i in range(nodes):
        temp = []
        for j in range(nodes):
            temp.append(0)
        adj_matrix.append(temp)

    for i in range(2, (edges * 2 + 2), 2):
        u = lists[i]
        v = lists[i + 1]
        print(f"i = {i}, u = {u}, v = {v}")

        adj_matrix[v][u] = adj_matrix[u][v] = 0.1

    print("adjacency matrix is : ")
    for i in range(nodes):
        print(adj_matrix[i])

    return adj_matrix

with open(fname) as f:
    lines = f.read().split()
    lines = [int(i) for i in lines]
    print(lines)

    nodes = lines[0]
    edges = lines[1]

    print(f"no of nodes = {nodes}")
    print(f"no of edges = {edges}")

    adj_matrix = graph_input(nodes, edges, lines)

# mass
alpha = 1.0
beta = .0001
spring_characteristic = 1.0

#damping
eta = .99
delta_t = .01

root = tkinter.Tk()
canvas = tkinter.Canvas(root, width=2000, height=2000, background="#FFFFFF")
canvas.pack()

nodes = []
lines = []


def move_nodes():
    for node in nodes:
        canvas.coords(
            node.canvas_id,
            int(node.coords[0] * 500 - 5),
            int(node.coords[1] * 500 - 5),
            int(node.coords[0] * 500 + 5),
            int(node.coords[1] * 500 + 5)
        )


for i in range(len(adj_matrix)):
    nodes.append(Node(
        coords=(random.random(), random.random()),
        velocity=(0.0, 0.0),
        canvas_id=canvas.create_oval(0, 0, 0, 0, fill="red")
    ))

def move_lines():
    for line in lines:
        canvas.coords(
            line.canvas_id,
            int(nodes[line.node_from].coords[0] * 500),
            int(nodes[line.node_from].coords[1] * 500),
            int(nodes[line.node_to].coords[0] * 500),
            int(nodes[line.node_to].coords[1] * 500)
        )

for i in range(len(adj_matrix)):
    for j in range(len(adj_matrix)):
        if adj_matrix[i][j] != 0: # i.e the line an edge exists
            lines.append(Line(
                    node_from=i,
                    node_to=j,
                    canvas_id=canvas.create_line(0, 0, 0, 0)
            ))


def coulomb_force(coords_i, coords_j):  #repulsive force
    distance_x = coords_j[0] - coords_i[0]
    distance_y = coords_j[1] - coords_i[1]
    distance = math.sqrt(
        distance_x * distance_x + 
        distance_y * distance_y
    )
    force = beta / (distance ** 3)
    return [-force * distance_x, -force * distance_y]


def hooke_force(coords_i, coords_j, adjacency_value): #attractive force
    distance_x = coords_j[0] - coords_i[0]
    distance_y = coords_j[1] - coords_i[1]
    distance = math.sqrt(
        distance_x * distance_x + 
        distance_y * distance_y
    )
    distance_delta = distance - adjacency_value
    force = spring_characteristic * distance_delta / distance
    return [force * distance_x, force * distance_y]


def move():
    e_kinetic = [0.0, 0.0]
    for i in range(len(adj_matrix)):
        force_x = 0.0
        force_y = 0.0
        for j in range(len(adj_matrix)):
            if i != j:
                force = []
                if adj_matrix[i][j] == 0.0: # nodes not connected
                    force = coulomb_force(nodes[i].coords, nodes[j].coords)
                else:
                    force = hooke_force(nodes[i].coords, nodes[j].coords, adj_matrix[i][j])
                force_x += force[0]
                force_y += force[1]
        nodes[i].velocity = (
            (nodes[i].velocity[0] + alpha * force_x * delta_t) * eta,
            (nodes[i].velocity[1] + alpha * force_y * delta_t) * eta
        )
        e_kinetic[0] = e_kinetic[0] + alpha * (nodes[i].velocity[0] ** 2)
        e_kinetic[1] = e_kinetic[1] + alpha * (nodes[i].velocity[1] ** 2)

    e_kinetic_total = math.sqrt(e_kinetic[0] * e_kinetic[0] + e_kinetic[1] * e_kinetic[1])
    print(f"total kinetic energy: {e_kinetic_total}")
    print(nodes)

    for i in range(len(adj_matrix)):
        nodes[i].coords = (
            nodes[i].coords[0] + nodes[i].velocity[0] * delta_t,
            nodes[i].coords[1] + nodes[i].velocity[1] * delta_t
        )

    move_nodes()
    move_lines()

    root.after(1, move)

root.after(1, move)
root.mainloop()
