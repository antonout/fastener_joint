#!/usr/bin/env python3

import pandas as pd
from math import pi

from interface import Interface


def main():
    class FastenerJoint(Interface):
        def __init__(self):
            super().__init__()
            self.fastener_loads_data = pd.DataFrame(
                {
                    "fastener_id": [],
                    "fastener_px": [],
                    "fastener_py": [],
                    "fastener_pm": [],
                    "fastener_pm_x": [],
                    "fastener_pm_y": [],
                    "fastener_p_horizontal": [],
                    "fastener_p_vertical": [],
                    "fastener_resultant_load": [],
                }
            )

        def joint_data_operations(self):
            # various operations with joint_data dataframe
            data, error = self.read_check_input_data()

            self.joint_data = data["joint"]
            self.joint_error = error["joint_error"]

            if self.joint_error == False:
                # calculate fastener_area series
                self.joint_data["fastener_area"] = pi * self.joint_data["fastener_dia"]

                # calculate fastener_area_x_loc series
                self.joint_data["fastener_area_x_loc"] = (
                    self.joint_data["fastener_area"] * self.joint_data["fastener_x_loc"]
                )

                # calculate fastener_area_x_loc series
                self.joint_data["fastener_area_y_loc"] = (
                    self.joint_data["fastener_area"] * self.joint_data["fastener_y_loc"]
                )

                # find the coordinates of resistance center of the joint
                self.centroid_x = (
                    self.joint_data["fastener_area_x_loc"].sum()
                    / self.joint_data["fastener_area"].sum()
                )
                self.centroid_y = (
                    self.joint_data["fastener_area_y_loc"].sum()
                    / self.joint_data["fastener_area"].sum()
                )

                # assign each row of joint_data dataframe with centroid values
                self.joint_data["centroid_x"] = self.centroid_x
                self.joint_data["centroid_y"] = self.centroid_y

                # calculate the distance from centroid to fasteners (components and magnitudes)
                self.joint_data["fastener_rx"] = (
                    self.joint_data["centroid_x"] - self.joint_data["fastener_x_loc"]
                )
                self.joint_data["fastener_ry"] = (
                    self.joint_data["centroid_y"] - self.joint_data["fastener_y_loc"]
                )
                self.joint_data["fastener_r"] = (
                    (self.joint_data["fastener_rx"] ** 2)
                    + (self.joint_data["fastener_ry"] ** 2)
                ) ** 0.5

                # calculate distance squares for polar moi
                self.joint_data["fastener_r2"] = self.joint_data["fastener_r"] ** 2

                return self.joint_data

            else:
                return None

        def loads_data_operations(self):
            # various operations with loads_data dataframe
            data, error = self.read_check_input_data()

            self.loads_data = data["loads"]
            self.loads_error = error["loads_error"]

            if self.loads_error == False:
                # assign each row of loads_data dataframe with centroid values
                # note: centroid calculated in joint_data_operations()
                self.loads_data["centroid_x"] = self.centroid_x
                self.loads_data["centroid_y"] = self.centroid_y

                # calculate the distance components from centroid to loads
                self.loads_data["loads_rx"] = (
                    self.loads_data["centroid_x"] - self.loads_data["load_x_loc"]
                )
                self.loads_data["loads_ry"] = (
                    self.loads_data["centroid_y"] - self.loads_data["load_y_loc"]
                )

                # translate loads from application points to centroid
                self.loads_data["load_px_c"] = self.loads_data["load_px"]
                self.loads_data["load_py_c"] = self.loads_data["load_py"]
                self.loads_data["load_mz_c"] = (
                    self.loads_data["load_mz"]
                    + self.loads_data["load_px"] * self.loads_data["loads_ry"]
                    + (-1) * self.loads_data["load_py"] * self.loads_data["loads_rx"]
                )

                # sum all centroid translated loading components
                self.px_c = self.loads_data["load_px_c"].sum()
                self.py_c = self.loads_data["load_py_c"].sum()
                self.mz_c = self.loads_data["load_mz_c"].sum()

                return (self.loads_data, self.px_c, self.py_c, self.mz_c)

            else:
                return None

        def fastener_loads_data_operations(self):
            # calculate fastener loading
            if (
                type(self.joint_data_operations()) == pd.DataFrame
                and type(self.loads_data_operations()) == tuple
            ):
                # fill fastener id series
                self.fastener_loads_data["fastener_id"] = self.joint_data["fastener_id"]

                # calculate fastener loads due applied forces
                self.fastener_loads_data["fastener_px"] = self.px_c / len(
                    self.fastener_loads_data
                )
                self.fastener_loads_data["fastener_py"] = self.py_c / len(
                    self.fastener_loads_data
                )

                # calculate polar moi
                joint_polar_moi = self.joint_data["fastener_r2"].sum()

                # calculate fastener loading due to moment
                self.fastener_loads_data["fastener_pm"] = (
                    self.mz_c * self.joint_data["fastener_r"] / joint_polar_moi
                )

                # calculate horizontal component of load due to moment
                self.fastener_loads_data["fastener_pm_x"] = (
                    self.fastener_loads_data["fastener_pm"]
                    * self.joint_data["fastener_ry"]
                    / self.joint_data["fastener_r"]
                )

                # calculate vertical component of load due to moment
                self.fastener_loads_data["fastener_pm_y"] = (
                    self.fastener_loads_data["fastener_pm"]
                    * (-1)
                    * self.joint_data["fastener_rx"]
                    / self.joint_data["fastener_r"]
                )

                # sum all horizontal components
                self.fastener_loads_data["fastener_p_horizontal"] = (
                    self.fastener_loads_data["fastener_px"]
                    + self.fastener_loads_data["fastener_pm_x"]
                )

                # sum all vertical components
                self.fastener_loads_data["fastener_p_vertical"] = (
                    self.fastener_loads_data["fastener_py"]
                    + self.fastener_loads_data["fastener_pm_y"]
                )

                # calculate the resultant fastener load magnitude
                self.fastener_loads_data["fastener_resultant_load"] = (
                    (self.fastener_loads_data["fastener_p_horizontal"]) ** 2
                    + (self.fastener_loads_data["fastener_p_vertical"]) ** 2
                ) ** 0.5

                self.fastener_loads_data.to_csv("fastener_loads.csv", index=False)

            else:
                self.error_message_gen(
                    "Error: Check input data. Use Read/Check for details."
                )
                return None

    app = FastenerJoint()
    app.mainloop()


if __name__ == "__main__":
    main()
