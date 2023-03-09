from abc import ABC, abstractmethod
import tkinter as tk
import customtkinter as ctk
import pandas as pd
import numpy as np

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class Interface(ctk.CTk, ABC):
    def __init__(self):
        super().__init__()
        self.joint_file_path = tk.StringVar(value="")
        self.loads_file_path = tk.StringVar(value="")
        self.error_message = tk.StringVar(value="")
        self.build_main_window()

    def build_main_window(self):
        # configure window
        self.title("Fastener Joint")
        self.geometry("600x165")
        self.resizable(width=False, height=False)

        self.grid_columnconfigure((0, 3), weight=0)
        self.grid_rowconfigure(0, weight=0)

        # configure labels and texboxes
        self.joint_label = ctk.CTkLabel(master=self, text="Joint")
        self.joint_label.grid(row=0, column=0, padx=10, pady=5)
        self.joint_entry = ctk.CTkEntry(
            master=self,
            width=380,
            height=28,
            border_width=2,
            state="disabled",
            textvariable=self.joint_file_path,
        )
        self.joint_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        self.loads_label = ctk.CTkLabel(master=self, text="Loads")
        self.loads_label.grid(row=1, column=0, padx=10)
        self.loads_entry = ctk.CTkEntry(
            master=self,
            width=380,
            height=28,
            border_width=2,
            state="disabled",
            textvariable=self.loads_file_path,
        )
        self.loads_entry.grid(row=1, column=1, columnspan=2, padx=5)

        # configure buttons and events
        # lambda avoids commands during init
        self.joint_browse_button = ctk.CTkButton(
            master=self,
            height=32,
            text="Browse",
            command=lambda: self.browse_file(b_id=1),
        )
        self.joint_browse_button.grid(row=0, column=3, padx=5, pady=5)

        self.loads_browse_button = ctk.CTkButton(
            master=self,
            height=32,
            text="Browse",
            command=lambda: self.browse_file(b_id=2),
        )
        self.loads_browse_button.grid(row=1, column=3, padx=5, pady=5)

        self.read_check_button = ctk.CTkButton(
            master=self,
            height=32,
            text="Read/Check",
            command=lambda: self.read_check_input_data(),
        )
        self.read_check_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="e")

        self.calculate_button = ctk.CTkButton(
            master=self,
            height=32,
            text="Calculate",
            command=lambda: self.fastener_loads_data_operations(),
        )
        self.calculate_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="w")

        # configure error message window
        self.error_textbox = ctk.CTkEntry(
            master=self,
            width=590,
            height=28,
            state="disabled",
            textvariable=self.error_message,
        )
        self.error_textbox.grid(
            row=4, column=0, columnspan=4, padx=5, pady=5, sticky="s"
        )

    def browse_file(self, b_id):
        # browse joint and load file
        try:
            file_path = tk.filedialog.askopenfilename(
                title="Select a CSV file",
                filetypes=(("CSV files", "*.csv"),),
                defaultextension=".csv",
            )
            if b_id == 1:
                self.joint_entry.configure(state="normal")
                self.joint_entry.delete(0, "end")
                self.joint_entry.insert(0, file_path)
                self.joint_entry.configure(state="disabled")
            elif b_id == 2:
                self.loads_entry.configure(state="normal")
                self.loads_entry.delete(0, "end")
                self.loads_entry.insert(0, file_path)
                self.loads_entry.configure(state="disabled")

        except ValueError:
            self.error_message_gen("Error: Selected file is not a .csv file.")

    def _read_joint_csv(self, *args):
        # get the joint data
        # note: function should be called only through input_data()
        try:
            return pd.read_csv(self.joint_file_path.get())
        except pd.errors.ParserError:
            self.error_message_gen(
                "Error: Cannot parse joint file. Select a .csv file."
            )
            return None
        except FileNotFoundError:
            self.error_message_gen("Error: Joint file not found.")
            return None

    def _read_loads_csv(self, *args):
        # get the loads data
        # note: function should be called only through read_check_input_data()
        try:
            return pd.read_csv(self.loads_file_path.get())
        except pd.errors.ParserError:
            self.error_message_gen(
                "Error: Cannot parse loads file. Select a .csv file."
            )
            return None
        except FileNotFoundError:
            self.error_message_gen("Error: Loads file not found.")
            return None

    def read_check_input_data(self, *args):
        # find index and row location of NaN values
        # create a dict with input data and a separate dict with error flags
        input_data = {
            "joint": self._read_joint_csv(),
            "loads": self._read_loads_csv(),
        }

        # error flags defensively set to True and changed to False after checks are passed
        check_errors = {
            "joint_error": True,
            "loads_error": True,
        }

        # check joint data
        try:
            if input_data["joint"] is not None:
                # check header
                joint_header = pd.Index(
                    ["fastener_id", "fastener_x_loc", "fastener_y_loc", "fastener_dia"]
                )
                if input_data["joint"].columns.equals(joint_header) == False:
                    # warning is not critical for execution, however does not remove error flag
                    self.error_message_gen(
                        "Warning: Joint file header is not compliant."
                    )

                # check contents
                # note: .isna() returns the masked df with bools, .any() returns Series of .isna() df
                # second .any() returns the single bool value of Series
                if input_data["joint"].isna().any().any():
                    rows, cols = np.where(input_data["joint"].isna())
                    for row, col in zip(rows, cols):
                        print(
                            f"NaN: row {input_data['joint'].index[row]+2}, column {input_data['joint'].columns[col]}"
                        )
                    raise ValueError
                else:
                    # change flag to False
                    check_errors["joint_error"] = False
            else:
                raise FileNotFoundError

        except ValueError:
            self.error_message_gen("Error: Missed data in joint file.")

        except FileNotFoundError:
            self.error_message_gen("Error: Joint file not found.")

        # check loads data
        try:
            if input_data["loads"] is not None:
                # check header
                loads_header = pd.Index(
                    [
                        "load_id",
                        "load_x_loc",
                        "load_y_loc",
                        "load_px",
                        "load_py",
                        "load_mz",
                    ]
                )
                if input_data["loads"].columns.equals(loads_header) == False:
                    # warning is not critical for execution, but does not remove an error flag
                    self.error_message_gen(
                        "Warning: Loads file header is not compliant."
                    )

                # check contents
                # same approach used in prev check
                if input_data["loads"].isna().any().any():
                    rows, cols = np.where(input_data["loads"].isna())
                    for row, col in zip(rows, cols):
                        print(
                            f"NaN: row {input_data['loads'].index[row]+2}, column {input_data['loads'].columns[col]}"
                        )
                    raise ValueError
                else:
                    # change flag to False
                    check_errors["loads_error"] = False
            else:
                raise FileNotFoundError

        except ValueError:
            self.error_message_gen("Error: Missed data in loads file.")

        except FileNotFoundError:
            self.error_message_gen("Error: Loads file not found.")

        return (input_data, check_errors)

    def error_message_gen(self, error_msg):
        # update the error field with the error messages
        self.error_textbox.configure(state="normal")
        self.error_textbox.delete(0, "end")
        self.error_textbox.insert(0, error_msg)
        self.error_textbox.configure(state="disabled")

    """abc methods implement operations with dataframes in main"""

    @abstractmethod
    def joint_data_operations(self):
        pass

    @abstractmethod
    def loads_data_operations(self):
        pass

    @abstractmethod
    def fastener_loads_data_operations(self):
        pass


def main():
    class Fastener(Interface):
        def __init__(self):
            super().__init__()

        def joint_data_operations(self):
            return super().joint_data_operations()

        def loads_data_operations(self):
            return super().loads_data_operations()

        def fastener_loads_data_operations(self):
            return super().fastener_loads_data_operations()

    app = Fastener()
    app.mainloop()


if __name__ == "__main__":
    main()
