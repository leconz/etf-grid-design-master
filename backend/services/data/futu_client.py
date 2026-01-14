import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from .cache_service import EnhancedCache, TradingDateManager
import futu as ft

logger = logging.getLogger(__name__)


class futuClient:
    """富途API数据客户端 - 使用增强缓存策略（兼容原TushareClient接口）"""
    
    def __init__(self, cache_dir: str = "cache"):
        """初始化富途API客户端"""
        self.host = os.getenv('FUTU_HOST', '127.0.0.1')
        self.port = int(os.getenv('FUTU_PORT', 11111))
        
        # 初始化富途API连接
        self.quote_ctx = ft.OpenQuoteContext(host=self.host, port=self.port)
        
        # 初始化增强缓存管理器
        self.cache = EnhancedCache(cache_dir)
        
        # 初始化交易日管理器
        self.trading_date_manager = TradingDateManager(self.cache)
        
        logger.info("富途API客户端初始化成功（增强缓存版本）")
    
    def get_etf_daily_data(self, etf_code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        获取ETF日线数据（历史数据范围缓存）
        
        Args:
            etf_code: ETF代码（不含市场后缀）
            start_date: 开始日期 (YYYYMMDD格式)
            end_date: 结束日期 (YYYYMMDD格式)
            
        Returns:
            DataFrame: ETF日线数据
        """
        # 1. 先检查历史数据缓存
        cached_data = self.cache.get_historical_cache(etf_code, start_date, end_date)
        if cached_data:
            logger.info(f"✓ 从历史缓存获取ETF {etf_code} 日线数据 ({start_date}~{end_date})")
            # 将缓存的字典数据转换回DataFrame
            df = pd.DataFrame(cached_data)
            # 确保trade_date是datetime类型
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            return df
        
        # 2. 缓存未命中，使用富途API获取真实数据
        logger.info(f"→ 历史缓存未命中，使用富途API获取ETF {etf_code} 日线数据 ({start_date}~{end_date})")
        
        try:
            # 补全ETF代码，添加市场前缀
            full_etf_code = self._complete_etf_code(etf_code)
            
            # 将YYYYMMDD格式转换为富途API期望的YYYY-MM-DD格式
            start_date_formatted = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
            end_date_formatted = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
            
            # 使用富途API获取日线数据，不指定fields参数，使用默认值
            ret, data, page_req_key = self.quote_ctx.request_history_kline(
                code=full_etf_code,
                start=start_date_formatted,
                end=end_date_formatted,
                ktype=ft.KLType.K_DAY,
                autype=ft.AuType.QFQ
            )
            
            if ret != ft.RET_OK:
                logger.error(f"✗ 富途API获取ETF {etf_code} 日线数据失败: {data}")
                return None
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            
            # 转换日期格式
            df['trade_date'] = pd.to_datetime(df['time_key']).dt.strftime('%Y%m%d')
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            # 转换数据类型为Python原生类型
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(int)
            df['turnover'] = df['turnover'].astype(float)
            
            # 计算前收盘价
            df['pre_close'] = df['close'].shift(1)
            df.loc[0, 'pre_close'] = df.loc[0, 'open']  # 第一个数据的前收盘价设为开盘价
            df['pre_close'] = df['pre_close'].astype(float)
            
            # 计算涨跌额和涨跌幅
            df['change'] = df['close'] - df['pre_close']
            df['pct_chg'] = df['change'] / df['pre_close'] * 100
            df['change'] = df['change'].astype(float)
            df['pct_chg'] = df['pct_chg'].astype(float)
            
            # 计算日振幅
            df['amplitude'] = (df['high'] - df['low']) / df['pre_close'] * 100
            df['amplitude'] = df['amplitude'].astype(float)
            
            # 重命名列以匹配Tushare格式
            df = df.rename(columns={
                'volume': 'vol',
                'turnover': 'amount'
            })
            
            # 添加ts_code列
            df['ts_code'] = etf_code
            
            # 只保留Tushare格式的列
            df = df[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 
                     'pre_close', 'change', 'pct_chg', 'vol', 'amount', 'amplitude']]
            
            # 数据排序和重置索引
            df = df.sort_values('trade_date')
            df = df.reset_index(drop=True)
            
            # 3. 保存真实数据到历史缓存（转换为字典格式）
            cache_data = df.to_dict('records')
            self.cache.set_historical_cache(etf_code, start_date, end_date, cache_data)
            logger.info(f"✓ ETF {etf_code} 日线数据获取成功并已缓存，共{len(df)}条记录")
            
            return df
            
        except Exception as e:
            logger.error(f"✗ 获取ETF {etf_code} 日线数据失败: {str(e)}")
            return None
    
    def get_security_basic_info(self, code: str) -> Optional[Dict]:
        """
        获取证券基本信息（永久缓存），支持ETF和股票
        
        Args:
            code: 证券代码（不含市场后缀）
            
        Returns:
            Dict: 证券基本信息
        """
        # 1. 先检查永久缓存
        cached_data = self.cache.get_permanent_cache("security_basic", code)
        if cached_data:
            logger.info(f"✓ 从永久缓存获取证券 {code} 基本信息")
            return cached_data
        
        # 2. 缓存未命中，使用富途API获取真实数据
        logger.info(f"→ 永久缓存未命中，使用富途API获取证券 {code} 基本信息")
        
        try:
            # 补全证券代码，添加市场前缀
            full_code = self._complete_etf_code(code)
            
            # 使用富途API获取股票基本信息，不指定stock_type以支持多种证券类型
            market = ft.Market.US if full_code.startswith('US.') else ft.Market.HK if full_code.startswith('HK.') else ft.Market.SH if full_code.startswith('SH.') else ft.Market.SZ
            code_list = [full_code]  # 使用完整的股票代码（包括市场前缀）
            ret, data = self.quote_ctx.get_stock_basicinfo(
                market=market,
                code_list=code_list
            )
            
            if ret != ft.RET_OK or data.empty:
                logger.error(f"✗ 富途API获取证券 {code} 基本信息失败: {data}")
                return None
            
            # 转换为Tushare兼容格式
            row = data.iloc[0]
            
            # 确定证券类型
            security_type = 'ETF' if 'ETF' in row.get('name', '') else 'STOCK'
            
            basic_info = {
                'ts_code': code,
                'name': row.get('name', f'{security_type}_{code}'),
                'management': row.get('list_board', '未知'),  # 富途API没有直接的管理人字段，这里用上市板块代替
                'found_date': '',
                'list_date': '',
                'issue_amount': int(row.get('issue_size', 1000000000)) if security_type == 'ETF' else 0,  # 转换为Python int类型
                'm_fee': 0.5 if security_type == 'ETF' else 0,  # 只有ETF有管理费率
                'c_fee': 0.1 if security_type == 'ETF' else 0,  # 只有ETF有托管费率
                'track_index_code': '',  # 富途API没有直接的跟踪指数代码字段
                'track_index_name': row.get('stock_name', '').replace('ETF', '') if 'ETF' in row.get('stock_name', '') else ''  # 尝试从名称中提取跟踪指数
            }
            
            # 3. 保存数据到永久缓存
            self.cache.set_permanent_cache("security_basic", code, basic_info)
            logger.info(f"✓ 证券 {code} 基本信息获取成功并已永久缓存")
            
            return basic_info
            
        except Exception as e:
            logger.error(f"✗ 获取证券 {code} 基本信息失败: {str(e)}")
            return None
            
    def get_etf_basic_info(self, etf_code: str) -> Optional[Dict]:
        """
        获取ETF基本信息（永久缓存）
        兼容旧版本方法，内部调用get_security_basic_info
        
        Args:
            etf_code: ETF代码（不含市场后缀）
            
        Returns:
            Dict: ETF基本信息
        """
        return self.get_security_basic_info(etf_code)
    
    def get_latest_price(self, etf_code: str) -> Optional[Dict]:
        """
        获取ETF最新价格（智能交易日缓存）
        
        Args:
            etf_code: ETF代码（不含市场后缀）
            
        Returns:
            Dict: 最新价格信息
        """
        # 1. 获取最近的交易日
        latest_trading_date = self.trading_date_manager.get_latest_trading_date(None)  # 富途API不需要pro参数
        
        # 2. 检查该交易日的缓存
        cached_data = self.cache.get_daily_cache(latest_trading_date, "price", etf_code)
        if cached_data:
            logger.info(f"✓ 从交易日缓存获取ETF {etf_code} 最新价格 (交易日: {latest_trading_date})")
            return cached_data
        
        # 3. 缓存未命中，使用富途API获取真实数据
        logger.info(f"→ 交易日缓存未命中，使用富途API获取ETF {etf_code} 最新价格")
        
        try:
            # 补全ETF代码，添加市场前缀
            full_etf_code = self._complete_etf_code(etf_code)
            
            # 使用富途API获取最新行情快照
            ret, data = self.quote_ctx.get_market_snapshot([full_etf_code])
            
            if ret != ft.RET_OK or data.empty:
                logger.error(f"✗ 富途API获取ETF {etf_code} 最新价格失败: {data}")
                return None
            
            # 转换为所需格式
            row = data.iloc[0]
            
            # 计算涨跌幅
            current_price = float(row.get('last_price', 0))
            pre_close = float(row.get('prev_close_price', current_price))
            pct_change = (current_price - pre_close) / pre_close * 100 if pre_close != 0 else 0
            
            price_info = {
                'current_price': round(current_price, 3),
                'pre_close': round(pre_close, 3),
                'pct_change': round(pct_change, 2),
                'volume': int(row.get('volume', 0)),  # 转换为Python int类型
                'amount': float(row.get('turnover', 0)),  # 转换为Python float类型
                'trade_date': latest_trading_date,
                'data_age_days': 0  # 真实数据，设为0
            }
            
            # 4. 保存真实数据到缓存
            self.cache.set_daily_cache(latest_trading_date, "price", etf_code, price_info)
            logger.info(f"✓ ETF {etf_code} 最新价格获取成功并已缓存 (实际交易日: {latest_trading_date})")
            
            return price_info
            
        except Exception as e:
            logger.error(f"✗ 获取ETF {etf_code} 最新价格失败: {str(e)}")
            return None
    
    def search_etf(self, query: str) -> List[Dict]:
        """
        搜索ETF - 不使用缓存，保持实时性
        
        Args:
            query: 搜索关键词（ETF代码或名称）
            
        Returns:
            List[Dict]: ETF列表
        """
        logger.info(f"→ 搜索ETF: '{query}' (不使用缓存)")
        
        try:
            # 获取所有ETF列表 - 富途API没有直接的搜索接口，需要先获取所有ETF，然后在本地过滤
            etf_list = []
            
            # 先检查查询是否是完整的ETF代码
            if query.isdigit():
                # 补全ETF代码，添加市场前缀
                full_etf_code = self._complete_etf_code(query)
                market = full_etf_code.split('.')[1]
                # 获取单只ETF的基本信息
                # 注意：富途API的get_stock_basicinfo方法中，code_list应该包含完整的股票代码（包括市场前缀）
                code_list = [full_etf_code]  # 使用完整的股票代码（包括市场前缀）
                ret, data = self.quote_ctx.get_stock_basicinfo(
                    market=market,
                    stock_type=ft.SecurityType.ETF,
                    code_list=code_list
                )
                
                if ret == ft.RET_OK and not data.empty:
                    # 转换为所需格式
                    row = data.iloc[0]
                    etf_list.append({
                        'ts_code': query,
                        'code': query,  # 不含市场后缀
                        'name': row.get('stock_name', f'ETF_{query}'),
                        'management': row.get('list_board', '未知基金公司'),  # 富途API没有直接的管理人字段，这里用上市板块代替
                        'found_date': row.get('list_time', '')[:8] if row.get('list_time') else '',
                        'list_date': row.get('list_time', '')[:8] if row.get('list_time') else ''
                    })
                    
                    logger.info(f"✓ 搜索ETF '{query}' 成功，找到{len(etf_list)}个结果")
                    return etf_list
            
            # 对于非数字查询或单只ETF查询失败的情况，尝试获取所有ETF并过滤
            # 注意：富途API获取所有ETF可能会返回大量数据，这里简化处理
            # 实际生产环境中应该使用更高效的搜索方式
            markets = [ft.Market.SH, ft.Market.SZ]  # 只搜索沪深市场的ETF
            
            for market in markets:
                ret, data = self.quote_ctx.get_stock_basicinfo(
                    market=market,
                    stock_type=ft.SecurityType.ETF
                )
                
                if ret == ft.RET_OK and not data.empty:
                    # 根据查询条件过滤
                    filtered_df = data[
                        data['code'].str.contains(query, na=False, case=False) |
                        data['stock_name'].str.contains(query, na=False, case=False)
                    ]
                    
                    # 转换为列表格式
                    for _, row in filtered_df.head(5).iterrows():  # 每个市场最多返回5个结果
                        etf_code = row['code'].split('.')[1] if '.' in row['code'] else row['code']
                        etf_list.append({
                            'ts_code': etf_code,
                            'code': etf_code,  # 不含市场后缀
                            'name': row.get('stock_name', f'ETF_{etf_code}'),
                            'management': row.get('list_board', '未知基金公司'),  # 富途API没有直接的管理人字段，这里用上市板块代替
                            'found_date': row.get('list_time', '')[:8] if row.get('list_time') else '',
                            'list_date': row.get('list_time', '')[:8] if row.get('list_time') else ''
                        })
            
            logger.info(f"✓ 搜索ETF '{query}' 成功，找到{len(etf_list)}个结果")
            return etf_list[:10]  # 最多返回10个结果
            
        except Exception as e:
            logger.error(f"✗ 搜索ETF '{query}' 失败: {str(e)}")
            return []
    
    def _complete_etf_code(self, etf_code: str) -> str:
        """
        自动补全ETF代码的市场前缀
        
        Args:
            etf_code: ETF代码（不含市场前缀）
            
        Returns:
            str: 完整的ETF代码（含市场前缀）
        """
        # 移除可能存在的前缀或后缀
        etf_code = etf_code.split('.')[-1]
        
        # 判断市场：15/16/18/3开头的是深交所，51/58开头的是上交所
        if etf_code.startswith(('15', '16', '18', '3')):
            return f"SZ.{etf_code}"
        elif etf_code.startswith(('51', '58')):
            return f"SH.{etf_code}"
        else:
            # 默认上交所
            return f"SH.{etf_code}"
    
    def get_security_name(self, code: str) -> Optional[str]:
        """
        轻量级获取证券名称（永久缓存），支持ETF和股票
        
        Args:
            code: 证券代码（不含市场后缀）
            
        Returns:
            str: 证券名称，如果获取失败返回None
        """
        # 1. 先检查永久缓存
        cached_data = self.cache.get_permanent_cache("security_name", code)
        if cached_data:
            logger.info(f"✓ 从永久缓存获取证券 {code} 名称")
            return cached_data
        
        # 2. 缓存未命中，使用富途API获取真实数据
        logger.info(f"→ 永久缓存未命中，使用富途API获取证券 {code} 名称")
        
        try:
            # 补全证券代码，添加市场前缀
            full_code = self._complete_etf_code(code)
            
            # 使用富途API获取股票基本信息，不指定stock_type以支持多种证券类型
            market = ft.Market.US if full_code.startswith('US.') else ft.Market.HK if full_code.startswith('HK.') else ft.Market.SH if full_code.startswith('SH.') else ft.Market.SZ
            code_list = [full_code]  # 使用完整的股票代码（包括市场前缀）
            ret, data = self.quote_ctx.get_stock_basicinfo(
                market=market,
                code_list=code_list
            )
            
            if ret != ft.RET_OK or data.empty:
                logger.error(f"✗ 富途API获取证券 {code} 名称失败: {data}")
                return None
            
            security_name = data.iloc[0].get('name')
            if not security_name:
                logger.error(f"✗ 富途API返回的证券 {code} 名称为空")
                return None
            
            # 3. 成功获取数据，保存到永久缓存
            self.cache.set_permanent_cache("security_name", code, security_name)
            logger.info(f"✓ 证券 {code} 名称获取成功并已永久缓存: {security_name}")
            
            return security_name
            
        except Exception as e:
            logger.error(f"✗ 获取证券 {code} 名称失败: {str(e)}")
            return None
            
    def get_etf_name(self, etf_code: str) -> Optional[str]:
        """
        轻量级获取ETF名称（永久缓存）
        兼容旧版本方法，内部调用get_security_name
        
        Args:
            etf_code: ETF代码（不含市场后缀）
            
        Returns:
            str: ETF名称，如果获取失败返回None
        """
        return self.get_security_name(etf_code)

    def get_trading_calendar(self, start_date: str, end_date: str) -> List[str]:
        """
        获取交易日历（兼容性方法，实际使用TradingDateManager）
        
        Args:
            start_date: 开始日期 (YYYYMMDD格式)
            end_date: 结束日期 (YYYYMMDD格式)
            
        Returns:
            List[str]: 交易日列表
        """
        try:
            # 解析年份范围
            start_year = int(start_date[:4])
            end_year = int(end_date[:4])
            
            all_trading_days = []
            
            # 富途API没有直接的交易日历接口，这里使用模拟数据
            # 实际使用中，建议使用富途API获取历史K线数据，然后提取交易日
            # 为了保持兼容性，这里返回一个模拟的交易日列表
            # 生成从start_date到end_date的所有日期，然后过滤掉周末
            start = datetime.strptime(start_date, '%Y%m%d')
            end = datetime.strptime(end_date, '%Y%m%d')
            delta = end - start
            
            for i in range(delta.days + 1):
                date = start + timedelta(days=i)
                # 只保留周一到周五
                if date.weekday() < 5:
                    all_trading_days.append(date.strftime('%Y%m%d'))
            
            logger.info(f"✓ 获取交易日历成功 ({start_date}~{end_date})，共{len(all_trading_days)}个交易日")
            return all_trading_days
            
        except Exception as e:
            logger.error(f"✗ 获取交易日历失败: {str(e)}")
            return []
    
    def get_cache_info(self) -> Dict:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 缓存统计信息
        """
        return self.cache.get_cache_info()
    
    def get_latest_trading_date(self) -> str:
        """
        获取最近的交易日
        
        Returns:
            str: 最近的交易日 (YYYYMMDD格式)
        """
        # 富途API没有直接获取最近交易日的接口，这里使用当前日期
        # 如果当前日期不是交易日（周末），则返回最近的工作日
        today = datetime.now()
        
        # 如果是周六或周日，返回上周五
        if today.weekday() == 5:  # 周六
            latest = today - timedelta(days=1)
        elif today.weekday() == 6:  # 周日
            latest = today - timedelta(days=2)
        else:
            latest = today
        
        return latest.strftime('%Y%m%d')
