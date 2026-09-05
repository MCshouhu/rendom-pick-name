#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QSoundEffect

# ==================== 配置管理 ====================

class ConfigManager:
    """配置文件管理器"""
    _cache = {}
    
    @staticmethod
    def load_json(filename, default=None):
        if filename in ConfigManager._cache:
            return ConfigManager._cache[filename]
            
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data:
                        ConfigManager._cache[filename] = data
                        return data
        except Exception as e:
            print(f"加载配置文件 {filename} 失败: {e}")
            
        ConfigManager._cache[filename] = default
        return default
    
    @staticmethod
    def save_json(filename, data):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            ConfigManager._cache[filename] = data
            return True
        except Exception as e:
            print(f"保存配置文件 {filename} 失败: {e}")
            return False

# ==================== 颜色管理 ====================

class ColorManager:
    """颜色管理器"""
    def __init__(self):
        self.color_rules = self.load_color_rules()
        self.student_colors = self.load_student_colors()
        self.preset_colors = self.load_preset_colors()
        
    def load_color_rules(self):
        default_rules = [
            {
                'name': '金色',
                'color': '#FFD700',
                'background': '#FFF8DC',
                'threshold': 2.0,
                'operator': '>=',  # 比较运算符
                'enabled': True
            },
            {
                'name': '紫色',
                'color': '#9C27B0',
                'background': '#F3E5F5',
                'threshold': 1.5,
                'operator': '>=',
                'enabled': True
            }
        ]
        return ConfigManager.load_json('color_rules.json', default_rules)
    
    def save_color_rules(self, rules):
        self.color_rules = rules
        ConfigManager.save_json('color_rules.json', rules)
        
    def load_student_colors(self):
        return ConfigManager.load_json('student_colors.json', {})
    
    def save_student_colors(self, student_colors):
        self.student_colors = student_colors
        ConfigManager.save_json('student_colors.json', student_colors)
        
    def load_preset_colors(self):
        default_presets = [
            {'name': '金色', 'color': '#FFD700', 'background': '#FFF8DC'},
            {'name': '紫色', 'color': '#9C27B0', 'background': '#F3E5F5'},
            {'name': '红色', 'color': '#F44336', 'background': '#FFEBEE'},
            {'name': '蓝色', 'color': '#2196F3', 'background': '#E3F2FD'},
            {'name': '绿色', 'color': '#4CAF50', 'background': '#E8F5E9'},
            {'name': '橙色', 'color': '#FF9800', 'background': '#FFF3E0'},
            {'name': '粉色', 'color': '#E91E63', 'background': '#FCE4EC'},
            {'name': '青色', 'color': '#00BCD4', 'background': '#E0F7FA'}
        ]
        return ConfigManager.load_json('preset_colors.json', default_presets)
    
    def save_preset_colors(self, presets):
        self.preset_colors = presets
        ConfigManager.save_json('preset_colors.json', presets)
        
    def get_student_color(self, group, student):
        if group in self.student_colors:
            if student in self.student_colors[group]:
                return self.student_colors[group][student]
        return None
        
    def set_student_color(self, group, student, color_info):
        if group not in self.student_colors:
            self.student_colors[group] = {}
        self.student_colors[group][student] = color_info
        
    def remove_student_color(self, group, student):
        if group in self.student_colors:
            if student in self.student_colors[group]:
                del self.student_colors[group][student]
                
    def get_color_for_student(self, group, student, probability):
        student_color = self.get_student_color(group, student)
        if student_color:
            return student_color
        return self.get_color_for_probability(probability)
        
    def compare_probability(self, probability, threshold, operator):
        """比较概率和阈值"""
        if operator == '>=':
            return probability >= threshold
        elif operator == '>':
            return probability > threshold
        elif operator == '<=':
            return probability <= threshold
        elif operator == '<':
            return probability < threshold
        elif operator == '==':
            return abs(probability - threshold) < 0.01
        elif operator == '!=':
            return abs(probability - threshold) >= 0.01
        return False
        
    def get_color_for_probability(self, probability):
        """根据概率获取颜色规则"""
        sorted_rules = sorted(
            [rule for rule in self.color_rules if rule.get('enabled', True)],
            key=lambda x: x.get('threshold', 0),
            reverse=True
        )
        
        for rule in sorted_rules:
            operator = rule.get('operator', '>=')
            threshold = rule.get('threshold', 0)
            if self.compare_probability(probability, threshold, operator):
                return rule
        return None
        
    def get_style_for_student(self, group, student, probability, font_size="80px", padding="30px"):
        color_rule = self.get_color_for_student(group, student, probability)
        
        if color_rule:
            return f"""
                font-size: {font_size};
                font-weight: bold;
                color: {color_rule['color']};
                background-color: {color_rule['background']};
                border: 4px solid {color_rule['color']};
                border-radius: 15px;
                padding: {padding};
            """
        else:
            return f"""
                font-size: {font_size};
                font-weight: bold;
                color: #4CAF50;
                background-color: #f0f8f0;
                border: 4px solid #4CAF50;
                border-radius: 15px;
                padding: {padding};
            """

# ==================== 颜色选择对话框 ====================

class ColorPickerDialog(QDialog):
    """颜色选择对话框"""
    def __init__(self, color_manager, parent=None):
        super().__init__(parent)
        self.color_manager = color_manager
        self.selected_color = None
        self.setWindowTitle('选择颜色')
        self.setFixedSize(400, 500)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        title = QLabel('🎨 选择预设颜色')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        grid_layout = QGridLayout(container)
        grid_layout.setSpacing(10)
        
        presets = self.color_manager.preset_colors
        
        for i, preset in enumerate(presets):
            row = i // 3
            col = i % 3
            
            color_btn = QPushButton(preset['name'])
            color_btn.setFixedSize(100, 60)
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {preset['background']};
                    color: {preset['color']};
                    border: 2px solid {preset['color']};
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border-width: 3px;
                }}
            """)
            color_btn.clicked.connect(lambda checked, p=preset: self.select_preset(p))
            grid_layout.addWidget(color_btn, row, col)
            
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)
        
        custom_btn = QPushButton('🎨 自定义颜色...')
        custom_btn.clicked.connect(self.custom_color)
        custom_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        layout.addWidget(custom_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #9e9e9e;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        layout.addWidget(cancel_btn)
        
    def select_preset(self, preset):
        self.selected_color = preset
        self.accept()
        
    def custom_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            bg_color = QColorDialog.getColor(QColor('#FFFFFF'), self, '选择背景色')
            if bg_color.isValid():
                self.selected_color = {
                    'name': '自定义',
                    'color': color.name(),
                    'background': bg_color.name()
                }
                self.accept()

# ==================== 声音管理 ====================

class SoundManager:
    """声音管理器"""
    def __init__(self):
        self.settings = self.load_settings()
        self.sound_effect = None
        
    def load_settings(self):
        default = {
            'enabled': True,
            'use_system_sound': True,
            'file': '',
            'volume': 0.5
        }
        return ConfigManager.load_json('sound_settings.json', default)
    
    def save_settings(self, settings):
        self.settings = settings
        ConfigManager.save_json('sound_settings.json', settings)
        
    def set_volume(self, volume):
        self.settings['volume'] = volume / 100.0
        if self.sound_effect:
            self.sound_effect.setVolume(self.settings['volume'])
        
    def play(self):
        if not self.settings.get('enabled', True):
            return
            
        try:
            if self.settings.get('use_system_sound', True):
                QApplication.beep()
            else:
                sound_file = self.settings.get('file', '')
                if sound_file and os.path.exists(sound_file):
                    if not self.sound_effect:
                        self.sound_effect = QSoundEffect()
                        self.sound_effect.setVolume(self.settings.get('volume', 0.5))
                    self.sound_effect.setSource(QUrl.fromLocalFile(sound_file))
                    self.sound_effect.play()
                else:
                    QApplication.beep()
        except:
            try:
                QApplication.beep()
            except:
                pass

# ==================== UI组件 ====================

class CollapsibleBox(QWidget):
    """可折叠容器"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.toggle_button = QToolButton()
        self.toggle_button.setStyleSheet("""
            QToolButton {
                font-size: 14px;
                font-weight: bold;
                border: none;
                padding: 5px;
            }
        """)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.on_toggle)
        
        self.content_area = QWidget()
        self.content_area.setVisible(False)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        
    def on_toggle(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.content_area.setVisible(checked)
        
    def set_content_layout(self, layout):
        self.content_area.setLayout(layout)

# ==================== 声音设置对话框 ====================

class SoundSettingsDialog(QDialog):
    """提示音设置对话框"""
    def __init__(self, sound_manager, parent=None):
        super().__init__(parent)
        self.sound_manager = sound_manager
        self.setWindowTitle('提示音设置')
        self.setMinimumSize(500, 450)
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel('🔊 提示音设置')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.enable_checkbox = QCheckBox('启用提示音')
        self.enable_checkbox.setChecked(self.sound_manager.settings.get('enabled', True))
        self.enable_checkbox.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.enable_checkbox)
        
        sound_type_group = QGroupBox('声音类型')
        sound_type_layout = QVBoxLayout()
        
        self.system_sound_radio = QRadioButton('使用系统提示音')
        self.system_sound_radio.setChecked(self.sound_manager.settings.get('use_system_sound', True))
        sound_type_layout.addWidget(self.system_sound_radio)
        
        self.custom_sound_radio = QRadioButton('使用自定义声音文件')
        self.custom_sound_radio.setChecked(not self.sound_manager.settings.get('use_system_sound', True))
        sound_type_layout.addWidget(self.custom_sound_radio)
        
        sound_type_group.setLayout(sound_type_layout)
        layout.addWidget(sound_type_group)
        
        file_group = QGroupBox('自定义声音文件')
        file_layout = QVBoxLayout()
        
        file_path_layout = QHBoxLayout()
        self.file_label = QLabel(os.path.basename(self.sound_manager.settings.get('file', '')) if self.sound_manager.settings.get('file', '') else '未选择文件')
        self.file_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f9f9f9;
                font-size: 12px;
            }
        """)
        self.file_label.setWordWrap(True)
        file_path_layout.addWidget(self.file_label, 1)
        
        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(self.browse_file)
        browse_btn.setFixedWidth(80)
        file_path_layout.addWidget(browse_btn)
        
        file_layout.addLayout(file_path_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        volume_group = QGroupBox('音量控制')
        volume_layout = QVBoxLayout()
        
        volume_slider_layout = QHBoxLayout()
        volume_label = QLabel('音量:')
        volume_slider_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.sound_manager.settings.get('volume', 0.5) * 100))
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_slider_layout.addWidget(self.volume_slider, 1)
        
        self.volume_value_label = QLabel(f"{self.volume_slider.value()}%")
        self.volume_value_label.setMinimumWidth(50)
        self.volume_value_label.setAlignment(Qt.AlignRight)
        volume_slider_layout.addWidget(self.volume_value_label)
        
        volume_layout.addLayout(volume_slider_layout)
        
        preset_layout = QHBoxLayout()
        preset_label = QLabel('预设:')
        preset_layout.addWidget(preset_label)
        
        for value in [25, 50, 75, 100]:
            preset_btn = QPushButton(f'{value}%')
            preset_btn.setFixedWidth(60)
            preset_btn.clicked.connect(lambda checked, v=value: self.set_volume_preset(v))
            preset_layout.addWidget(preset_btn)
        
        preset_layout.addStretch()
        volume_layout.addLayout(preset_layout)
        
        volume_group.setLayout(volume_layout)
        layout.addWidget(volume_group)
        
        test_btn = QPushButton('🔊 测试声音')
        test_btn.clicked.connect(self.test_sound)
        test_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        layout.addWidget(test_btn)
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #9e9e9e;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择声音文件', '', 
            '声音文件 (*.wav);;所有文件 (*.*)'
        )
        if file_path:
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setToolTip(file_path)
            
    def on_volume_changed(self, value):
        self.volume_value_label.setText(f"{value}%")
        self.sound_manager.set_volume(value)
        
    def set_volume_preset(self, value):
        self.volume_slider.setValue(value)
        
    def test_sound(self):
        temp_settings = self.sound_manager.settings.copy()
        
        self.sound_manager.settings['enabled'] = self.enable_checkbox.isChecked()
        self.sound_manager.settings['use_system_sound'] = self.system_sound_radio.isChecked()
        if self.custom_sound_radio.isChecked():
            self.sound_manager.settings['file'] = self.file_label.toolTip() if self.file_label.toolTip() else ''
        
        self.sound_manager.play()
        self.sound_manager.settings = temp_settings
        
    def save_settings(self):
        settings = {
            'enabled': self.enable_checkbox.isChecked(),
            'use_system_sound': self.system_sound_radio.isChecked(),
            'file': self.file_label.toolTip() if self.custom_sound_radio.isChecked() else '',
            'volume': self.volume_slider.value() / 100.0
        }
        self.sound_manager.save_settings(settings)
        QMessageBox.information(self, '成功', '设置已保存')
        self.accept()

# ==================== 学生管理对话框 ====================

class StudentManagerDialog(QDialog):
    """学生管理对话框"""
    def __init__(self, student_groups, parent=None):
        super().__init__(parent)
        self.student_groups = student_groups
        self.setWindowTitle('学生名单管理')
        self.setFixedSize(600, 550)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel('选择分组:'))
        self.group_combo = QComboBox()
        self.group_combo.addItems(self.student_groups.keys())
        self.group_combo.currentTextChanged.connect(self.load_students)
        group_layout.addWidget(self.group_combo)
        group_layout.addStretch()
        layout.addLayout(group_layout)
        
        self.student_list = QListWidget()
        layout.addWidget(self.student_list)
        
        add_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('输入学生姓名')
        self.name_input.returnPressed.connect(self.add_student)
        add_layout.addWidget(self.name_input)
        
        add_btn = QPushButton('添加')
        add_btn.clicked.connect(self.add_student)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)
        
        batch_layout = QHBoxLayout()
        self.batch_input = QTextEdit()
        self.batch_input.setPlaceholderText('批量添加（每行一个名字）')
        self.batch_input.setMaximumHeight(60)
        batch_layout.addWidget(self.batch_input)
        
        batch_btn = QPushButton('批量添加')
        batch_btn.clicked.connect(self.batch_add_students)
        batch_layout.addWidget(batch_btn)
        layout.addLayout(batch_layout)
        
        file_layout = QHBoxLayout()
        
        read_txt_btn = QPushButton('📄 读取TXT文件')
        read_txt_btn.clicked.connect(self.read_txt_file)
        file_layout.addWidget(read_txt_btn)
        
        read_csv_btn = QPushButton('📊 读取CSV文件')
        read_csv_btn.clicked.connect(self.read_csv_file)
        file_layout.addWidget(read_csv_btn)
        
        file_layout.addStretch()
        layout.addLayout(file_layout)
        
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton('删除选中')
        delete_btn.clicked.connect(self.delete_student)
        btn_layout.addWidget(delete_btn)
        
        clear_btn = QPushButton('清空名单')
        clear_btn.clicked.connect(self.clear_students)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.load_students()
        
    def load_students(self):
        self.student_list.clear()
        current_group = self.group_combo.currentText()
        if current_group in self.student_groups:
            for student in self.student_groups[current_group]:
                self.student_list.addItem(student)
                
    def add_student(self):
        name = self.name_input.text().strip()
        if name:
            current_group = self.group_combo.currentText()
            if current_group not in self.student_groups:
                self.student_groups[current_group] = []
            if name not in self.student_groups[current_group]:
                self.student_groups[current_group].append(name)
                self.student_list.addItem(name)
                self.name_input.clear()
            else:
                QMessageBox.warning(self, '警告', '该学生已存在！')
                
    def batch_add_students(self):
        text = self.batch_input.toPlainText().strip()
        if text:
            names = [name.strip() for name in text.split('\n') if name.strip()]
            self.add_students_to_group(names)
            self.batch_input.clear()
            
    def read_txt_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择TXT文件', '', '文本文件 (*.txt);;所有文件 (*.*)'
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    names = [line.strip() for line in content.split('\n') if line.strip()]
                    self.add_students_to_group(names)
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        content = f.read()
                        names = [line.strip() for line in content.split('\n') if line.strip()]
                        self.add_students_to_group(names)
                except Exception as e:
                    QMessageBox.warning(self, '错误', f'读取文件失败: {str(e)}')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'读取文件失败: {str(e)}')
                
    def read_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择CSV文件', '', 'CSV文件 (*.csv);;所有文件 (*.*)'
        )
        if file_path:
            try:
                import csv
                names = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row:
                            name = row[0].strip()
                            if name:
                                names.append(name)
                self.add_students_to_group(names)
            except Exception as e:
                QMessageBox.warning(self, '错误', f'读取CSV文件失败: {str(e)}')
                
    def add_students_to_group(self, names):
        current_group = self.group_combo.currentText()
        if current_group not in self.student_groups:
            self.student_groups[current_group] = []
            
        added_count = 0
        skipped_count = 0
        
        for name in names:
            if name and name not in self.student_groups[current_group]:
                self.student_groups[current_group].append(name)
                self.student_list.addItem(name)
                added_count += 1
            else:
                skipped_count += 1
                
        message = f'成功添加 {added_count} 名学生'
        if skipped_count > 0:
            message += f'\n跳过 {skipped_count} 名重复学生'
        QMessageBox.information(self, '完成', message)
            
    def delete_student(self):
        current_row = self.student_list.currentRow()
        if current_row >= 0:
            current_group = self.group_combo.currentText()
            if current_group in self.student_groups and current_row < len(self.student_groups[current_group]):
                name = self.student_groups[current_group][current_row]
                reply = QMessageBox.question(self, '确认删除', 
                                           f'确定要删除 {name} 吗？',
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    del self.student_groups[current_group][current_row]
                    self.student_list.takeItem(current_row)
                    
    def clear_students(self):
        current_group = self.group_combo.currentText()
        reply = QMessageBox.question(self, '确认清空', 
                                   f'确定要清空 {current_group} 组的所有学生吗？',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if current_group in self.student_groups:
                self.student_groups[current_group].clear()
            self.student_list.clear()

# ==================== 概率设置对话框 ====================

class ProbabilityDialog(QDialog):
    """概率设置对话框"""
    def __init__(self, student_groups, probabilities, color_manager, parent=None):
        super().__init__(parent)
        self.student_groups = student_groups
        self.probabilities = probabilities
        self.color_manager = color_manager
        self.setWindowTitle('概率设置')
        self.setMinimumSize(700, 750)
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        tab_widget = QTabWidget()
        
        # 概率设置标签页
        prob_tab = QWidget()
        prob_layout = QVBoxLayout(prob_tab)
        
        info_label = QLabel('设置每个学生的抽取概率（0.1-10.0）')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        prob_layout.addWidget(info_label)
        
        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel('分组:'))
        self.group_combo = QComboBox()
        self.group_combo.addItems(self.student_groups.keys())
        self.group_combo.currentTextChanged.connect(self.load_probabilities)
        group_layout.addWidget(self.group_combo)
        group_layout.addStretch()
        prob_layout.addLayout(group_layout)
        
        self.prob_table = QTableWidget()
        self.prob_table.setColumnCount(4)
        self.prob_table.setHorizontalHeaderLabels(['学生姓名', '概率倍数', '颜色', '单独颜色'])
        self.prob_table.horizontalHeader().setStretchLastSection(True)
        self.prob_table.setColumnWidth(0, 150)
        self.prob_table.setColumnWidth(1, 80)
        self.prob_table.setColumnWidth(2, 80)
        self.prob_table.setColumnWidth(3, 100)
        self.prob_table.itemChanged.connect(self.on_probability_changed)
        prob_layout.addWidget(self.prob_table)
        
        quick_layout = QHBoxLayout()
        
        equal_btn = QPushButton('平均概率')
        equal_btn.clicked.connect(self.set_equal_probability)
        quick_layout.addWidget(equal_btn)
        
        random_btn = QPushButton('随机概率')
        random_btn.clicked.connect(self.set_random_probability)
        quick_layout.addWidget(random_btn)
        
        prob_layout.addLayout(quick_layout)
        
        # 颜色规则标签页
        color_tab = QWidget()
        color_layout = QVBoxLayout(color_tab)
        
        color_info = QLabel('设置概率条件对应的显示颜色')
        color_info.setAlignment(Qt.AlignCenter)
        color_info.setStyleSheet("font-size: 12px; color: #666; margin: 5px;")
        color_layout.addWidget(color_info)
        
        self.rules_container = QWidget()
        self.rules_layout = QVBoxLayout(self.rules_container)
        self.rules_layout.setSpacing(5)
        
        self.load_color_rules()
        
        color_scroll = QScrollArea()
        color_scroll.setWidgetResizable(True)
        color_scroll.setWidget(self.rules_container)
        color_layout.addWidget(color_scroll)
        
        add_btn = QPushButton('➕ 添加颜色规则')
        add_btn.clicked.connect(self.add_color_rule)
        color_layout.addWidget(add_btn)
        
        preset_layout = QHBoxLayout()
        preset_label = QLabel('快速添加:')
        preset_layout.addWidget(preset_label)
        
        gold_btn = QPushButton('金色')
        gold_btn.clicked.connect(lambda: self.add_preset_rule('金色', '#FFD700', '#FFF8DC', 2.0, '>='))
        gold_btn.setStyleSheet("background-color: #FFD700; color: #333; padding: 5px; border-radius: 3px;")
        preset_layout.addWidget(gold_btn)
        
        purple_btn = QPushButton('紫色')
        purple_btn.clicked.connect(lambda: self.add_preset_rule('紫色', '#9C27B0', '#F3E5F5', 1.5, '>='))
        purple_btn.setStyleSheet("background-color: #9C27B0; color: white; padding: 5px; border-radius: 3px;")
        preset_layout.addWidget(purple_btn)
        
        red_btn = QPushButton('红色')
        red_btn.clicked.connect(lambda: self.add_preset_rule('红色', '#F44336', '#FFEBEE', 3.0, '>='))
        red_btn.setStyleSheet("background-color: #F44336; color: white; padding: 5px; border-radius: 3px;")
        preset_layout.addWidget(red_btn)
        
        preset_layout.addStretch()
        color_layout.addLayout(preset_layout)
        
        tab_widget.addTab(prob_tab, '概率设置')
        tab_widget.addTab(color_tab, '颜色规则')
        
        main_layout.addWidget(tab_widget)
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存全部设置')
        save_btn.clicked.connect(self.save_all_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        btn_layout.addWidget(save_btn)
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #9e9e9e;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        btn_layout.addWidget(close_btn)
        
        main_layout.addLayout(btn_layout)
        
        self.load_probabilities()
        
    def load_probabilities(self):
        self.prob_table.blockSignals(True)
        self.prob_table.setRowCount(0)
        current_group = self.group_combo.currentText()
        
        if current_group not in self.probabilities:
            self.probabilities[current_group] = {}
            
        students = self.student_groups.get(current_group, [])
        self.prob_table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            if student not in self.probabilities[current_group]:
                self.probabilities[current_group][student] = 1.0
                
            name_item = QTableWidgetItem(student)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.prob_table.setItem(row, 0, name_item)
            
            prob_value = self.probabilities[current_group][student]
            prob_item = QTableWidgetItem(str(prob_value))
            self.prob_table.setItem(row, 1, prob_item)
            
            color_item = QTableWidgetItem()
            color_item.setFlags(color_item.flags() & ~Qt.ItemIsEditable)
            
            student_color = self.color_manager.get_student_color(current_group, student)
            if student_color:
                color_item.setText(student_color.get('name', '自定义'))
                color_item.setForeground(QBrush(QColor(student_color['color'])))
                color_item.setBackground(QBrush(QColor(student_color['background'])))
            else:
                color_rule = self.color_manager.get_color_for_probability(prob_value)
                if color_rule:
                    color_item.setText(color_rule['name'])
                    color_item.setForeground(QBrush(QColor(color_rule['color'])))
                    color_item.setBackground(QBrush(QColor(color_rule['background'])))
                else:
                    color_item.setText('默认')
                    color_item.setForeground(QBrush(QColor('#4CAF50')))
                    color_item.setBackground(QBrush(QColor('#f0f8f0')))
                    
            self.prob_table.setItem(row, 2, color_item)
            
            if student_color:
                color_btn = QPushButton('清除颜色')
                color_btn.clicked.connect(lambda checked, r=row, s=student: self.clear_student_color(r, s))
            else:
                color_btn = QPushButton('设置颜色')
                color_btn.clicked.connect(lambda checked, r=row, s=student: self.set_student_color(r, s))
                
            self.prob_table.setCellWidget(row, 3, color_btn)
            
        self.prob_table.blockSignals(False)
        
    def on_probability_changed(self, item):
        if item.column() == 1:
            try:
                prob_value = float(item.text())
                prob_value = max(0.1, min(10.0, prob_value))
                
                row = item.row()
                student = self.prob_table.item(row, 0).text()
                current_group = self.group_combo.currentText()
                
                color_item = self.prob_table.item(row, 2)
                
                student_color = self.color_manager.get_student_color(current_group, student)
                if student_color:
                    color_item.setText(student_color.get('name', '自定义'))
                    color_item.setForeground(QBrush(QColor(student_color['color'])))
                    color_item.setBackground(QBrush(QColor(student_color['background'])))
                else:
                    color_rule = self.color_manager.get_color_for_probability(prob_value)
                    if color_rule:
                        color_item.setText(color_rule['name'])
                        color_item.setForeground(QBrush(QColor(color_rule['color'])))
                        color_item.setBackground(QBrush(QColor(color_rule['background'])))
                    else:
                        color_item.setText('默认')
                        color_item.setForeground(QBrush(QColor('#4CAF50')))
                        color_item.setBackground(QBrush(QColor('#f0f8f0')))
                    
            except ValueError:
                pass
                
    def set_student_color(self, row, student):
        current_group = self.group_combo.currentText()
        
        dialog = ColorPickerDialog(self.color_manager, self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_color:
            color_info = dialog.selected_color
            self.color_manager.set_student_color(current_group, student, color_info)
            
            color_item = self.prob_table.item(row, 2)
            color_item.setText(color_info.get('name', '自定义'))
            color_item.setForeground(QBrush(QColor(color_info['color'])))
            color_item.setBackground(QBrush(QColor(color_info['background'])))
            
            button = self.prob_table.cellWidget(row, 3)
            if button:
                button.setText('清除颜色')
                button.clicked.disconnect()
                button.clicked.connect(lambda checked, r=row, s=student: self.clear_student_color(r, s))
                
    def clear_student_color(self, row, student):
        current_group = self.group_combo.currentText()
        self.color_manager.remove_student_color(current_group, student)
        
        prob_value = float(self.prob_table.item(row, 1).text())
        color_item = self.prob_table.item(row, 2)
        
        color_rule = self.color_manager.get_color_for_probability(prob_value)
        if color_rule:
            color_item.setText(color_rule['name'])
            color_item.setForeground(QBrush(QColor(color_rule['color'])))
            color_item.setBackground(QBrush(QColor(color_rule['background'])))
        else:
            color_item.setText('默认')
            color_item.setForeground(QBrush(QColor('#4CAF50')))
            color_item.setBackground(QBrush(QColor('#f0f8f0')))
            
        button = self.prob_table.cellWidget(row, 3)
        if button:
            button.setText('设置颜色')
            button.clicked.disconnect()
            button.clicked.connect(lambda checked, r=row, s=student: self.set_student_color(r, s))
                
    def load_color_rules(self):
        while self.rules_layout.count():
            item = self.rules_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for rule in self.color_manager.color_rules:
            self.add_color_rule_widget(rule)
            
    def add_color_rule_widget(self, rule=None):
        rule_widget = QWidget()
        rule_layout = QHBoxLayout(rule_widget)
        rule_layout.setContentsMargins(5, 2, 5, 2)
        
        # 启用复选框
        enabled_checkbox = QCheckBox()
        enabled_checkbox.setChecked(rule.get('enabled', True) if rule else True)
        rule_layout.addWidget(enabled_checkbox)
        
        # 颜色名称
        name_edit = QLineEdit()
        name_edit.setPlaceholderText('名称')
        name_edit.setText(rule.get('name', '') if rule else '')
        name_edit.setFixedWidth(70)
        rule_layout.addWidget(name_edit)
        
        # 颜色选择按钮
        color_btn = QPushButton()
        color_btn.setFixedSize(25, 25)
        color_btn.setStyleSheet(f"background-color: {rule.get('color', '#FFD700') if rule else '#FFD700'}; border: 1px solid #ddd; border-radius: 3px;")
        color_btn.clicked.connect(lambda: self.choose_color(color_btn))
        rule_layout.addWidget(color_btn)
        
        # 背景色选择按钮
        bg_btn = QPushButton()
        bg_btn.setFixedSize(25, 25)
        bg_btn.setStyleSheet(f"background-color: {rule.get('background', '#FFF8DC') if rule else '#FFF8DC'}; border: 1px solid #ddd; border-radius: 3px;")
        bg_btn.clicked.connect(lambda: self.choose_color(bg_btn))
        rule_layout.addWidget(bg_btn)
        
        # 比较运算符选择
        operator_combo = QComboBox()
        operator_combo.addItems(['>=', '>', '<=', '<', '==', '!='])
        operator_combo.setCurrentText(rule.get('operator', '>=') if rule else '>=')
        operator_combo.setFixedWidth(60)
        rule_layout.addWidget(operator_combo)
        
        # 阈值输入
        threshold_spinbox = QDoubleSpinBox()
        threshold_spinbox.setRange(0.1, 10.0)
        threshold_spinbox.setValue(rule.get('threshold', 2.0) if rule else 2.0)
        threshold_spinbox.setSingleStep(0.1)
        threshold_spinbox.setSuffix(' 倍')
        threshold_spinbox.setFixedWidth(70)
        rule_layout.addWidget(threshold_spinbox)
        
        # 删除按钮
        delete_btn = QPushButton('✕')
        delete_btn.setFixedSize(25, 25)
        delete_btn.clicked.connect(lambda: self.delete_color_rule(rule_widget))
        rule_layout.addWidget(delete_btn)
        
        self.rules_layout.addWidget(rule_widget)
        
    def choose_color(self, button):
        color = QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ddd; border-radius: 3px;")
            
    def delete_color_rule(self, rule_widget):
        self.rules_layout.removeWidget(rule_widget)
        rule_widget.deleteLater()
        
    def add_color_rule(self):
        self.add_color_rule_widget()
        
    def add_preset_rule(self, name, color, background, threshold, operator='>='):
        rule = {
            'name': name,
            'color': color,
            'background': background,
            'threshold': threshold,
            'operator': operator,
            'enabled': True
        }
        self.add_color_rule_widget(rule)
        
    def save_color_rules(self):
        rules = []
        
        for i in range(self.rules_layout.count()):
            item = self.rules_layout.itemAt(i)
            if item.widget():
                rule_widget = item.widget()
                rule_layout = rule_widget.layout()
                
                enabled_checkbox = rule_layout.itemAt(0).widget()
                name_edit = rule_layout.itemAt(1).widget()
                color_btn = rule_layout.itemAt(2).widget()
                bg_btn = rule_layout.itemAt(3).widget()
                operator_combo = rule_layout.itemAt(4).widget()
                threshold_spinbox = rule_layout.itemAt(5).widget()
                
                color_style = color_btn.styleSheet()
                color = color_style.split('background-color:')[1].split(';')[0].strip()
                
                bg_style = bg_btn.styleSheet()
                background = bg_style.split('background-color:')[1].split(';')[0].strip()
                
                rule = {
                    'name': name_edit.text() or f'规则{i+1}',
                    'color': color,
                    'background': background,
                    'threshold': threshold_spinbox.value(),
                    'operator': operator_combo.currentText(),
                    'enabled': enabled_checkbox.isChecked()
                }
                rules.append(rule)
                
        self.color_manager.save_color_rules(rules)
        
    def save_all_settings(self):
        current_group = self.group_combo.currentText()
        if current_group not in self.probabilities:
            self.probabilities[current_group] = {}
            
        students = self.student_groups.get(current_group, [])
        
        for row, student in enumerate(students):
            prob_item = self.prob_table.item(row, 1)
            if prob_item:
                try:
                    prob_value = float(prob_item.text())
                    prob_value = max(0.1, min(10.0, prob_value))
                    self.probabilities[current_group][student] = round(prob_value, 1)
                    prob_item.setText(str(round(prob_value, 1)))
                except ValueError:
                    QMessageBox.warning(self, '错误', f'学生 {student} 的概率输入无效')
                    return
                    
        ConfigManager.save_json('probabilities.json', self.probabilities)
        self.save_color_rules()
        self.color_manager.save_student_colors(self.color_manager.student_colors)
        
        QMessageBox.information(self, '成功', '所有设置已保存')
        
    def set_equal_probability(self):
        current_group = self.group_combo.currentText()
        if current_group not in self.probabilities:
            self.probabilities[current_group] = {}
            
        students = self.student_groups.get(current_group, [])
        for student in students:
            self.probabilities[current_group][student] = 1.0
        self.load_probabilities()
        
    def set_random_probability(self):
        current_group = self.group_combo.currentText()
        if current_group not in self.probabilities:
            self.probabilities[current_group] = {}
            
        students = self.student_groups.get(current_group, [])
        for student in students:
            self.probabilities[current_group][student] = round(random.uniform(0.5, 2.0), 1)
        self.load_probabilities()

# ==================== 主窗口 ====================

class RandomNamePicker(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.sound_manager = SoundManager()
        self.color_manager = ColorManager()
        self.student_groups = self.load_students()
        self.probabilities = self.load_probabilities()
        
        self.history_records = []
        self.current_group = "全部学生"
        self.is_multi_draw = False
        self.multi_draw_count = 0
        self.multi_draw_results = []
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.roll_name)
        
        self.auto_stop_timer = QTimer()
        self.auto_stop_timer.timeout.connect(self.stop_roll)
        
        self.initUI()
        
    def load_students(self):
        default_groups = {
            "全部学生": ["张三", "李四", "王五", "赵六", "钱七", 
                        "孙八", "周九", "吴十", "郑冬", "冯夏",
                        "陈春", "褚秋", "卫东", "蒋南", "沈西"],
            "男生": ["张三", "李四", "王五", "赵六", "钱七", 
                    "孙八", "周九", "吴十"],
            "女生": ["郑冬", "冯夏", "陈春", "褚秋", "卫东", 
                    "蒋南", "沈西"]
        }
        return ConfigManager.load_json('students.json', default_groups)
        
    def load_probabilities(self):
        return ConfigManager.load_json('probabilities.json', {})
        
    def get_student_probability(self, student):
        prob = 1.0
        if self.current_group in self.probabilities:
            if student in self.probabilities[self.current_group]:
                prob = float(self.probabilities[self.current_group][student])
        return prob
        
    def initUI(self):
        self.setWindowTitle('随机点名器')
        self.setFixedSize(600, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        title_label = QLabel('🎯 随机点名器')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel('选择分组:'))
        
        self.group_combo = QComboBox()
        self.group_combo.addItems(self.student_groups.keys())
        self.group_combo.currentTextChanged.connect(self.change_group)
        group_layout.addWidget(self.group_combo)
        
        self.count_label = QLabel(f'({len(self.student_groups.get(self.current_group, []))}人)')
        group_layout.addWidget(self.count_label)
        
        group_layout.addStretch()
        
        manage_btn = QPushButton('👥 名单管理')
        manage_btn.clicked.connect(self.manage_students)
        group_layout.addWidget(manage_btn)
        
        prob_btn = QPushButton('⚖️ 概率设置')
        prob_btn.clicked.connect(self.manage_probabilities)
        group_layout.addWidget(prob_btn)
        
        sound_btn = QPushButton('🔊 提示音设置')
        sound_btn.clicked.connect(self.manage_sound)
        group_layout.addWidget(sound_btn)
        
        layout.addLayout(group_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 4px solid #4CAF50;
                border-radius: 20px;
            }
        """)
        
        self.result_container = QWidget()
        self.result_container.setStyleSheet("background-color: white;")
        self.result_layout = QGridLayout(self.result_container)
        self.result_layout.setSpacing(15)
        self.result_layout.setContentsMargins(30, 30, 30, 30)
        
        self.name_label = QLabel('准备点名')
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("""
            font-size: 60px;
            font-weight: bold;
            color: #333;
            background-color: transparent;
            border: none;
            padding: 30px;
        """)
        self.result_layout.addWidget(self.name_label, 0, 0, 1, 3)
        
        self.scroll_area.setWidget(self.result_container)
        layout.addWidget(self.scroll_area, 1)
        
        settings_layout = QHBoxLayout()
        
        settings_layout.addWidget(QLabel('连抽:'))
        self.multi_checkbox = QCheckBox('启用')
        settings_layout.addWidget(self.multi_checkbox)
        
        self.multi_spinbox = QSpinBox()
        self.multi_spinbox.setRange(1, 12)
        self.multi_spinbox.setValue(1)
        self.multi_spinbox.setSuffix(' 人')
        settings_layout.addWidget(self.multi_spinbox)
        
        settings_layout.addSpacing(20)
        
        settings_layout.addWidget(QLabel('自动停止:'))
        self.auto_stop_checkbox = QCheckBox('启用')
        self.auto_stop_checkbox.setChecked(True)
        settings_layout.addWidget(self.auto_stop_checkbox)
        
        self.auto_stop_time = QDoubleSpinBox()
        self.auto_stop_time.setRange(0.1, 10.0)
        self.auto_stop_time.setValue(1.0)
        self.auto_stop_time.setSingleStep(0.1)
        self.auto_stop_time.setDecimals(1)
        self.auto_stop_time.setSuffix(' 秒')
        settings_layout.addWidget(self.auto_stop_time)
        
        settings_layout.addStretch()
        layout.addLayout(settings_layout)
        
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton('🎲 开始点名')
        self.start_btn.clicked.connect(self.start_roll)
        self.start_btn.setStyleSheet(self.get_button_style('#4CAF50', '#45a049'))
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('⏹ 停止')
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_roll)
        self.stop_btn.setStyleSheet(self.get_button_style('#f44336', '#da190b'))
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        history_box = CollapsibleBox("📝 历史记录 (点击展开)")
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        
        clear_btn = QPushButton('清空记录')
        clear_btn.clicked.connect(self.clear_history)
        history_layout.addWidget(clear_btn)
        
        history_box.set_content_layout(history_layout)
        layout.addWidget(history_box)
        
    def get_button_style(self, color, hover_color):
        return f"""
            QPushButton {{
                font-size: 18px;
                padding: 15px;
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """
        
    def manage_students(self):
        dialog = StudentManagerDialog(self.student_groups, self)
        dialog.exec_()
        self.group_combo.clear()
        self.group_combo.addItems(self.student_groups.keys())
        self.update_count_label()
        ConfigManager.save_json('students.json', self.student_groups)
        
    def manage_probabilities(self):
        dialog = ProbabilityDialog(self.student_groups, self.probabilities, self.color_manager, self)
        dialog.exec_()
        
    def manage_sound(self):
        dialog = SoundSettingsDialog(self.sound_manager, self)
        dialog.exec_()
        
    def get_weighted_student(self):
        current_students = self.student_groups.get(self.current_group, [])
        if not current_students:
            return None
            
        weights = []
        for student in current_students:
            weights.append(max(0.1, self.get_student_probability(student)))
            
        return random.choices(current_students, weights=weights)[0]
        
    def clear_result_layout(self):
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def change_group(self, group_name):
        self.current_group = group_name
        self.update_count_label()
        self.clear_result_layout()
        self.name_label = QLabel('准备点名')
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("""
            font-size: 60px;
            font-weight: bold;
            color: #333;
            background-color: transparent;
            border: none;
            padding: 30px;
        """)
        self.result_layout.addWidget(self.name_label, 0, 0, 1, 3)
        
    def update_count_label(self):
        count = len(self.student_groups.get(self.current_group, []))
        self.count_label.setText(f'({count}人)')
        
    def start_roll(self):
        if not self.student_groups.get(self.current_group, []):
            QMessageBox.warning(self, '警告', f'{self.current_group}组没有学生！')
            return
            
        if self.multi_checkbox.isChecked():
            self.is_multi_draw = True
            self.multi_draw_count = self.multi_spinbox.value()
            self.multi_draw_results = []
            
            group_size = len(self.student_groups.get(self.current_group, []))
            if self.multi_draw_count > group_size:
                QMessageBox.warning(self, '警告', 
                                  f'连抽人数({self.multi_draw_count})超过组内人数({group_size})！')
                return
        else:
            self.is_multi_draw = False
            
        self.timer.start(50)
        self.set_ui_enabled(False)
        
        if self.auto_stop_checkbox.isChecked():
            auto_stop_ms = int(self.auto_stop_time.value() * 1000)
            self.auto_stop_timer.start(auto_stop_ms)
            
    def stop_roll(self):
        self.timer.stop()
        self.auto_stop_timer.stop()
        self.set_ui_enabled(True)
        
        if self.is_multi_draw:
            self.handle_multi_draw()
        else:
            selected_name = self.get_weighted_student()
            if selected_name:
                self.show_result(selected_name)
                self.add_to_history(selected_name)
                self.sound_manager.play()
                
    def set_ui_enabled(self, enabled):
        self.start_btn.setEnabled(enabled)
        self.stop_btn.setEnabled(not enabled)
        self.group_combo.setEnabled(enabled)
        self.multi_checkbox.setEnabled(enabled)
        self.multi_spinbox.setEnabled(enabled)
        self.auto_stop_checkbox.setEnabled(enabled)
        self.auto_stop_time.setEnabled(enabled)
        
    def show_result(self, name):
        self.clear_result_layout()
        result_label = QLabel(name)
        result_label.setAlignment(Qt.AlignCenter)
        
        probability = self.get_student_probability(name)
        style = self.color_manager.get_style_for_student(self.current_group, name, probability)
        result_label.setStyleSheet(style)
        
        self.result_layout.addWidget(result_label, 0, 0, 1, 3)
        
    def handle_multi_draw(self):
        current_students = self.student_groups.get(self.current_group, []).copy()
        
        for i in range(self.multi_draw_count):
            if current_students:
                weights = []
                for student in current_students:
                    weights.append(max(0.1, self.get_student_probability(student)))
                    
                name = random.choices(current_students, weights=weights)[0]
                self.multi_draw_results.append(name)
                current_students.remove(name)
                
        if self.multi_draw_results:
            self.show_multi_results(self.multi_draw_results)
            for name in self.multi_draw_results:
                self.add_to_history(name, is_multi=True)
            self.sound_manager.play()
            
    def show_multi_results(self, results):
        self.clear_result_layout()
        
        if len(results) <= 3:
            font_size = "36px"
            padding = "20px"
        elif len(results) <= 6:
            font_size = "28px"
            padding = "15px"
        else:
            font_size = "22px"
            padding = "10px"
            
        for i, name in enumerate(results):
            row = i // 3
            col = i % 3
            
            name_label = QLabel(name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setWordWrap(True)
            
            probability = self.get_student_probability(name)
            style = self.color_manager.get_style_for_student(self.current_group, name, probability, font_size, padding)
            name_label.setStyleSheet(style)
            
            self.result_layout.addWidget(name_label, row, col)
            
    def roll_name(self):
        name = self.get_weighted_student()
        if name:
            self.clear_result_layout()
            self.name_label = QLabel(name)
            self.name_label.setAlignment(Qt.AlignCenter)
            
            probability = self.get_student_probability(name)
            color_rule = self.color_manager.get_color_for_student(self.current_group, name, probability)
            
            if color_rule:
                self.name_label.setStyleSheet(f"""
                    font-size: 60px;
                    font-weight: bold;
                    color: {color_rule['color']};
                    background-color: transparent;
                    border: none;
                    padding: 30px;
                """)
            else:
                self.name_label.setStyleSheet("""
                    font-size: 60px;
                    font-weight: bold;
                    color: #333;
                    background-color: transparent;
                    border: none;
                    padding: 30px;
                """)
                
            self.result_layout.addWidget(self.name_label, 0, 0, 1, 3)
            
    def add_to_history(self, name, is_multi=False):
        current_time = datetime.now().strftime("%H:%M:%S")
        group_name = self.current_group
        
        if is_multi:
            record = f'[{current_time}] {group_name} (连抽) - {name}'
        else:
            record = f'[{current_time}] {group_name} - {name}'
            
        self.history_records.append(record)
        
        item = QListWidgetItem(record)
        
        probability = self.get_student_probability(name)
        color_rule = self.color_manager.get_color_for_student(group_name, name, probability)
        
        if color_rule:
            item.setForeground(QBrush(QColor(color_rule['color'])))
            
        self.history_list.insertItem(0, item)
        
        if len(self.history_records) > 100:
            self.history_records.pop()
            self.history_list.takeItem(self.history_list.count() - 1)
            
    def clear_history(self):
        reply = QMessageBox.question(self, '确认清空', 
                                   '确定要清空所有历史记录吗？',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history_records.clear()
            self.history_list.clear()

# ==================== 程序入口 ====================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = RandomNamePicker()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
