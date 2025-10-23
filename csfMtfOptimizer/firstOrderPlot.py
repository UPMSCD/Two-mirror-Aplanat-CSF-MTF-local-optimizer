import solveAplanat
import matplotlib.pyplot as plt
import quickPlot
from matplotlib.widgets import Slider, Button
import optilandDataGraphs

class TelescopeGUI:

    def __init__(self):

        ############################ initialize plots
        #plt.ion() #interactive plot
        self.fig = plt.figure(figsize=(14, 8)) #main window size
        gs = self.fig.add_gridspec(3, 2, height_ratios=[5, 1, 1], width_ratios=[4, 1])
        self.ax_layout = self.fig.add_subplot(gs[0, 0]) # mirror plot
        self.ax_bars = self.fig.add_subplot(gs[0, 1]) #aberration plot 
        self.ax_text = self.fig.add_subplot(gs[1, :]) #system geometry data text
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.01, hspace=0.01) #make room for sliders
        self.ax_text.axis('off')

        ########################### === SLIDERS ===
        ax_slider_f1 = plt.axes([0.2, 0.07, 0.6, 0.03])
        self.slider_f1 = Slider(ax_slider_f1, 'F1 (Intermediate Focus)', -500, 500, valinit=-50)

        ax_slider_l = plt.axes([0.2, 0.03, 0.6, 0.03])
        self.slider_l = Slider(ax_slider_l, 'L (Secondary Distance)', -500, 500, valinit=-66)

        ########################## === BUTTON ===
        ax_button = plt.axes([0.85, 0.05, 0.1, 0.05])
        self.button = Button(ax_button, 'Graph', color='lightgray', hovercolor='skyblue')

        self.current_optical_system = None

        # connect callbacks to methods (note the 'self.')
        self.button.on_clicked(self.on_button_clicked)
        self.slider_f1.on_changed(self.update)
        self.slider_l.on_changed(self.update)

        # initial plot
        self.update()

        #initialize optiland Graphs
        self.optilandGraphs = optilandDataGraphs.analysisGraphs()

    def run_solves(self, opticalGeometry): #solves geometry
        ### geometric solves
        opticalGeometry.solve_paraxial()
        opticalGeometry.solve_spherical_aberrations()
        opticalGeometry.solve_coma_aberrations()
        opticalGeometry.solve_astigmatism_aberrations()
        opticalGeometry.solve_median_field_curvature_aberrations()
        opticalGeometry.solve_image_height()
        opticalGeometry.solve_accomodation_ratio()

    def update(self, val=None): #updates plot

        # create aplanat object Initialization
        self.current_optical_system = solveAplanat.aplanat(self.slider_l.val, self.slider_f1.val)
        self.current_optical_system.efl = -300
        self.current_optical_system.ca = 50
        self.current_optical_system.field = 0.9 #45 deg eyepiece at 25x m
        self.current_optical_system.eflEye = 12 #eyepiece efl

        # run analysis
        self.run_solves(self.current_optical_system)

        # update plots with latest object
        quickPlot.plotMirrors(self.current_optical_system, self.ax_layout)
        quickPlot.plot_simple_rays(self.current_optical_system, self.ax_layout)
        quickPlot.plot_aberrations_bar(self.current_optical_system, self.ax_bars)
        quickPlot.plot_aberration_text(self.current_optical_system, self.ax_text)

        self.fig.canvas.draw_idle()

    # Placeholder function for the button
    def on_button_clicked(self, event):
        if self.current_optical_system:
            plt.close('all')
            #if not hasattr(self, 'analysis_gui'):
                #self.optilandGraphs = optilandDataGraphs.analysisGraphs()
            print(self.current_optical_system.__dict__)
            self.optilandGraphs.update(self.current_optical_system)

    def show(self):
        plt.show()
