# GraphWork01
图形学作业——多边形裁剪
-----
## Algorithm: 
Weiler-Atherton
## Environment:

Package | Version | Latest Version

PyQt5 |	5.15.1 | 5.15.1

PyQt5-sip	| 12.8.1 | 12.8.1

PyQt5-stubs | 5.14.2.2 | 5.14.2.2

packaging | 20.4 | 20.4

pip | 20.2.3 | 20.2.3

pyparsing | 2.4.7 | 2.4.7

setuptools | 50.3.0 | 50.3.0

sip | 5.4.0 | 5.4.0

six | 1.15.0 | 1.15.0

toml | 0.10.1 | 0.10.1  

## Run:
python main.py

## Description:
界面由画板，以及三个按钮组成。**左键**点击画板添加当前多边形的顶点，**右键**闭合当前多边形。两个按钮分别切换当前所画多边形为主多边形内容还是裁剪多边形内容。

## Input Description:
1.默认主多边形和裁剪多边形的第一个点集输入为其最外面的边框，也即再输入主多边形和裁剪多边形点集均被视为内环输入
2.多边形（内环）至少存在三个不共线顶点
3.多边形（内环）不可自交
4.内环之间不可相交

## Output Description:
蓝色区域为内裁区域
绿色区域为外裁区域
