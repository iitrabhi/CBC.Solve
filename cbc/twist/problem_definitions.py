__author__ = "Harish Narayanan"
__copyright__ = "Copyright (C) 2009 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

from dolfin import *
from cbc.common import CBCProblem
from cbc.twist.solution_algorithms import StaticMomentumBalanceSolver, MomentumBalanceSolver, CG1MomentumBalanceSolver
from sys import exit

class StaticHyperelasticity(CBCProblem):
    """Base class for all static hyperelasticity problems"""

    def __init__(self):
        """Create the static hyperelasticity problem"""
        self.solver = StaticMomentumBalanceSolver(self)

    def solve(self):
        """Solve for and return the computed displacement field, u"""
        return self.solver.solve()

    def body_force(self):
        """Return body force, B"""
        return []

    def dirichlet_conditions(self):
        """Return Dirichlet boundary conditions for the displacment
        field"""
        return []

    def dirichlet_boundaries(self):
        """Return boundaries over which Dirichlet conditions act"""
        return []

    def neumann_conditions(self):
        """Return Neumann boundary conditions for the stress field"""
        return []

    def neumann_boundaries(self):
        """Return boundaries over which Neumann conditions act"""
        return []

    def material_model(self):
        pass

    def first_pk_stress(self, u):
        """Return the first Piola-Kirchhoff stress tensor, P, given a
        displacement field, u"""
        return self.material_model().FirstPiolaKirchhoffStress(u)

    def second_pk_stress(self, u):
        """Return the second Piola-Kirchhoff stress tensor, S, given a
        displacement field, u"""
        return self.material_model().SecondPiolaKirchhoffStress(u)

    def functional(self, u):
        """Return value of goal functional"""
        return None

    def reference(self):
        """Return reference value for the goal functional"""
        return None

    def __str__(self):
        """Return a short description of the problem"""
        return "Static hyperelasticity problem"

class Hyperelasticity(StaticHyperelasticity):
    """Base class for all quasistatic/dynamic hyperelasticity
    problems"""

    def __init__(self):

        """Create the hyperelasticity problem"""
        if self.time_stepping() is "CG1":
            print "Using CG1 time-stepping"
            self.solver = CG1MomentumBalanceSolver(self)
        elif self.time_stepping() is "HHT":
            print "Using HHT time-stepping"
            self.solver = MomentumBalanceSolver(self)
        else:
            print "%s time-stepping scheme not supported" % str(self.time_stepping())
            exit(2)

    def solve(self):
        """Solve for and return the computed displacement field, u"""
        return self.solver.solve()

    def step(self, dt):
        "Take a time step of size dt"
        return self.solver.step(dt)

    def update(self):
        "Propagate values to next time step"
        return self.solver.update()

    def end_time(self):
        """Return the end time of the computation"""
        pass

    def time_step(self):
        """Return the time step size"""
        pass

    def is_dynamic(self):
        """Return True if the inertia term is to be considered, or
        False if it is to be neglected (quasi-static)"""
        return False

    def time_stepping(self):
        """Set the default time-stepping scheme to
        Hilber-Hughes-Taylor"""
        return "HHT"

    def reference_density(self):
        """Return the reference density of the material"""
        return []

    def initial_conditions(self):
        """Return initial conditions for displacement field, u0, and
        velocity field, v0""" 
        return [], []

    def dirichlet_conditions(self):
        """Return Dirichlet boundary conditions for the displacment
        field"""
        return []

    def dirichlet_boundaries(self):
        """Return boundaries over which Dirichlet conditions act"""
        return []

    def neumann_conditions(self):
        """Return Neumann boundary conditions for the stress field"""
        return []

    def neumann_boundaries(self):
        """Return boundaries over which Neumann conditions act"""
        return []
