from pathlib import Path
import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsProxyWidget,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QGridLayout,
    QLabel,
    QStyle,
    QWidget,
)
from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database import SessionMaker
from src.models.area import Area
from src.models.map import Map
from src.models.sub_area import SubArea


class ArrowIcon(QLabel):
    def __init__(self, icon: QStyle.StandardPixmap, *args, **kwargs):
        super().__init__(*args, **kwargs)
        st_icon = self.style().standardIcon(icon)
        up_pixmap = st_icon.pixmap(QSize(16, 16))
        self.setPixmap(up_pixmap)


CELL_WIDTH = 50
CELL_HEIGHT = 50


class CellMapWidget(QWidget):
    def __init__(self, map: Map, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setFixedSize(CELL_WIDTH - 2, CELL_HEIGHT - 2)
        self.m_layout = QGridLayout()
        self.setLayout(self.m_layout)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: grey;")
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        if map.left_map:
            self.m_layout.addWidget(ArrowIcon(self.style().SP_ArrowLeft), 1, 0)
        else:
            self.m_layout.addWidget(QLabel(" "), 1, 0)

        if map.right_map:
            self.m_layout.addWidget(ArrowIcon(self.style().SP_ArrowRight), 1, 2)
        else:
            self.m_layout.addWidget(QLabel(" "), 1, 2)

        if map.top_map:
            self.m_layout.addWidget(ArrowIcon(self.style().SP_ArrowUp), 0, 1)
        else:
            self.m_layout.addWidget(QLabel(" "), 0, 1)

        if map.bot_map:
            self.m_layout.addWidget(ArrowIcon(self.style().SP_ArrowDown), 2, 1)
        else:
            self.m_layout.addWidget(QLabel(" "), 2, 1)


class GridMap(QGraphicsView):
    def __init__(self, session: Session, *args, **kwargs):
        super().__init__(*args, **kwargs)

        scene = QGraphicsScene()
        maps = (
            session.query(Map)
            .join(SubArea, Map.sub_area_id == SubArea.id)
            .join(Area, Area.id == SubArea.area_id)
            .filter(Area.name == "Bonta", Map.x <= -24, Map.y > -62)
            .distinct(Map.x, Map.y)
            .all()
        )
        for map in maps:
            if map.y >= 0:
                continue

            cell_widget = CellMapWidget(map)
            proxy = QGraphicsProxyWidget()
            proxy.setWidget(cell_widget)
            proxy.setPos(map.x * CELL_WIDTH, map.y * CELL_HEIGHT)
            scene.addItem(proxy)

        x_min = min(map.x for map in maps) * CELL_WIDTH
        x_max = max(map.x for map in maps) * CELL_WIDTH
        y_min = min(map.y for map in maps) * CELL_HEIGHT
        y_max = max(map.y for map in maps if map.y < 0) * CELL_HEIGHT

        for x in range(x_min, x_max + 1, CELL_WIDTH):
            text_item = QGraphicsTextItem(str(x // CELL_WIDTH))
            text_item.setPos(x + CELL_WIDTH // 4, y_min - 20)
            scene.addItem(text_item)

        for y in range(y_min, y_max + 1, CELL_HEIGHT):
            text_item = QGraphicsTextItem(str(y // CELL_HEIGHT))
            text_item.setPos(x_min - 30, y + CELL_HEIGHT // 4)
            scene.addItem(text_item)

        self.setScene(scene)


def draw_grid():
    app = QApplication(sys.argv)

    session = SessionMaker()

    scene = GridMap(session)
    scene.show()

    app.exec()


if __name__ == "__main__":
    draw_grid()
