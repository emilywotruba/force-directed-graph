import tkinter
import random
import math


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
        node_velocity = lists[i + 1]
        print(f"i = {i}, u = {u}, node_velocity = {node_velocity}")

        adj_matrix[node_velocity][u] = adj_matrix[u][node_velocity] = 0.1

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

    adj_matrix = graph_input(nodes, edges,lines)

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

node_coords = []
node_velocity = []
node_ids = []


def move_oval(i):
    new_x = int(node_coords[i][0] * 500)
    new_y = int(node_coords[i][1] * 500)
    canvas.coords(
        node_ids[i],
        new_x - 5,
        new_y - 5,
        new_x + 5,
        new_y + 5
    )


for i in range(len(adj_matrix)):
    xi = [random.random(), random.random()]
    node_coords.append(xi)
    node_velocity.append([0.0, 0.0])
    id = canvas.create_oval(245, 245, 255, 255, fill="red")

    node_ids.append(id)
    move_oval(i)

line_ids = []


def move_line(canvas_id, xi, xj):
    canvas.coords(
        canvas_id,
        int(xi[0] * 500),
        int(xi[1] * 500),
        int(xj[0] * 500),
        int(xj[1] * 500)
    )

for i in range(len(adj_matrix)):
    for j in range(len(adj_matrix)):
        if adj_matrix[i][j] != 0:    #i.e the line an edge exists
            canvas_id = canvas.create_line(0, 0, 0, 0)
            line_ids.append(canvas_id)
            move_line(canvas_id, node_coords[i], node_coords[j])


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
                    force = coulomb_force(node_coords[i], node_coords[j])
                else:
                    force = hooke_force(node_coords[i], node_coords[j], adj_matrix[i][j])
                force_x += force[0]
                force_y += force[1]
        node_velocity[i][0] = (node_velocity[i][0] + alpha * force_x * delta_t) * eta
        node_velocity[i][1] = (node_velocity[i][1] + alpha * force_y * delta_t) * eta
        e_kinetic[0] = e_kinetic[0] + alpha * (node_velocity[i][0] * node_velocity[i][0])
        e_kinetic[1] = e_kinetic[1] + alpha * (node_velocity[i][1] * node_velocity[i][1])

    e_kinetic_total = math.sqrt(e_kinetic[0] * e_kinetic[0] + e_kinetic[1] * e_kinetic[1])
    print(f"total kinetic energy: {e_kinetic_total}")

    for i in range(len(adj_matrix)):
        node_coords[i][0] += node_velocity[i][0] * delta_t
        node_coords[i][1] += node_velocity[i][1] * delta_t
        move_oval(i)

    line_i = 0
    for i in range(len(adj_matrix)):
        for j in range(len(adj_matrix)):
            if adj_matrix[i][j] != 0:
                canvas_id = line_ids[line_i]
                move_line(canvas_id, node_coords[i], node_coords[j])
                line_i += 1

    root.after(1, move)

root.after(1, move)
root.mainloop()
