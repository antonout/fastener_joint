import pandas as pd
from math import pi

print(pd.__version__)

def main():
    def read_joint_csv():
        # get the joint data
        return pd.read_csv("joint_1.csv")

    def read_loads_csv():
        # get the loads data
        return pd.read_csv("loads_1.csv")

    def fastener_loads_to_csv(df):
        # save output data to csv
        return df.to_csv("fastener_loads.csv", index=False)

    def find_joint_centroid(joint_data):
        # find the center of resistance of the joint
        joint_centroid = (
            joint_data["fastener_area_x_loc"].sum() / joint_data["fastener_area"].sum(),
            joint_data["fastener_area_y_loc"].sum() / joint_data["fastener_area"].sum(),
        )
        return joint_centroid

    def sum_loading_at_centroid(loads_data):
        # sum all centroid translated loading components
        sum_loading = (
            loads_data["load_px_c"].sum(),
            loads_data["load_py_c"].sum(),
            loads_data["load_mz_c"].sum(),
        )
        return sum_loading

    # make operations with joint data
    joint_data = read_joint_csv()

    joint_data["fastener_area"] = pi * joint_data["fastener_dia"]

    joint_data["fastener_area_x_loc"] = (
        joint_data["fastener_area"] * joint_data["fastener_x_loc"]
    )

    joint_data["fastener_area_y_loc"] = (
        joint_data["fastener_area"] * joint_data["fastener_y_loc"]
    )

    centroid_x, centroid_y = find_joint_centroid(joint_data)

    joint_data["centroid_x"] = centroid_x
    joint_data["centroid_y"] = centroid_y

    joint_data["fastener_rx"] = joint_data["centroid_x"] - joint_data["fastener_x_loc"]
    joint_data["fastener_ry"] = joint_data["centroid_y"] - joint_data["fastener_y_loc"]
    joint_data["fastener_r"] = (
        (joint_data["fastener_rx"] ** 2) + (joint_data["fastener_ry"] ** 2)
    ) ** 0.5
    joint_data["fastener_r2"] = joint_data["fastener_r"] ** 2

    # make operations with loads data
    loads_data = read_loads_csv()

    loads_data["centroid_x"] = centroid_x
    loads_data["centroid_y"] = centroid_y

    loads_data["loads_rx"] = loads_data["centroid_x"] - loads_data["load_x_loc"]
    loads_data["loads_ry"] = loads_data["centroid_y"] - loads_data["load_y_loc"]

    loads_data["load_px_c"] = loads_data["load_px"]
    loads_data["load_py_c"] = loads_data["load_py"]
    loads_data["load_mz_c"] = (
        loads_data["load_mz"]
        + loads_data["load_px"] * loads_data["loads_ry"]
        + (-1) * loads_data["load_py"] * loads_data["loads_rx"]
    )

    px_c, py_c, mz_c = sum_loading_at_centroid(loads_data)

    # calculate fastener loading
    fastener_loads = {
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
    fastener_loads_df = pd.DataFrame(fastener_loads)

    fastener_loads_df["fastener_id"] = joint_data["fastener_id"]
    fastener_loads_df["fastener_px"] = px_c / len(fastener_loads_df)
    fastener_loads_df["fastener_py"] = py_c / len(fastener_loads_df)

    joint_polar_moi = joint_data["fastener_r2"].sum()

    fastener_loads_df["fastener_pm"] = mz_c * joint_data["fastener_r"] / joint_polar_moi
    fastener_loads_df["fastener_pm_x"] = (
        fastener_loads_df["fastener_pm"]
        * joint_data["fastener_ry"]
        / joint_data["fastener_r"]
    )
    
    fastener_loads_df["fastener_pm_y"] = (
        fastener_loads_df["fastener_pm"]
        * (-1)
        * joint_data["fastener_rx"]
        / joint_data["fastener_r"]
    )

    fastener_loads_df["fastener_p_horizontal"] = (
        fastener_loads_df["fastener_px"] + fastener_loads_df["fastener_pm_x"]
    )

    fastener_loads_df["fastener_p_vertical"] = (
        fastener_loads_df["fastener_py"] + fastener_loads_df["fastener_pm_y"]
    )

    fastener_loads_df["fastener_resultant_load"] = (
        (fastener_loads_df["fastener_p_horizontal"]) ** 2
        + (fastener_loads_df["fastener_p_vertical"]) ** 2
    ) ** 0.5

    #fastener_loads_to_csv(fastener_loads_df)


if __name__ == "__main__":
    main()
