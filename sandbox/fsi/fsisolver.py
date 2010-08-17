__author__ = "Kristoffer Selim and Anders Logg"
__copyright__ = "Copyright (C) 2010 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

# Last changed: 2010-08-17

__all__ = ["FSISolver"]

from dolfin import *
from cbc.common import CBCSolver

from primalsolver import PrimalSolver
from dualsolver import DualSolver
from adaptivity import estimate_error, refine_mesh

class FSISolver(CBCSolver):

    def __init__(self, problem):
        "Initialize FSI solver"

        # Initialize base class
        CBCSolver.__init__(self)

        # Set solver parameters
        self.parameters = Parameters("solver_parameters")
        self.parameters.add("plot_solution", False)
        self.parameters.add("save_solution", True)
        self.parameters.add("save_series", True)
        self.parameters.add("tolerance", 0.1)
        self.parameters.add("maxiter", 100)
        self.parameters.add("itertol", 1e-10)
        self.parameters.add("num_smoothings", 50)

        # Set DOLFIN parameters
        parameters["form_compiler"]["cpp_optimize"] = True

        # Store problem
        self.problem = problem

    def solve(self):
        "Solve the FSI problem (main adaptive loop)"

        # Adaptive loop
        while True:

            # Solve primal problem
            begin("Solving primal problem")
            primal_solver = PrimalSolver(self.problem, self.parameters)
            U = primal_solver.solve()
            end()

            # Solve dual problem
            begin("Solving dual problem")
            dual_solver = DualSolver(self.problem, self.parameters)
            dual_solver.solve()
            end()


            return


            # Estimate error and compute error indicators
            begin("Estimating error and computing error indicators")
            error, indicators = estimate_error()
            end()

            # Check if error is small enough
            begin("Checking error estimate")
            if error < self.parameters["tolerance"]:
                info_green("Adaptive solver converged: error = %g < tolerance = %g" % (error, tolerance))
                break
            end()

            # Refine mesh
            begin("Refining mesh")
            mesh = None
            mesh = refine_mesh(mesh, indicators)
            end()

        # Return solution
        return U

    def _solve_primal(self):
        "Solve primal problem"

        begin("Solving primal problem")

        # Write solver here

        end()

    def _solve_dual(self):
        "Solve dual problem"

        begin("Solving dual problem")

        # Write solver here

        end()