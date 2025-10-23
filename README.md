# Two-mirror-Aplanat-CSF-MTF-local-optimizer
A optiland based script which solves for any gregorian or cassegrain aplanatic geometry. Using visisipy Navarro eye model then optimizes a CSF weighted MTF merit function to maximize subjective quality factor.  

I'd like to preface this by saying this code is far from production ready and still contains many notes/ bugs but the essential functions have been proven. 

Basic usage:
1) install all dependencies
2) run mainGui.py to start script.
3) As a note the first run may take a while from all the imports
4) The program should pop up with the initial solving screen which can solve for any 2 mirror aplanat gregorian or cassegrain telescope. The EFL and CA are fixed variables for now which can be changed in the solveAplanat class
<img width="289" height="237" alt="image" src="https://github.com/user-attachments/assets/cc9e3b67-7714-4325-a5ce-5d010b5958f3" />
5)The initial window should look like this with sliders to change the primary focal length and mirror separation. The bar graph on the right should show only astigmatism on axis for basic verification that the aplanatic sovle did work. The starting geometry is gregorian but the sliders can change it to cassegrain.
<img width="1582" height="896" alt="image" src="https://github.com/user-attachments/assets/40b47a6a-9ffe-4153-815b-edcf7a6c8a61" />
6) After defining basic first order geometry hit the graph button in the bottom right. Depending on how the scripts are set up in the console the maingui was run in should start showing merit funciton values and opitmization outputs.
7) The way the script is currently set up the optic for the objective is created, a modeled eyepiece is created and the Navarro eye model is inserted before optimization.

<img width="1220" height="512" alt="image" src="https://github.com/user-attachments/assets/0c3d8890-28ba-49a3-af80-fd6efdae9c60" />
8)The main optimization controls are located in the optilandDataGraphs class where different eye models and eyepieces can be inserted here. Their respective settings and additional eyepieces can be added in the imported classes.
9) As the current setup shows the objective is inserted. the eye model is inserted then a few optimizations take place. First the eyepiece and the eye are shifted to find best focus. Next a few iterations of full field wavefront optimization occur to get a basic good design for further optimization. Finally the csf optimization occurs where the minimum tangential or sagittal CSF x MTF is optimized per field resulting in bringing the two mtf results closer together. 
10) If the process hangs in the console press space bar to see if the output is just frozen. In the meantime during optimization the console should be outputting a number which ideally increases. This number is the total area under the CSF x MTF curve which we are trying to maximize. After a good result occurs hit the escape key in the console to stop the optimization. The best result will be reinserted into the system and the results graphed.

Here are some sample results. 
Before optimization aplanatic gregorian.
<img width="1920" height="1033" alt="Aplanat" src="https://github.com/user-attachments/assets/ff7a214b-9fcc-4b70-91dc-fd6100264834" />
Aplanat with WFE optimization before CSF x MTF
<img width="1536" height="762" alt="BeforeCSFOptimization" src="https://github.com/user-attachments/assets/fdce5bc4-814b-4e36-9576-b94236b1e8da" />
And finally aplanat after WFE and CSF x MTF optimization
<img width="1536" height="762" alt="AfterCSFOptimization" src="https://github.com/user-attachments/assets/d80a9c83-17e4-455f-a9f2-eab49dc3266e" />

As you can see from the results and the very basic image simulation the system improved between standard WFE optimization across the field compared to the CSF weighted MTF merit function. None of these simualtions account for accomodation of the eye yet either so there is more room for optimization in the future.

