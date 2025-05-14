from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor

class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setRenderHint(QPainter.Antialiasing)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def load_dxf(self, file_path, scale=1.0):
        import ezdxf
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        self.scene.clear()

        pen = QPen(QColor("black"))

        for entity in msp:
            if entity.dxftype() == "LINE":
                start = entity.dxf.start
                end = entity.dxf.end
                self.scene.addLine(
                    start[0]*scale, -start[1]*scale, end[0]*scale, -end[1]*scale, pen
                )

            elif entity.dxftype() in ["POLYLINE", "LWPOLYLINE"]:
                points = entity.points()
                for i in range(len(points)-1):
                    start, end = points[i], points[i+1]
                    self.scene.addLine(
                        start[0]*scale, -start[1]*scale, end[0]*scale, -end[1]*scale, pen
                    )

        # 自動調整可視範圍
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
