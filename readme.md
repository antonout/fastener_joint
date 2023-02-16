# Fastener Joint
Bolted/riveted joints are commonly used in a wide spectrum of engineering disciplines. Designing of joints require the justification of both fastener sizing and its amount, thus require a corresponding methodologies to address such needs.

Current tool is based on the method presented in *Ref. 1* and is used to estimate the shear loading distribution among fasteners in a joint due to applied eccentric loading. Please refer to **Background** section for theoretical substantiation, assumptions and examples.

### Usage
Tool expects two *.csv* files - the one containing the fastener details and another one containing loading. The following file structures should be implemented for tool to work correctly.

**NOTE:** tool is using `pandas` for processing *.csv* data, thus ensure the correct data structure by including the headers depicted for each case below. 

**Joint *.csv*:**

| fastener_id | fastener_x_loc | fastener_y_loc | fastener_dia |
| ------------ | ------------ | ------------ | ------------ |
| *name* | *int, float* | *int, float* | *int, float* |

**Loads *.csv*:**

| load_id | load_x_loc | load_y_loc | load_px | load_py | load_mz |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
| *name* | *int, float* | *int, float* | *int, float* | *int, float* | *int, float* |

Tool is designed to process any number of rows in each of the data sets, so cases like* 60 fasteners subjected to 10 different eccentric load sources* seem practically feasible to be computed.

As an outcome, the tool produces the output *.csv* file for further use. The structure of the output file looks looks like the one below.

**Fastener loads *.csv*:**

| fastener_id | fastener_px | fastener_py | fastener_pm | fastener_pm_x | fastener_pm_y | fastener_p_horizontal | fastener_p_vertical | fastener_resultant_load |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
| *name* | *float* | *float* | *float* | *float* | *float* | *float* | *float* | *float* |

Resultant fastener loads should be considered as applied loads for future analysis purposes. Due to complexity, the calculation of safety margins does not fall under the scope of this tool, leaving that task to the stress analyst.

However, as a general advice, analysts should consider the variety of possible failures, e.g. fastener shear failure, sheet bearing or shear-out failures. Allowables should be taken from the test data of a corresponding fastener/sheet pair. 

Some fastener strength estimates might use material shear strength to determine the allowable shear force in a fastener, possibly some precautions of applying a certain fitting factor can be made.

### Installation
Clone the repository: `git clone https://github.com/antonout/fastener_joint.git`
**NOTE: ** As of  2/16/23 the tool is under active development.

# Background
According to *Ref. 2* all fastener clusters, which are carrying the moment load as well as shear force in members should be investigated for combined loads.

Engineering practice suggests spliting the shear force loading evenly among the fasteners and the moment proportionally to the distance from each individual fastener to the joint centroid. 

This is true in cases of same size fasteners, indeed. However it becomes tricky, when different size fasteners are used.

The underlying methodology provides the means to calculate the fastener loading, however as suggested in *Ref. 2*, current method is subjected to the following assumptions.

##### Assumptions
- Fastener materials are the same;
- Fastener bearing on the same material and thickness;
- Fastener shear load assumes straight line distribution.

**NOTE: ** the underlying approaches in both *Ref. 1* and *Ref. 2* are quite similar. The use of *Ref. 1* as a main reference source is primarily dictated by a slightly generalized approach.

### Analysis

The following section represents the steps implemented in the tool. Please note, that we assume, that all data requirements are met. 

**1. Find the location of centroid of resistance.**

For convenience, centroid of resistance can be treated as a CG of a joint. The location of centroid depends on the fastener locations as well as their cross-section area. 

So the coordinates of the centroid are calculated as:

`X = sum (x_i * A_i) / sum (A_i)`
`Y = sum (y_i * A_i) / sum (A_i)`

*x_i, y_i* - x and y coordinates of individual fastener;
*A_i* - cross section area of invidual fastener;

**NOTE:** cross-section area is a circle (unless you are not analyzing custom ring shape bolts with different inner diameters), thus the main driving factor for centroid estimation will be fastener diameter.

However the diameters (and areas as their "derivatives") are not that crucial for the analysis compared to their ratio.

Meaning, that the approach is fine to be fed with proportional values, rather than the specific diameter values. 

So if we have two bolts with 0.25 in and 0.50 in diameters, it is not the diameter what meters, but rather its ratio. So the methodology would work as fine if you provide 1 instead of 0.25 and 2 instead of 0.50.

Tool is fine with any decision, however I suggest to keep the consistency and provide specific diameter values if possible to avoid miscalculations.

**2. Calculate the fastener relative to centroid distances.**

These distances to be used to further spread the moment among the fasteners. For this purpose we need to acquire 3 distance values: in x, y directions and straight line distance, which happens to be a magnitude of previous two.

`rx_i = X - x_i`
`ry_i = Y - y_i`
`r_i = sqrt( rx_i ^ 2 + ry_i ^ 2)`

**NOTE:** Even though for usual engineering practices the value of relative distances is absolute, current tool utilizes exactly these formulas to ensure the right sign convention for the loading.

**3. Calculate the load relative to centroid distances.**

This is done to estimate the distance in order to correctly translate the in-plane moment to the center of resistance. Same calculation logic as above is applied here as well.

`lrx_i = X - lx_i`
`lry_i = Y - ly_i`

*lx_i, ly_i* - x, y location of each applied load (l stands for load)

**4. Translate applied forces to centroid.**

That is pretty straight forward. Couple of things to remember. 

All forces and moments can be translated to any given spot on a plane keeping its magnitude and direction. **Do not forget,** that additionally to that all forces produce an "extra" moment.

The tool utilizes the right hand **sign convention**, which sums up as:

- Positive Fx direction - to the right,
- Positive Fy direction - upward,
- Positive Mz direction - counter clock-wise.

Translated loads are calculated as follows:

`Px_c_i = Px_i`
`Py_c_i = Py_i`
`Mz_c_i = Mz_i + Px_i * lry_i + (-1) * Py_i * lrx_i `

As described in *Step 2* the **-1** multiplier is used to sustain the right sign convention for this tool purposes. Formula could use a minus sign instead, but it would be a bit unclear for unfamiliar eye, **-1** presence ensures that the multiplier is put on purpose and there is no error.

**NOTE:** Also note the *i index* next to the loading. *Index i* stands for a variety of loads, which can be incorporated in the loads *.csv* file. Due we translate all these forces and moments to the center of resistance we end up with summarized loading value.

**5. Estimate the polar moment of inertia of a joint.**

Every stress engineer is familiar with *Mc/I* concept. This is something similar in spirit to what we try to accomplish here. So in order to calculate the amount of force taken by each fastener due to the applied in-plane moment, we need to acquire the polar moment of inertia of a joint. 

It is calculated as a sum of all fastener to centroid distances squared:

`I = sum ( r_i ^ 2 )`

**6. Calculate the fastener load due to applied force.**

It is fair to assume that applied force components will split evenly among the fasteners for ultimate load condition (all gaps are closed), thus the fastener load due to applied force is calculated as follows:

`Px_f_i = Px_c / amount of fasteners` (same for all fasteners)
`Py_f_i = Py_c / amount of fasteners` (same for all fasteners)

These loads act in *x* and *y* direction respectively. 

**7. Calculate the fastener load due to applied moment.**

The force taken by distributing the in-plane moment is acting normal to the fastener to centroid distance. 

`Pm_f_i = Mz_c * r_i / I `

Unless a fastener is not in line with the centroid (one of the coordinates is equal to zero), the force due to moment will produce the projections on both x and y axis.

`Pmx_f_i = Pm_f_i * ry_i / r_i `
`Pmy_f_i = Pm_f_i * rx_i / r_i `

**NOTE:** the division of distances represents the *cos* and *sin* of a corresponding angle.

**8. Calculate the resultant fastener load.**

Now we are ready to sum-up all the components and get the resultant fastener shear load.

`P_hor_f_i = Px_f_i + Pmx_f_i `
`P_ver_f_i = Py_f_i + Pmy_f_i `
`R_f_i = sqrt( P_hor_f_i ^ 2 + P_ver_f_i ^ 2 ) `

### References
1. Bruhn, E.F. (1973) *Analysis and Design of Flight Vehicle Structures.* Indianapolis: S.R. Jacobs & Associates, Inc.
2. Niu, Michael C.Y. (1999) *Airframe Stress Analysis and Sizing. Second Edition.* Hong Kong: Conmilit Press Ltd.
