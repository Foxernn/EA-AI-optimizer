from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QFileDialog, QTabWidget,
                            QGroupBox, QTextEdit, QComboBox, QSpinBox,
                            QDoubleSpinBox, QFormLayout, QProgressBar,
                            QSplitter, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont, QIcon
from src.core.file_handler import FileHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Titan EA Optimizer")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel for file management
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel for tabs
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        main_layout.addWidget(splitter)
        
        # Add status bar with progress
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.setAcceptDrops(True)

    def create_left_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File upload section
        upload_group = QGroupBox("EA Files")
        upload_layout = QVBoxLayout()
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["EA Files"])
        self.file_tree.setAcceptDrops(True)
        upload_layout.addWidget(self.file_tree)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Files")
        add_button.clicked.connect(self.browse_files)
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_selected_file)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        upload_layout.addLayout(button_layout)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        return widget

    def create_right_panel(self):
        tab_widget = QTabWidget()
        
        # Analysis tab
        analysis_tab = self.create_analysis_tab()
        tab_widget.addTab(analysis_tab, "Analysis")
        
        # Optimization tab
        optimization_tab = self.create_optimization_tab()
        tab_widget.addTab(optimization_tab, "Optimization")
        
        # Results tab
        results_tab = self.create_results_tab()
        tab_widget.addTab(results_tab, "Results")
        
        return tab_widget

    def create_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # EA Information
        info_group = QGroupBox("EA Details")
        info_layout = QFormLayout()
        
        self.ea_info_fields = {
            'Type': QLabel("Not loaded"),
            'Version': QLabel("Not loaded"),
            'Timeframes': QLabel("Not loaded"),
            'Symbols': QLabel("Not loaded"),
            'Creation Date': QLabel("Not loaded")
        }
        
        for label, field in self.ea_info_fields.items():
            info_layout.addRow(f"{label}:", field)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Analysis Output
        output_group = QGroupBox("Analysis Output")
        output_layout = QVBoxLayout()
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        output_layout.addWidget(self.analysis_text)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        return widget

    def create_optimization_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Parameter Settings
        param_group = QGroupBox("Optimization Settings")
        param_layout = QFormLayout()
        
        # Add parameter controls
        self.param_controls = {
            'Symbol': QComboBox(),
            'Timeframe': QComboBox(),
            'Lots': QDoubleSpinBox(),
            'Take Profit': QSpinBox(),
            'Stop Loss': QSpinBox(),
            'Max Spread': QDoubleSpinBox()
        }
        
        # Configure controls
        self.param_controls['Symbol'].addItems(['EURUSD', 'GBPUSD', 'USDJPY'])
        self.param_controls['Timeframe'].addItems(['M5', 'M15', 'M30', 'H1', 'H4'])
        self.param_controls['Lots'].setRange(0.01, 1.0)
        self.param_controls['Lots'].setSingleStep(0.01)
        self.param_controls['Take Profit'].setRange(10, 1000)
        self.param_controls['Stop Loss'].setRange(10, 1000)
        self.param_controls['Max Spread'].setRange(0.1, 50.0)
        self.param_controls['Max Spread'].setSingleStep(0.1)
        
        for label, control in self.param_controls.items():
            param_layout.addRow(label + ":", control)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Optimization Controls
        control_group = QGroupBox("Controls")
        control_layout = QHBoxLayout()
        
        start_button = QPushButton("Start Optimization")
        start_button.setStyleSheet("background-color: #4CAF50; color: white;")
        stop_button = QPushButton("Stop")
        stop_button.setStyleSheet("background-color: #f44336; color: white;")
        
        control_layout.addWidget(start_button)
        control_layout.addWidget(stop_button)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        return widget

    def create_results_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        results_group = QGroupBox("Optimization Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        return widget

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.process_files(files)
        
    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Titan EA Files",
            "",
            "MetaTrader Files (*.ex5 *.set);;All Files (*.*)"
        )
        if files:
            self.process_files(files)
    
    def remove_selected_file(self):
        selected_items = self.file_tree.selectedItems()
        for item in selected_items:
            self.file_tree.takeTopLevelItem(
                self.file_tree.indexOfTopLevelItem(item)
            )

    def process_files(self, files):
        for file_path in files:
            try:
                result = self.file_handler.process_file(file_path)
                self.update_ui_with_results(result)
                self.status_bar.showMessage(f"Successfully processed {file_path}", 3000)
            except Exception as e:
                self.analysis_text.append(f"Error processing file {file_path}: {str(e)}\n")
                self.status_bar.showMessage(f"Error processing file: {str(e)}", 5000)

    def update_ui_with_results(self, result):
        # Update EA information
        if 'ea_type' in result:
            self.ea_info_fields['Type'].setText(result['ea_type'])
            self.ea_info_fields['Version'].setText(result.get('version', 'Unknown'))
            self.ea_info_fields['Timeframes'].setText(
                ', '.join(result.get('supported_timeframes', []))
            )
            self.ea_info_fields['Symbols'].setText(
                ', '.join(result.get('supported_symbols', []))
            )
            self.ea_info_fields['Creation Date'].setText(
                result.get('creation_date', 'Unknown')
            )
        
        # Add to file tree
        item = QTreeWidgetItem([result.get('file_name', 'Unknown File')])
        self.file_tree.addTopLevelItem(item)
        
        # Update analysis output
        self.analysis_text.append(f"Processed: {result.get('file_name', '')}\n")
        self.analysis_text.append(f"Details: {str(result)}\n\n")
