1. 创建docs目录（如果不存在）
2. 从tushare\_data.md获取所有tushare Etf数据接口链接
3. 使用firecrawl\_scrape工具分别抓取每个链接的内容，转换为markdown格式
4. 将抓取的内容保存到docs目录中，文件名根据接口名称命名
5. 验证所有文档是否成功保存

