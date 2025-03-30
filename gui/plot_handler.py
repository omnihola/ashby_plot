import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import filedialog, messagebox
import matplotlib
import tkinter as tk
from tkinter import ttk
import matplotlib.patches as patches

from src.plot_utilities import (
    create_legend,
    draw_plot,
    plotting_presets,
    draw_guideline,
    common_definitions,
    save_high_quality_figure
)
from src.plot_convex_hull import draw_hull
from gui.unit_cell_handler import UnitCellHandler

class CustomNavigationToolbar(NavigationToolbar2Tk):
    """自定义导航工具栏，添加图表位置调整工具"""
    
    def __init__(self, canvas, window, plot_handler):
        self.toolitems = list(NavigationToolbar2Tk.toolitems)
        # 在保存按钮后添加新工具，使用matplotlib内置图标
        save_idx = next(i for i, item in enumerate(self.toolitems) if item[0] == 'Save')
        self.toolitems.insert(save_idx + 1, ('Adjust', '调整图表位置和大小', 'subplots', 'adjust_figure'))
        # 添加图例调整工具，使用已知存在的图标以避免FileNotFoundError
        self.toolitems.insert(save_idx + 2, ('Legend', '调整图例大小和位置', 'hand', 'adjust_legend'))
        
        self.plot_handler = plot_handler
        self.parent_window = window  # 存储父窗口的引用
        super().__init__(canvas, window)
    
    def adjust_figure(self):
        """打开图表位置和大小调整对话框"""
        print("Opening adjust figure dialog")  # 调试信息
        dialog = FigureAdjustDialog(self.canvas.figure, self.parent_window)  # 使用保存的父窗口引用
        # 更新画布
        if dialog.result:
            self.canvas.draw()
    
    def adjust_legend(self):
        """打开图例调整对话框"""
        print("Opening legend adjust dialog")  # 调试信息
        dialog = LegendAdjustDialog(self.canvas.figure, self.plot_handler, self.parent_window)
        # 更新画布
        if dialog.result:
            self.canvas.draw()
            
    # 确保配置工具栏按钮时包含这个方法    
    def _init_toolbar(self):
        super()._init_toolbar()
        # 添加调试信息
        print("Toolbar initialized with custom tools")


class PlotHandler:
    """Handler for plot operations"""
    
    def __init__(self, plot_frame, variables):
        self.plot_frame = plot_frame
        self.variables = variables
        
        # Initialize figure
        self.fig, self.ax = plt.subplots(figsize=(8, 7))
        
        # Make sure the figure has enough DPI for good display
        self.fig.set_dpi(100)
        
        # Create canvas and add it to the plot frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill='both', expand=True)
        
        # Add custom toolbar with figure adjustment tool
        self.toolbar = CustomNavigationToolbar(self.canvas, self.plot_frame, self)
        self.toolbar.update()
    
    def generate_plot(self):
        """Generate the Ashby plot based on user inputs"""
        try:
            # Clear the current plot
            self.ax.clear()
            
            # Validate inputs for standard plot
            if not self.variables['unit_cell_flag'].get() and not self.variables['file_path'].get():
                messagebox.showwarning("Warning", "Please select a material properties file.")
                return
                
            if not self.variables['x_axis_quantity'].get() or not self.variables['y_axis_quantity'].get():
                messagebox.showwarning("Warning", "Please select X and Y axis quantities.")
                return
            
            # Get common definitions
            units, material_colors = common_definitions()
            
            # Set up plot formatting
            plotting_presets(self.variables['figure_type'].get())
            
            # Set x and y labels
            try:
                x_quantity = self.variables['x_axis_quantity'].get()
                y_quantity = self.variables['y_axis_quantity'].get()
                
                if x_quantity == 'Poisson difference':
                    # 使用普通文本代替LaTeX格式
                    x_label = 'Hyperbolic Poisson Ratio 1/(1+v), ' + units[x_quantity]
                else:
                    x_label = x_quantity + ', ' + units[x_quantity]
                
                if y_quantity == 'Poisson difference':
                    # 使用普通文本代替LaTeX格式
                    y_label = 'Hyperbolic Poisson Ratio 1/(1+v), ' + units[y_quantity]
                else:
                    y_label = y_quantity + ', ' + units[y_quantity]
                
                self.ax.set_xlabel(x_label)
                self.ax.set_ylabel(y_label)
            except:
                messagebox.showerror("Error", "Could not set correct x- and y-labels. Make sure your axis quantities have units defined.")
                return
            
            # Set axes limits
            try:
                x_lim = [float(self.variables['x_min'].get()), float(self.variables['x_max'].get())]
                y_lim = [float(self.variables['y_min'].get()), float(self.variables['y_max'].get())]
                self.ax.set(xlim=x_lim, ylim=y_lim)
            except ValueError:
                messagebox.showerror("Error", "Invalid axis limits. Please enter numeric values.")
                return
            
            # Set log scale if needed
            if self.variables['log_flag'].get():
                self.ax.loglog()
            
            # Add grid lines
            self.ax.grid(which='major', axis='both', linestyle='-.', zorder=0.5)
            
            # Draw guideline if enabled
            if self.variables['guideline_flag'].get():
                try:
                    guideline = {
                        'power': float(self.variables['guideline_power'].get()),
                        'x_lim': [float(self.variables['guideline_x_min'].get()), float(self.variables['guideline_x_max'].get())],
                        'string': self.variables['guideline_string'].get(),
                        'y_intercept': float(self.variables['guideline_y_intercept'].get()),
                        'string_position': (float(self.variables['guideline_string_pos_x'].get()), 
                                           float(self.variables['guideline_string_pos_y'].get())),
                    }
                    draw_guideline(guideline, ax=self.ax, log_flag=self.variables['log_flag'].get())
                except ValueError:
                    messagebox.showerror("Error", "Invalid guideline parameters. Please enter numeric values.")
                    return
            
            # Draw standard material data if file is provided
            if self.variables['file_path'].get():
                self._plot_material_data(x_quantity, y_quantity, material_colors)
            
            # Plot individual materials if enabled
            if self.variables['individual_material_flag'].get():
                self._plot_individual_materials(x_quantity, y_quantity)
            
            # Plot unit cell data if enabled
            if self.variables['unit_cell_flag'].get():
                self._plot_unit_cell_data(x_quantity, y_quantity)
            
            # Update the canvas
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot: {str(e)}")
    
    def _plot_material_data(self, x_quantity, y_quantity, material_colors):
        """Plot standard material data from file"""
        try:
            data = pd.read_excel(self.variables['file_path'].get())
            
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
                data_type=self.variables['data_type'].get(),
            )
            
            # 获取图表类型，用于确定字体大小
            figure_type = self.variables['figure_type'].get()
            fontsize = 8 if figure_type == 'publication' else 14
            
            # Create legend with improved settings
            create_legend(
                material_classes=data.groupby('Category').groups.keys(),
                material_colors=material_colors,
                ncol=2,  # 使用2列减少重叠
                fontsize=fontsize,  # 根据图表类型设置字体大小
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot material data: {str(e)}")
    
    def _plot_individual_materials(self, x_quantity, y_quantity):
        """Plot individual materials as stars"""
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
    
    def _plot_unit_cell_data(self, x_quantity, y_quantity):
        """Plot unit cell data"""
        unit_cell_data = UnitCellHandler.load_unit_cell_data(self.variables['unit_cell_material'].get())
        
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
                
                # 为单元格数据准备图例项
                handles = []
                labels = []
                
                # 定义单元格类型的颜色和标签
                unit_cell_colors = {'Chiral': 'r', 'Lattice': 'b', 'Re-entrant': 'g'}
                
                # 添加图例项
                for unit_cell_type, group_data in unit_cell_data.groupby('Unit Cell'):
                    if len(group_data) > 2:  # Need at least 3 points for a hull
                        color = unit_cell_colors.get(unit_cell_type, 'k')
                        label = f"{unit_cell_type} ({self.variables['unit_cell_material'].get()})"
                        
                        # 创建图例项
                        patch = patches.Patch(color=color, alpha=0.75, hatch='+', label=label)
                        handles.append(patch)
                        labels.append(label)
                
                # 添加图例，如果有图例项且没有显示材料数据图例
                if handles and not self.variables['file_path'].get():
                    # 获取图表类型，用于确定字体大小
                    figure_type = self.variables['figure_type'].get()
                    fontsize = 8 if figure_type == 'publication' else 14
                    
                    # 创建图例
                    self.ax.legend(
                        handles=handles,
                        loc='upper center',
                        bbox_to_anchor=(0.5, 1.08),
                        ncol=1,  # 单列显示单元格类型
                        fontsize=fontsize
                    )
            else:
                messagebox.showwarning("Warning", f"Selected properties not available in unit cell data: {x_field} or {y_field}")
    
    def save_plot(self):
        """Save the current plot to a file"""
        options = {
            "defaultextension": ".png",
            "filetypes": [
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("EPS files", "*.eps"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*"),
            ]
        }
        
        # 保存位置选项
        save_option = messagebox.askyesnocancel(
            "保存选项", 
            "是否保存到 ./figures 目录？\n\n选择'是'：保存到./figures\n选择'否'：选择保存位置\n选择'取消'：取消保存"
        )
        
        if save_option is None:  # 用户选择了取消
            return
        
        if save_option:  # 用户选择了是，保存到./figures
            # 打开简化的对话框，只需要输入文件名
            filename = filedialog.asksaveasfilename(
                title="输入文件名（不含扩展名）",
                initialdir="./figures",
            )
            
            if filename:
                try:
                    # 获取文件格式
                    format_dialog = FormatDialog(self.plot_frame)
                    format_info = format_dialog.result
                    
                    if format_info:  # 用户没有取消对话框
                        format, dpi, transparent = format_info
                        
                        # 使用高质量保存函数
                        filepath = save_high_quality_figure(
                            self.fig, 
                            os.path.basename(filename),  # 只使用文件名部分
                            dpi=dpi, 
                            format=format,
                            transparent=transparent
                        )
                        
                        messagebox.showinfo("成功", f"高清图表已保存至:\n{filepath}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")
        else:  # 用户选择了否，选择保存位置
            file_path = filedialog.asksaveasfilename(**options)
            if file_path:
                try:
                    self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                    messagebox.showinfo("成功", f"图表已保存至: {file_path}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")


class FormatDialog(tk.Toplevel):
    """图表格式设置对话框"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("设置保存格式")
        self.geometry("300x200")
        self.resizable(False, False)
        
        # 结果变量，返回 (format, dpi, transparent)
        self.result = None
        
        # 创建变量
        self.format_var = tk.StringVar(value="png")
        self.dpi_var = tk.StringVar(value="300")
        self.transparent_var = tk.BooleanVar(value=False)
        
        # 创建控件
        self.create_widgets()
        
        # 设置模态对话框
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # 等待用户操作
        self.wait_window(self)
    
    def create_widgets(self):
        # 格式选择
        ttk.Label(self, text="文件格式:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        format_combo = ttk.Combobox(self, textvariable=self.format_var, 
                              values=["png", "pdf", "svg", "eps", "jpg"], 
                              width=10, state="readonly")
        format_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # DPI设置
        ttk.Label(self, text="分辨率(DPI):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        dpi_combo = ttk.Combobox(self, textvariable=self.dpi_var, 
                           values=["100", "200", "300", "600"], 
                           width=10)
        dpi_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # 透明背景选择
        ttk.Checkbutton(self, text="透明背景", variable=self.transparent_var).grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
    
    def on_ok(self):
        # 验证DPI输入
        try:
            dpi = int(self.dpi_var.get())
            if dpi <= 0:
                raise ValueError("DPI必须是正整数")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的DPI值（正整数）")
            return
        
        self.result = (self.format_var.get(), dpi, self.transparent_var.get())
        self.destroy()
    
    def on_cancel(self):
        self.result = None
        self.destroy()


class FigureAdjustDialog(tk.Toplevel):
    """图表位置和大小调整对话框"""
    
    def __init__(self, figure, parent):
        super().__init__(parent)
        self.title("调整图表位置和大小")
        self.geometry("450x350")
        self.resizable(True, True)
        
        self.figure = figure
        self.result = False
        
        # 获取当前子图的位置和大小
        current = self.figure.subplotpars
        
        # 创建变量
        self.left_var = tk.DoubleVar(value=current.left)
        self.right_var = tk.DoubleVar(value=current.right)
        self.bottom_var = tk.DoubleVar(value=current.bottom)
        self.top_var = tk.DoubleVar(value=current.top)
        self.wspace_var = tk.DoubleVar(value=current.wspace)
        self.hspace_var = tk.DoubleVar(value=current.hspace)
        
        # 创建控件
        self.create_widgets()
        
        # 设置模态对话框
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # 等待用户操作
        self.wait_window(self)
    
    def create_widgets(self):
        # 创建滑块和标签框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 横向边距
        ttk.Label(main_frame, text="左边距:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        left_slider = ttk.Scale(main_frame, from_=0, to=0.5, variable=self.left_var, 
                          command=self.update_preview)
        left_slider.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.left_var, width=6).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(main_frame, text="右边距:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        right_slider = ttk.Scale(main_frame, from_=0.5, to=1.0, variable=self.right_var, 
                           command=self.update_preview)
        right_slider.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.right_var, width=6).grid(row=1, column=2, padx=5, pady=5)
        
        # 纵向边距
        ttk.Label(main_frame, text="底边距:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        bottom_slider = ttk.Scale(main_frame, from_=0, to=0.5, variable=self.bottom_var, 
                            command=self.update_preview)
        bottom_slider.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.bottom_var, width=6).grid(row=2, column=2, padx=5, pady=5)
        
        ttk.Label(main_frame, text="顶边距:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        top_slider = ttk.Scale(main_frame, from_=0.5, to=1.0, variable=self.top_var, 
                         command=self.update_preview)
        top_slider.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.top_var, width=6).grid(row=3, column=2, padx=5, pady=5)
        
        # 间距
        ttk.Label(main_frame, text="水平间距:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        wspace_slider = ttk.Scale(main_frame, from_=0, to=1, variable=self.wspace_var, 
                            command=self.update_preview)
        wspace_slider.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.wspace_var, width=6).grid(row=4, column=2, padx=5, pady=5)
        
        ttk.Label(main_frame, text="垂直间距:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        hspace_slider = ttk.Scale(main_frame, from_=0, to=1, variable=self.hspace_var, 
                            command=self.update_preview)
        hspace_slider.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.hspace_var, width=6).grid(row=5, column=2, padx=5, pady=5)
        
        # 预设按钮
        presets_frame = ttk.Frame(main_frame)
        presets_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Button(presets_frame, text="紧凑型", 
                  command=lambda: self.apply_preset(0.125, 0.9, 0.1, 0.9, 0.2, 0.2)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(presets_frame, text="宽松型", 
                  command=lambda: self.apply_preset(0.15, 0.85, 0.15, 0.85, 0.3, 0.3)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(presets_frame, text="标准型", 
                  command=lambda: self.apply_preset(0.125, 0.95, 0.1, 0.95, 0.2, 0.2)).pack(side=tk.LEFT, padx=5)
        
        # 确定取消按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="应用", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="重置", command=self.reset_values).pack(side=tk.LEFT, padx=10)
        
        # 配置网格权重，使其可扩展
        main_frame.columnconfigure(1, weight=1)
        
        # 帮助提示
        help_text = "调整滑块来改变图表位置和大小。左/底值越大，边距越大；右/顶值越小，边距越大。"
        ttk.Label(main_frame, text=help_text, wraplength=400).grid(row=8, column=0, columnspan=3, pady=10)
    
    def update_preview(self, *args):
        """实时更新图表预览"""
        try:
            self.figure.subplots_adjust(
                left=self.left_var.get(),
                right=self.right_var.get(),
                bottom=self.bottom_var.get(),
                top=self.top_var.get(),
                wspace=self.wspace_var.get(),
                hspace=self.hspace_var.get()
            )
            self.figure.canvas.draw_idle()
        except Exception as e:
            # 忽略可能出现的临时错误（例如，当左边距大于右边距时）
            pass
    
    def apply_preset(self, left, right, bottom, top, wspace, hspace):
        """应用预设值"""
        self.left_var.set(left)
        self.right_var.set(right)
        self.bottom_var.set(bottom)
        self.top_var.set(top)
        self.wspace_var.set(wspace)
        self.hspace_var.set(hspace)
        self.update_preview()
    
    def reset_values(self):
        """重置为默认值"""
        self.apply_preset(0.125, 0.9, 0.1, 0.9, 0.2, 0.2)
    
    def on_ok(self):
        """应用更改并关闭对话框"""
        self.update_preview()  # 确保最终应用了更改
        self.result = True
        self.destroy()
    
    def on_cancel(self):
        """取消更改并关闭对话框"""
        self.result = False
        self.destroy()


class LegendAdjustDialog(tk.Toplevel):
    """图例大小和位置调整对话框"""
    
    def __init__(self, figure, plot_handler, parent):
        super().__init__(parent)
        self.title("调整图例大小和位置")
        self.geometry("450x400")
        self.resizable(True, True)
        
        self.figure = figure
        self.ax = figure.axes[0] if figure.axes else None
        self.plot_handler = plot_handler
        self.result = False
        
        # 获取当前图例（如果存在）
        self.current_legend = None
        if self.ax:
            legends = self.ax.get_legend()
            if legends:
                self.current_legend = legends
        
        # 创建变量
        self.loc_var = tk.StringVar(value="best")
        self.ncol_var = tk.IntVar(value=2)
        self.fontsize_var = tk.IntVar(value=10)
        self.alpha_var = tk.DoubleVar(value=0.8)
        self.frameon_var = tk.BooleanVar(value=True)
        
        # bbox_to_anchor参数
        self.bbox_x_var = tk.DoubleVar(value=0.5)
        self.bbox_y_var = tk.DoubleVar(value=1.0)
        self.use_bbox_var = tk.BooleanVar(value=False)
        
        # 填充当前图例设置（如果存在）
        self.load_current_settings()
        
        # 创建控件
        self.create_widgets()
        
        # 设置模态对话框
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # 等待用户操作
        self.wait_window(self)
    
    def safe_get_float(self, var, default=0.0):
        """安全获取浮点数值，处理None和转换错误"""
        try:
            value = var.get()
            if value is None or value == "None":
                return default
            return float(value)
        except (ValueError, TypeError, tk.TclError):
            return default
            
    def safe_get_int(self, var, default=0):
        """安全获取整数值，处理None和转换错误"""
        try:
            value = var.get()
            if value is None or value == "None":
                return default
            return int(value)
        except (ValueError, TypeError, tk.TclError):
            return default
            
    def safe_get_bool(self, var, default=False):
        """安全获取布尔值，处理None和转换错误"""
        try:
            value = var.get()
            if value is None or value == "None":
                return default
            return bool(value)
        except (ValueError, TypeError, tk.TclError):
            return default
    
    def load_current_settings(self):
        """加载当前图例设置"""
        if not self.current_legend:
            return
            
        # 尝试获取当前设置
        try:
            # 获取位置
            loc = self.current_legend._loc
            if isinstance(loc, str):
                self.loc_var.set(loc)
            
            # 获取列数
            if hasattr(self.current_legend, "_ncol"):
                self.ncol_var.set(self.current_legend._ncol)
                
            # 获取字体大小
            if hasattr(self.current_legend, "_fontsize"):
                self.fontsize_var.set(self.current_legend._fontsize)
            
            # 获取透明度
            if hasattr(self.current_legend, "_alpha"):
                self.alpha_var.set(self.current_legend._alpha)
            
            # 获取框架设置
            if hasattr(self.current_legend, "_frameon"):
                self.frameon_var.set(self.current_legend._frameon)
            
            # 获取位置微调
            if hasattr(self.current_legend, "_bbox_to_anchor"):
                bbox = self.current_legend._bbox_to_anchor
                if bbox:
                    self.use_bbox_var.set(True)
                    if hasattr(bbox, "x0"):
                        self.bbox_x_var.set(bbox.x0)
                    if hasattr(bbox, "y0"):
                        self.bbox_y_var.set(bbox.y0)
        except:
            # 如果获取失败，使用默认值
            pass
    
    def create_widgets(self):
        # 创建滑块和标签框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 位置设置
        ttk.Label(main_frame, text="图例位置:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        loc_values = ["best", "upper right", "upper left", "lower left", "lower right", 
                     "right", "center left", "center right", "lower center", "upper center", "center"]
        loc_combo = ttk.Combobox(main_frame, textvariable=self.loc_var, values=loc_values, width=15)
        loc_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5, columnspan=2)
        
        # 列数设置
        ttk.Label(main_frame, text="列数:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(main_frame, from_=1, to=10, textvariable=self.ncol_var, width=5).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 字体大小
        ttk.Label(main_frame, text="字体大小:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        font_slider = ttk.Scale(main_frame, from_=6, to=20, variable=self.fontsize_var, 
                          command=lambda s: self.fontsize_var.set(int(float(s))))
        font_slider.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(main_frame, textvariable=self.fontsize_var).grid(row=2, column=2, padx=5, pady=5)
        
        # 透明度
        ttk.Label(main_frame, text="透明度:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        alpha_slider = ttk.Scale(main_frame, from_=0.0, to=1.0, variable=self.alpha_var)
        alpha_slider.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(main_frame, textvariable=self.alpha_var).grid(row=3, column=2, padx=5, pady=5)
        
        # 显示框架
        ttk.Checkbutton(main_frame, text="显示边框", variable=self.frameon_var).grid(
            row=4, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        # 位置微调
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=5, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        ttk.Checkbutton(main_frame, text="自定义位置", variable=self.use_bbox_var, 
                       command=self.toggle_bbox).grid(
            row=6, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        # 创建一个框架来包含bbox相关控件
        self.bbox_frame = ttk.Frame(main_frame)
        self.bbox_frame.grid(row=7, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(self.bbox_frame, text="X坐标:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        x_slider = ttk.Scale(self.bbox_frame, from_=0.0, to=1.0, variable=self.bbox_x_var)
        x_slider.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(self.bbox_frame, textvariable=self.bbox_x_var).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(self.bbox_frame, text="Y坐标:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        y_slider = ttk.Scale(self.bbox_frame, from_=0.0, to=1.5, variable=self.bbox_y_var)
        y_slider.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(self.bbox_frame, textvariable=self.bbox_y_var).grid(row=1, column=2, padx=5, pady=5)
        
        # 预览按钮
        ttk.Button(main_frame, text="预览", command=self.update_preview).grid(
            row=8, column=0, columnspan=3, pady=10)
        
        # 确定取消按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="应用", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="重置", command=self.reset_values).pack(side=tk.LEFT, padx=10)
        
        # 配置网格权重，使其可扩展
        main_frame.columnconfigure(1, weight=1)
        
        # 初始化bbox框架的状态
        self.toggle_bbox()
    
    def toggle_bbox(self):
        """根据复选框状态切换位置微调选项的可用性"""
        state = tk.NORMAL if self.use_bbox_var.get() else tk.DISABLED
        for child in self.bbox_frame.winfo_children():
            child.configure(state=state)
    
    def update_preview(self):
        """预览图例设置"""
        if not self.ax:
            return
            
        try:
            # 移除当前图例
            if self.current_legend:
                self.current_legend.remove()
            
            # 使用安全的getter方法获取所有值
            fontsize = self.safe_get_int(self.fontsize_var, 10)
            framealpha = self.safe_get_float(self.alpha_var, 0.8)
            ncol = self.safe_get_int(self.ncol_var, 2)
            frameon = self.safe_get_bool(self.frameon_var, True)
            loc = self.loc_var.get() or "best"
            
            # 构建参数字典
            kwargs = {
                'fontsize': fontsize,
                'framealpha': framealpha,
                'ncol': ncol,
                'loc': loc,
                'frameon': frameon
            }
            
            # 添加位置微调，使用安全的getter方法
            if self.use_bbox_var.get():
                x_coord = self.safe_get_float(self.bbox_x_var, 0.5)
                y_coord = self.safe_get_float(self.bbox_y_var, 1.0)
                kwargs['bbox_to_anchor'] = (x_coord, y_coord)
                
                # 同步UI显示
                if x_coord != self.bbox_x_var.get():
                    self.bbox_x_var.set(x_coord)
                if y_coord != self.bbox_y_var.get():
                    self.bbox_y_var.set(y_coord)
            
            # 打印调试信息
            print(f"图例参数: {kwargs}")
            
            # 创建新图例
            handles, labels = self.ax.get_legend_handles_labels()
            if handles and labels:
                self.current_legend = self.ax.legend(handles=handles, labels=labels, **kwargs)
                self.figure.canvas.draw_idle()
            else:
                messagebox.showwarning("警告", "当前图表没有图例项")
        except Exception as e:
            import traceback
            traceback.print_exc()  # 打印详细错误信息到控制台
            messagebox.showerror("错误", f"更新图例失败: {str(e)}")
    
    def reset_values(self):
        """重置为默认值"""
        try:
            self.loc_var.set("best")
            self.ncol_var.set(2)
            self.fontsize_var.set(10)
            self.alpha_var.set(0.8)
            self.frameon_var.set(True)
            self.bbox_x_var.set(0.5)
            self.bbox_y_var.set(1.0)
            self.use_bbox_var.set(False)
            self.toggle_bbox()
        except Exception as e:
            messagebox.showerror("错误", f"重置值失败: {str(e)}")
    
    def on_ok(self):
        """应用更改并关闭对话框"""
        self.update_preview()  # 确保最终应用了更改
        self.result = True
        self.destroy()
    
    def on_cancel(self):
        """取消更改并关闭对话框"""
        # 如果是取消，恢复原始图例（如果存在）
        if self.current_legend:
            self.current_legend.remove()
        
        # 重新绘制图表以恢复原始图例
        if self.plot_handler:
            self.plot_handler.generate_plot()
            
        self.result = False
        self.destroy() 