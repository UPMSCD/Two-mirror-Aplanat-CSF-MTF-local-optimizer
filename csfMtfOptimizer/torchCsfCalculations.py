import optiland.backend as be
from optiland.mtf import FFTMTF
from optiland import analysis, optic, optimization
from optiland.optimization.operand import operand_registry
import signal




class mtfProcessing:

    def __init__(self, system, opticalGeometry, eyeModelGeometry, opticalEyeModel):
        self.system = system
        self.opticalGeometry = opticalGeometry
        self.eyeModelGeometry = eyeModelGeometry
        self.opticalEyeModel = opticalEyeModel
        self.field = 0 #for now
        self.freqs_cpd = 0

    def csf_weight_mtf(self, mtfData):

        mm_per_degree = self.opticalGeometry.eyeMilimetersPerDeg

        # Convert MTF data to tensor of shape [num_fields, 2, num_freqs]
        mtf_tensor = be.tensor([
            [be.to_numpy(field[0]), be.to_numpy(field[1])]
            for field in mtfData.mtf
        ], dtype=be.float32)  # shape: [fields, 2, freqs]

        # Convert freq to tensor and scale
        freqs = be.tensor(be.to_numpy(mtfData.freq), dtype=be.float32)
        self.freqs_cpd = freqs * mm_per_degree  # mm to cycles/deg

        #weights
        csf_weights = self.mannos_sakrison_csf(self.freqs_cpd)

        weighted_mtf = mtf_tensor * csf_weights

        return weighted_mtf

    def mannos_sakrison_csf(self, freqs_cpd):
        a = 0.114 * freqs_cpd
        return 2.6 * (0.0192 + a) * be.exp(-a ** 1.1)


    def csf_mtf_merit(self, weighted_mtf):
        avg_mtf = weighted_mtf.mean(dim=1)
        aucs = avg_mtf.sum(dim=1)
        total_auc = aucs.sum()

        return total_auc.item()

    def compute_csf_merit_torch(self):
        opticalGeometry = self.opticalGeometry
        system = self.system

        if opticalGeometry.stopFlag:
            return 999 #set to max merit if stop
        try:
            fft_mtf = FFTMTF(optic=system, num_rays=256)
        except:
            return 0
        csf_mtf = self.csf_weight_mtf(fft_mtf) #add find max field later of obj

        csf_merit = self.csf_mtf_merit(csf_mtf)

        opticalGeometry.meritValue = ((csf_merit))

        
        if  opticalGeometry.meritValue > opticalGeometry.bestScore:
            opticalGeometry.bestScore = opticalGeometry.meritValue
            opticalGeometry.bestSystem = system
        print (str((csf_merit)))

        return (csf_merit)

        

    def csfOptimizer_problem(self):
        system = self.system
        opticalGeometry = self.opticalGeometry
        opticalEyeModel = self.opticalEyeModel
        eyeModelGeometry = self.eyeModelGeometry

        operand_registry.register("csf_optimizer", csfOptimizer, overwrite=True)

        problem = optimization.OptimizationProblem()

        #for field in range(len(system.fields.fields)):
        input_data = {"system":system, "opticalGeometry":opticalGeometry, "opticalEyeModel":opticalEyeModel, "eyeModelGeometry":eyeModelGeometry}

        problem.add_operand(
            operand_type = "csf_optimizer",
            target=999,
            #weight=len(system.fields.fields) - field,
            weight=1,
            input_data=input_data,
        )

        r1 = (system.surface_group.surfaces[1].geometry.radius)
        r2 = (system.surface_group.surfaces[2].geometry.radius)


        problem.add_variable(system, "radius", surface_number=1, min_val=(r1 - 2), max_val=(r1 + 2))
        problem.add_variable(system, "thickness", surface_number=1, min_val=-150, max_val=30)
        problem.add_variable(system, "conic", surface_number=1, min_val=-6, max_val=0)


        problem.add_variable(system, "radius", surface_number=2, min_val=(r2 - 2), max_val=(r2 + 2))
        problem.add_variable(system, "thickness", surface_number=2, min_val=30, max_val=150)
        problem.add_variable(system, "conic", surface_number=2, min_val=-6, max_val=0)


        problem.add_variable(system, "thickness", surface_number=8, min_val=1, max_val=20)


        
        def handler(signum, frame):
            opticalGeometry.stopFlag = True
            print(opticalGeometry.stopFlag)
            print("\n[Interrupt detected] Preparing to stop after this step...")


        signal.signal(signal.SIGINT, handler)  # Catch Ctrl+C


        problem.info()
        optimizer = optimization.DualAnnealing(problem)
        try:
            optimizer.optimize()
        except KeyboardInterrupt:
            print("\n[Optimization interrupted by user.]")
            # Continue to use opticalGeometry.bestSystem
        del system
        del optimizer
        del problem
        be.set_backend("numpy")
        be.grad_mode.disable()
        opticalGeometry.bestSystem = be.to_numpy(opticalGeometry.bestSystem)
        return(opticalGeometry.bestSystem)




        

        
