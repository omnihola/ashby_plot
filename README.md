# Ashby Plot Generator GUI

一个基于Python的图形界面应用，用于生成材料性能的Ashby图。

## 功能特点

- 从Excel文件加载材料属性数据
- 交互式选择X轴和Y轴的材料属性
- 自定义坐标轴范围和比例（线性/对数）
- 添加和自定义参考指导线
- 选择不同的图表类型（演示或出版物）
- 保存生成的图表为PNG、PDF或SVG格式
- 支持显示单元格（Unit Cell）数据
- 支持添加个别材料标记

## 安装依赖

使用以下命令安装所需的Python依赖库：

```
pip install -r requirements.txt
```

## 使用方法

1. 运行GUI应用：

```
python main.py
```

2. 在"File"选项卡中：
   - 点击"Browse"选择包含材料属性的Excel文件
   - 选择数据类型（范围或单值）
   - 选择图表类型（演示或出版物）
   - 勾选是否使用对数坐标

3. 在"Axis Settings"选项卡中：
   - 选择X轴和Y轴的材料属性
   - 设置坐标轴范围

4. 在"Guidelines"选项卡中：
   - 启用/禁用参考指导线
   - 配置指导线参数

5. 在"Materials"选项卡中：
   - 启用/禁用个别材料标记

6. 在"Unit Cells"选项卡中：
   - 启用/禁用单元格数据
   - 选择填充材料类型

7. 点击"Generate Plot"按钮生成Ashby图
8. 点击"Save Plot"按钮将图表保存为图像文件

## 数据格式要求

输入Excel文件必须包含以下内容：
- "Category"列：用于标识材料类别
- 数值属性列：如"Density"、"Young Modulus"等

## 项目结构

- `main.py`: 应用入口点
- `gui/app.py`: 主应用类
- `gui/panels.py`: UI面板组件
- `gui/plot_handler.py`: 绘图处理器
- `gui/unit_cell_handler.py`: 单元格数据处理
- `src/`: 包含原始绘图脚本和函数 