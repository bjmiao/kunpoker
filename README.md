<!--
 * @Author: zgong
 * @Date: 2021-01-15 15:12:59
 * @LastEditors: zgong
 * @LastEditTime: 2021-01-15 23:00:29
-->
# kunpoker
GUI, Multi-player game server, AI, cheat code, etc. Everything you need about Texas Hold'em

Initialized for Ubiquant Texas Hold'em poker championship.

# 20210111
1. 组件开发：
  牌力模块：1. 模拟模块 2. 采样 3. value 
 
  历史模块: 1. 单局比赛 2。玩家行动轨迹 

  决策模块： API 包装 
  
2. 核心组件
  玩家画像模块：1. 统计模块 2.
  胜率估算：1
  决策：

# 20210113

From MBJ:

I completed the lookup table. Usage:

``` bash
cd modules/texaspoker/lib
python card_value.py  # this is used to construct the lookup table

# this should generate a `lookup_table.pkl` in that directory

python read_lookup_table.py  # this is a demo on how to use this lookup table
```

Also, read the code `read_lookup_table.py` to see how to use the lookup table.

The larger the value is, the stronger the the card is.
 
# 20210115
From zgong:

1. 修改client.py 使用-u 制定用户名 -a 指定使用的ai
2. 初代ai_v2:
  - 发牌圈采用牌力打法,大牌raise,中牌limp，小牌fold,较紧。牌力分级见表('AAp','ATs','78o',表示成对，同花，非同花)
  - 翻牌，河牌，转牌 均使用较粗糙的胜率 蒙特卡洛(偏高) 
  - 按照胜率计算期望估计作决策，没有作牌力平衡

## 可修改方向
1. 根据对手行为，估计牌力范围，修正蒙特卡洛结果，提高读牌能力
2. 修正raise行为，加入随机数 对牌力作平衡

学习 poker_ai
1. 全局信息 PokerStates
2. 学习算法     
Evaluates hand strengths using a variant of Cactus Kev's algorithm:
    http://suffe.cool/poker/evaluator.html