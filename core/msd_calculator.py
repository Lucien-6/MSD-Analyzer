import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import os

class MSDCalculator:
    def __init__(self):
        # 确定可用的CPU核心数，留2个核心给系统
        self.n_cores = max(1, multiprocessing.cpu_count() - 2)
        # 标记是否正在计算
        self.is_calculating = False
        
    def calculate(self, trajectories, dimension, excluded_particles=None, time_unit='s', space_unit='μm', parent_window=None):
        """
        计算颗粒的均方位移(MSD)
        
        参数:
        trajectories: 字典，键为颗粒ID，值为包含轨迹数据的DataFrame
        dimension: 轨迹维度（2或3）
        excluded_particles: 要排除的颗粒ID列表
        time_unit: 时间单位
        space_unit: 空间单位
        parent_window: 父窗口引用，防止创建新窗口
        
        返回:
        msd_results: 包含MSD计算结果的字典
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
                
            # 计算每个颗粒的MSD - 使用并行计算
            individual_msd = {}
            all_lag_times = set()
            
            # 判断是否使用并行计算 - 考虑粒子数量和轨迹长度
            # 计算总计算量：粒子数 × 平均轨迹长度的平方
            total_computation = 0
            for data in filtered_trajectories.values():
                traj_len = len(data)
                total_computation += traj_len * traj_len
            
            # 设置并行计算阈值 - 当总计算量大或粒子数量多时使用并行
            use_parallel = (len(filtered_trajectories) > 10 or total_computation > 100000)
            
            if use_parallel:
                # 使用ThreadPoolExecutor代替ProcessPoolExecutor，避免创建多个进程
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
                            print(f"计算粒子 {pid} 的MSD时出错: {str(e)}")
            else:
                # 串行计算
                for particle_id, data in filtered_trajectories.items():
                    # 获取时间和位置数据
                    times = data['t'].values
                    positions = data[['x', 'y']].values if dimension == 2 else data[['x', 'y', 'z']].values
                    
                    # 计算该颗粒的MSD - 使用向量化方法
                    lag_times, msd_values = self._calculate_single_msd_vectorized(times, positions)
                    
                    individual_msd[particle_id] = {
                        'lag_time': lag_times,
                        'msd': msd_values
                    }
                    
                    # 收集所有出现的lag time
                    all_lag_times.update(lag_times)
                
            # 计算平均MSD - 使用字典加速查找
            sorted_lag_times = np.array(sorted(all_lag_times))
            avg_msd = np.zeros(len(sorted_lag_times))
            counts = np.zeros(len(sorted_lag_times), dtype=int)
            
            # 创建时间延迟到索引的映射，加速查找
            lag_time_to_idx = {lag_time: i for i, lag_time in enumerate(sorted_lag_times)}
            
            for particle_data in individual_msd.values():
                particle_lag_times = particle_data['lag_time']
                particle_msd = particle_data['msd']
                
                # 使用向量化操作更新平均MSD和计数
                for i, lag_time in enumerate(particle_lag_times):
                    idx = lag_time_to_idx[lag_time]
                    avg_msd[idx] += particle_msd[i]
                    counts[idx] += 1
            
            # 避免除零错误
            valid_indices = counts > 0
            avg_msd[valid_indices] /= counts[valid_indices]
            
            # 计算RDC (Relative Diffusion Coefficient)
            rdc = self._calculate_rdc_vectorized(sorted_lag_times, avg_msd, dimension)
            
            # 整理结果（不包含单位信息）
            msd_results = {
                'individual': individual_msd,
                'average': {
                    'lag_time': sorted_lag_times,
                    'msd': avg_msd
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
        
        参数:
        times: 时间点数组
        positions: 位置数组，形状为(n, 2)或(n, 3)
        
        返回:
        lag_times: 时间延迟数组
        msd_values: 对应的MSD值数组
        """
        n = len(times)
        
        # 预分配结果数组
        max_delta = n - 1
        lag_times = np.zeros(max_delta)
        msd_values = np.zeros(max_delta)
        
        # 计算所有可能的时间延迟
        lag_times = times[1:] - times[0]
        
        # 对每个时间延迟计算MSD
        for i in range(1, n):
            # 计算所有可能的位移平方
            displacements = []
            
            # 使用向量化操作计算位移
            for j in range(n - i):
                # 计算位移平方
                displacement = positions[j + i] - positions[j]
                squared_displacement = np.sum(displacement ** 2)
                displacements.append(squared_displacement)
            
            # 计算平均MSD
            if displacements:
                msd_values[i-1] = np.mean(displacements)
            
        # 过滤掉未计算的值
        valid_indices = msd_values > 0
        return lag_times[valid_indices], msd_values[valid_indices]
    
    def _calculate_rdc_vectorized(self, lag_times, msd_values, dimension):
        """
        使用向量化操作计算动态扩散系数(RDC)
        
        参数:
        lag_times: 时间延迟数组
        msd_values: MSD值数组
        dimension: 维度
        
        返回:
        rdc_data: 包含RDC计算结果的字典
        """
        # 预分配结果数组
        rdc_values = np.zeros_like(lag_times)
        n = len(lag_times)
        
        if n < 2:
            return {'lag_time': lag_times, 'rdc': rdc_values}
        
        # 对于第一个点，使用前向差分
        rdc_values[0] = (msd_values[1] - msd_values[0]) / (lag_times[1] - lag_times[0])
        
        # 对于中间点，使用中心差分 - 向量化操作
        if n > 2:
            indices = np.arange(1, n-1)
            rdc_values[indices] = (msd_values[indices+1] - msd_values[indices-1]) / (lag_times[indices+1] - lag_times[indices-1])
        
        # 对于最后一个点，使用后向差分
        rdc_values[-1] = (msd_values[-1] - msd_values[-2]) / (lag_times[-1] - lag_times[-2])
        
        # 除以2*维度得到RDC
        rdc_values /= (2 * dimension)
        
        return {
            'lag_time': lag_times,
            'rdc': rdc_values
        }