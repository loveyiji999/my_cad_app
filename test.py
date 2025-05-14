import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QFileDialog, QTextEdit
)
import ezdxf

class DXFChecker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DXF 圖元檢查工具")
        self.resize(600, 400)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.check_button = QPushButton("開啟 DXF 並檢查圖元")
        self.check_button.clicked.connect(self.load_and_check_dxf)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addWidget(self.check_button)
        layout.addWidget(self.result_text)

        self.setCentralWidget(central_widget)

    def load_and_check_dxf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇 DXF 檔案", "", "DXF 檔案 (*.dxf)")
        if file_path:
            self.check_dxf(file_path)

    def check_dxf(self, file_path):
        try:
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()

            entity_types = set()
            for entity in msp:
                entity_types.add(entity.dxftype())

            if not entity_types:
                self.result_text.setPlainText("❌ 此 DXF 檔案中沒有任何圖元！")
            else:
                result_str = "✅ DXF 檔案內含的圖元類型：\n"
                result_str += "\n".join(entity_types)
                self.result_text.setPlainText(result_str)

        except Exception as e:
            self.result_text.setPlainText(f"讀取檔案錯誤：{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DXFChecker()
    window.show()
    sys.exit(app.exec())
