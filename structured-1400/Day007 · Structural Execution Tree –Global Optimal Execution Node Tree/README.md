# 结构化执行树算法 - 全局最优执行节点树

本项目实现了一种用于结构化期权组合优化的执行树算法，可以在不同的市场情景下找到全局最优执行路径。

## 主要功能

1. **路径模拟器** - 使用几何布朗运动模拟相关资产价格路径
2. **结构依赖图** - 构建期权之间的依赖关系图
3. **执行树搜索器** - 使用回溯法搜索最优执行序列
4. **结果聚合** - 汇总不同路径的执行结果
5. **可视化** - 可视化依赖关系和模拟结果

## 可视化结果

所有生成的图表保存在`simulation_charts`文件夹中，主要包括：

- 期权依赖关系图 (`dependency_graph.png`)
- 总收益分布图 (`payoff_distribution.png`)
- 期权执行频率图 (`execution_frequency.png`)

## 使用方法

运行`pricing_model.py`文件即可执行完整的模拟和优化过程：

```bash
python pricing_model.py
```

## 相关文档

- [白皮书](whitepaper.md) - 算法原理详细说明
- [条款表](term-sheet.md) - 结构化产品条款说明
- [情景示例](scenario-examples.md) - 典型市场情景下的执行案例
- [风险披露](risk-disclosure.md) - 模型和产品相关风险