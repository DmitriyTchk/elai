from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                                 QHBoxLayout, QLabel, QPushButton,
                                 QFileDialog, QListWidget, QMenuBar,
                                 QStatusBar, QAction, QMessageBox,
                                 QLineEdit, QToolBar)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
import numpy as np
import os
from PIL import Image

class MarkupToolWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Инструмент разметки")
        self.setGeometry(100, 100, 1200, 800)

        # Инициализация переменных
        self.image = None
        self.image_path = None
        self.drawing = False
        self.annotations = []
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.scale_factor = 1.0

        self.create_widgets()
        self.create_menu()
        self.create_toolbar()

        self.statusBar().showMessage("Готов к работе")

    def create_widgets(self):
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный горизонтальный layout
        layout = QHBoxLayout(central_widget)

        # Область для изображения
        self.image_label = QLabel()
        self.image_label.setMinimumSize(800, 600)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.image_label.setText("Загрузите изображение для начала работы")
        layout.addWidget(self.image_label)

        # Панель информации
        info_panel = QWidget()
        info_panel.setMaximumWidth(300)
        info_layout = QVBoxLayout(info_panel)

        info_title = QLabel("Информация о разметке")
        info_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(info_title)

        # Список аннотаций
        self.anno_list = QListWidget()
        info_layout.addWidget(self.anno_list)

        # Кнопка удаления выбранной аннотации
        delete_btn = QPushButton("Удалить выбранное")
        delete_btn.clicked.connect(self.delete_selected)
        info_layout.addWidget(delete_btn)

        # Кнопка очистки всех аннотаций
        clear_btn = QPushButton("Очистить все")
        clear_btn.clicked.connect(self.clear_annotations)
        info_layout.addWidget(clear_btn)

        layout.addWidget(info_panel)

    def create_menu(self):
        # Создание меню
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")

        open_action = QAction("Открыть изображение", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        save_action = QAction("Сохранить разметку", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_annotations)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Инструменты"
        tools_menu = menubar.addMenu("Инструменты")

        clear_action = QAction("Очистить разметку", self)
        clear_action.triggered.connect(self.clear_annotations)
        tools_menu.addAction(clear_action)

        # Меню "Помощь"
        help_menu = menubar.addMenu("Помощь")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Кнопки инструментов
        open_btn = QAction("📁 Открыть", self)
        open_btn.triggered.connect(self.open_image)
        toolbar.addAction(open_btn)

        save_btn = QAction("💾 Сохранить", self)
        save_btn.triggered.connect(self.save_annotations)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        # Поле для ввода класса
        toolbar.addWidget(QLabel("Класс объекта:"))
        self.class_input = QLineEdit()
        self.class_input.setMaximumWidth(150)
        self.class_input.setText("object")
        self.class_input.setPlaceholderText("Введите класс объекта")
        toolbar.addWidget(self.class_input)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение",
            "",
            "Image files (*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp)")

        if file_name:
            self.image_path = file_name
            self.load_image()

    def load_image(self):
        if not self.image_path:
            QMessageBox.warning(self, "Предупреждение",
                              "Не выбран файл изображения")
            return

        if not os.path.exists(self.image_path):
            QMessageBox.warning(self, "Ошибка",
                              f"Файл не найден: {self.image_path}")
            self.statusBar().showMessage("Ошибка: файл не найден")
            return

        try:
            # Используем PIL для загрузки изображения (лучше работает с кириллицей)
            pil_image = Image.open(self.image_path)

            # Конвертируем в RGB если необходимо
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # Конвертируем PIL изображение в numpy array
            self.image = np.array(pil_image)

            if self.image is not None:
                self.display_image()
                self.statusBar().showMessage(f"Загружено изображение: {os.path.basename(self.image_path)}")
                # Очищаем аннотации при загрузке нового изображения
                self.annotations = []
                self.update_annotations_list()
            else:
                QMessageBox.warning(self, "Ошибка",
                                  "Не удалось загрузить изображение")
                self.statusBar().showMessage("Ошибка загрузки изображения")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Произошла ошибка при загрузке изображения:\n{str(e)}")
            self.statusBar().showMessage(f"Ошибка загрузки: {str(e)}")

    def display_image(self):
        if self.image is not None:
            try:
                height, width, channel = self.image.shape
                bytes_per_line = 3 * width

                # Создаем QImage из numpy array
                q_image = QImage(self.image.data, width, height,
                               bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)

                # Масштабирование изображения под размер label
                label_size = self.image_label.size()
                scaled_pixmap = pixmap.scaled(label_size,
                                            Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)

                # Вычисляем коэффициент масштабирования
                self.scale_factor = min(label_size.width() / width, 
                                      label_size.height() / height)

                self.image_label.setPixmap(scaled_pixmap)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Произошла ошибка при отображении изображения:\n{str(e)}")
                self.statusBar().showMessage(f"Ошибка отображения: {str(e)}")

    def mousePressEvent(self, event):
        if (self.image is not None and 
            event.button() == Qt.LeftButton and 
            self.image_label.geometry().contains(event.pos())):

            self.drawing = True
            # Преобразуем координаты относительно image_label
            relative_pos = event.pos() - self.image_label.pos()
            self.start_point = relative_pos
            self.end_point = self.start_point

    def mouseMoveEvent(self, event):
        if (self.drawing and 
            self.image_label.geometry().contains(event.pos())):

            # Преобразуем координаты относительно image_label
            relative_pos = event.pos() - self.image_label.pos()
            self.end_point = relative_pos
            self.update()

    def mouseReleaseEvent(self, event):
        if (self.drawing and 
            event.button() == Qt.LeftButton and
            self.image_label.geometry().contains(event.pos())):

            self.drawing = False

            # Преобразуем координаты относительно image_label
            relative_pos = event.pos() - self.image_label.pos()

            # Проверяем, что прямоугольник имеет минимальный размер
            if (abs(relative_pos.x() - self.start_point.x()) > 5 and
                abs(relative_pos.y() - self.start_point.y()) > 5):

                # Добавление аннотации
                annotation = {
                    'class': self.class_input.text() or 'object',
                    'start': self.start_point,
                    'end': relative_pos
                }
                self.annotations.append(annotation)
                self.update_annotations_list()
                self.statusBar().showMessage(f"Добавлена аннотация: {annotation['class']}")

            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.image is not None:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

            # Получаем позицию image_label
            label_pos = self.image_label.pos()

            # Отрисовка существующих аннотаций
            for anno in self.annotations:
                start_x = label_pos.x() + anno['start'].x()
                start_y = label_pos.y() + anno['start'].y()
                end_x = label_pos.x() + anno['end'].x()
                end_y = label_pos.y() + anno['end'].y()

                painter.drawRect(start_x, start_y, 
                               end_x - start_x, end_y - start_y)

                # Рисуем подпись класса
                painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
                painter.drawText(start_x, start_y - 5, anno['class'])
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

            # Отрисовка текущего прямоугольника
            if self.drawing:
                start_x = label_pos.x() + self.start_point.x()
                start_y = label_pos.y() + self.start_point.y()
                end_x = label_pos.x() + self.end_point.x()
                end_y = label_pos.y() + self.end_point.y()

                painter.setPen(QPen(Qt.blue, 2, Qt.DashLine))
                painter.drawRect(start_x, start_y, 
                               end_x - start_x, end_y - start_y)

    def update_annotations_list(self):
        self.anno_list.clear()
        for i, anno in enumerate(self.annotations):
            width = abs(anno['end'].x() - anno['start'].x())
            height = abs(anno['end'].y() - anno['start'].y())
            self.anno_list.addItem(
                f"{i+1}. {anno['class']} "
                f"[{width}x{height}] "
                f"({anno['start'].x()}, {anno['start'].y()})")

    def delete_selected(self):
        current_row = self.anno_list.currentRow()
        if current_row >= 0:
            deleted_class = self.annotations[current_row]['class']
            del self.annotations[current_row]
            self.update_annotations_list()
            self.update()
            self.statusBar().showMessage(f"Удалена аннотация: {deleted_class}")
        else:
            QMessageBox.information(self, "Информация",
                                  "Выберите аннотацию для удаления")

    def save_annotations(self):
        if not self.annotations:
            QMessageBox.warning(self, "Предупреждение",
                              "Нет аннотаций для сохранения")
            return

        if not self.image_path:
            QMessageBox.warning(self, "Предупреждение",
                              "Сначала загрузите изображение")
            return

        # Предлагаем сохранить в той же папке, что и изображение
        base_name = os.path.splitext(self.image_path)[0]
        default_name = f"{base_name}_annotations.txt"

        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить аннотации",
            default_name,
            "Text files (*.txt);;YOLO format (*.txt);;JSON files (*.json)")

        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    for anno in self.annotations:
                        # Сохраняем в формате: class x1 y1 x2 y2
                        f.write(f"{anno['class']} "
                               f"{anno['start'].x()} {anno['start'].y()} "
                               f"{anno['end'].x()} {anno['end'].y()}\n")

                QMessageBox.information(self, "Успех",
                                      f"Аннотации сохранены в файл:\n{file_name}")
                self.statusBar().showMessage(f"Аннотации сохранены: {os.path.basename(file_name)}")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось сохранить аннотации:\n{str(e)}")

    def clear_annotations(self):
        if not self.annotations:
            QMessageBox.information(self, "Информация",
                                  "Нет аннотаций для очистки")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                   f"Очистить все аннотации ({len(self.annotations)} шт.)?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.annotations = []
            self.update_annotations_list()
            self.update()
            self.statusBar().showMessage("Все аннотации очищены")

    def show_about(self):
        QMessageBox.information(
            self, "О программе",
            "Инструмент разметки изображений\n"
            "Версия 1.1\n"
            "© 2024 AI Vision Tools\n\n"
            "Возможности:\n"
            "• Загрузка изображений различных форматов\n"
            "• Создание прямоугольных аннотаций\n"
            "• Присвоение классов объектам\n"
            "• Сохранение разметки в текстовый файл\n"
            "• Поддержка путей с кириллицей")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MarkupToolWindow()
    window.show()
    sys.exit(app.exec_())
