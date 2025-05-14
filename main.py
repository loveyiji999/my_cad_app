import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog, QMessageBox,
    QToolBar, QWidget, QVBoxLayout, QComboBox, QSpinBox, QTextEdit, QPushButton, QDockWidget
)
from PySide6.QtGui import QAction, QFont, QIcon, QFontDatabase
from PySide6.QtCore import Qt
import ezdxf

from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtGui import QPen
from PySide6.QtCore import QPointF
from canvas import Canvas
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("我的中文CAD專案")
        self.resize(800, 600)

        label = QLabel("歡迎來到皆豪CAD", self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Microsoft JhengHei", 20))
        self.setCentralWidget(label)

        self.init_menu_bar()
        self.init_tool_bar()
        self.init_font_test_panel()

        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)

    def init_menu_bar(self):
        menubar = self.menuBar()
        tools_menu = menubar.addMenu("工具")
        font_test_action = QAction("中文字型測試", self)
        font_test_action.triggered.connect(self.toggle_font_test_panel)
        tools_menu.addAction(font_test_action)

    def init_tool_bar(self):
        toolbar = QToolBar("主工具列")
        self.addToolBar(toolbar)

        open_action = QAction(QIcon("resources/open.png"), "開啟", self)
        open_action.triggered.connect(self.open_file)  # <-- 新增這行！
        toolbar.addAction(open_action)

    def init_font_test_panel(self):
        self.font_dock = QDockWidget("中文字型測試面板", self)
        self.font_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 字型選擇器
        self.font_selector = QComboBox()
        fonts = QFontDatabase.families()
        self.font_selector.addItems(fonts)
        layout.addWidget(self.font_selector)

        # 字型大小選擇器
        self.size_selector = QSpinBox()
        self.size_selector.setRange(6, 72)
        self.size_selector.setValue(14)
        layout.addWidget(self.size_selector)

        # 文字輸入區
        self.text_edit = QTextEdit("輸入測試文字（例如：皆豪CAD中文字型測試）")
        layout.addWidget(self.text_edit)

        # 更新按鈕
        update_btn = QPushButton("更新顯示")
        update_btn.clicked.connect(self.update_preview)
        layout.addWidget(update_btn)

        # 預覽區
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
        file_path, _ = QFileDialog.getOpenFileName(self, "開啟 DXF 檔案", "", "DXF 檔案 (*.dxf);;所有檔案 (*.*)")
        if file_path:
            try:
                import ezdxf
                doc = ezdxf.readfile(file_path)
                msp = doc.modelspace()

                self.canvas.scene.clear()  # 清除現有圖元

                for entity in msp:
                    if entity.dxftype() == 'LINE':
                        start = entity.dxf.start
                        end = entity.dxf.end
                        line = QGraphicsLineItem(start[0], -start[1], end[0], -end[1])
                        pen = QPen(Qt.GlobalColor.black)
                        pen.setWidth(1)
                        line.setPen(pen)
                        self.canvas.scene.addItem(line)

                QMessageBox.information(self, "載入成功", f"成功載入 {file_path}")

            except Exception as e:
                QMessageBox.warning(self, "讀取 DXF 檔案錯誤", f"錯誤訊息：{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
