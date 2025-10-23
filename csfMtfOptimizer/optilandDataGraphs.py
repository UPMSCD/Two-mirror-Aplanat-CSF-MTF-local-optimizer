import matplotlib.pyplot as plt


import optiland.backend as be
from optiland import optic
import matplotlib
matplotlib.use('TkAgg')


import matplotlib.pyplot as plt

from optiland.analysis import RayFan

from optiland.analysis import RmsSpotSizeVsField

from optiland.analysis import SpotDiagram

from optiland.analysis import FieldCurvature

from optiland.mtf import FFTMTF

from optiland.mtf import HuygensMTF

import createEye

import createEyepiece

import csfCalculations

import gc

import imageSimulation

from optiland.fileio import optiland_handler

class analysisGraphs:
    def __init__(self):
        self.graphsBroken = True

    def createGraphs(self):
        plt.close('all')
        # Create 2x3 grid layout (5 plots + 1 blank or used for legend/title)
        self.fig, self.axes = plt.subplots(2, 3, figsize=(14, 8))
        self.fig.tight_layout()
        self.ax_spot_vs_field = self.axes[0, 0]
        self.ax_ray_fan = self.axes[0, 1]
        self.ax_field_curvature = self.axes[0, 2]
        self.ax_mtf = self.axes[1, 0]
        self.ax_optic = self.axes[1, 1]
        self.ax_csf = self.fig.add_subplot(self.axes[1, 2])
        self.ax_csf.axis("off")
        self.axes[1, 2].axis("off")  # Leave one blank or use for legends/titles


    def update(self, opticalGeometry):
        #system setup and drawing
        system = optic.Optic()


        #overrides from zemax geometry
        #opticalGeometry.r1 = -7.557489022866126E+001
        #opticalGeometry.r2 = 2.180184678127181E+001
       # opticalGeometry.l = -5.004634861909000E+001
       # opticalGeometry.bfl = 98.40598
       # opticalGeometry.k1 = -9.874041998926979E-001
       # opticalGeometry.k2 = -6.332479154203354E-001

        system.add_surface(index=0, thickness=be.inf)#object
        system.add_surface(index=1, radius=opticalGeometry.r1, thickness=opticalGeometry.l, is_stop=True, material="mirror", conic=opticalGeometry.k1, aperture=opticalGeometry.ca)
        system.add_surface(index=2, radius=opticalGeometry.r2, thickness=opticalGeometry.bfl, material='mirror', conic=opticalGeometry.k2)
        system.add_surface(index=3)



        #entrance pupil
        system.set_aperture(aperture_type="EPD", value=opticalGeometry.ca)

        #field
        system.set_field_type(field_type="angle")
        system.add_field(y=0)
        system.add_field(y=0.5)
        system.add_field(y=0.9)




        #wavelngth
        system.add_wavelength(value=0.587, is_primary=True)
        opticalGeometry.wavelength = float(system.wavelengths.wavelengths[0]._value) / 1000 #milimeters


        system.image_solve() #moves image surface to paraxial focus
        #system.update_paraxial()



        #insert eyepiece
        system = createEyepiece.rke(system, opticalGeometry)



        eyeModelGeometry = createEye.createGeometry()
        opticalEyeModel = createEye.createEyeModel(eyeModelGeometry, opticalGeometry) 
        print(str(opticalGeometry.eyeMilimetersPerDeg))
        print("mm per deg")

        system = createEye.insert(system, opticalEyeModel)# use visisipy to insert eyehole

        for x in range(5): #optimize 5 times
            system = createEyepiece.optimizeAfterEye_wfeFieldSystem(system, 2, 8) #move eye and eyepiece for best focus

        system.info()

        
        #csf mtf optmization remove comment to run CSF optimizer
        #system = csfCalculations.csfOptimizer_problem(system, opticalGeometry, opticalEyeModel, eyeModelGeometry)  
        system.info()




        ###### plotting after optimization
        self.createGraphs()
        plt.close(3)
        plt.close(4)
        for ax in self.axes.flatten():
            ax.clear()

        gc.collect()
        plt.pause(0.3)#clears stale windows?
        self.fig.canvas.draw_idle()
        plt.pause(0.3)#clears stale windows?


        #CSF mtf graphing
        csfGrapher = csfCalculations.csfGrapher(system, opticalGeometry, opticalEyeModel, eyeModelGeometry)
        csfCalculations.csfGrapher.get_csf_mtf_result(csfGrapher)

        fft_mtf = csfGrapher.fft_mtf
        csf_mtf = csfGrapher.csf_mtf



        


        #spot vs field
        rms_vs_field = RmsSpotSizeVsField(system)


        #spot diagram
        spot_diagram = SpotDiagram(system)
        spot_diagram.view()


        #ray fan aberrations
        ray_fan = RayFan(system)


        #field curvature
        field_curvature = FieldCurvature(system)


        
        
        # === 1. RMS Spot Size vs Field ===
        rms_vs_field = RmsSpotSizeVsField(system)
        y_field = be.to_numpy(rms_vs_field._field[:, 1])
        spot_data = be.to_numpy(rms_vs_field._spot_size)

        for i, wavelength in enumerate(rms_vs_field.wavelengths):
            self.ax_spot_vs_field.plot(
                y_field,
                spot_data[:, i],
                label=f"{wavelength:.4f} µm"
            )
        self.ax_spot_vs_field.set_title("RMS Spot Size vs Field")
        self.ax_spot_vs_field.set_xlabel("Field (normalized Y)")
        self.ax_spot_vs_field.set_ylabel("RMS Spot Size (mm)")
        self.ax_spot_vs_field.grid(True)
        self.ax_spot_vs_field.legend()



        # === 2. Ray Fan ===

        # Px and Py are the pupil coordinates
        Px = be.to_numpy(ray_fan.data["Px"])
        Py = be.to_numpy(ray_fan.data["Py"])

        # We'll plot only the primary field (or you can loop over more)
        for field in ray_fan.fields:
            for wavelength in ray_fan.wavelengths:
                ex = ray_fan.data[f"{field}"][f"{wavelength}"]["x"]
                ey = ray_fan.data[f"{field}"][f"{wavelength}"]["y"]
                i_x = ray_fan.data[f"{field}"][f"{wavelength}"]["intensity_x"]
                i_y = ray_fan.data[f"{field}"][f"{wavelength}"]["intensity_y"]

                ex[i_x == 0] = be.nan  # mask out zero intensity
                ey[i_y == 0] = be.nan

                # Plot both directions on the same axes or split to two axes
                self.ax_ray_fan.plot(Px, be.to_numpy(ex), label=f"x λ={wavelength:.3f}µm")
                self.ax_ray_fan.plot(Py, be.to_numpy(ey), label=f"y λ={wavelength:.3f}µm")

        self.ax_ray_fan.set_title("Ray Fan")
        self.ax_ray_fan.set_xlabel("Pupil Coordinate")
        self.ax_ray_fan.set_ylabel("Ray Aberration (mm)")
        self.ax_ray_fan.grid(True)
        self.ax_ray_fan.legend()


        # === 3. Field Curvature ===
        # === 3. Field Curvature ===
        self.ax_field_curvature.clear()

        field_curvature = FieldCurvature(system)
        field = be.linspace(0, system.fields.max_field, field_curvature.num_points)
        field_np = be.to_numpy(field)

        for k, wavelength in enumerate(field_curvature.wavelengths):
            delta_tangential = be.to_numpy(field_curvature.data[k][0])
            delta_sagittal = be.to_numpy(field_curvature.data[k][1])

            self.ax_field_curvature.plot(
                delta_tangential, field_np, label=f"{wavelength:.4f} µm, Tangential", color=f"C{k}"
            )
            self.ax_field_curvature.plot(
                delta_sagittal, field_np, linestyle='--', label=f"{wavelength:.4f} µm, Sagittal", color=f"C{k}"
            )

        self.ax_field_curvature.set_xlabel("Image Plane Delta (mm)")
        self.ax_field_curvature.set_ylabel("Field")
        self.ax_field_curvature.set_ylim([0, system.fields.max_field])
        self.ax_field_curvature.axvline(x=0, color="k", linewidth=0.5)
        self.ax_field_curvature.grid(True)
        self.ax_field_curvature.set_title("Field Curvature")
        self.ax_field_curvature.legend(loc="best")



        # === 4. FFT MTF ===
        # === 4. FFT MTF ===
        self.ax_mtf.clear()

        freq = be.to_numpy(fft_mtf.freq)

        for i, (Hx, Hy) in enumerate(fft_mtf.resolved_fields):
            mtf_tan = be.to_numpy(fft_mtf.mtf[i][0])  # Tangential
            mtf_sag = be.to_numpy(fft_mtf.mtf[i][1])  # Sagittal

            self.ax_mtf.plot(freq, mtf_tan, label=f"Hx: {Hx:.1f}, Hy: {Hy:.1f} Tangential", linestyle="-", color=f"C{i}")
            self.ax_mtf.plot(freq, mtf_sag, label=f"Hx: {Hx:.1f}, Hy: {Hy:.1f} Sagittal", linestyle="--", color=f"C{i}")

        self.ax_mtf.set_title("FFT MTF")
        self.ax_mtf.set_xlabel("Spatial Frequency (cycles/mm)")
        self.ax_mtf.set_ylabel("MTF")
        self.ax_mtf.set_ylim(0, 1.05)
        self.ax_mtf.grid(True)
        self.ax_mtf.legend(fontsize="small", loc="best")



        system.draw(num_rays=10)





        # === 4. CSF MTF ===
        self.ax_csf.clear()

        freq = be.to_numpy(csf_mtf.freq)

        for i, (Hx, Hy) in enumerate(csf_mtf.resolved_fields):
            mtf_tan = be.to_numpy(csf_mtf.mtf[i][0])  # Tangential
            mtf_sag = be.to_numpy(csf_mtf.mtf[i][1])  # Sagittal

            self.ax_csf.plot(freq, mtf_tan, label=f"Hx: {Hx:.1f}, Hy: {Hy:.1f} Tangential", linestyle="-", color=f"C{i}")
            self.ax_csf.plot(freq, mtf_sag, label=f"Hx: {Hx:.1f}, Hy: {Hy:.1f} Sagittal", linestyle="--", color=f"C{i}")

        self.ax_csf.set_title("CSF MTF")
        self.ax_csf.set_xlabel("Spatial Frequency (cycles/deg)")
        self.ax_csf.set_ylabel("MTFxCSF")
        self.ax_csf.set_ylim(0, 1.05)
        self.ax_csf.set_xlim(0, 70) #change to max diff limit cutoff laters
        self.ax_csf.grid(True)
        self.ax_csf.legend(fontsize="small", loc="best")




        
        ####image simulation
        system.fields.fields = [] #clear fields before image sim
        system.set_field_type(field_type="angle")

        #interpolate points between field angles for image sim
        field_angles = opticalGeometry.field_angles
        interp_points_between = 2 ################ change me
        new_angles = []

        for i in range(len(field_angles) - 1):
            start = field_angles[i]
            stop = field_angles[i + 1]
            # +1 to include stop point at the end of interval except last interval
            segment = be.linspace(start, stop, interp_points_between + 1, endpoint=(i == len(field_angles) - 2))
            new_angles.append(segment[:-1])  # exclude last point to avoid duplicates

        new_angles.append(be.array([field_angles[-1]]))  # add the last point

        new_field_angles = be.concatenate(new_angles)

        for y in new_field_angles:
            for x in new_field_angles:
                system.add_field(x=x, y=y) #make field grid

        opticalGeometry.field_angles = []

        # Get unique Y angles only
        opticalGeometry.field_angles = be.unique([f.y for f in system.fields.fields]).tolist()
        
        imageSim = imageSimulation.createImage(system, opticalGeometry)
        image = imageSimulation.createImage.simulate(imageSim)

        img_np = image[0]
        blurred_img = image[1]

        self.ax_optic.clear()
        self.ax_optic.imshow(blurred_img, cmap='gray')



        system.fields.fields = [] #clear fields after image sim
        system.set_field_type(field_type="angle")
        system.add_field(y=0)
        system.add_field(y=0.5)
        system.add_field(y=0.9)
        plt.pause(5)#clears stale windows?



        ########
        plt.show(block=False)



