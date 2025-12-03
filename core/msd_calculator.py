"""
MSD Analyzer MSD 计算模块

Author: Lucien
Email: lucien-6@qq.com
"""
import logging
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

# 获取模块级日志记录器
logger = logging.getLogger(__name__)


class MSDCalculator:
    """
    均方位移 (MSD) 计算器
    
    支持 2D/3D 轨迹数据的 MSD 计算，包含并行计算优化。
    """
    
    def __init__(self):
        """初始化 MSD 计算器"""
        # 确定可用的CPU核心数，留2个核心给系统
        self.n_cores = max(1, multiprocessing.cpu_count() - 2)
        # 标记是否正在计算
        self.is_calculating = False
        
    def calculate(self, trajectories, dimension, excluded_particles=None, 
                  progress_callback=None):
        """
        计算颗粒的均方位移(MSD)
        
        Parameters
        ----------
        trajectories : dict
            轨迹数据字典，键为颗粒ID，值为包含轨迹数据的DataFrame
        dimension : int
            轨迹维度（2或3）
        excluded_particles : list, optional
            要排除的颗粒ID列表
        progress_callback : callable, optional
            进度回调函数，签名为 callback(percent, message)
        
        Returns
        -------
        dict
            包含MSD计算结果的字典，包括:
            - 'individual': 每个颗粒的MSD
            - 'average': 平均MSD
            - 'stats': 统计信息
            - 'rdc': 动态扩散系数
        """
        # 防止重复计算
        if self.is_calculating:
            return None
            
        self.is_calculating = True
        
        try:
            if excluded_particles is None:
                excluded_particles = []
                
            # 过滤排除的颗粒
            filtered_trajectories = {pid: data for pid, data in trajectories.items() 
                                   if pid not in excluded_particles}
            
            if not filtered_trajectories:
                raise ValueError("没有可用的轨迹数据进行计算")
            
            # 报告初始进度
            if progress_callback:
                progress_callback(5, "正在准备数据...")
                
            # 计算每个颗粒的MSD
            individual_msd = {}
            all_lag_times = set()
            
            # 判断是否使用并行计算
            total_computation = sum(len(data) ** 2 for data in filtered_trajectories.values())
            use_parallel = (len(filtered_trajectories) > 10 or total_computation > 100000)
            
            particle_ids = list(filtered_trajectories.keys())
            total_particles = len(particle_ids)
            
            if use_parallel:
                # 使用ThreadPoolExecutor并行计算
                with ThreadPoolExecutor(max_workers=self.n_cores) as executor:
                    # 创建任务
                    future_to_pid = {
                        executor.submit(
                            self._calculate_single_msd_vectorized,
                            data['t'].values,
                            data[['x', 'y']].values if dimension == 2 else data[['x', 'y', 'z']].values
                        ): pid
                        for pid, data in filtered_trajectories.items()
                    }
                    
                    # 收集结果
                    completed = 0
                    for future in as_completed(future_to_pid):
                        pid = future_to_pid[future]
                        try:
                            lag_times, msd_values = future.result()
                            individual_msd[pid] = {
                                'lag_time': lag_times,
                                'msd': msd_values
                            }
                            all_lag_times.update(lag_times)
                        except Exception as e:
                            logger.warning(f"计算粒子 {pid} 的MSD时出错: {str(e)}")
                        
                        # 更新进度
                        completed += 1
                        if progress_callback:
                            percent = 10 + int(70 * completed / total_particles)
                            progress_callback(percent, f"正在计算粒子 MSD ({completed}/{total_particles})...")
            else:
                # 串行计算
                for idx, (particle_id, data) in enumerate(filtered_trajectories.items()):
                    # 获取时间和位置数据
                    times = data['t'].values
                    positions = data[['x', 'y']].values if dimension == 2 else data[['x', 'y', 'z']].values
                    
                    # 计算该颗粒的MSD
                    lag_times, msd_values = self._calculate_single_msd_vectorized(times, positions)
                    
                    individual_msd[particle_id] = {
                        'lag_time': lag_times,
                        'msd': msd_values
                    }
                    
                    # 收集所有出现的lag time
                    all_lag_times.update(lag_times)
                    
                    # 更新进度
                    if progress_callback:
                        percent = 10 + int(70 * (idx + 1) / total_particles)
                        progress_callback(percent, f"正在计算粒子 MSD ({idx + 1}/{total_particles})...")
            
            # 报告进度
            if progress_callback:
                progress_callback(85, "正在计算平均 MSD...")
            
            # 计算平均MSD和标准差
            sorted_lag_times = np.array(sorted(all_lag_times))
            n_times = len(sorted_lag_times)
            avg_msd = np.zeros(n_times)
            std_msd = np.zeros(n_times)
            counts = np.zeros(n_times, dtype=int)
            
            # 创建时间延迟到索引的映射
            lag_time_to_idx = {lag_time: i for i, lag_time in enumerate(sorted_lag_times)}
            
            # 第一遍：计算平均值
            for particle_data in individual_msd.values():
                particle_lag_times = particle_data['lag_time']
                particle_msd = particle_data['msd']
                
                for i, lag_time in enumerate(particle_lag_times):
                    idx = lag_time_to_idx[lag_time]
                    avg_msd[idx] += particle_msd[i]
                    counts[idx] += 1
            
            # 避免除零错误
            valid_indices = counts > 0
            avg_msd[valid_indices] /= counts[valid_indices]
            
            # 第二遍：计算标准差
            sum_sq_diff = np.zeros(n_times)
            for particle_data in individual_msd.values():
                particle_lag_times = particle_data['lag_time']
                particle_msd = particle_data['msd']
                
                for i, lag_time in enumerate(particle_lag_times):
                    idx = lag_time_to_idx[lag_time]
                    sum_sq_diff[idx] += (particle_msd[i] - avg_msd[idx]) ** 2
            
            # 计算标准差 (使用 n-1 作为分母，样本标准差)
            valid_for_std = counts > 1
            std_msd[valid_for_std] = np.sqrt(sum_sq_diff[valid_for_std] / (counts[valid_for_std] - 1))
            # 对于只有一个样本的点，标准差设为0
            std_msd[counts == 1] = 0
            
            # 报告进度
            if progress_callback:
                progress_callback(95, "正在计算 RDC...")
            
            # 计算RDC (Relative Diffusion Coefficient)
            rdc = self._calculate_rdc_vectorized(sorted_lag_times, avg_msd, dimension)
            
            # 整理结果
            msd_results = {
                'individual': individual_msd,
                'average': {
                    'lag_time': sorted_lag_times,
                    'msd': avg_msd,
                    'std': std_msd
                },
                'stats': {
                    'lag_time': sorted_lag_times,
                    'count': counts
                },
                'rdc': {
                    'lag_time': rdc['lag_time'],
                    'rdc': rdc['rdc']
                }
            }
            
            return msd_results
            
        finally:
            # 无论计算成功与否，都重置计算状态
            self.is_calculating = False
    
    def _calculate_single_msd_vectorized(self, times, positions):
        """
        使用向量化操作计算单个颗粒的MSD
        
        Parameters
        ----------
        times : np.ndarray
            时间点数组
        positions : np.ndarray
            位置数组，形状为 (n, 2) 或 (n, 3)
        
        Returns
        -------
        tuple
            (lag_times, msd_values) 时间延迟数组和对应的MSD值数组
        """
        n = len(times)
        
        if n < 2:
            return np.array([]), np.array([])
        
        # 计算所有可能的时间延迟
        lag_times = times[1:] - times[0]
        msd_values = np.zeros(n - 1)
        
        # 向量化计算每个时间延迟的MSD
        for delta in range(1, n):
            # 向量化：一次性计算所有索引差为 delta 的位移
            displacements = positions[delta:] - positions[:-delta]
            # 向量化：计算每个位移的平方和
            squared_displacements = np.sum(displacements ** 2, axis=1)
            # 计算平均MSD
            msd_values[delta - 1] = np.mean(squared_displacements)
        
        # 过滤掉无效值
        valid_indices = msd_values > 0
        return lag_times[valid_indices], msd_values[valid_indices]
    
    def _calculate_rdc_vectorized(self, lag_times, msd_values, dimension):
        """
        使用向量化操作计算动态扩散系数(RDC)
        
        Parameters
        ----------
        lag_times : np.ndarray
            时间延迟数组
        msd_values : np.ndarray
            MSD值数组
        dimension : int
            维度
        
        Returns
        -------
        dict
            包含RDC计算结果的字典
        """
        rdc_values = np.zeros_like(lag_times)
        n = len(lag_times)
        
        if n < 2:
            return {'lag_time': lag_times, 'rdc': rdc_values}
        
        # 对于第一个点，使用前向差分
        rdc_values[0] = (msd_values[1] - msd_values[0]) / (lag_times[1] - lag_times[0])
        
        # 对于中间点，使用中心差分
        if n > 2:
            indices = np.arange(1, n - 1)
            rdc_values[indices] = (msd_values[indices + 1] - msd_values[indices - 1]) / \
                                  (lag_times[indices + 1] - lag_times[indices - 1])
        
        # 对于最后一个点，使用后向差分
        rdc_values[-1] = (msd_values[-1] - msd_values[-2]) / (lag_times[-1] - lag_times[-2])
        
        # 除以2*维度得到RDC
        rdc_values /= (2 * dimension)
        
        return {
            'lag_time': lag_times,
            'rdc': rdc_values
        }
