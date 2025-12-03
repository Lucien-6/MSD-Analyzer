"""
MSD Analyzer 应用状态管理模块

Author: Lucien
Email: lucien-6@qq.com
Date: 2025-12-03
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class AnalysisSettings:
    """
    分析设置数据类
    
    Attributes
    ----------
    time_unit : str
        时间单位
    space_unit : str
        空间单位
    model_type : str
        扩散模型类型 ('brownian', 'drift', 'confined')
    auto_fit : bool
        是否使用自动拟合
    start_time : float
        拟合起始时间
    end_time : float
        拟合终止时间
    r_squared_threshold : float
        R² 阈值
    """
    time_unit: str = 's'
    space_unit: str = 'μm'
    model_type: str = 'brownian'
    auto_fit: bool = True
    start_time: float = 0.0
    end_time: float = 10.0
    r_squared_threshold: float = 0.95


@dataclass
class AppState:
    """
    应用程序状态管理类
    
    集中管理所有应用状态，包括数据、计算结果和设置。
    
    Attributes
    ----------
    trajectories : Optional[Dict]
        轨迹数据字典，键为粒子ID，值为DataFrame
    dimension : Optional[int]
        轨迹维度（2或3）
    excluded_particles : List[str]
        被排除的粒子ID列表
    msd_results : Optional[Dict]
        MSD计算结果
    fitting_results : Optional[Dict]
        拟合结果
    scaling_results : Optional[Dict]
        标度律分析结果
    settings : AnalysisSettings
        分析设置
    current_file_path : Optional[str]
        当前文件路径
    """
    # 数据状态
    trajectories: Optional[Dict] = None
    dimension: Optional[int] = None
    excluded_particles: List[str] = field(default_factory=list)
    
    # 计算结果
    msd_results: Optional[Dict] = None
    fitting_results: Optional[Dict] = None
    scaling_results: Optional[Dict] = None
    
    # 分析设置
    settings: AnalysisSettings = field(default_factory=AnalysisSettings)
    
    # 文件信息
    current_file_path: Optional[str] = None
    
    def reset(self):
        """重置所有状态到初始值"""
        self.trajectories = None
        self.dimension = None
        self.excluded_particles = []
        self.msd_results = None
        self.fitting_results = None
        self.scaling_results = None
        self.current_file_path = None
    
    def reset_results(self):
        """仅重置计算结果，保留数据"""
        self.msd_results = None
        self.fitting_results = None
        self.scaling_results = None
    
    def has_trajectories(self) -> bool:
        """
        检查是否有轨迹数据
        
        Returns
        -------
        bool
            如果有轨迹数据返回True
        """
        return self.trajectories is not None and len(self.trajectories) > 0
    
    def has_msd_results(self) -> bool:
        """
        检查是否有MSD计算结果
        
        Returns
        -------
        bool
            如果有MSD结果返回True
        """
        return self.msd_results is not None
    
    def has_fitting_results(self) -> bool:
        """
        检查是否有拟合结果
        
        Returns
        -------
        bool
            如果有拟合结果返回True
        """
        return self.fitting_results is not None
    
    def has_scaling_results(self) -> bool:
        """
        检查是否有标度律分析结果
        
        Returns
        -------
        bool
            如果有标度律结果返回True
        """
        return self.scaling_results is not None
    
    def get_active_particles(self) -> List[str]:
        """
        获取未被排除的粒子列表
        
        Returns
        -------
        List[str]
            未被排除的粒子ID列表
        """
        if not self.trajectories:
            return []
        return [pid for pid in self.trajectories.keys() 
                if pid not in self.excluded_particles]
    
    def get_particle_count(self) -> int:
        """
        获取总粒子数量
        
        Returns
        -------
        int
            粒子总数
        """
        if not self.trajectories:
            return 0
        return len(self.trajectories)
    
    def get_active_particle_count(self) -> int:
        """
        获取未被排除的粒子数量
        
        Returns
        -------
        int
            未被排除的粒子数量
        """
        return len(self.get_active_particles())

