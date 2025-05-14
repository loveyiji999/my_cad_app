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
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        self.scene.clear()
        pen = QPen(QColor("black"))

        huge_entities = []

        for entity in msp:
            try:
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
                        item.addToGroup(line_item)

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

                else:
                    continue

                bbox = item.boundingRect()
                if bbox.width() > 5000 or bbox.height() > 5000:
                    huge_entities.append((entity.dxftype(), bbox))
                else:
                    item.setPen(pen)
                    item.setFlags(QGraphicsLineItem.ItemIsSelectable | QGraphicsLineItem.ItemIsMovable)
                    self.scene.addItem(item)

            except Exception as e:
                print(f"Error processing {entity.dxftype()}: {e}")

        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

        if huge_entities:
            huge_info = "\n".join([f"{etype}: {bbox}" for etype, bbox in huge_entities])
            QMessageBox.warning(self, "偵測到巨大圖元！", f"以下圖元過於巨大可能導致顯示異常：\n{huge_info}")


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
