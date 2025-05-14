from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QWheelEvent, QMouseEvent
from PySide6.QtWidgets import QGraphicsItemGroup

class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def load_dxf(self, file_path, scale=1.0):
        import ezdxf
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        self.scene.clear()

        layers = {}

        for entity in msp:
            layer_name = entity.dxf.layer
            if layer_name not in layers:
                layers[layer_name] = QGraphicsItemGroup()
                self.scene.addItem(layers[layer_name])

            pen = QPen(QColor("black"))  # 可依照layer設定顏色
            if entity.dxftype() == "LINE":
                start, end = entity.dxf.start, entity.dxf.end
                line_item = QGraphicsLineItem(
                    start[0]*scale, -start[1]*scale, end[0]*scale, -end[1]*scale
                )
                line_item.setPen(pen)
                layers[layer_name].addToGroup(line_item)

            elif entity.dxftype() in ["POLYLINE", "LWPOLYLINE"]:
                with entity.points() as points:
                    points = list(points)
                    for i in range(len(points)-1):
                        start, end = points[i], points[i+1]
                        line_item = QGraphicsLineItem(
                            start[0]*scale, -start[1]*scale, end[0]*scale, -end[1]*scale
                        )
                        line_item.setPen(pen)
                        layers[layer_name].addToGroup(line_item)

        self.layers = layers  # 存圖層字典，供後續控制
        self.scene.setSceneRect(self.scene.itemsBoundingRect())

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.scene.selectedItems():
                self.scene.removeItem(item)
