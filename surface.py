"""
Visualizes 2-variable convex(?) optimization problems as 3D surfaces
--------------------------------------------------------------------------
Specify objective and constraints in their standard (convex optimization problem) forms
"""
objective = "x**2 + 3*x*y + 9*y**2 + 2*x - 5*y"
inequality_constraints = ""
equality_constraints = ""

x_limits = "-10,10"
y_limits = "-10,10"
n_points = "50"


from matplotlib import pyplot
from matplotlib.ticker import LinearLocator
from mpl_toolkits.mplot3d import Axes3D

import numpy as numpy
import sympy
from sympy.parsing.sympy_parser import parse_expr


class Surface:
    def __init__(self, function_expr=None):
        self.x_axis = None
        self.y_axis = None
        self.x_vals = None
        self.y_vals = None
        self.z_vals = None
        self.function = function_expr
        self.inequality_constraints = []
        self.equality_constraints = []

    def add_constraint(self, constraint_expr, type="inequality"):
        if type == "inequality":
            self.inequality_constraints.append(constraint_expr)
        elif type == "equality":
            self.equality_constraints.append(constraint_expr)


    def populate(self, xlim, ylim, n_points):
        self.x_axis = numpy.linspace(xlim[0], xlim[1], n_points)
        self.y_axis = numpy.linspace(ylim[0], ylim[1], n_points)
        self.x_vals, self.y_vals = numpy.meshgrid(self.x_axis, self.y_axis)

        self.z_vals = numpy.zeros_like(self.x_vals)
        for i in range(n_points):
            for j in range(n_points):
                self.z_vals[i][j] = self.function.subs(
                        [("x", self.x_vals[i][j]), ("y", self.y_vals[i][j])]
                        )
                for constraint in self.inequality_constraints:
                    if constraint.subs([("x", self.x_vals[i][j]), ("y", self.y_vals[i][j])]) > 0:
                        self.z_vals[i][j] = numpy.nan

                for constraint in self.equality_constraints:
                    if not numpy.isclose(float(constraint.subs([("x", self.x_vals[i][j]), ("y", self.y_vals[i][j])])), 0, 
                                         atol=(self.x_axis[2]-self.x_axis[0])):
                        self.z_vals[i][j] = numpy.nan

    def plot(self, axis):
        axis.plot_surface(self.x_vals, self.y_vals, self.z_vals, color='gray', alpha=0.8)
        axis.zaxis.set_major_locator(LinearLocator(5))
        axis.zaxis.set_major_formatter('{x:.00f}')

        x, y = sympy.symbols('x y')
        if self.inequality_constraints:
            inequalities = [constraint < 0 for constraint in self.inequality_constraints]
            if self.equality_constraints:
                inequalities += [sympy.Eq(constraint, 0) for constraint in self.equality_constraints]
            sympy.plot_implicit(sympy.And(*inequalities), 
                                (x, float(x_limits.split(",")[0]), float(x_limits.split(",")[1])),  
                                (y, float(y_limits.split(",")[0]), float(y_limits.split(",")[1])),
                                line_color='maroon', xlabel="", ylabel="", axis=axis)

        pyplot.show()


fig = pyplot.figure()
axis = fig.add_subplot(111, projection='3d')

surface = Surface(function_expr=parse_expr(objective))

if inequality_constraints:
    for constraint in inequality_constraints.split(","):
        surface.add_constraint(parse_expr(constraint), type="inequality")

if equality_constraints:
    print("Warning: Equality constraint implementation may be lacking visually... "
          + "makes thin lines that are difficult to see")
    for constraint in equality_constraints.split(","):
        surface.add_constraint(parse_expr(constraint), type="equality")

surface.populate(xlim=[float(_s) for _s in x_limits.split(",")], 
                 ylim=[float(_s) for _s in y_limits.split(",")], 
                 n_points=int(n_points))

surface.plot(axis)
