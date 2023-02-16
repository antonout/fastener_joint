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



### References
1. Bruhn, E.F. (1973) *Analysis and Design of Flight Vehicle Structures.* Indianapolis: S.R. Jacobs & Associates, Inc.
2. Niu, Michael C.Y. (1999) *Airframe Stress Analysis and Sizing. Second Edition.* Hong Kong: Conmilit Press Ltd.
