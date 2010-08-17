__author__ = "Kristoffer Selim and Anders Logg"
__copyright__ = "Copyright (C) 2010 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

# Last changed: 2010-08-17

from dolfin import *
from numpy import array, append
from cbc.common import CBCProblem

from fsisolver import FSISolver

class FSI(CBCProblem):
    "Base class for all FSI problems"

    def __init__(self, parameters=None):
        "Create FSI problem"

        # Initialize base class
        CBCProblem.__init__(self)

        # Create solver
        self.solver = FSISolver(self)

        # Set up parameters
        self.parameters = Parameters("problem_parameters")
        self.parameters.add(self.solver.parameters)

        # Create mappings between submeshes
        self.init_mappings()

    def solve(self):
        "Solve and return computed solution (u_F, p_F, U_S, P_S, U_M, P_M)"

        # Update solver parameters
        self.solver.parameters.update(self.parameters["solver_parameters"])

        # Call solver
        return self.solver.solve()

    def init_mappings(self):
        "Create mappings between submeshes"

        info("Computing mappings between submeshes")

        # Get meshes
        Omega   = self.mesh()
        Omega_F = self.fluid_mesh()
        Omega_S = self.structure_mesh()

        # Extract matching indices for fluid and structure
        structure_to_fluid = compute_vertex_map(Omega_S, Omega_F)

        # Extract matching indices for fluid and structure
        fluid_indices = array([i for i in structure_to_fluid.itervalues()])
        structure_indices = array([i for i in structure_to_fluid.iterkeys()])

        # Extract matching dofs for fluid and structure (for vector P1 elements)
        fdofs = append(fluid_indices, fluid_indices + Omega_F.num_vertices())
        sdofs = append(structure_indices, structure_indices + Omega_S.num_vertices())

        # Initialize FSI boundary and orientation markers
        D = Omega.topology().dim()
        Omega.init(D - 1, D)
        fsi_boundary = MeshFunction("uint", Omega, D - 1)
        fsi_boundary.set_all(0)
        fsi_orientation = Omega.data().create_mesh_function("facet orientation", D - 1)
        fsi_orientation.set_all(0)

        # Compute FSI boundary and orientation markers
        for facet in facets(Omega):

            # Skip facets on the boundary
            if facet.num_entities(D) == 1:
                continue

            # Create the two cells
            c0, c1 = facet.entities(D)
            cell0 = Cell(Omega, c0)
            cell1 = Cell(Omega, c1)

            # Get the two midpoints
            p0 = cell0.midpoint()
            p1 = cell1.midpoint()

            # Check if the points are inside
            p0_inside = self.structure.inside(p0, False)
            p1_inside = self.structure.inside(p1, False)

            # Look for points where exactly one is inside the structure
            if p0_inside and not p1_inside:
                fsi_boundary[facet.index()] = 1
                fsi_orientation[facet.index()] = c1
            elif p1_inside and not p0_inside:
                fsi_boundary[facet.index()] = 1
                fsi_orientation[facet.index()] = c0
            else:
                # Just set c0, will not be used
                fsi_orientation[facet.index()] = c0

        # Store data
        self.fdofs = fdofs
        self.sdofs = sdofs
        self.fsi_boundary = fsi_boundary
        self.fsi_orientation = fsi_orientation

    def add_f2s(self, xs, xf):
        "Compute xs += xf for corresponding indices"
        xs_array = xs.array()
        xf_array = xf.array()
        xs_array[self.sdofs] += xf_array[self.fdofs]
        xs[:] = xs_array

    def add_s2f(self, xf, xs):
        "Compute xf += xs for corresponding indices"
        xf_array = xf.array()
        xs_array = xs.array()
        xf_array[self.fdofs] += xs_array[self.sdofs]
        xf[:] = xf_array