import numpy as np
from optiland import optic, optimization




def differentialEvolution(system):
    problem = optimization.OptimizationProblem()
    input_data = {"optic": system}

    #efl target
    problem.add_operand(operand_type="f2", target=0, weight=1, input_data=input_data)


    # wavefront error target
    for field in system.fields.get_field_coords():
        input_data = {
            "optic": system,
            "Hx": field[0],
            "Hy": field[1],
            "num_rays": 3,
            "wavelength": 0.587,
            "distribution": "gaussian_quad",
        }
        problem.add_operand(
            operand_type="OPD_difference",
            target=0,
            weight=1,
            input_data=input_data,
        )

    problem.add_variable(system, "radius", surface_number=1, min_val=-150, max_val=-30)
    problem.add_variable(system, "thickness", surface_number=1, min_val=-100, max_val=-20)
    problem.add_variable(system, "conic", surface_number=1, min_val=-100, max_val=100)


    problem.add_variable(system, "radius", surface_number=2, min_val=5, max_val=75)
    problem.add_variable(system, "thickness", surface_number=2, min_val=30, max_val=150)
    problem.add_variable(system, "conic", surface_number=2, min_val=100, max_val=100)


    problem.add_variable(system, "thickness", surface_number=8, min_val=-100, max_val=100)



    optimizer = optimization.DifferentialEvolution(problem)
    
    optimizer.optimize(maxiter=1, disp=False, workers=-1)
    problem.info()

    return(system)