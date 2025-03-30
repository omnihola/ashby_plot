# -*- coding: utf-8 -*-
"""
Plot utilities script.
Contains all the misc. functions to generate the ashby plot (not related to the actual ellipses).


@author: Walgren
"""
import os

import numpy as np

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import colors

from src.plot_convex_hull import (
    draw_ellipses,
    draw_hull,
    )

from src.rotation_aware_annotation import RotationAwareAnnotation


def save_high_quality_figure(fig, filename, dpi=300, format='png', transparent=False):
    '''
    将图表以高分辨率保存到./figures目录下

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        要保存的图表对象
    filename : str
        文件名（不包含路径和扩展名）
    dpi : int, optional
        分辨率，默认300（出版质量），更高的值会产生更大的文件
    format : str, optional
        文件格式，可选：'png', 'pdf', 'svg', 'eps', 'jpg'等
    transparent : bool, optional
        是否使用透明背景，对于PNG等支持透明的格式有效
    
    Returns
    -------
    str
        保存的文件的完整路径
    '''
    # 确保figures目录存在
    figures_dir = os.path.join(os.getcwd(), 'figures')
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)
    
    # 构建完整文件路径
    full_filename = f"{filename}.{format}" if '.' not in filename else filename
    filepath = os.path.join(figures_dir, full_filename)
    
    # 保存图表
    fig.savefig(
        filepath, 
        dpi=dpi, 
        format=format, 
        bbox_inches='tight',  # 裁剪多余的空白区域
        transparent=transparent
    )
    
    print(f"高清图表已保存至: {filepath}")
    return filepath


def plotting_presets(figure_type='publication'):
    """
    设置绘图样式的函数。控制图表的整体外观和风格。
    
    参数:
    ------
    figure_type : str
        'publication' - 为出版物优化的样式（小字体，紧凑）
        'presentation' - 为演示优化的样式（大字体，宽松）
    """
    # 禁用LaTeX渲染，防止因系统没有安装LaTeX导致的错误
    plt.rcParams['text.usetex'] = False
    
    # 设置字体系列
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # 设置SVG输出选项
    plt.rcParams['svg.fonttype'] = 'none'
    
    # 根据图表类型配置样式
    if figure_type == 'publication':
        # 小字体适合出版物
        plt.rcParams['font.size'] = 12  # 基本字体大小
        plt.rcParams['axes.labelsize'] = 12  # 轴标签字体大小
        plt.rcParams['xtick.labelsize'] = 10  # x轴刻度标签字体大小
        plt.rcParams['ytick.labelsize'] = 10  # y轴刻度标签字体大小
        plt.rcParams['legend.fontsize'] = 8  # 图例字体大小
        plt.rcParams['figure.titlesize'] = 14  # 图表标题字体大小
        
        # 标记和线条的大小
        plt.rcParams['lines.markersize'] = 5  # 标记大小
        plt.rcParams['lines.linewidth'] = 1.0  # 线条宽度
        
    elif figure_type == 'presentation':
        # 大字体适合演示
        plt.rcParams['font.size'] = 16  # 基本字体大小
        plt.rcParams['axes.labelsize'] = 18  # 轴标签字体大小
        plt.rcParams['xtick.labelsize'] = 14  # x轴刻度标签字体大小
        plt.rcParams['ytick.labelsize'] = 14  # y轴刻度标签字体大小
        plt.rcParams['legend.fontsize'] = 14  # 图例字体大小
        plt.rcParams['figure.titlesize'] = 20  # 图表标题字体大小
        
        # 标记和线条的大小
        plt.rcParams['lines.markersize'] = 8  # 标记大小
        plt.rcParams['lines.linewidth'] = 2.0  # 线条宽度


def draw_plot(
        data,
        x_axis_quantity,
        y_axis_quantity,
        ax,
        material_colors,
        data_type = 'ranges'
        ):
    '''
    绘制材料数据及其凸包。
    可以修改本函数内的参数来调整数据点的显示方式和凸包样式。

    Parameters
    ----------
    data : pandas dataframe
        包含所有材料数据的数据框
    x_axis_quantity : str
        X轴显示的属性名称
    y_axis_quantity : str
        Y轴显示的属性名称
    ax : matplotlib.pyplot.axis
        绘图的坐标轴对象
    material_colors : dict
        材料类别及其对应颜色的字典
    data_type : str, optional
        数据类型，可选值：'ranges'（范围值）或'values'（单一值）
    '''
    for category, material_data in data.groupby('Category'):

        if data_type == 'ranges':
            # ===== 范围数据处理 =====
            X = np.zeros(shape=(2*len(material_data),2))
            X[:len(material_data),1] = material_data[y_axis_quantity + ' low']
            X[:len(material_data),0] = material_data[x_axis_quantity + ' low']

            X[len(material_data):,1] = material_data[y_axis_quantity + ' high']
            X[len(material_data):,0] = material_data[x_axis_quantity + ' high']

            # ===== 绘制椭圆表示材料属性范围 =====
            # 可以调整alpha值来改变椭圆的透明度
            for i in range(len(material_data)):
                draw_ellipses(
                        x = [material_data[x_axis_quantity + ' low'].iloc[i],
                             material_data[x_axis_quantity + ' high'].iloc[i]],
                        y = [material_data[y_axis_quantity + ' low'].iloc[i],
                             material_data[y_axis_quantity + ' high'].iloc[i]],
                        plot_kwargs = {
                            'facecolor': colors.to_rgba(
                                material_colors[category],
                                alpha=0.25  # 椭圆填充的透明度，0.0-1.0之间
                                ),
                            'edgecolor': material_colors[category]  # 椭圆边缘的颜色
                            },
                        ax = ax,
                        )

        elif data_type == 'values':
            # ===== 单一值数据处理 =====
            X = np.zeros(shape = (len(material_data),2))
            X[:,0] = material_data[x_axis_quantity]
            X[:,1] = material_data[y_axis_quantity]

            # ===== 绘制散点图表示单一材料属性值 =====
            ax.scatter(
                X[:,0],
                X[:,1],
                c=material_colors[category])  # 点的颜色

        else:
            raise(ValueError, 'Only options for data_type in draw_plot are ranges or values')

        # ===== 绘制材料类别的凸包 =====
        draw_hull(
            X,
            scale = 1.1,         # 凸包放大比例，>1.0放大，<1.0缩小
            padding = 'scale',   # 凸包内边距类型
            n_interpolate = 1000, # 凸包轮廓点数量，越大越平滑
            interpolation = 'cubic', # 凸包插值方法，可选：'linear', 'quadratic', 'cubic'
            ax = ax,
            plot_kwargs = {
                'color': material_colors[category],  # 凸包颜色
                'alpha': 0.2                         # 凸包透明度，0.0-1.0之间
                }
            )


def create_legend(
        material_classes,
        material_colors,
        ncol=2,  # 减少列数，防止文本重叠
        loc='upper center',  # 更改位置到图表上方中央
        fontsize=None,  # 可选的字体大小参数
        ):
    '''
    创建图例，显示在图表上方。
    可以修改本函数内的参数来调整图例的位置和样式。

    Parameters
    ----------
    material_classes : 可迭代对象
        材料类别列表或字典键对象
    material_colors : 字典
        材料类别及其对应颜色的字典
    ncol : int, optional
        图例的列数，默认为2，减少可以避免文本重叠
    loc : str, optional
        图例位置，默认为'upper center'
    fontsize : int or str, optional
        图例字体大小，可以是整数或'small', 'medium', 'large'等
    '''
    handles = []
    # 为每个材料类别创建图例项
    for material_class in material_classes:
        patch = patches.Patch(
            color = material_colors[material_class],  # 图例颜色
            label = material_class                    # 图例标签
            )
        handles.append(patch)

    # 在图表外部放置图例
    legend = plt.legend(
        handles=handles,
        bbox_to_anchor = (0.5, 1.08),  # 图例位置(x, y)，以轴的中心为锚点
        loc = loc,                    # 图例锚点位置
        ncol = ncol,                  # 图例的列数，减少列数可以避免重叠
        borderaxespad = 0,            # 图例与轴的间距
        frameon=True,                 # 添加图例边框
        framealpha=0.8,               # 图例背景透明度
        )
    
    # 如果指定了字体大小，则设置
    if fontsize is not None:
        for text in legend.get_texts():
            text.set_fontsize(fontsize)
    
    return legend


def draw_guideline(
        guideline,
        ax,
        log_flag = True,
        ):
    '''
    绘制材料指数参考线。
    可以修改本函数内的参数来调整参考线的样式和注释。

    Parameters
    ----------
    guideline : dict
        包含参考线设置的字典：
        power : 参考线的幂次
        x_lim : X轴范围
        y_intercept : Y轴截距
        string : 显示的公式文本
        string_position : 文本位置
    ax : matplotlib坐标轴对象
    log_flag : 是否使用对数坐标系
    '''
    power = guideline['power']
    x_lim = guideline['x_lim']
    y_intercept = guideline['y_intercept']
    string = guideline['string']
    string_position = guideline['string_position']

    # 创建X轴点
    num_points = 5  # 参考线上的点数，增加此值可使线条更平滑
    x_values = np.linspace(x_lim[0], x_lim[1], num_points)
    y_values = np.zeros(shape = num_points)

    # 创建参考线
    for i in range(len(x_values)):
        if log_flag:
            # 对数坐标系下的幂函数
            y_values[i] = y_intercept * x_values[i]**power
        else:
            # 线性坐标系下的线性函数
            y_values[i] = power * x_values[i] + y_intercept

    # 绘制参考线
    ax.plot(
        x_values,
        y_values,
        'k--',  # 黑色虚线，可以修改为其他样式，如'r-'红色实线
        )

    # 添加参考线的注释
    RotationAwareAnnotation(
        string,  # 显示的文本
        xy=string_position,  # 文本位置
        p=(x_values[3], y_values[3]),  # 参考点
        pa=(x_values[0], y_values[0]),  # 另一参考点，用于计算旋转
        ax=ax,
        xytext=(0,0),  # 文本偏移
        textcoords="offset points",
        va="top"  # 垂直对齐方式
        )


def common_definitions():
    '''
    定义常用的单位和材料颜色。
    可以在此函数中添加新的单位或修改材料颜色。

    Returns
    -------
    units : dict
        各物理量及其对应单位的字典
    material_colors : dict
        材料类别及其对应颜色的字典
    '''
    # ===== 常用单位定义 =====
    # 为添加新物理量，请在此字典中添加对应的单位
    units = {
        'Density': 'kg/m$^3$',
        'Tensile Strength': 'MPa',
        "Young Modulus": 'GPa',
        "Fracture Toughness": r"MPa$\sqrt{\text{m}}$",
        "Thermal Conductivity": r"W/m$\cdot$K",
        "Thermal expansion": "1$^-6$/m",
        "Resistivity": r"$\Omega \cdot$m",
        "Poisson": "-",
        "Poisson difference": "-",
        }

    # ===== 材料类别颜色定义 =====
    # 可以修改颜色值来改变不同材料类别的显示颜色
    # 支持的颜色名称：'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'white'等
    # 也可以使用十六进制颜色代码如'#FF5733'
    material_colors = {
        'Foams': 'blue',
        'Elastomers': 'orange',
        'Natural materials': 'green',
        'Polymers': 'red',
        'Nontechnical ceramics': 'purple',
        'Composites': 'Brown',
        'Technical ceramics': 'pink',
        'Metals': 'grey',
        }

    return units, material_colors
