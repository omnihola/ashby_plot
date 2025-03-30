import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

class BasePanel(ttk.Frame):
    """Base panel class with common functionality"""
    def __init__(self, parent, variables):
        super().__init__(parent)
        self.variables = variables

class FilePanel(BasePanel):
    """Panel for file selection and basic settings"""
    def __init__(self, parent, variables, refresh_callback=None):
        super().__init__(parent, variables)
        self.refresh_callback = refresh_callback
        self.create_widgets()
        
    def create_widgets(self):
        # File selection
        ttk.Label(self, text="Material Properties File:").pack(anchor=tk.W, padx=5, pady=5)
        file_frame = ttk.Frame(self)
        file_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Entry(file_frame, textvariable=self.variables['file_path']).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.RIGHT)
        
        # Data type selection
        ttk.Label(self, text="Data Type:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Radiobutton(self, text="Ranges", variable=self.variables['data_type'], 
                       value="ranges").pack(anchor=tk.W, padx=25)
        ttk.Radiobutton(self, text="Values", variable=self.variables['data_type'], 
                       value="values").pack(anchor=tk.W, padx=25)
        
        # Figure type selection
        ttk.Label(self, text="Figure Type:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Radiobutton(self, text="Presentation", variable=self.variables['figure_type'], 
                       value="presentation").pack(anchor=tk.W, padx=25)
        ttk.Radiobutton(self, text="Publication", variable=self.variables['figure_type'], 
                       value="publication").pack(anchor=tk.W, padx=25)
        
        # Log-log plot option
        ttk.Checkbutton(self, text="Log-Log Plot", variable=self.variables['log_flag']).pack(anchor=tk.W, padx=5, pady=5)
    
    def browse_file(self):
        """Browse for material properties file"""
        filename = filedialog.askopenfilename(
            title="Select Material Properties File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.variables['file_path'].set(filename)
            self.load_file_columns()
    
    def load_file_columns(self):
        """Load column names from the selected Excel file for the axis combo boxes"""
        try:
            data = pd.read_excel(self.variables['file_path'].get())
            columns = data.columns.tolist()
            
            # Remove 'Category' from the list if it exists
            if 'Category' in columns:
                columns.remove('Category')
            
            # Create filtered lists for property columns
            property_columns = []
            for col in columns:
                # Remove ' low' and ' high' suffixes for property names
                if ' low' in col:
                    base_prop = col.replace(' low', '')
                    if base_prop not in property_columns:
                        property_columns.append(base_prop)
                elif ' high' in col:
                    base_prop = col.replace(' high', '')
                    if base_prop not in property_columns:
                        property_columns.append(base_prop)
                else:
                    if col not in property_columns:
                        property_columns.append(col)
            
            # Update the standard properties list
            if property_columns:
                self.variables['standard_properties'] = property_columns
                
                # If the refresh callback exists, call it to update the UI
                if self.refresh_callback:
                    self.refresh_callback()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")


class AxisPanel(BasePanel):
    """Panel for axis settings"""
    def __init__(self, parent, variables):
        super().__init__(parent, variables)
        self.create_widgets()
        
    def create_widgets(self):
        # X-Axis settings
        ttk.Label(self, text="X-Axis Quantity:").pack(anchor=tk.W, padx=5, pady=5)
        x_axis_frame = ttk.Frame(self)
        x_axis_frame.pack(fill=tk.X, padx=5, pady=2)
        self.x_axis_combo = ttk.Combobox(x_axis_frame, textvariable=self.variables['x_axis_quantity'])
        self.x_axis_combo['values'] = self.variables['standard_properties']
        self.x_axis_combo.pack(fill=tk.X)
        
        # Set default value if not already set
        if not self.variables['x_axis_quantity'].get() and self.variables['standard_properties']:
            self.variables['x_axis_quantity'].set(self.variables['standard_properties'][0])
        
        # Y-Axis settings
        ttk.Label(self, text="Y-Axis Quantity:").pack(anchor=tk.W, padx=5, pady=5)
        y_axis_frame = ttk.Frame(self)
        y_axis_frame.pack(fill=tk.X, padx=5, pady=2)
        self.y_axis_combo = ttk.Combobox(y_axis_frame, textvariable=self.variables['y_axis_quantity'])
        self.y_axis_combo['values'] = self.variables['standard_properties']
        self.y_axis_combo.pack(fill=tk.X)
        
        # Set default value if not already set
        if not self.variables['y_axis_quantity'].get() and len(self.variables['standard_properties']) > 1:
            self.variables['y_axis_quantity'].set(self.variables['standard_properties'][1])
        elif not self.variables['y_axis_quantity'].get() and self.variables['standard_properties']:
            self.variables['y_axis_quantity'].set(self.variables['standard_properties'][0])
        
        # X-Axis limits
        ttk.Label(self, text="X-Axis Limits:").pack(anchor=tk.W, padx=5, pady=5)
        x_limit_frame = ttk.Frame(self)
        x_limit_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(x_limit_frame, text="Min:").pack(side=tk.LEFT)
        ttk.Entry(x_limit_frame, textvariable=self.variables['x_min'], width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(x_limit_frame, text="Max:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(x_limit_frame, textvariable=self.variables['x_max'], width=10).pack(side=tk.LEFT)
        
        # Y-Axis limits
        ttk.Label(self, text="Y-Axis Limits:").pack(anchor=tk.W, padx=5, pady=5)
        y_limit_frame = ttk.Frame(self)
        y_limit_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(y_limit_frame, text="Min:").pack(side=tk.LEFT)
        ttk.Entry(y_limit_frame, textvariable=self.variables['y_min'], width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(y_limit_frame, text="Max:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(y_limit_frame, textvariable=self.variables['y_max'], width=10).pack(side=tk.LEFT)


class GuidelinePanel(BasePanel):
    """Panel for guideline settings"""
    def __init__(self, parent, variables):
        super().__init__(parent, variables)
        self.create_widgets()
        
    def create_widgets(self):
        # Enable/disable guideline
        ttk.Checkbutton(self, text="Show Guideline", 
                       variable=self.variables['guideline_flag']).pack(anchor=tk.W, padx=5, pady=5)
        
        # Guideline settings
        guideline_frame = ttk.LabelFrame(self, text="Guideline Settings")
        guideline_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Power
        ttk.Label(guideline_frame, text="Power:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(guideline_frame, textvariable=self.variables['guideline_power'], 
                 width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # X Limits
        ttk.Label(guideline_frame, text="X Limits:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        x_limit_guideline_frame = ttk.Frame(guideline_frame)
        x_limit_guideline_frame.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(x_limit_guideline_frame, text="Min:").pack(side=tk.LEFT)
        ttk.Entry(x_limit_guideline_frame, textvariable=self.variables['guideline_x_min'], 
                 width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(x_limit_guideline_frame, text="Max:").pack(side=tk.LEFT)
        ttk.Entry(x_limit_guideline_frame, textvariable=self.variables['guideline_x_max'], 
                 width=10).pack(side=tk.LEFT)
        
        # String
        ttk.Label(guideline_frame, text="String:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(guideline_frame, textvariable=self.variables['guideline_string']).grid(
            row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Y-Intercept
        ttk.Label(guideline_frame, text="Y-Intercept:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(guideline_frame, textvariable=self.variables['guideline_y_intercept'], 
                 width=10).grid(row=3, column=1, padx=5, pady=5)
        
        # String Position
        ttk.Label(guideline_frame, text="String Position:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        string_pos_frame = ttk.Frame(guideline_frame)
        string_pos_frame.grid(row=4, column=1, padx=5, pady=5)
        ttk.Label(string_pos_frame, text="X:").pack(side=tk.LEFT)
        ttk.Entry(string_pos_frame, textvariable=self.variables['guideline_string_pos_x'], 
                 width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(string_pos_frame, text="Y:").pack(side=tk.LEFT)
        ttk.Entry(string_pos_frame, textvariable=self.variables['guideline_string_pos_y'], 
                 width=10).pack(side=tk.LEFT)


class MaterialsPanel(BasePanel):
    """Panel for individual materials settings"""
    def __init__(self, parent, variables):
        super().__init__(parent, variables)
        self.create_widgets()
        
    def create_widgets(self):
        # Enable/disable individual materials
        ttk.Checkbutton(self, text="Show Individual Materials", 
                       variable=self.variables['individual_material_flag']).pack(anchor=tk.W, padx=5, pady=5)
        
        # Material settings
        materials_frame = ttk.LabelFrame(self, text="Individual Materials")
        materials_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(materials_frame, text="Individual materials can be defined in the code.").pack(padx=5, pady=5)
        ttk.Label(materials_frame, text="Examples:").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(materials_frame, text="• Foam (E=0.124E-3 GPa, ν=0.45, ρ=400 kg/m³)").pack(anchor=tk.W, padx=15, pady=2)
        ttk.Label(materials_frame, text="• PLA (E=2.009 GPa, ν=0.3, ρ=1300 kg/m³)").pack(anchor=tk.W, padx=15, pady=2)


class UnitCellPanel(BasePanel):
    """Panel for unit cell settings"""
    def __init__(self, parent, variables):
        super().__init__(parent, variables)
        self.create_widgets()
        
    def create_widgets(self):
        # Enable/disable unit cell
        ttk.Checkbutton(self, text="Show Unit Cell Data", 
                       variable=self.variables['unit_cell_flag']).pack(anchor=tk.W, padx=5, pady=5)
        
        # Unit cell settings
        unit_cell_frame = ttk.LabelFrame(self, text="Unit Cell Settings")
        unit_cell_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Infill Material selection
        ttk.Label(unit_cell_frame, text="Infill Material:").pack(anchor=tk.W, padx=5, pady=5)
        material_combo = ttk.Combobox(unit_cell_frame, textvariable=self.variables['unit_cell_material'], 
                                     values=["foamed elastomer", "dense elastomer", "none"])
        material_combo.pack(fill=tk.X, padx=5, pady=2)
        
        # File path information
        ttk.Label(unit_cell_frame, text="Note: Unit cell data must be in folders:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Chiral_All_inputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Chiral_All_outputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Lattice_All_inputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Lattice_All_outputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Re-entrant_All_inputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Re-entrant_All_outputs.csv").pack(anchor=tk.W, padx=25, pady=2) 