import os
import re
import numpy as np
import pandas as pd
from datetime import datetime

def natural_sort_key(s):
    """实现自然排序的键函数，将字符串中的数字部分作为数字处理"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def ensure_directory(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def generate_output_filename(base_dir, prefix, extension):
    """生成带有时间戳的输出文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension}"
    return os.path.join(base_dir, filename)


def export_results_to_excel(output_path, msd_results, fitting_results, scaling_results, settings):
    """将分析结果导出到Excel文件"""
    # 创建Excel写入器
    with pd.ExcelWriter(output_path) as writer:
        model_type_map = {
            'brownian': '简单扩散(纯布朗运动)',
            'drift': '定向扩散(漂移速度恒定)',
            'confined': '受限扩散(圆内或球内)',
            'active': '活性细菌扩散(Run-and-Tumble)'
        }
        model_name = model_type_map.get(settings['model_type'], settings['model_type'])
        # 导出设置信息
        settings_df = pd.DataFrame({
            '参数': ['时间单位', '空间单位', '扩散模型', '拟合模式', '起始时间', '终止时间', 'R²阈值'],
            '值': [
                settings['time_unit'],
                settings['space_unit'],
                model_name,
                '自动拟合' if settings.get('auto_fit', True) else '手动拟合',
                f"{settings['start_time']} {settings['time_unit']}",
                f"{settings['end_time']} {settings['time_unit']}",
                settings.get('r_squared_threshold') if settings.get('auto_fit', True) else None
            ]
        })
        settings_df.to_excel(writer, sheet_name='分析设置', index=False)
        
        # 导出MSD数据
        avg_msd = msd_results['average']
        stats = msd_results['stats']
        
        msd_df = pd.DataFrame({
            f"时间延迟 ({settings['time_unit']})": avg_msd['lag_time'],
            f"平均MSD ({settings['space_unit']}²)": avg_msd['msd'],
            f"RDC ({settings['space_unit']}²/{settings['time_unit']})": msd_results['rdc']['rdc'],
            "数据点数": stats['count']
        })
        msd_df.to_excel(writer, sheet_name='平均MSD数据', index=False)
        
        # 导出拟合结果
        model_type = settings.get('model_type', 'brownian')
        
        # 准备拟合结果数据
        fit_data = {
            "参数": [],
            "值": [],
            "95%置信区间": [],
            "单位": []
        }
        
        # 添加扩散系数
        D_conf = fitting_results.get('D_conf_interval', [0, 0])
        D_conf_str = f"[{D_conf[0]:.6e}, {D_conf[1]:.6e}]" if 'D_conf_interval' in fitting_results else "N/A"
        
        fit_data["参数"].append("扩散系数 (D)")
        fit_data["值"].append(f"{fitting_results['D']:.6e}")
        fit_data["95%置信区间"].append(D_conf_str)
        fit_data["单位"].append(f"{settings['space_unit']}²/{settings['time_unit']}")
        
        # 根据模型类型添加特定参数
        if model_type == 'drift':
            # 定速漂移模型
            V_conf = fitting_results.get('V_conf_interval', [0, 0])
            V_conf_str = f"[{V_conf[0]:.6e}, {V_conf[1]:.6e}]" if 'V_conf_interval' in fitting_results else "N/A"
            
            fit_data["参数"].append("漂移速度 (V)")
            fit_data["值"].append(f"{fitting_results.get('V', 0):.6e}")
            fit_data["95%置信区间"].append(V_conf_str)
            fit_data["单位"].append(f"{settings['space_unit']}/{settings['time_unit']}")
        elif model_type == 'confined':
            # 受限扩散模型
            L_conf = fitting_results.get('L_conf_interval', [0, 0])
            L_conf_str = f"[{L_conf[0]:.6e}, {L_conf[1]:.6e}]" if 'L_conf_interval' in fitting_results else "N/A"
            
            fit_data["参数"].append("限制范围 (L)")
            fit_data["值"].append(f"{fitting_results.get('L', 0):.6e}")
            fit_data["95%置信区间"].append(L_conf_str)
            fit_data["单位"].append(f"{settings['space_unit']}")
        elif model_type == 'active':
            # 活性细菌扩散模型
            tau_r_conf = fitting_results.get('tau_r_conf_interval', [0, 0])
            tau_r_conf_str = f"[{tau_r_conf[0]:.6e}, {tau_r_conf[1]:.6e}]" if 'tau_r_conf_interval' in fitting_results else "N/A"
            
            fit_data["参数"].append("重定向时间 (τ_r)")
            fit_data["值"].append(f"{fitting_results.get('tau_r', 0):.6e}")
            fit_data["95%置信区间"].append(tau_r_conf_str)
            fit_data["单位"].append(f"{settings['time_unit']}")
        else:
            # 自由扩散模型
            pass
        
        # 添加通用参数
        fit_data["参数"].append("拟合优度 (R²)")
        fit_data["值"].append(f"{fitting_results['r_squared']:.6f}")
        fit_data["95%置信区间"].append("N/A")
        fit_data["单位"].append("")
        
        fit_data["参数"].append("拟合起始时间")
        fit_data["值"].append(f"{fitting_results['start_time']:.4f}")
        fit_data["95%置信区间"].append("N/A")
        fit_data["单位"].append(f"{settings['time_unit']}")
        
        fit_data["参数"].append("拟合终止时间")
        fit_data["值"].append(f"{fitting_results['end_time']:.4f}")
        fit_data["95%置信区间"].append("N/A")
        fit_data["单位"].append(f"{settings['time_unit']}")
        
        fit_df = pd.DataFrame(fit_data)
        fit_df.to_excel(writer, sheet_name='平均MSD拟合结果', index=False)
        
        # 导出标度律分析结果
        if scaling_results and 'alpha' in scaling_results:
            alpha = scaling_results['alpha']
            
            # 确定扩散类型
            if alpha < 0.9:
                interpretation = "亚扩散 (Sub-diffusion)"
            elif 0.9 <= alpha <= 1.1:
                interpretation = "正常扩散 (Normal diffusion)"
            else:
                interpretation = "超扩散 (Super-diffusion)"
            
            # 获取置信区间
            alpha_conf = scaling_results.get('alpha_conf_interval', [0, 0])
            alpha_conf_str = f"[{alpha_conf[0]:.6f}, {alpha_conf[1]:.6f}]" if 'alpha_conf_interval' in scaling_results else "N/A"
            
            K_conf = scaling_results.get('K_conf_interval', [0, 0])
            K_conf_str = f"[{K_conf[0]:.6e}, {K_conf[1]:.6e}]" if 'K_conf_interval' in scaling_results else "N/A"
            
            scaling_data = {
                "参数": ["标度指数 (α)", "系数 (K)", "拟合优度 (R²)", "扩散类型"],
                "值": [
                    f"{alpha:.6f}",
                    f"{scaling_results['K']:.6e}",
                    f"{scaling_results['r_squared']:.6f}",
                    interpretation
                ],
                "95%置信区间": [
                    alpha_conf_str,
                    K_conf_str,
                    "N/A",
                    "N/A"
                ],
                "单位": [
                    "",
                    f"{settings['space_unit']}²/{settings['time_unit']}^α",
                    "",
                    ""
                ]
            }
            
            scaling_df = pd.DataFrame(scaling_data)
            scaling_df.to_excel(writer, sheet_name='标度律分析结果', index=False)
            
            # 导出标度律拟合曲线数据
            scaling_curve_df = pd.DataFrame({
                f'时间延迟 ({settings["time_unit"]})': scaling_results['fit_times'],
                f'拟合MSD ({settings["space_unit"]}²)': scaling_results['fit_msd']
            })
            scaling_curve_df.to_excel(writer, sheet_name='标度律拟合曲线', index=False)
        
        # 导出拟合曲线数据
        fit_curve_df = pd.DataFrame({
            f'时间延迟 ({settings["time_unit"]})': fitting_results['fit_times'],
            f'拟合MSD ({settings["space_unit"]}²)': fitting_results['fit_msd']
        })
        fit_curve_df.to_excel(writer, sheet_name='平均MSD拟合曲线', index=False)

        # 导出每个颗粒的MSD（按颗粒ID自然排序）
        sorted_particle_ids = sorted(msd_results['individual'].keys(), key=natural_sort_key)
        for particle_id in sorted_particle_ids:
            data = msd_results['individual'][particle_id]
            particle_df = pd.DataFrame({
                f"时间延迟 ({settings['time_unit']})": data['lag_time'],
                f"MSD ({settings['space_unit']}²)": data['msd']
            })
            particle_df.to_excel(writer, sheet_name=f'{particle_id}', index=False)
        
    return output_path