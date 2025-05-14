import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog, QMessageBox,
    QToolBar, QWidget, QVBoxLayout, QComboBox, QSpinBox, QTextEdit,
    QPushButton, QDockWidget, QTabWidget
)
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtGui import QAction, QFont, QIcon, QFontDatabase
from PySide6.QtCore import Qt
from canvas import Canvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("我的中文CAD專案")
        self.resize(1024, 768)

        self.init_menu_bar()
        self.init_tool_bar()
        self.init_font_test_panel()

        # 正確設定 Tabs 作為中央視窗
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

    def init_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("檔案")
        open_action = QAction("開啟 DXF", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        tools_menu = menubar.addMenu("工具")
        font_test_action = QAction("中文字型測試", self)
        font_test_action.triggered.connect(self.toggle_font_test_panel)
        tools_menu.addAction(font_test_action)

    def init_tool_bar(self):
        toolbar = QToolBar("主工具列")
        self.addToolBar(toolbar)

        open_action = QAction(QIcon("resources/open.png"), "開啟", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

    def init_font_test_panel(self):
        self.font_dock = QDockWidget("中文字型測試面板", self)
        self.font_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.font_selector = QComboBox()
        fonts = QFontDatabase.families()
        self.font_selector.addItems(fonts)
        layout.addWidget(self.font_selector)

        self.size_selector = QSpinBox()
        self.size_selector.setRange(6, 72)
        self.size_selector.setValue(14)
        layout.addWidget(self.size_selector)

        self.text_edit = QTextEdit("輸入測試文字（例如：皆豪CAD中文字型測試）")
        layout.addWidget(self.text_edit)

        update_btn = QPushButton("更新顯示")
        update_btn.clicked.connect(self.update_preview)
        layout.addWidget(update_btn)

        self.preview_label = QLabel("預覽文字會顯示在這裡")
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        self.font_dock.setWidget(panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.font_dock)
        self.font_dock.hide()

    def toggle_font_test_panel(self):
        if self.font_dock.isVisible():
            self.font_dock.hide()
        else:
            self.font_dock.show()

    def update_preview(self):
        font_name = self.font_selector.currentText()
        font_size = self.size_selector.value()
        test_text = self.text_edit.toPlainText()

        font = QFont(font_name, font_size)
        self.preview_label.setFont(font)
        self.preview_label.setText(test_text)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "開啟 DXF 檔案", "", "DXF 檔案 (*.dxf)"
        )
        if file_path:
            self.add_dxf_tab(file_path)

    def add_dxf_tab(self, file_path):
        canvas = Canvas()
        canvas.load_dxf(file_path, scale=0.1)
        filename = file_path.split("/")[-1]
        self.tabs.addTab(canvas, filename)
        self.tabs.setCurrentWidget(canvas)

        # 更新圖層列表
        self.layer_list.clear()
        for layer_name in canvas.layers.keys():
            item = QListWidgetItem(layer_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.layer_list.addItem(item)
            
    def toggle_layer_visibility(self, item):
        layer_name = item.text()
        visible = item.checkState() == Qt.Checked

        canvas = self.tabs.currentWidget()
        if canvas and layer_name in canvas.layers:
            canvas.layers[layer_name].setVisible(visible)

    def init_layer_panel(self):
        self.layer_dock = QDockWidget("圖層管理", self)
        self.layer_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.layer_list = QListWidget()
        self.layer_list.itemChanged.connect(self.toggle_layer_visibility)

        self.layer_dock.setWidget(self.layer_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layer_dock)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
