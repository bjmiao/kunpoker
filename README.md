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

Also, read the code `read_lookup_table.p` to see how to use the lookup table.

The larger the value is, the stronger the the card is.
 

