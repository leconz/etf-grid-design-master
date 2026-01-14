## 程序功能
1. 提供ETF网格设计功能
2. 分析ETF价格趋势
3. 计算ATR值
4. 评估网格设计的适宜度

## 开发记录
### 获取股票名称
1. 从futu接口获取股票名称，富途API的get_stock_basicinfo方法的stock_type参数并不是严格限制的，使用ETF类型也能查询到普通股票，甚至不指定stock_type参数可以同时查询多种类型的证券
2. 缓存股票名称，避免重复请求

## 限制
不调用tushare接口，只使用futu接口

## 项目代码托管
1. 项目代码托管在GitHub上，位置是https://github.com/leconz/etf-grid-design-master.git
2. 采用Python编写，依赖于futu-api库
3. 提供详细的注释和文档，方便其他开发者理解和使用