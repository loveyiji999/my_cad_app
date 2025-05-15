from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QWheelEvent, QMouseEvent
from PySide6.QtWidgets import QGraphicsItemGroup
from PySide6.QtWidgets import QMessageBox

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
        from PySide6.QtGui import QFont, QPainterPath
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        self.scene.clear()
        layers = {}

        for entity in msp:
            layer_name = entity.dxf.layer
        if layer_name not in layers:
            layers[layer_name] = QGraphicsItemGroup()
            self.scene.addItem(layers[layer_name])

        pen = QPen(QColor("black"))

        item = None  # 明確初始化 item

        if entity.dxftype() == "LINE":
            start, end = entity.dxf.start, entity.dxf.end
            item = QGraphicsLineItem(
                start[0]*scale, -start[1]*scale, end[0]*scale, -end[1]*scale
            )

        elif entity.dxftype() in ["POLYLINE", "LWPOLYLINE"]:
            with entity.points() as points:
                points = list(points)
                item = QGraphicsItemGroup()
                for i in range(len(points)-1):
                    s, e = points[i], points[i+1]
                    line_item = QGraphicsLineItem(
                        s[0]*scale, -s[1]*scale, e[0]*scale, -e[1]*scale
                    )
                    line_item.setPen(pen)
                    item.addToGroup(line_item)
            self.scene.addItem(item)  

        elif entity.dxftype() == "POINT":
            center = entity.dxf.location
            point_size = 5
            item = self.scene.addEllipse(
                center[0]*scale - point_size/2,
                -center[1]*scale - point_size/2,
                point_size, point_size, pen
            )

        elif entity.dxftype() == "CIRCLE":
            center = entity.dxf.center
            radius = entity.dxf.radius
            item = self.scene.addEllipse(
                (center[0]-radius)*scale,
                -(center[1]+radius)*scale,
                radius*2*scale,
                radius*2*scale, pen
            )

        elif entity.dxftype() == "ARC":
            center = entity.dxf.center
            radius = entity.dxf.radius
            start_angle = entity.dxf.start_angle
            end_angle = entity.dxf.end_angle

            path = QPainterPath()
            path.arcMoveTo(
                (center[0] - radius)*scale,
                -(center[1] + radius)*scale,
                radius*2*scale,
                radius*2*scale,
                -start_angle
            )
            path.arcTo(
                (center[0] - radius)*scale,
                -(center[1] + radius)*scale,
                radius*2*scale,
                radius*2*scale,
                -start_angle,
                -(end_angle - start_angle)
            )
            item = self.scene.addPath(path, pen)

        elif entity.dxftype() == "TEXT":
            insert_point = entity.dxf.insert
            text = entity.dxf.text
            height = entity.dxf.height
            font = QFont("Microsoft JhengHei", height * scale)
            item = self.scene.addText(text, font)
            item.setPos(insert_point[0] * scale, -insert_point[1] * scale)
            item.setDefaultTextColor(QColor("black"))

        # 統一設定（注意有些圖元無法設定筆刷）
        if entity.dxftype() in ["LINE", "ARC", "CIRCLE", "POINT"]:
            item.setPen(pen)

        if item:
            item.setFlags(QGraphicsLineItem.ItemIsSelectable | QGraphicsLineItem.ItemIsMovable)
            layers[layer_name].addToGroup(item)

        self.layers = layers
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)


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
