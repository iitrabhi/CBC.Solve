"""This module defines the fluid problem (F)
"""

__author__ = "Kristoffer Selim and Anders Logg"
__copyright__ = "Copyright (C) 2010 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

# Last changed: 2011-01-28

__all__ = ["FluidProblem", "extract_solution"]

from dolfin import *
from cbc.flow import NavierStokes

# Define fluid problem
class FluidProblem(NavierStokes):

    def __init__(self, problem):

        # Store problem
        self.problem = problem

        # Store fluid mesh as Omega
        self.Omega= problem.fluid_mesh()

        # Initialize base class
        NavierStokes.__init__(self)

        # Don't plot and save solution in subsolvers
        self.parameters["solver_parameters"]["plot_solution"] = False
        self.parameters["solver_parameters"]["save_solution"] = False

    def mesh(self):
        return self.Omega
    
    def viscosity(self):
        return self.problem.viscosity()

    def density(self):
        return self.problem.density()

    def velocity_dirichlet_values(self):
        return self.problem.velocity_dirichlet_values()

    def velocity_dirichlet_boundaries(self):
        return self.problem.velocity_dirichlet_boundaries()

    def pressure_dirichlet_values(self):
        return self.problem.pressure_dirichlet_values()

    def pressure_dirichlet_boundaries(self):
        return self.problem.pressure_dirichlet_boundaries()

    def velocity_initial_condition(self):
        return self.problem.velocity_initial_condition()

    def pressure_initial_condition(self):
        return self.problem.pressure_initial_condition()

    def end_time(self):
        return self.problem.end_time()

    def time_step(self):
        # Time step will be selected elsewhere
        return self.end_time()

    def __str__(self):
        return "The fluid problem (F)"

def extract_solution(F):
    "Extract solution from the fluid problem"

    # Extract solutions from subproblems
    u, p = F.solution()
    
    # Pack up solutions
    U = (u, p)

    return U
