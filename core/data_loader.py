import pandas as pd
import os

class DataLoader:
    def __init__(self):
        """
        初始化数据加载器
        
        参数:
        column_mapping: 字典，用于映射自定义列名到标准列名，例如 {'time': 't', 'position_x': 'x'}
        """
        # 默认列名映射
        self.column_mapping = {
            'time': 't',
            'position_x': 'x',
            'position_y': 'y',  
            'position_z': 'z',
            'particle_id': 'particle_id',
            'T': 't',
            'X': 'x',
            'Y': 'y',
            'Z': 'z',
            'ParticleID': 'particle_id',
            'Time': 't',
            'PositionX': 'x',
            'PositionY': 'y',
            'PositionZ': 'z',
            'Particle_ID': 'particle_id',
            'Times': 't',
            'times': 't',
            'Position_X': 'x',
            'Position_Y': 'y',
            'Position_Z': 'z',
            'Particle_id': 'particle_id',
            'Position_x': 'x',
            'Position_y': 'y',
            'Position_z': 'z',
            'Center_X': 'x',
            'Center_Y': 'y',
            'Center_Z': 'z',
            'Center_x': 'x',
            'Center_y': 'y',
            'Center_z': 'z',
            'CenterX': 'x',
            'CenterY': 'y',
            'CenterZ': 'z',
            'center_x': 'x',
            'center_y': 'y',
            'center_z': 'z',
            'ID': 'particle_id',
            'id': 'particle_id',
            'PID': 'particle_id',
            'pid': 'particle_id',
            'Particle': 'particle_id',
        }
        
    def _apply_column_mapping(self, df):
        """
        应用列名映射到DataFrame
        
        参数:
        df: 原始DataFrame
        
        返回:
        mapped_df: 应用列名映射后的DataFrame
        """
        # 创建一个新的DataFrame以避免修改原始数据
        mapped_df = df.copy()
        
        # 应用列名映射
        for custom_col, standard_col in self.column_mapping.items():
            if custom_col in mapped_df.columns and standard_col not in mapped_df.columns:
                mapped_df[standard_col] = mapped_df[custom_col]
                
        return mapped_df
        
    def load_excel(self, file_path):
        """
        从Excel文件加载颗粒轨迹数据
        
        参数:
        file_path: Excel文件路径
        
        返回:
        trajectories: 字典，键为颗粒ID，值为包含轨迹数据的DataFrame
        dimension: 轨迹维度（2或3）
        """
        # 获取所有sheet名称
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names
        
        if not sheet_names:
            raise ValueError("Excel文件中没有数据表")
            
        # 加载第一个sheet以确定维度
        first_sheet = pd.read_excel(file_path, sheet_name=sheet_names[0])
        # 应用列名映射
        first_sheet = self._apply_column_mapping(first_sheet)
        
        # 检查列数确定维度
        if 't' not in first_sheet.columns:
            raise ValueError("数据必须包含't'列表示时间（或通过列名映射提供）")
            
        if 'x' in first_sheet.columns and 'y' in first_sheet.columns and 'z' in first_sheet.columns:
            dimension = 3
            required_columns = ['t', 'x', 'y', 'z']
        elif 'x' in first_sheet.columns and 'y' in first_sheet.columns:
            dimension = 2
            required_columns = ['t', 'x', 'y']
        else:
            raise ValueError("数据格式不正确，必须包含't,x,y'列（二维）或't,x,y,z'列（三维）（或通过列名映射提供）")
            
        # 加载所有sheet的数据
        trajectories = {}
        
        for sheet_name in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            # 应用列名映射
            df = self._apply_column_mapping(df)
            
            # 检查必要的列是否存在
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"数据表'{sheet_name}'缺少必要的列: {col}（或通过列名映射提供）")
                    
            # 存储轨迹数据
            trajectories[sheet_name] = df[required_columns]
            
        return trajectories, dimension
    
    def load_csv(self, file_path):
        """
        从CSV文件加载颗粒轨迹数据
        
        参数:
        file_path: CSV文件路径
        
        返回:
        trajectories: 字典，键为颗粒ID，值为包含轨迹数据的DataFrame
        dimension: 轨迹维度（2或3）
        """
        # 读取CSV文件
        df = pd.read_csv(file_path)
        # 应用列名映射
        df = self._apply_column_mapping(df)
        
        # 检查必要的列是否存在
        if 't' not in df.columns:
            raise ValueError("数据必须包含't'列表示时间（或通过列名映射提供）")
            
        if 'x' in df.columns and 'y' in df.columns and 'z' in df.columns:
            dimension = 3
            required_columns = ['t', 'x', 'y', 'z']
        elif 'x' in df.columns and 'y' in df.columns:
            dimension = 2
            required_columns = ['t', 'x', 'y']
        else:
            raise ValueError("数据格式不正确，必须包含't,x,y'列（二维）或't,x,y,z'列（三维）（或通过列名映射提供）")
        
        # 检查是否有粒子ID列（也考虑映射后的particle_id）
        particle_id_col = None
        if 'particle_id' in df.columns:
            particle_id_col = 'particle_id'
        else:
            # 检查是否有映射到particle_id的列
            for custom_col, standard_col in self.column_mapping.items():
                if standard_col == 'particle_id' and custom_col in df.columns:
                    particle_id_col = custom_col
                    break
        
        if particle_id_col:
            # 按粒子ID分组
            trajectories = {}
            for particle_id, group in df.groupby(particle_id_col):
                trajectories[str(particle_id)] = group[required_columns]
        else:
            # 如果没有粒子ID列，则将所有数据视为单个粒子
            trajectories = {'1': df[required_columns]}
            
        return trajectories, dimension
    
    def load_data(self, file_path):
        """
        根据文件扩展名加载数据
        
        参数:
        file_path: 文件路径
        
        返回:
        trajectories: 字典，键为颗粒ID，值为包含轨迹数据的DataFrame
        dimension: 轨迹维度（2或3）
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.xlsx', '.xls']:
            return self.load_excel(file_path)
        elif file_ext == '.csv':
            return self.load_csv(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}，请使用Excel(.xlsx, .xls)或CSV(.csv)文件")