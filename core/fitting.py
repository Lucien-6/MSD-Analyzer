import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

class FittingAnalyzer:
        
    def fit_msd(self, msd_results, dimension, fit_settings):
        """
        拟合MSD曲线
        
        参数:
        msd_results: MSD计算结果
        dimension: 维度
        fit_settings: 拟合设置
        
        返回:
        fitting_results: 拟合结果
        """
        # 获取平均MSD数据
        avg_msd = msd_results['average']
        lag_time = avg_msd['lag_time']
        msd = avg_msd['msd']
        
        # 确定拟合范围
        start_time = fit_settings['start_time']
        
        if fit_settings['auto_fit']:
            try:
                # 自动确定拟合终止时间
                end_time = self._find_best_fit_range(
                    msd_results['rdc']['lag_time'],
                    msd_results['rdc']['rdc'],
                    start_time,
                    fit_settings['r_squared_threshold']
                )
            except Exception as e:
                # 如果自动拟合失败，使用默认终止时间
                end_time = min(start_time * 10, lag_time[-1])
                print(f"自动拟合范围确定失败: {str(e)}，使用默认终止时间: {end_time}")
        else:
            # 使用手动设置的终止时间
            end_time = fit_settings['end_time']
            
        # 确保终止时间不超过数据范围
        end_time = min(end_time, lag_time[-1])
        
        # 选择拟合范围内的数据
        mask = (lag_time >= start_time) & (lag_time <= end_time)
        fit_lag_time = lag_time[mask]
        fit_msd = msd[mask]
        
        if len(fit_lag_time) < 2:
            raise ValueError("拟合范围内的数据点不足，请调整拟合范围")
            
        # 根据选择的模型进行拟合
        try:
            model_type = fit_settings.get('model_type', 'brownian')
            
            if model_type == 'brownian':
                # 布朗运动: MSD = 2*d*D*t
                popt, pcov = curve_fit(
                    lambda t, D: 2 * dimension * D * t,
                    fit_lag_time, fit_msd, p0=[1e-2], bounds=(0, np.inf)
                )
                D = popt[0]
                
                # 计算95%置信区间
                perr = np.sqrt(np.diag(pcov))
                D_err = perr[0]
                D_conf_interval = [D - 1.96 * D_err, D + 1.96 * D_err]
                
                # 计算拟合曲线
                fit_times = np.linspace(0, end_time * 1.2, 100)
                fit_msd_values = 2 * dimension * D * fit_times
                
                # 计算R^2
                residuals = fit_msd - (2 * dimension * D * fit_lag_time)
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((fit_msd - np.mean(fit_msd))**2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                # 整理结果
                fitting_results = {
                    'model': 'brownian',
                    'D': D,
                    'D_err': D_err,
                    'D_conf_interval': D_conf_interval,
                    'V': None,
                    'V_err': None,
                    'V_conf_interval': None,
                    'L': None,
                    'L_err': None,
                    'L_conf_interval': None,
                    'r_squared': r_squared,
                    'fit_times': fit_times,
                    'fit_msd': fit_msd_values,
                    'start_time': start_time,
                    'end_time': end_time
                }
                
            elif model_type == 'drift':
                # 带漂移的布朗运动: MSD = 2*d*D*t + V^2*t^2
                popt, pcov = curve_fit(
                    lambda t, D, V: 2 * dimension * D * t + V**2 * t**2,
                    fit_lag_time, fit_msd, p0=[1e-2, 1e-1], bounds=(0, np.inf)
                )
                D, V = popt
                
                # 计算95%置信区间
                perr = np.sqrt(np.diag(pcov))
                D_err, V_err = perr
                D_conf_interval = [D - 1.96 * D_err, D + 1.96 * D_err]
                V_conf_interval = [V - 1.96 * V_err, V + 1.96 * V_err]
                
                # 计算拟合曲线
                fit_times = np.linspace(0, end_time * 1.2, 100)
                fit_msd_values = 2 * dimension * D * fit_times + V**2 * fit_times**2
                
                # 计算R^2
                residuals = fit_msd - (2 * dimension * D * fit_lag_time + V**2 * fit_lag_time**2)
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((fit_msd - np.mean(fit_msd))**2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                # 整理结果
                fitting_results = {
                    'model': 'drift',
                    'D': D,
                    'D_err': D_err,
                    'D_conf_interval': D_conf_interval,
                    'V': V,
                    'V_err': V_err,
                    'V_conf_interval': V_conf_interval,
                    'L': None,
                    'L_err': None,
                    'L_conf_interval': None,
                    'r_squared': r_squared,
                    'fit_times': fit_times,
                    'fit_msd': fit_msd_values,
                    'start_time': start_time,
                    'end_time': end_time
                }
                
            elif model_type == 'confined':
                # 受限扩散模型: MSD = L^2 * (1 - exp(-4*D*t/L^2))
                # 其中L是约束长度，D是扩散系数
                def confined_model(t, D, L):
                    return L**2 * (1 - np.exp(-2 * dimension * D * t / L**2))
                
                # 初始猜测值：D为布朗运动扩散系数，L为MSD最大值的平方根
                p0 = [1e-2, np.sqrt(np.max(fit_msd))]
                
                popt, pcov = curve_fit(
                    confined_model,
                    fit_lag_time, fit_msd, p0=p0, bounds=(0, np.inf)
                )
                D, L = popt
                
                # 计算95%置信区间
                perr = np.sqrt(np.diag(pcov))
                D_err, L_err = perr
                D_conf_interval = [D - 1.96 * D_err, D + 1.96 * D_err]
                L_conf_interval = [L - 1.96 * L_err, L + 1.96 * L_err]
                
                # 计算拟合曲线
                fit_times = np.linspace(0, end_time * 1.2, 100)
                fit_msd_values = confined_model(fit_times, D, L)
                
                # 计算R^2
                residuals = fit_msd - confined_model(fit_lag_time, D, L)
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((fit_msd - np.mean(fit_msd))**2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                # 整理结果
                fitting_results = {
                    'model': 'confined',
                    'D': D,
                    'D_err': D_err,
                    'D_conf_interval': D_conf_interval,
                    'L': L,
                    'L_err': L_err,
                    'L_conf_interval': L_conf_interval,
                    'V': None,
                    'V_err': None,
                    'V_conf_interval': None,
                    'r_squared': r_squared,
                    'fit_times': fit_times,
                    'fit_msd': fit_msd_values,
                    'start_time': start_time,
                    'end_time': end_time
                }
            else:
                raise ValueError(f"未知的拟合模型类型: {model_type}")
                
        except Exception as e:
            raise ValueError(f"MSD拟合失败: {str(e)}")
        
        return fitting_results
        
    def _find_best_fit_range(self, lag_times, rdc_values, start_time, r_squared_threshold):
        """
        自动寻找最佳拟合区间 - 寻找满足拟合优度阈值的最长区间
        
        参数:
        lag_times: 时间延迟数组
        rdc_values: RDC值数组
        start_time: 起始时间
        r_squared_threshold: R^2阈值
        
        返回:
        end_time: 最佳终止时间
        """
        # 确保输入数据是一维数组
        lag_times = np.array(lag_times)
        rdc_values = np.array(rdc_values)
            
        # 检查数据是否足够
        if len(lag_times) < 3:
            raise ValueError("数据点不足，无法进行自动拟合")
            
        # 找到起始时间对应的索引
        start_idx_array = np.where(lag_times >= start_time)[0]
        if len(start_idx_array) == 0:
            raise ValueError(f"起始时间 {start_time} 超出数据范围")
        start_idx = start_idx_array[0]
        
        # 确保有足够的数据点进行拟合
        if len(lag_times) - start_idx < 2:
            raise ValueError("拟合范围内的数据点不足，请调整起始时间")
        
        # 初始化最佳终止索引 - 默认为起始索引之后的点
        best_end_idx = start_idx + 1
        # 初始化找到的最长区间长度
        max_interval_length = 0
        
        # 尝试不同的终止索引
        for end_idx in range(start_idx + 2, len(lag_times)):
            # 选择当前范围内的数据
            x = lag_times[start_idx:end_idx+1]
            y = rdc_values[start_idx:end_idx+1]
            
            # 计算当前区间长度
            current_interval_length = end_idx - start_idx + 1
            
            # 线性拟合 - 改进异常处理
            try:
                slope, intercept = np.polyfit(x, y, 1)
                
                # 计算拟合值
                y_fit = slope * x + intercept
                
                # 计算R^2
                residuals = y - y_fit
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((y - np.mean(y))**2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                # 如果R^2大于等于阈值且区间长度大于当前最长区间，更新最佳终止索引
                if r_squared >= r_squared_threshold and current_interval_length > max_interval_length:
                    max_interval_length = current_interval_length
                    best_end_idx = end_idx
            except np.linalg.LinAlgError as e:
                # 具体捕获线性代数错误，提供更明确的错误信息
                print(f"拟合区间 [{start_idx}:{end_idx}] 线性拟合失败: {str(e)}")
                continue
            except Exception as e:
                # 捕获其他可能的错误
                print(f"拟合区间 [{start_idx}:{end_idx}] 发生错误: {str(e)}")
                continue
        
        # 如果没有找到满足条件的区间，使用默认的终止索引
        if max_interval_length == 0:
            if len(lag_times) > start_idx + 5:
                best_end_idx = start_idx + 5
            else:
                best_end_idx = len(lag_times) - 1
            print(f"未找到满足R²阈值 {r_squared_threshold} 的区间，使用默认终止索引: {best_end_idx}")
            
        return lag_times[best_end_idx]

    def analyze_scaling(self, msd_results, fit_settings, fitting_results=None):
        """
        进行标度律分析
        
        参数:
        msd_results: MSD计算结果
        fit_settings: 拟合设置
        fitting_results: 如果提供，将使用其中的终止时间
        
        返回:
        scaling_results: 标度律分析结果
        """
        # 获取平均MSD数据
        avg_msd = msd_results['average']
        lag_time = avg_msd['lag_time']
        msd = avg_msd['msd']
        
        # 确定起始时间 - 保持原有逻辑
        start_time = fit_settings['start_time']

        # 如果起始时间为0，找到第一个非零时间点
        if start_time <= 0:
            non_zero_indices = np.where(lag_time > 0)[0]
            if len(non_zero_indices) > 0:
                start_time = lag_time[non_zero_indices[0]]
            else:
                start_time = 1e-6  # 如果没有非零点，使用一个很小的正数
        
        # 确定终止时间 - 优先使用fitting_results中的终止时间
        if fitting_results and 'end_time' in fitting_results:
            end_time = fitting_results['end_time']
            print(f"使用平均MSD拟合的终止时间: {end_time}")
        else:
            # 如果没有提供fitting_results，则使用原来的逻辑确定终止时间
            if fit_settings['auto_fit']:
                try:
                    # 自动确定拟合终止时间
                    end_time = self._find_best_fit_range(
                        msd_results['rdc']['lag_time'],
                        msd_results['rdc']['rdc'],
                        start_time,
                        fit_settings['r_squared_threshold']
                    )
                except Exception as e:
                    # 如果自动拟合失败，使用默认终止时间
                    end_time = min(start_time * 10, lag_time[-1])
                    print(f"自动拟合范围确定失败: {str(e)}，使用默认终止时间: {end_time}")
            else:
                # 使用手动设置的终止时间
                end_time = fit_settings['end_time']
                
        # 确保终止时间不超过数据范围
        end_time = min(end_time, lag_time[-1])
        
        # 选择拟合范围内的数据
        mask = (lag_time >= start_time) & (lag_time <= end_time)
        fit_lag_time = lag_time[mask]
        fit_msd = msd[mask]
        
        if len(fit_lag_time) < 2:
            raise ValueError("拟合范围内的数据点不足，请调整拟合范围")
        try:    
            # 对数变换
            log_time = np.log10(fit_lag_time)
            log_msd = np.log10(fit_msd)
            
            # 线性拟合: log(MSD) = alpha * log(t) + log(K)
            popt, pcov = np.polyfit(log_time, log_msd, 1, cov=True)
            alpha, log_K = popt
            K = 10**log_K

            # 计算95%置信区间
            perr = np.sqrt(np.diag(pcov))
            alpha_err, log_K_err = perr
            
            # 计算alpha的置信区间
            alpha_conf_interval = [alpha - 1.96 * alpha_err, alpha + 1.96 * alpha_err]
            
            # 计算K的置信区间 (需要考虑对数转换)
            K_err = 10**log_K_err
            K_lower = K - 1.96 * K_err
            K_upper = K + 1.96 * K_err
            K_conf_interval = [K_lower, K_upper]
            
            fit_times = np.logspace(np.log10(start_time), np.log10(end_time * 1.2), 100)
            fit_msd_values = K * fit_times ** alpha
            
            # 计算R^2
            y_fit = alpha * log_time + log_K
            residuals = log_msd - y_fit
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((log_msd - np.mean(log_msd))**2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # 整理结果
            scaling_results = {
                'alpha': alpha,
                'alpha_err': alpha_err,
                'alpha_conf_interval': alpha_conf_interval,
                'K': K,
                'K_err': K_err,  
                'K_conf_interval': K_conf_interval,
                'r_squared': r_squared,
                'fit_times': fit_times,
                'fit_msd': fit_msd_values
            }
            return scaling_results
        except Exception as e:
            raise ValueError(f"标度律分析失败: {str(e)}")