import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Import functions from utility modules
from src.plot_utilities import (
    create_legend,
    draw_plot,
    plotting_presets,
    draw_guideline,
    common_definitions,
)
from src.plot_convex_hull import draw_hull

class AshbyPlotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ashby Plot Generator")
        self.root.geometry("1200x800")
        
        # Variables
        self.file_path = tk.StringVar()
        self.x_axis_quantity = tk.StringVar()
        self.y_axis_quantity = tk.StringVar()
        self.data_type = tk.StringVar(value="ranges")
        self.figure_type = tk.StringVar(value="presentation")
        self.log_flag = tk.BooleanVar(value=True)
        self.guideline_flag = tk.BooleanVar(value=True)
        self.individual_material_flag = tk.BooleanVar(value=False)
        self.unit_cell_flag = tk.BooleanVar(value=False)
        
        # Unit cell variables
        self.unit_cell_material = tk.StringVar(value="foamed elastomer")
        
        # X and Y limits
        self.x_min = tk.StringVar(value="10")
        self.x_max = tk.StringVar(value="30000")
        self.y_min = tk.StringVar(value="1E-4")
        self.y_max = tk.StringVar(value="1E3")
        
        # Guideline variables
        self.guideline_power = tk.StringVar(value="2")
        self.guideline_x_min = tk.StringVar(value="1E1")
        self.guideline_x_max = tk.StringVar(value="1E5")
        self.guideline_string = tk.StringVar(value=r"$\frac{E^{1/2}}{\rho} \equiv k$")
        self.guideline_y_intercept = tk.StringVar(value="1E-4")
        self.guideline_string_pos_x = tk.StringVar(value="65")
        self.guideline_string_pos_y = tk.StringVar(value="3")
        
        # Material property lists
        self.standard_properties = [
            "Density", "Young Modulus", "Tensile Strength", "Fracture Toughness", 
            "Thermal Conductivity", "Thermal expansion", "Resistivity", 
            "Poisson", "Poisson difference"
        ]
        
        # Create GUI layout
        self.create_gui()
        
        # Initialize plot frame
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        
    def create_gui(self):
        # Main layout - left panel for controls, right panel for plot
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        control_frame = ttk.Frame(main_paned)
        main_paned.add(control_frame, weight=1)
        
        # Right panel - Plot
        self.plot_frame = ttk.Frame(main_paned)
        main_paned.add(self.plot_frame, weight=3)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        file_tab = ttk.Frame(notebook)
        axis_tab = ttk.Frame(notebook)
        guideline_tab = ttk.Frame(notebook)
        materials_tab = ttk.Frame(notebook)
        unit_cell_tab = ttk.Frame(notebook)
        
        notebook.add(file_tab, text="File")
        notebook.add(axis_tab, text="Axis Settings")
        notebook.add(guideline_tab, text="Guidelines")
        notebook.add(materials_tab, text="Materials")
        notebook.add(unit_cell_tab, text="Unit Cells")
        
        # File Tab
        ttk.Label(file_tab, text="Material Properties File:").pack(anchor=tk.W, padx=5, pady=5)
        file_frame = ttk.Frame(file_tab)
        file_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Entry(file_frame, textvariable=self.file_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.RIGHT)
        
        ttk.Label(file_tab, text="Data Type:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Radiobutton(file_tab, text="Ranges", variable=self.data_type, value="ranges").pack(anchor=tk.W, padx=25)
        ttk.Radiobutton(file_tab, text="Values", variable=self.data_type, value="values").pack(anchor=tk.W, padx=25)
        
        ttk.Label(file_tab, text="Figure Type:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Radiobutton(file_tab, text="Presentation", variable=self.figure_type, value="presentation").pack(anchor=tk.W, padx=25)
        ttk.Radiobutton(file_tab, text="Publication", variable=self.figure_type, value="publication").pack(anchor=tk.W, padx=25)
        
        ttk.Checkbutton(file_tab, text="Log-Log Plot", variable=self.log_flag).pack(anchor=tk.W, padx=5, pady=5)
        
        # Axis Settings Tab
        ttk.Label(axis_tab, text="X-Axis Quantity:").pack(anchor=tk.W, padx=5, pady=5)
        x_axis_frame = ttk.Frame(axis_tab)
        x_axis_frame.pack(fill=tk.X, padx=5, pady=2)
        self.x_axis_combo = ttk.Combobox(x_axis_frame, textvariable=self.x_axis_quantity, values=self.standard_properties)
        self.x_axis_combo.pack(fill=tk.X)
        self.x_axis_combo.current(0)  # Set default to first item (Density)
        
        ttk.Label(axis_tab, text="Y-Axis Quantity:").pack(anchor=tk.W, padx=5, pady=5)
        y_axis_frame = ttk.Frame(axis_tab)
        y_axis_frame.pack(fill=tk.X, padx=5, pady=2)
        self.y_axis_combo = ttk.Combobox(y_axis_frame, textvariable=self.y_axis_quantity, values=self.standard_properties)
        self.y_axis_combo.pack(fill=tk.X)
        self.y_axis_combo.current(1)  # Set default to second item (Young Modulus)
        
        # X and Y limits
        ttk.Label(axis_tab, text="X-Axis Limits:").pack(anchor=tk.W, padx=5, pady=5)
        x_limit_frame = ttk.Frame(axis_tab)
        x_limit_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(x_limit_frame, text="Min:").pack(side=tk.LEFT)
        ttk.Entry(x_limit_frame, textvariable=self.x_min, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(x_limit_frame, text="Max:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(x_limit_frame, textvariable=self.x_max, width=10).pack(side=tk.LEFT)
        
        ttk.Label(axis_tab, text="Y-Axis Limits:").pack(anchor=tk.W, padx=5, pady=5)
        y_limit_frame = ttk.Frame(axis_tab)
        y_limit_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(y_limit_frame, text="Min:").pack(side=tk.LEFT)
        ttk.Entry(y_limit_frame, textvariable=self.y_min, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(y_limit_frame, text="Max:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(y_limit_frame, textvariable=self.y_max, width=10).pack(side=tk.LEFT)
        
        # Guideline Tab
        ttk.Checkbutton(guideline_tab, text="Show Guideline", variable=self.guideline_flag).pack(anchor=tk.W, padx=5, pady=5)
        
        guideline_frame = ttk.LabelFrame(guideline_tab, text="Guideline Settings")
        guideline_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(guideline_frame, text="Power:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(guideline_frame, textvariable=self.guideline_power, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(guideline_frame, text="X Limits:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        x_limit_guideline_frame = ttk.Frame(guideline_frame)
        x_limit_guideline_frame.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(x_limit_guideline_frame, text="Min:").pack(side=tk.LEFT)
        ttk.Entry(x_limit_guideline_frame, textvariable=self.guideline_x_min, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(x_limit_guideline_frame, text="Max:").pack(side=tk.LEFT)
        ttk.Entry(x_limit_guideline_frame, textvariable=self.guideline_x_max, width=10).pack(side=tk.LEFT)
        
        ttk.Label(guideline_frame, text="String:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(guideline_frame, textvariable=self.guideline_string).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(guideline_frame, text="Y-Intercept:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(guideline_frame, textvariable=self.guideline_y_intercept, width=10).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(guideline_frame, text="String Position:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        string_pos_frame = ttk.Frame(guideline_frame)
        string_pos_frame.grid(row=4, column=1, padx=5, pady=5)
        ttk.Label(string_pos_frame, text="X:").pack(side=tk.LEFT)
        ttk.Entry(string_pos_frame, textvariable=self.guideline_string_pos_x, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(string_pos_frame, text="Y:").pack(side=tk.LEFT)
        ttk.Entry(string_pos_frame, textvariable=self.guideline_string_pos_y, width=10).pack(side=tk.LEFT)
        
        # Materials Tab - individual materials
        ttk.Checkbutton(materials_tab, text="Show Individual Materials", variable=self.individual_material_flag).pack(anchor=tk.W, padx=5, pady=5)
        
        materials_frame = ttk.LabelFrame(materials_tab, text="Individual Materials")
        materials_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(materials_frame, text="Individual materials can be defined in the code.").pack(padx=5, pady=5)
        ttk.Label(materials_frame, text="Examples: Foam (E=0.124E-3 GPa, ν=0.45, ρ=400 kg/m³)").pack(padx=5, pady=2)
        ttk.Label(materials_frame, text="PLA (E=2.009 GPa, ν=0.3, ρ=1300 kg/m³)").pack(padx=5, pady=2)
        
        # Unit Cell Tab
        ttk.Checkbutton(unit_cell_tab, text="Show Unit Cell Data", variable=self.unit_cell_flag).pack(anchor=tk.W, padx=5, pady=5)
        
        unit_cell_frame = ttk.LabelFrame(unit_cell_tab, text="Unit Cell Settings")
        unit_cell_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(unit_cell_frame, text="Infill Material:").pack(anchor=tk.W, padx=5, pady=5)
        material_combo = ttk.Combobox(unit_cell_frame, textvariable=self.unit_cell_material, 
                                      values=["foamed elastomer", "dense elastomer", "none"])
        material_combo.pack(fill=tk.X, padx=5, pady=2)
        material_combo.current(0)
        
        ttk.Label(unit_cell_frame, text="Note: Unit cell data must be in folders:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Chiral_All_inputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Chiral_All_outputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Lattice_All_inputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Lattice_All_outputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Re-entrant_All_inputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Re-entrant_All_outputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        
        # Bottom buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(button_frame, text="Generate Plot", command=self.generate_plot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Plot", command=self.save_plot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Material Properties File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.load_file_columns()
    
    def load_file_columns(self):
        """Load column names from the selected Excel file for the combo boxes"""
        try:
            data = pd.read_excel(self.file_path.get())
            columns = data.columns.tolist()
            # Remove 'Category' from the list if it exists
            if 'Category' in columns:
                columns.remove('Category')
            
            # Create filtered lists for different column types
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
            
            # Update comboboxes with the filtered lists
            if property_columns:
                self.x_axis_combo['values'] = property_columns
                self.y_axis_combo['values'] = property_columns
                
                # Set default values if not already set
                if not self.x_axis_quantity.get() and 'Density' in property_columns:
                    self.x_axis_quantity.set('Density')
                elif not self.x_axis_quantity.get() and property_columns:
                    self.x_axis_quantity.set(property_columns[0])
                    
                if not self.y_axis_quantity.get() and 'Young Modulus' in property_columns:
                    self.y_axis_quantity.set('Young Modulus')
                elif not self.y_axis_quantity.get() and len(property_columns) > 1:
                    self.y_axis_quantity.set(property_columns[1])
                elif not self.y_axis_quantity.get() and property_columns:
                    self.y_axis_quantity.set(property_columns[0])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def load_unit_cell_data(self):
        """Load unit cell data from CSV files"""
        try:
            # Define file paths
            OV_file_names = ['Chiral_All_outputs.csv', 'Lattice_All_outputs.csv', 'Re-entrant_All_outputs.csv']
            DV_file_names = ['Chiral_All_inputs.csv', 'Lattice_All_inputs.csv', 'Re-entrant_All_inputs.csv']
            
            # Concatenate all data
            counter = 0
            for OV_file_name, DV_file_name in zip(OV_file_names, DV_file_names):
                OV_file = os.path.join(os.getcwd(), 'unit_cell_data', OV_file_name)
                DV_file = os.path.join(os.getcwd(), 'unit_cell_data', DV_file_name)
                
                if not os.path.exists(OV_file) or not os.path.exists(DV_file):
                    messagebox.showerror("Error", f"Unit cell data file not found: {OV_file_name} or {DV_file_name}")
                    return None
                
                if counter == 0:
                    OV_data_frame = pd.read_csv(OV_file)
                    DV_data_frame = pd.read_csv(DV_file)
                else:
                    OV_data_frame = pd.concat([OV_data_frame, pd.read_csv(OV_file)])
                    DV_data_frame = pd.concat([DV_data_frame, pd.read_csv(DV_file)])
                counter += 1
            
            # Merge data
            merged_data = OV_data_frame.merge(DV_data_frame, on=['ID', 'Unit Cell'])
            
            # Apply orthonormal rotation - simplified implementation
            data_to_plot = merged_data.copy()
            data_to_plot = data_to_plot[data_to_plot['Infill material'] == self.unit_cell_material.get()]
            data_to_plot = data_to_plot.reset_index(drop=True)
            
            # Create basic baseline materials
            stiff = {'E': 200, 'nu': 0.3, 'rho': 7800, 'name': 'stiff'}
            compliant_dense = {'E': 0.1, 'nu': 0.48, 'rho': 1000, 'name': 'dense elastomer'}
            compliant_foam = {'E': 0.001, 'nu': 0.3, 'rho': 100, 'name': 'foamed elastomer'}
            null_material = {'E': 0, 'nu': 0, 'rho': 0, 'name': 'none'}
            
            # Set compliant material based on selection
            if self.unit_cell_material.get() == 'foamed elastomer':
                compliant_material = compliant_foam
            elif self.unit_cell_material.get() == 'dense elastomer':
                compliant_material = compliant_dense
            else:  # 'none'
                compliant_material = null_material
            
            # Create density field
            data_to_plot['Density'] = 1E6 * (
                data_to_plot['Stiff volume'] * stiff['rho'] + 
                (data_to_plot['Total volume'] - data_to_plot['Stiff volume']) * compliant_material['rho']
            ) / data_to_plot['Total volume']
            
            # Create Poisson difference field
            data_to_plot['Poisson difference'] = 1 / (1 + data_to_plot['Nu12'])
            
            # Filter out invalid data points
            data_to_plot = data_to_plot[
                (data_to_plot['E1'] > compliant_material['E']) & 
                (data_to_plot['E2'] > compliant_material['E'])
            ]
            
            return data_to_plot
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load unit cell data: {str(e)}")
            return None
    
    def generate_plot(self):
        """Generate the Ashby plot based on user inputs"""
        try:
            # Clear the current plot
            self.ax.clear()
            
            # Validate inputs for standard plot
            if not self.unit_cell_flag.get() and not self.file_path.get():
                messagebox.showwarning("Warning", "Please select a material properties file.")
                return
                
            if not self.x_axis_quantity.get() or not self.y_axis_quantity.get():
                messagebox.showwarning("Warning", "Please select X and Y axis quantities.")
                return
            
            # Get common definitions
            units, material_colors = common_definitions()
            
            # Set up plot formatting
            plotting_presets(self.figure_type.get())
            
            # Set x and y labels
            try:
                x_quantity = self.x_axis_quantity.get()
                y_quantity = self.y_axis_quantity.get()
                
                if x_quantity == 'Poisson difference':
                    x_label = r'Hyperbolic Poisson Ratio $\frac{1}{1+\nu}$, ' + units[x_quantity]
                else:
                    x_label = x_quantity + ', ' + units[x_quantity]
                
                if y_quantity == 'Poisson difference':
                    y_label = r'Hyperbolic Poisson Ratio $\frac{1}{1+\nu}$, ' + units[y_quantity]
                else:
                    y_label = y_quantity + ', ' + units[y_quantity]
                
                self.ax.set_xlabel(x_label)
                self.ax.set_ylabel(y_label)
            except:
                messagebox.showerror("Error", "Could not set correct x- and y-labels. Make sure your axis quantities have units defined.")
                return
            
            # Set axes limits
            try:
                x_lim = [float(self.x_min.get()), float(self.x_max.get())]
                y_lim = [float(self.y_min.get()), float(self.y_max.get())]
                self.ax.set(xlim=x_lim, ylim=y_lim)
            except ValueError:
                messagebox.showerror("Error", "Invalid axis limits. Please enter numeric values.")
                return
            
            # Set log scale if needed
            if self.log_flag.get():
                self.ax.loglog()
            
            # Add grid lines
            self.ax.grid(which='major', axis='both', linestyle='-.', zorder=0.5)
            
            # Draw guideline if enabled
            if self.guideline_flag.get():
                try:
                    guideline = {
                        'power': float(self.guideline_power.get()),
                        'x_lim': [float(self.guideline_x_min.get()), float(self.guideline_x_max.get())],
                        'string': self.guideline_string.get(),
                        'y_intercept': float(self.guideline_y_intercept.get()),
                        'string_position': (float(self.guideline_string_pos_x.get()), float(self.guideline_string_pos_y.get())),
                    }
                    draw_guideline(guideline, ax=self.ax, log_flag=self.log_flag.get())
                except ValueError:
                    messagebox.showerror("Error", "Invalid guideline parameters. Please enter numeric values.")
                    return
            
            # Draw standard material data if file is provided
            if self.file_path.get():
                try:
                    data = pd.read_excel(self.file_path.get())
                    
                    # Handle Poisson difference calculation if needed
                    if (x_quantity == 'Poisson difference') or (y_quantity == 'Poisson difference'):
                        data['Poisson difference high'] = 1/(1+data['Poisson low'])
                        data['Poisson difference low'] = 1/(1+data['Poisson high'])
                    
                    # Draw the plot
                    draw_plot(
                        data,
                        x_quantity,
                        y_quantity,
                        self.ax,
                        material_colors,
                        data_type=self.data_type.get(),
                    )
                    
                    # Create legend
                    create_legend(
                        material_classes=data.groupby('Category').groups.keys(),
                        material_colors=material_colors,
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to plot material data: {str(e)}")
            
            # Plot individual materials if enabled
            if self.individual_material_flag.get():
                marker_size = 500
                
                # Example materials - these could be made configurable in the future
                foam = {
                    'Young Modulus': 0.124E-3,
                    'Poisson': 0.45,
                    'Density': 400,
                    'name': 'Foam',
                    'color': 'b'
                }
                
                pla = {
                    'Young Modulus': 2.009,
                    'Poisson': 0.3,
                    'Density': 1300,
                    'name': 'PLA',
                    'color': 'r'
                }
                
                materials = [foam, pla]
                
                for material in materials:
                    x_value = material[x_quantity] if x_quantity in material else (
                        1/(1+material['Poisson']) if x_quantity == 'Poisson difference' else None
                    )
                    y_value = material[y_quantity] if y_quantity in material else (
                        1/(1+material['Poisson']) if y_quantity == 'Poisson difference' else None
                    )
                    
                    if x_value is not None and y_value is not None:
                        self.ax.scatter(
                            x_value,
                            y_value,
                            c=material['color'],
                            edgecolors='k',
                            marker='*',
                            s=marker_size,
                            label=material['name']
                        )
            
            # Plot unit cell data if enabled
            if self.unit_cell_flag.get():
                unit_cell_data = self.load_unit_cell_data()
                if unit_cell_data is not None and len(unit_cell_data) > 0:
                    # Map property names for unit cell data
                    if x_quantity == 'Young Modulus':
                        x_field = 'E1'
                    elif x_quantity == 'Poisson':
                        x_field = 'Nu12'
                    elif x_quantity == 'Poisson difference':
                        x_field = 'Poisson difference'
                    else:
                        x_field = x_quantity
                        
                    if y_quantity == 'Young Modulus':
                        y_field = 'E1'
                    elif y_quantity == 'Poisson':
                        y_field = 'Nu12'
                    elif y_quantity == 'Poisson difference':
                        y_field = 'Poisson difference'
                    else:
                        y_field = y_quantity
                    
                    if x_field in unit_cell_data.columns and y_field in unit_cell_data.columns:
                        # Create array for hull drawing
                        X = np.zeros(shape=(len(unit_cell_data), 2))
                        X[:, 0] = unit_cell_data[x_field]
                        X[:, 1] = unit_cell_data[y_field]
                        
                        # Draw hull for all unit cell data
                        draw_hull(
                            X,
                            scale=1.1,
                            padding='scale',
                            n_interpolate=1000,
                            interpolation='cubic',
                            ax=self.ax,
                            plot_kwargs={
                                'color': 'b',
                                'alpha': 0.75,
                                'hatch': '+'
                            }
                        )
                        
                        # Optional: Draw hulls for each unit cell type separately
                        unit_cell_colors = {'Chiral': 'r', 'Lattice': 'b', 'Re-entrant': 'g'}
                        for unit_cell_type, group_data in unit_cell_data.groupby('Unit Cell'):
                            if len(group_data) > 2:  # Need at least 3 points for a hull
                                X_group = np.zeros(shape=(len(group_data), 2))
                                X_group[:, 0] = group_data[x_field]
                                X_group[:, 1] = group_data[y_field]
                                
                                # Add a patch for the legend
                                self.ax.scatter(
                                    [],  # Empty data for legend only
                                    [],
                                    c=unit_cell_colors.get(unit_cell_type, 'k'),
                                    label=f"{unit_cell_type} ({self.unit_cell_material.get()})"
                                )
                        
                        # Add legend for unit cells
                        if not self.file_path.get():  # Only if no material data legend
                            plt.legend()
                    else:
                        messagebox.showwarning("Warning", f"Selected properties not available in unit cell data: {x_field} or {y_field}")
            
            # Update the canvas
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot: {str(e)}")
    
    def save_plot(self):
        """Save the current plot to a file"""
        if hasattr(self, 'fig'):
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg"),
                    ("All files", "*.*"),
                ]
            )
            if file_path:
                try:
                    self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                    messagebox.showinfo("Success", f"Plot saved to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save plot: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No plot to save. Generate a plot first.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AshbyPlotGUI(root)
    root.mainloop() 