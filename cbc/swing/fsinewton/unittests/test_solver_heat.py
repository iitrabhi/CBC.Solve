"""
A set of tests to insure that FSINewtonSolver is working properly, using a heat equation
"""

__author__ = "Gabriel Balaban"
__copyright__ = "Copyright (C) 2012 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

from dolfin import *
import numpy as np
import fsinewton.problems.minimal_problem as pm
import fsinewton.problems.base as pfsi
import fsinewton.solver.solver_fsinewton as sfsi
import fsinewton.utils.misc_func as mf
np.set_printoptions(precision = 3, edgeitems = np.inf)


#Class used for heat equation tests
class HeatSolver(object):
    """Contains forms for heat equation"""
    def heatforms(self,u1,u0,Iu,v,kn,dx):
        """Heat Equation"""
        r = ((1/kn)*(u1 - u0)*v + dot(grad(0.5*(u1 + u0)),grad(v)))*dx
        j = ((1/kn)*Iu*v + dot(grad(0.5*Iu),grad(v)))*dx
        return r,j

class HeatProblem(pm.FSIMini):
    """FSI mini but made for heat problem testing"""
    def fluid_pressure_initial_condition(self):
        return "1.0 - (x[0]/%g)*(x[0]/%g)" % (pm.meshlength,pm.meshlength)

class TestFSINewtonSolverHeat():
    """A Test class to test the class FSINewtonSolver using Heat Equations"""
    def setup_class(self):
        """Give the class a tolerance value for tests"""
        self.TOL = 1.0 #High tolerance for faster testing

    def get_SingleHeatSolver(self,problem):
        """Generate a SingleHeatSolver object"""
        class SingleHeatSolver(sfsi.FSINewtonSolver,HeatSolver):
            """Heat equation solver for the pressure space"""
            def __init__(self,problem):
                super(SingleHeatSolver,self).__init__(problem)

                #Make the full solution space just the pressure space
                self.fsispace = self.Q_F.collapse()
                self.U1 = Function(self.fsispace)
                
                #Extract the pressure from self.U0 (belongs to the FSINewtonSolver)
                U0new = Function(self.fsispace)
                U0new.assign(self.U0.split()[1])
                self.U0 = U0new

                #Just pressure BC
                self.Q_F = self.fsispace
                self.bcall = self.create_fluid_pressure_bc()

                #Create pressure heat forms
                v = TestFunction(self.fsispace)
                iu = TrialFunction(self.fsispace)
                self.r,self.j = self.heatforms(self.U1,self.U0,iu,v,self.kn,self.problem.dxF)
            def __str__(self):
                return "FSI Newton Single Heat Solver"
        return SingleHeatSolver(problem)

    def get_FullHeatSolver(self,problem):
        """Generate a FullHeatSolver object"""
        class FullHeatSolver(sfsi.FSINewtonSolver,HeatSolver):
            """Heat equation solver for testing the FSINewtonSolver in all spaces"""
            def __init__(self,problem):
                super(FullHeatSolver,self).__init__(problem)

                #Just pressure BC
                self.bcall = self.create_fluid_pressure_bc()
                
                #Overwrite forms Note split() is usually a bad idea but it works here
                self.r,self.j = self.heatforms(self.U1.split()[1],self.U0.split()[1],self.IU[1],self.V[1],self.kn,self.problem.dxF)
            
            def __str__(self):
                return "FSI Newton Full Heat Solver"
        return FullHeatSolver(problem)
    
    def test_heat_single(self, plot_initial = False):
        """
        The FSI minimal problem is set up with a heat equation in the fluid pressure with a parabolic initial value.
        The solution is expected to be smoothed out to be linear over time
        """
        
        #Solve the heat problem for pressure
        problem = HeatProblem()
        solver = self.get_SingleHeatSolver(problem)
        if plot_initial == True:
            plot(solver.U0, title = "Initial Value")
        solver.solve()
        self.compare_to_reference_heat(solver,solver.U1,plotfuncs = False)
    
    def test_heat_fullspace(self,plot_initial = False):
        """Test a heat equation in the pressure space with all other spaces and BC present"""
                
        #Solve the heat problem for pressure
        problem = HeatProblem()
        #Change the final time to speed up the test
        problem.end_time = lambda :1.0
        problem.initial_step = lambda:0.2
        
        solver = self.get_FullHeatSolver(problem)
        if plot_initial == True:
            mf.plot_single(solver.U0,1,"Initial Value")
        solver.solve(single_step = False)
        self.compare_to_reference_heat(solver,solver.U1.split()[1],plotfuncs = False)

    def compare_to_reference_heat(self,solver,solution, plotfuncs = False):
        """Compare the solution generated by the solver to the reference solution""" 
        #Get the Solution out of the mixed space
        try:
            solutionspace = solution.function_space().collapse()
        except:
            #Ok its not a mixed space so no need to collapse
            solutionspace = solution.function_space()
        storesolution = Function(solutionspace)
        storesolution.assign(solution)
        
        #Check to make sure the solution is close to the reference solution
        ref = interpolate(Expression("1.0 - (x[0]/%g)"%(pm.meshlength)),solutionspace)
        
        #Zero out the non fluid DOFs
        mf.assign_to_region(ref,0,solver.problem.strucdomain,exclude = solver.fsi_dofs(solutionspace))

        #Get L2 error and compare to TOL
        E = mf.L2error(ref,storesolution)
        print "L2 error of ", solver.__str__() ,E

        if plotfuncs == True:
            plot(ref, title = "Reference solution, t = infinity")
            plot(storesolution, title = "Calculated Solution")
        assert E < self.TOL,"Error in" + solver.__str__() + " L2 error " + str(E) + " with respect to reference solution greater than TOL " + str(self.TOL)

if __name__ == "__main__":
    tester = TestFSINewtonSolverHeat()
    tester.setup_class()
    tester.test_heat_fullspace()
