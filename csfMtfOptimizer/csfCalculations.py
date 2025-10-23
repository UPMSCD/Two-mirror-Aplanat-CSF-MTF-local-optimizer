import optiland.backend as be
import copy
from optiland.mtf import FFTMTF
from optiland import analysis, optic, optimization
from optiland.optimization.operand import operand_registry
import signal
from pynput import keyboard

class mtfProcessing:

    def __init__(self, system, opticalGeometry, eyeModelGeometry, opticalEyeModel):
        self.system = system
        self.opticalGeometry = opticalGeometry
        self.eyeModelGeometry = eyeModelGeometry
        self.opticalEyeModel = opticalEyeModel
        self.field = 0 #for now

    def convert_mtf_to_cpd(self, mtfData):

        mm_per_degree = self.opticalGeometry.eyeMilimetersPerDeg

        cpdData = copy.deepcopy(mtfData)
        
        cpdData.freq = cpdData.freq * mm_per_degree

        return cpdData

    def mannos_sakrison_csf(self, f):
        """
        Compute the CSF from the Mannos–Sakrison model.
        
        Parameters:
        - f: spatial frequency (cycles per degree)
        
        Returns:
        - CSF value
        """
        a = 0.114 * f
        return 2.6 * (0.0192 + a) * be.exp(-(a) ** 1.1)

    def csf_weight_mtf(self, mtfData):
        for f in range(len(self.system.fields.fields)):
            for i in range(len(mtfData.freq)):
                weight = self.mannos_sakrison_csf(mtfData.freq[i])
                mtfData.mtf[f][0][i] = mtfData.mtf[f][0][i] * weight #sagittal
                mtfData.mtf[f][1][i] = mtfData.mtf[f][1][i] * weight #tangential
            
        return mtfData






    def get_average_mtf(self, mtfData):
        frequency = mtfData.freq

        field = self.field

        mtf_modulations = csfData.mtf[field]


        sagittal = mtf_modulations[0]
        tangential = mtf_modulations[1]

        average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)

        frequency_cpd = frequency * mm_per_degree
        with open("output.txt", "w") as file:
            file.write(f"Field {field}")
            file.write("\n")

            file.write("Averages: ")
            file.write(str(frequency_cpd))

            file.write("\n")
            file.write(str(average_mtf))




class csfGrapher:
    def __init__(self, system, opticalGeometry, opticalEyeModel, eyeModelGeometry ):
        self.system = system
        self.opticalGeometry = opticalGeometry
        self.opticalEyeModel = opticalEyeModel
        self.eyeModelGeometry = eyeModelGeometry
        self.fft_mtf = 0
        self.csf_mtf = 0
        self.meritValue = 0


    def get_csf_mtf_result(self):
        visualFidelityOptimizer = mtfProcessing(self.system, self.opticalGeometry, self.opticalEyeModel, self.eyeModelGeometry) #add find max field later of obj

        self.fft_mtf = FFTMTF(optic=self.system, num_rays=256)
        cpd_mtf = mtfProcessing.convert_mtf_to_cpd(visualFidelityOptimizer, self.fft_mtf) #add find max field later of obj

        self.csf_mtf = mtfProcessing.csf_weight_mtf(visualFidelityOptimizer, cpd_mtf)

        self.meritValue = self.csf_weighted_mtf_sum(self.csf_mtf)
        self.meritValue = self.csf_weighted_mtf_sum(self.fft_mtf)
        print(f"Total System FFT MTF auc: {str(self.meritValue)}")



    def csf_weighted_mtf_sum(self, mtfData):
        freq = mtfData.freq
        aucs = 0
        for field in range(len(mtfData.mtf)): # while in all fields avg and sum
            mtf_modulations = mtfData.mtf[field]

            sagittal = mtf_modulations[0]
            tangential = mtf_modulations[1]

            average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
            aucs = aucs + be.sum(average_mtf)
        return aucs



def csfFieldOptimizer(system, opticalGeometry, opticalEyeModel, eyeModelGeometry, field):

    if opticalGeometry.stopFlag:
        return 999 #set to max merit if stop
    visualFidelityOptimizer = mtfProcessing(system, opticalGeometry, opticalEyeModel, eyeModelGeometry) #add find max field later of obj
    try:
        fft_mtf = FFTMTF(optic=system, num_rays=256)
    except:
        return 0
    cpd_mtf = mtfProcessing.convert_mtf_to_cpd(visualFidelityOptimizer, fft_mtf) #add find max field later of obj

    csf_mtf = mtfProcessing.csf_weight_mtf(visualFidelityOptimizer, cpd_mtf)


    freq = csf_mtf.freq
    aucs = 0
    mtf_modulations = csf_mtf.mtf[field]

    sagittal = mtf_modulations[0]
    tangential = mtf_modulations[1]

    average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
    aucs = aucs + (be.sum(average_mtf))
    

    print (str((aucs)))


    aucs2 = 0
    for field in range(len(csf_mtf.mtf)): # while in all fields avg and sum
        mtf_modulations = csf_mtf.mtf[field]

        sagittal = mtf_modulations[0]
        tangential = mtf_modulations[1]

        average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
        aucs2 = aucs2 + be.sum(average_mtf)
    # Return the average AUC across all curves
    opticalGeometry.meritValue = ((aucs2))

    
    if  opticalGeometry.meritValue > opticalGeometry.bestScore:
        opticalGeometry.bestScore = opticalGeometry.meritValue
        opticalGeometry.bestSystem = copy.deepcopy(system)

    return (aucs)




def csfFieldDifferenceOptimizer(system, opticalGeometry, opticalEyeModel, eyeModelGeometry, field):

    if opticalGeometry.stopFlag:
        return 999 #set to max merit if stop
    visualFidelityOptimizer = mtfProcessing(system, opticalGeometry, opticalEyeModel, eyeModelGeometry) #add find max field later of obj
    try:
        fft_mtf = FFTMTF(optic=system, num_rays=256)
    except:
        return 0
    cpd_mtf = mtfProcessing.convert_mtf_to_cpd(visualFidelityOptimizer, fft_mtf) #add find max field later of obj

    csf_mtf = mtfProcessing.csf_weight_mtf(visualFidelityOptimizer, cpd_mtf)


    freq = csf_mtf.freq
    aucs = 0
    mtf_modulations = csf_mtf.mtf[field]

    sagittal = mtf_modulations[0]
    tangential = mtf_modulations[1]

    sagittalAvg = be.sum(sagittal)
    tangentialAvg = be.sum(tangential)

    if(sagittalAvg != tangentialAvg):
        if(sagittalAvg > tangentialAvg):
            diff = sagittalAvg - tangentialAvg
            average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
            aucs = aucs + (be.sum(average_mtf)) - diff
        if(sagittalAvg < tangentialAvg):
            diff = tangentialAvg - sagittalAvg
            average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
            aucs = aucs + (be.sum(average_mtf)) - diff
    else:
        average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
        aucs = aucs + (be.sum(average_mtf))
        
   



    aucs2 = 0
    for field in range(len(csf_mtf.mtf)): # while in all fields avg and sum
        mtf_modulations = csf_mtf.mtf[field]

        sagittal = mtf_modulations[0]
        tangential = mtf_modulations[1]

        sagittalAvg = be.sum(sagittal)
        tangentialAvg = be.sum(tangential)

        if(sagittalAvg != tangentialAvg):
            if(sagittalAvg > tangentialAvg):
                diff = sagittalAvg - tangentialAvg
                average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
                aucs2 = aucs2 + ((be.sum(average_mtf)) - diff) * (len(system.fields.fields) - field)
            if(sagittalAvg < tangentialAvg):
                diff = tangentialAvg - sagittalAvg
                average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
                aucs2 = aucs2 + ((be.sum(average_mtf)) - diff) * (len(system.fields.fields) - field)
        else:
            average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
            aucs2 = (aucs2 + (be.sum(average_mtf))) * (len(system.fields.fields) - field)
        
    opticalGeometry.meritValue = ((aucs2))
    print(str(aucs2))

    
    if  opticalGeometry.meritValue > opticalGeometry.bestScore:
        opticalGeometry.bestScore = opticalGeometry.meritValue
        opticalGeometry.bestSystem = copy.deepcopy(system)

    return (aucs)


def csfOptimizer(system, opticalGeometry, opticalEyeModel, eyeModelGeometry):

    if opticalGeometry.stopFlag:
        return 999 #set to max merit if stop
    visualFidelityOptimizer = mtfProcessing(system, opticalGeometry, opticalEyeModel, eyeModelGeometry) #add find max field later of obj
    try:
        fft_mtf = FFTMTF(optic=system, num_rays=256)
    except:
        return 0
    cpd_mtf = mtfProcessing.convert_mtf_to_cpd(visualFidelityOptimizer, fft_mtf) #add find max field later of obj

    csf_mtf = mtfProcessing.csf_weight_mtf(visualFidelityOptimizer, cpd_mtf)


    aucs2 = 0
    for field in range(len(csf_mtf.mtf)): # while in all fields avg and sum
        mtf_modulations = csf_mtf.mtf[field]

        sagittal = mtf_modulations[0]
        tangential = mtf_modulations[1]

        average_mtf = be.mean(be.stack([sagittal, tangential]), axis=0)
        aucs2 = aucs2 + be.sum(average_mtf)
    # Return the average AUC across all curves
    opticalGeometry.meritValue = ((aucs2))

    
    if  opticalGeometry.meritValue > opticalGeometry.bestScore:
        opticalGeometry.bestScore = opticalGeometry.meritValue
        opticalGeometry.bestSystem = copy.deepcopy(system)
    print (str((aucs2)))

    return (aucs2)


def csfMinimumOptimizer(system, opticalGeometry, opticalEyeModel, eyeModelGeometry):

    if opticalGeometry.stopFlag:
        return 999 #set to max merit if stop
    visualFidelityOptimizer = mtfProcessing(system, opticalGeometry, opticalEyeModel, eyeModelGeometry) #add find max field later of obj
    try:
        fft_mtf = FFTMTF(optic=system, num_rays=256)
    except:
        return 0
    cpd_mtf = mtfProcessing.convert_mtf_to_cpd(visualFidelityOptimizer, fft_mtf) #add find max field later of obj

    csf_mtf = mtfProcessing.csf_weight_mtf(visualFidelityOptimizer, cpd_mtf)


    aucs2 = 0
    for field in range(len(csf_mtf.mtf)): # while in all fields
        mtf_modulations = csf_mtf.mtf[1]

        sagittal = mtf_modulations[0]
        tangential = mtf_modulations[1]

        sagittalAvg = be.sum(sagittal)
        tangentialAvg = be.sum(tangential)

        if(sagittalAvg > tangentialAvg):
            #print('tangential bad')
            aucs2 = aucs2 + tangentialAvg
        if(sagittalAvg < tangentialAvg):
            #print('sagittal bad')
            aucs2 = aucs2 + sagittalAvg

    # Return the average AUC across all curves
    opticalGeometry.meritValue = ((aucs2))

    
    if  opticalGeometry.meritValue > opticalGeometry.bestScore:
        opticalGeometry.bestScore = opticalGeometry.meritValue
        opticalGeometry.bestSystem = copy.deepcopy(system)
    print (str((aucs2)))

    return (aucs2)

    

def csfOptimizer_problem(system, opticalGeometry, opticalEyeModel, eyeModelGeometry):
    operand_registry.register("csf_field_optimizer", csfFieldOptimizer, overwrite=True)
    operand_registry.register("csf_optimizer", csfOptimizer, overwrite=True)
    operand_registry.register("csf_field_difference_optimizer", csfFieldDifferenceOptimizer, overwrite=True)
    operand_registry.register("csf_minimum_optimizer", csfMinimumOptimizer, overwrite=True)

    problem = optimization.OptimizationProblem()

    #for field in range(len(system.fields.fields)):
    input_data = {"system":system, "opticalGeometry":opticalGeometry, "opticalEyeModel":opticalEyeModel, "eyeModelGeometry":eyeModelGeometry}
    #input_data = {"system":system, "opticalGeometry":opticalGeometry, "opticalEyeModel":opticalEyeModel, "eyeModelGeometry":eyeModelGeometry, "field":field}

    problem.add_operand(
        operand_type = "csf_minimum_optimizer",
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


    
    #def handler(signum, frame):

    #signal.signal(signal.SIGINT, handler)  # Catch Ctrl+C

    def on_press(key):
        if key == keyboard.Key.esc:
            opticalGeometry.stopFlag = True
            print(opticalGeometry.stopFlag)
            print("\n[Interrupt detected] Preparing to stop after this step...")

    #runingOptimizer = True
    #def on_press(key):
    #    if key.char == '~':
    #        runingOptimizer = False

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    problem.info()
    optimizer = optimization.DualAnnealing(problem)
    #while(runingOptimizer):
    optimizer.optimize()

    del system
    del optimizer
    del problem
    print(f"Best Scored sysem value: {opticalGeometry.bestScore}")
    return(opticalGeometry.bestSystem)




    

        
