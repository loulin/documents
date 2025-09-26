import matplotlib.pyplot as plt
  import numpy as np
  import pandas as pd

  # 读取数据
  data = {
      '三文鱼': [9.2,0.1,9.5,9.0,9.8,8.5,9.7,8.0],
      '牛油果': [2.0,2.5,9.8,8.5,9.5,8.8,8.2,7.5],
      '菠菜': [3.5,1.8,0.5,10.0,9.9,4.0,9.5,8.5],
      '燕麦': [4.5,8.5,2.8,8.0,6.5,8.5,7.0,7.0],
      '白米饭': [2.5,9.5,0.1,3.0,2.0,4.5,3.0,9.5]
  }

  categories = ['蛋白质含量','碳水化合物含量','健康脂肪','营养密度',
                '血糖影响','饱腹感','抗炎效果','消化友好']

  # 创建雷达图
  fig = plt.figure(figsize=(12, 10))
  angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
  angles += angles[:1]  # 闭合图形

  for food_name, values in data.items():
      values += values[:1]  # 闭合数据
      ax = fig.add_subplot(2, 3, list(data.keys()).index(food_name)+1, projection='polar')
      ax.plot(angles, values, 'o-', linewidth=2, label=food_name)
      ax.fill(angles, values, alpha=0.25)
      ax.set_xticks(angles[:-1])
      ax.set_xticklabels(categories)
      ax.set_ylim(0, 10)
      ax.set_title(food_name, size=16, weight='bold')
      ax.grid(True)

  plt.tight_layout()
  plt.show()
