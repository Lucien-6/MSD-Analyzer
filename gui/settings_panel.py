from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QComboBox, QDoubleSpinBox, QCheckBox, 
                            QGroupBox, QListWidget, QAbstractItemView, QPushButton,
                            QRadioButton, QButtonGroup, QSpinBox)
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utils.helpers import natural_sort_key 

class SettingsPanel(QWidget):
    # 定义信号：当排除颗粒列表变化时发射
    excluded_particles_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        # 设置固定宽度为500像素
        self.setFixedWidth(500)
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # 单位设置组
        units_group = self._create_group_with_bold_title("单位设置")
        units_layout = QFormLayout()
        
        self.time_unit_combo = QComboBox()
        self.time_unit_combo.addItems(["μs", "ms", "s", "min", "h"])
        self.time_unit_combo.setCurrentText("s")
        
        self.space_unit_combo = QComboBox()
        self.space_unit_combo.addItems(["m", "mm", "μm", "nm"])
        self.space_unit_combo.setCurrentText("μm")

        # 为下拉框设置统一字体
        font = QFont("Times New Roman", 9)
        self.time_unit_combo.setFont(font)
        self.space_unit_combo.setFont(font)
        
        units_layout.addRow("时间单位:", self.time_unit_combo)
        units_layout.addRow("空间单位:", self.space_unit_combo)
        units_group.setLayout(units_layout)
        
        # 模型选择组
        model_group = self._create_group_with_bold_title("模型选择")
        model_layout = QFormLayout()  # 改为QFormLayout
        
        self.model_combo = QComboBox()
        self.model_combo.addItem("简单扩散(纯布朗运动)", "brownian")
        self.model_combo.addItem("定向扩散(漂移速度恒定)", "drift")
        self.model_combo.addItem("受限扩散(圆内或球内)", "confined")
        self.model_combo.addItem("活性细菌扩散(Run-and-Tumble)", "active")
        self.model_combo.setCurrentIndex(0)
        self.model_combo.currentIndexChanged.connect(self._update_fit_controls)
        
        # 为模型选择下拉框设置与单位设置相同的字体
        font = QFont("Times New Roman", 9)
        self.model_combo.setFont(font)
        
        # 使用addRow方法添加标签和下拉框
        model_layout.addRow("扩散模型:", self.model_combo)
        model_group.setLayout(model_layout)
        
        # 拟合设置组
        fit_group = self._create_group_with_bold_title("拟合设置")
        fit_layout = QVBoxLayout()
        
        # 拟合模式选择
        fit_mode_layout = QHBoxLayout()
        fit_mode_layout.addWidget(QLabel("拟合模式:"))
        
        self.fit_mode_group = QButtonGroup(self)
        self.auto_fit_radio = QRadioButton("自动拟合")
        self.manual_fit_radio = QRadioButton("手动拟合")
        self.auto_fit_radio.setChecked(True)  # 默认自动拟合
        
        self.fit_mode_group.addButton(self.auto_fit_radio)
        self.fit_mode_group.addButton(self.manual_fit_radio)
        
        fit_mode_layout.addWidget(self.auto_fit_radio)
        fit_mode_layout.addWidget(self.manual_fit_radio)
        
        # 拟合参数
        fit_params_layout = QFormLayout()
        
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0, 10000)
        self.start_time_spin.setValue(0)
        self.start_time_spin.setSuffix(" s")
        
        self.end_time_spin = QDoubleSpinBox()
        self.end_time_spin.setRange(0, 10000)
        self.end_time_spin.setValue(10)
        self.end_time_spin.setSuffix(" s")
        self.end_time_spin.setEnabled(False)  # 自动拟合模式下禁用
        
        self.r_squared_threshold_spin = QDoubleSpinBox()
        self.r_squared_threshold_spin.setRange(0, 1)
        self.r_squared_threshold_spin.setValue(0.9500)
        self.r_squared_threshold_spin.setSingleStep(0.01)
        self.r_squared_threshold_spin.setDecimals(4)  # 设置精度为四位小数
        
        fit_params_layout.addRow("起始时间:", self.start_time_spin)
        fit_params_layout.addRow("终止时间:", self.end_time_spin)
        fit_params_layout.addRow("拟合优度阈值:", self.r_squared_threshold_spin)
        
        fit_layout.addLayout(fit_mode_layout)
        fit_layout.addLayout(fit_params_layout)
        fit_group.setLayout(fit_layout)
        
        # 颗粒选择组
        particles_group = self._create_group_with_bold_title("颗粒筛选")
        particles_layout = QVBoxLayout()

        # 设置颗粒选择组的尺寸策略，使其能在垂直方向扩展
        particles_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        self.particles_list = QListWidget()
        self.particles_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.particles_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.particles_list.setMinimumHeight(200)
        
        particles_buttons_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("全选")
        self.deselect_all_btn = QPushButton("全不选")
        
        particles_buttons_layout.addWidget(self.select_all_btn)
        particles_buttons_layout.addWidget(self.deselect_all_btn)
        
        particles_layout.addWidget(QLabel("选择要排除的颗粒:"))
        particles_layout.addWidget(self.particles_list)
        particles_layout.addLayout(particles_buttons_layout)
        particles_group.setLayout(particles_layout)
        
        # 添加所有组到主布局
        main_layout.addWidget(units_group, 0)
        main_layout.addWidget(model_group, 0)  # 替换原来的gravity_group
        main_layout.addWidget(fit_group, 0)
        main_layout.addWidget(particles_group, 1)
        # main_layout.addStretch()
        
        # 连接信号和槽
        self.auto_fit_radio.toggled.connect(self._update_fit_controls)
        self.manual_fit_radio.toggled.connect(self._update_fit_controls)
        self.select_all_btn.clicked.connect(self._select_all_particles)
        self.deselect_all_btn.clicked.connect(self._deselect_all_particles)
        self.time_unit_combo.currentTextChanged.connect(self._update_time_unit)
        
        # 连接颗粒列表选择变化信号
        self.particles_list.itemSelectionChanged.connect(self._on_particle_selection_changed)
        
        # 初始化控件状态
        # 删除对_update_gravity_controls的调用
        self._update_fit_controls()

    def _create_group_with_bold_title(self, title):
        """创建带有加粗居中标题的组"""
        group = QGroupBox(title)
        group.setAlignment(Qt.AlignCenter)
        
        # 为组标题设置粗体字体
        font = QFont()
        font.setBold(True)
        group.setFont(font)
        
        # 使用样式表确保只有标题加粗，内容不加粗
        group.setStyleSheet("QGroupBox { font-weight: bold; } QGroupBox::title { font-weight: bold; } QGroupBox * { font-weight: normal; }")
        
        return group
    
    def _update_fit_controls(self):
        """更新拟合相关控件的启用状态"""
        auto_mode = self.auto_fit_radio.isChecked()
        
        # 获取当前选择的模型
        model_type = self.model_combo.currentData()
        
        # 如果是自由扩散或受限扩散模型，禁用自动拟合
        if model_type == "confined":
            self.manual_fit_radio.setChecked(True)
            self.auto_fit_radio.setEnabled(False)
            auto_mode = False
        else:
            self.auto_fit_radio.setEnabled(True)
        
        # 更新控件状态
        self.end_time_spin.setEnabled(not auto_mode)
        self.r_squared_threshold_spin.setEnabled(auto_mode)
        
    def _select_all_particles(self):
        """选择所有颗粒"""
        for i in range(self.particles_list.count()):
            self.particles_list.item(i).setSelected(True)
            
    def _deselect_all_particles(self):
        """取消选择所有颗粒"""
        for i in range(self.particles_list.count()):
            self.particles_list.item(i).setSelected(False)

    def _update_time_unit(self, unit):
        """更新时间单位显示（仅显示，不转换数值）"""
        # 更新单位显示
        self.start_time_spin.setSuffix(f" {unit}")
        self.end_time_spin.setSuffix(f" {unit}")
        
    def update_particle_list(self, particle_ids):
        """更新颗粒列表（使用自然排序）"""
        self.particles_list.clear()
        # 使用自然排序
        sorted_ids = sorted(particle_ids, key=natural_sort_key)
        self.particles_list.addItems(sorted_ids)
        
    def get_excluded_particles(self):
        """获取被排除的颗粒ID列表"""
        excluded = []
        for i in range(self.particles_list.count()):
            item = self.particles_list.item(i)
            if item.isSelected():
                excluded.append(item.text())
        return excluded
    
    def _on_particle_selection_changed(self):
        """当颗粒选择发生变化时触发"""
        excluded = self.get_excluded_particles()
        # 发射信号通知主窗口
        self.excluded_particles_changed.emit(excluded)
        
    def get_time_unit(self):
        """获取时间单位"""
        return self.time_unit_combo.currentText()
        
    def get_space_unit(self):
        """获取空间单位"""
        return self.space_unit_combo.currentText()
        

    def get_fit_settings(self):
        """获取拟合设置"""
        settings = {
            'auto_fit': self.auto_fit_radio.isChecked(),
            'start_time': self.start_time_spin.value(),
            'end_time': self.end_time_spin.value(),
            'r_squared_threshold': self.r_squared_threshold_spin.value(),
            'model_type': self.model_combo.currentData(),
            'time_unit': self.get_time_unit(),
            'space_unit': self.get_space_unit()
        }
        return settings

    def validate_settings(self):
        """验证设置参数是否合理"""
        # 验证起始时间小于终止时间
        if self.start_time_spin.value() >= self.end_time_spin.value() and not self.auto_fit_radio.isChecked():
            return False, "起始时间必须小于终止时间"
        
        # 验证R^2阈值在合理范围内
        if self.r_squared_threshold_spin.value() <= 0 or self.r_squared_threshold_spin.value() > 1:
            return False, "拟合优度阈值必须在(0,1]范围内"
        
        return True, ""