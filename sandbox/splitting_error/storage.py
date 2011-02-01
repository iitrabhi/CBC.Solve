"""This module implements storing/retrieving primal and dual solutions
to and from file. It is used by the primal solver to store solutions,
by the dual solver to read the primal solution, and in the computation
of error indicators to read both the primal and dual solutions.
"""

__author__ = "Kristoffer Selim and Anders Logg"
__copyright__ = "Copyright (C) 2010 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

# Last changed: 2011-01-30

from numpy import append
from dolfin import *

def create_primal_series():
    "Create time series for primal velocity"
    u = TimeSeries("bin/u")
    p = TimeSeries("bin/p")
    return u, p

def create_dual_series():
    "Create time series for dual solution"
    dual_sol = TimeSeries("bin/dual_sol")
    return dual_sol

def read_primal_data(U, t, Omega, series):
    "Read primal variables at given time"

    info("Reading primal data at t = %g" % t)

    # Get primal variables
    (u, p) = U

    # Create vectors for 
    u = Vector()
    p = Vector()

    # Retrieve primal data
    series[0].retrieve(u, t)
    series[1].retrieve(p, t)

def read_dual_data(z, y, t, series):
    "Read dual solution at given time"
    info("Reading dual data at t = %g" % t)
    series.retrieve(z.vector(), t)
    series.retrieve(y.vector(), t)

def read_timestep_range(T, series):
    "Read time step range"

    # Get nodal points for primal time series
    t = series[0].vector_times()

#     # Check that time series is not empty and covers the interval
#     if not (len(t) > 1 and t[0] == 0.0 and t[-1] == T):
#         print "Nodal points for primal time series:", t
#         raise RuntimeError, "Missing primal data"

    return t

def write_primal_data(U, t, series):
    "Write primal data at given time"
    [series[i].store(U[i].vector(), t) for i in range(2)]


def write_dual_data(dual_sol, t, series):
    "Write dual solution at given time"
    series.store(dual_sol.vector(), t)