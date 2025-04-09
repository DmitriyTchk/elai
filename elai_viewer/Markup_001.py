# Импорт модуля взаимодействия с ОС, выполняет операции с файлами и папками
import os
# Импорт библиотеки OpenCV для обработки изображений и видео, для задач компьютерного зрения (CV)
import cv2
# Импорт библиотеки NumPy для работы с массивами и математическими операциями
import numpy as np
# Импорт классов Image и ImageTk из библиотеки PIL для работы с изображениями и их отображения в Tkinter
from PIL import Image, ImageTk
# Импорт библиотеки Tkinter для создания графического интерфейса
import tkinter as tk
# Импорт модуля messagebox из Tkinter для вывода всплывающих сообщений об ошибках или уведомлениях
from tkinter import messagebox

#================================================================
# Функция для просмотра аннотированных кадров. Проверяет существование
# указанных директорий с кадрами и аннотациями, выводит информацию о них.
# Если директории не существуют - прерывает выполнение с сообщением.
# Создаёт окно с интерфейсом для просмотра и редактирования изображений.
#================================================================
def view_annotated_frames(frames_dir, annotations_dir):
    # Вывод пути к директории с кадрами для проверки
    print(f"Проверяемый путь frames_dir: '{frames_dir}'")
    # Проверка и вывод информации о существовании директории с кадрами
    print(f"Существует ли frames_dir? {os.path.exists(frames_dir)}")
    # Если директория существует, показать первые 5 элементов содержимого
    if os.path.exists(frames_dir):
        print(f"Содержимое frames_dir: {os.listdir(frames_dir)[:5]}")
    # Вывод пути к директории с аннотациями для проверки
    print(f"Проверяемый путь annotations_dir: '{annotations_dir}'")
    # Проверка и вывод информации о существовании директории с аннотациями
    print(f"Существует ли annotations_dir? {os.path.exists(annotations_dir)}")
    # Если директория существует, показать первые 5 элементов содержимого
    if os.path.exists(annotations_dir):
        print(f"Содержимое annotations_dir: {os.listdir(annotations_dir)[:5]}")
    # Проверка отсутствия любой из директорий
    if not os.path.exists(frames_dir) or not os.path.exists(annotations_dir):
        # Вывод сообщения об ошибке, если какая-то директория отсутствует
        print("Папки с кадрами или аннотациями не найдены.")
        # Выход из функции без выполнения дальнейших операций
        return
    
    # Определение внутреннего класса для управления интерфейсом просмотра и редактирования
    class ImageViewer:
        # Инициализация объекта просмотра с передачей параметров    
        def __init__(self, master, frames_dir, annotations_dir):
            # Сохранение ссылки на главное окно Tkinter
            self.master = master
            # Сохранение пути к директории с кадрами
            self.frames_dir = frames_dir
            # Сохранение пути к директории с аннотациями
            self.annotations_dir = annotations_dir
            # Создание отсортированного списка файлов изображений с расширениями .png, .jpg, .jpeg
            self.image_files = sorted([f for f in os.listdir(frames_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
            # Установка начального индекса текущего изображения (первое изображение)
            self.index = 0
            # Установка начального коэффициента масштабирования изображения (1.0 - без масштаба)
            self.scale_factor = 1.0
            # Установка начальной чувствительности перетаскивания изображения
            self.drag_sensitivity = 0.5
            # Установка начальной прозрачности затемнения (50%)
            self.transparency = 0.5
            # Создание пустого словаря для кэширования обработанных изображений
            self.image_cache = {}
            # Установка начального смещения изображения по оси X на canvas
            self.image_x = 0
            # Установка начального смещения изображения по оси Y на canvas
            self.image_y = 0
            # Установка начальной относительной позиции центра изображения по X (центр по умолчанию)
            self.relative_center_x = 0.5
            # Установка начальной относительной позиции центра изображения по Y (центр по умолчанию)
            self.relative_center_y = 0.5
            # Создание пустого списка для хранения bounding box'ов текущего кадра
            self.bboxes = []
            # Инициализация переменной для хранения исходного изображения (пока None)
            self.original_frame = None
            # Создание словаря для хранения цветов классов (по умолчанию несколько цветов)
            self.class_colors = {"person": (0, 255, 0), "table": (255, 0, 0), "chair": (0, 0, 255)}
            # Инициализация переменной для хранения текущего редактируемого бокса
            self.current_box = None
            # Инициализация переменной для хранения окна редактирования
            self.edit_window = None
            # Инициализация переменной для создания нового бокса
            self.creating_box = False
            # Инициализация начальных координат для создания бокса
            self.start_x = self.start_y = None
            
            # Установка заголовка главного окна
            master.title("Просмотр и редактирование размеченных кадров")
            # Установка размеров и положения окна (ширина 1024, высота 768, смещение +100 по X, +50 по Y)
            master.geometry("1024x768+100+50")
            
            # Создание фрейма для размещения элементов управления
            self.controls_frame = tk.Frame(master)
            # Размещение фрейма с отступом 5 пикселей сверху и снизу
            self.controls_frame.pack(pady=5)
            
            # Создание фрейма для кнопок навигации
            self.nav_frame = tk.Frame(self.controls_frame)
            # Размещение фрейма навигации внутри controls_frame
            self.nav_frame.pack()
            # Создание кнопки "Назад" с командой перехода к предыдущему изображению
            self.prev_btn = tk.Button(self.nav_frame, text="← Назад", command=self.prev_image)
            # Размещение кнопки "Назад" слева с отступом 5 пикселей
            self.prev_btn.pack(side=tk.LEFT, padx=5)
            # Создание кнопки "Вперёд" с командой перехода к следующему изображению
            self.next_btn = tk.Button(self.nav_frame, text="Вперед →", command=self.next_image)
            # Размещение кнопки "Вперёд" слева с отступом 5 пикселей
            self.next_btn.pack(side=tk.LEFT, padx=5)
            
            # Создание надписи с информацией о текущем кадре и общем количестве
            self.info_label = tk.Label(self.controls_frame, text=f"Кадр 1 из {len(self.image_files)}")
            # Размещение надписи с отступом 5 пикселей сверху и снизу
            self.info_label.pack(pady=5)
            
            # Создание фрейма для элементов перехода к конкретному кадру
            self.goto_frame = tk.Frame(self.controls_frame)
            # Размещение фрейма перехода
            self.goto_frame.pack()
            # Создание надписи для поля ввода номера или имени кадра
            self.frame_entry_label = tk.Label(self.goto_frame, text="Перейти к кадру (№ или имя):")
            # Размещение надписи слева с отступом 5 пикселей
            self.frame_entry_label.pack(side=tk.LEFT, padx=5)
            # Создание поля ввода для номера или имени кадра шириной 20 символов
            self.frame_entry = tk.Entry(self.goto_frame, width=20)
            # Размещение поля ввода слева с отступом 5 пикселей
            self.frame_entry.pack(side=tk.LEFT, padx=5)
            # Создание кнопки "Перейти" с командой перехода к указанному кадру
            self.go_btn = tk.Button(self.goto_frame, text="Перейти", command=self.go_to_frame)
            # Размещение кнопки "Перейти" слева с отступом 5 пикселей
            self.go_btn.pack(side=tk.LEFT, padx=5)
            
            # Создание фрейма для размещения ползунков управления
            self.sliders_frame = tk.Frame(self.controls_frame)
            # Размещение фрейма ползунков с отступом 5 пикселей сверху и снизу
            self.sliders_frame.pack(pady=5)
            # Создание ползунка масштаба с диапазоном от 0.1 до 3.0, шагом 0.1, горизонтальной ориентацией
            self.scale_slider = tk.Scale(self.sliders_frame, from_=0.1, to=3.0, resolution=0.1,
                                        orient=tk.HORIZONTAL, length=200, label="Масштаб",
                                        command=self.update_scale)
            # Установка начального значения ползунка масштаба
            self.scale_slider.set(self.scale_factor)
            # Размещение ползунка масштаба слева с отступом 10 пикселей
            self.scale_slider.pack(side=tk.LEFT, padx=10)
            
            # Создание ползунка чувствительности перетаскивания с диапазоном от 0.1 до 1.0, шагом 0.1
            self.sensitivity_slider = tk.Scale(self.sliders_frame, from_=0.1, to=1.0, resolution=0.1,
                                            orient=tk.HORIZONTAL, length=200, label="Плавность",
                                            command=self.update_sensitivity)
            # Установка начального значения ползунка чувствительности
            self.sensitivity_slider.set(self.drag_sensitivity)
            # Размещение ползунка чувствительности слева с отступом 10 пикселей
            self.sensitivity_slider.pack(side=tk.LEFT, padx=10)
            
            # Создание ползунка прозрачности затемнения с диапазоном от 0.0 до 1.0, шагом 0.1
            self.transparency_slider = tk.Scale(self.sliders_frame, from_=0.0, to=1.0, resolution=0.1,
                                            orient=tk.HORIZONTAL, length=200, label="Прозрачность затемнения",
                                            command=self.update_transparency)
            # Установка начального значения ползунка прозрачности
            self.transparency_slider.set(self.transparency)
            # Размещение ползунка прозрачности слева с отступом 10 пикселей
            self.transparency_slider.pack(side=tk.LEFT, padx=10)
            
            # Создание надписи с именем текущего файла (по умолчанию "ещё не загружен")
            self.filename_label = tk.Label(master, text="Файл: (ещё не загружен)")
            # Размещение надписи с отступом 5 пикселей сверху и снизу
            self.filename_label.pack(pady=5)
            
            # Создание фрейма для области отображения изображения
            self.canvas_frame = tk.Frame(master)
            # Размещение фрейма с заполнением всего доступного пространства и возможностью расширения
            self.canvas_frame.pack(fill=tk.BOTH, expand=True)
            
            # Создание canvas для отображения изображения
            self.canvas = tk.Canvas(self.canvas_frame)
            # Создание горизонтальной полосы прокрутки, связанной с canvas
            self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
            # Создание вертикальной полосы прокрутки, связанной с canvas
            self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            # Настройка canvas для работы с полосами прокрутки
            self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
            
            # Размещение горизонтальной полосы прокрутки внизу с заполнением по горизонтали
            self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            # Размещение вертикальной полосы прокрутки справа с заполнением по вертикали
            self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            # Размещение canvas слева с заполнением пространства и возможностью расширения
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Создание метки для отображения изображения внутри canvas
            self.image_label = tk.Label(self.canvas, cursor="crosshair")
            # Вставка метки с изображением в canvas с привязкой к верхнему левому углу
            self.image_id = self.canvas.create_window((0, 0), window=self.image_label, anchor="nw")
            
            # Привязка событий для создания и редактирования bounding box'ов с учётом Ctrl
            self.image_label.bind("<Button-1>", self.start_box_or_drag)
            self.image_label.bind("<B1-Motion>", self.update_box_or_drag)
            self.image_label.bind("<ButtonRelease-1>", self.finish_box_or_drag)
            self.image_label.bind("<Motion>", self.on_mouse_motion)
            self.image_label.bind("<MouseWheel>", self.on_mouse_wheel)
            
            # Создание словаря для хранения данных о перетаскивании изображения
            self.drag_data = {"x": 0, "y": 0, "dragging": False}
            # Создание словаря для хранения данных о редактировании бокса
            self.edit_data = {"mode": None, "corner": None, "edge": None}
            
            # Запуск загрузки первого изображения через 100 миллисекунд после инициализации
            self.master.after(100, self.load_image)

        #================================================================
        # Функция загрузки и отображения текущего изображения. Открывает файл,
        # считывает аннотации, рисует bounding box'ы с цветами по классам и обновляет интерфейс.
        #================================================================
        def load_image(self):
            # Проверка наличия изображений в списке
            if not self.image_files:
                # Вывод сообщения, если изображений нет
                print("Нет изображений для отображения")
                # Выход из функции
                return
            
            # Закрытие окна редактирования, если оно открыто
            if self.edit_window:
                self.edit_window.destroy()
                self.edit_window = None
                self.current_box = None
            
            # Формирование полного пути к текущему изображению
            image_path = os.path.join(self.frames_dir, self.image_files[self.index])
            # Создание ключа для кэша на основе имени файла и текущего масштаба
            cache_key = (self.image_files[self.index], self.scale_factor)
            
            # Проверка наличия изображения в кэше
            if cache_key in self.image_cache:
                # Использование кэшированного изображения
                self.tk_image = self.image_cache[cache_key]
            # Если изображения нет в кэше, выполнить загрузку и обработку
            else:
                # Попытка открытия изображения
                try:
                    # Открытие файла изображения с помощью PIL
                    img = Image.open(image_path)
                # Обработка возможных ошибок при открытии файла
                except Exception as e:
                    # Вывод сообщения об ошибке с указанием пути
                    print(f"Ошибка загрузки изображения {image_path}: {e}")
                    # Выход из функции
                    return
                
                # Преобразование изображения в формат BGR для работы с OpenCV
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                # Сохранение копии исходного изображения для последующей обработки
                self.original_frame = frame.copy()
                # Очистка списка bounding box'ов перед загрузкой новых
                self.bboxes = []
                
                # Формирование имени файла аннотации (замена расширения на .txt)
                current_frame_name = self.image_files[self.index].replace('.jpg', '.txt')
                # Формирование полного пути к файлу аннотации
                annotation_path = os.path.join(self.annotations_dir, current_frame_name)
                
                # Проверка существования файла аннотации
                if os.path.exists(annotation_path):
                    # Открытие файла аннотации для чтения
                    with open(annotation_path, 'r') as f:
                        # Чтение всех строк из файла аннотации
                        annotations = f.readlines()
                    # Обработка каждой строки аннотации
                    for ann in annotations:
                        # Разделение строки на части (класс и координаты)
                        parts = ann.strip().split()
                        # Проверка, что строка содержит 5 элементов (класс и 4 координаты)
                        if len(parts) == 5:
                            # Попытка парсинга данных аннотации
                            try:
                                # Первый элемент - класс объекта (строка)
                                class_name = parts[0]
                                # Преобразование координат в числа с плавающей точкой
                                x1, y1, x2, y2 = map(float, parts[1:])
                                # Преобразование координат в целые числа для OpenCV
                                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                                # Добавление bounding box'а в список (класс и координаты)
                                self.bboxes.append((class_name, x1, y1, x2, y2))
                                # Получение цвета для текущего класса (по умолчанию зелёный, если класса нет в словаре)
                                color = self.class_colors.get(class_name, (0, 255, 0))
                                # Рисование прямоугольника bounding box'а на изображении с цветом класса
                                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                # Добавление текста с классом над bounding box'ом
                                cv2.putText(frame, f"{class_name}", (x1, y1 - 10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                            # Обработка ошибок при парсинге аннотации
                            except ValueError as e:
                                # Вывод сообщения об ошибке парсинга
                                print(f"Ошибка разбора аннотации: {e}")
                
                # Преобразование изображения обратно в RGB для отображения
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Создание объекта PIL Image из массива RGB
                img = Image.fromarray(frame_rgb)
                # Вычисление новой ширины изображения с учётом масштаба
                new_width = int(img.width * self.scale_factor)
                # Вычисление новой высоты изображения с учётом масштаба
                new_height = int(img.height * self.scale_factor)
                # Изменение размера изображения с использованием алгоритма LANCZOS
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Преобразование изображения в формат, пригодный для Tkinter
                self.tk_image = ImageTk.PhotoImage(image=img)
                # Сохранение обработанного изображения в кэш
                self.image_cache[cache_key] = self.tk_image
            
            # Установка нового изображения в метку для отображения
            self.image_label.configure(image=self.tk_image)
            # Сохранение ссылки на изображение для предотвращения удаления сборщиком мусора
            self.image_label.image = self.tk_image
            
            # Получение ширины canvas (по умолчанию 1024, если не определена)
            canvas_width = self.canvas.winfo_width() or 1024
            # Получение высоты canvas (по умолчанию 768, если не определена)
            canvas_height = self.canvas.winfo_height() or 768
            # Получение ширины текущего изображения
            img_width = self.tk_image.width()
            # Получение высоты текущего изображения
            img_height = self.tk_image.height()
            
            # Вычисление координаты X центра изображения
            center_x = img_width * self.relative_center_x
            # Вычисление координаты Y центра изображения
            center_y = img_height * self.relative_center_y
            # Вычисление смещения по X для центрирования изображения на canvas
            self.image_x = center_x - canvas_width // 2
            # Вычисление смещения по Y для центрирования изображения на canvas
            self.image_y = center_y - canvas_height // 2
            
            # Обновление позиции изображения на canvas
            self.update_position()
            
            # Обновление текста надписи с информацией о текущем кадре и масштабе
            self.info_label.configure(text=f"Кадр {self.index + 1} из {len(self.image_files)} (Масштаб: {self.scale_factor:.1f}x)")
            # Обновление текста надписи с именем текущего файла
            self.filename_label.configure(text=f"Файл: {self.image_files[self.index]}")

        #================================================================
        # Функция начала создания нового бокса или перетаскивания изображения.
        # Разделяет действия: создание бокса (ЛКМ) и перетаскивание (Ctrl + ЛКМ).
        #================================================================
        def start_box_or_drag(self, event):
            # Преобразование координат мыши в исходные координаты изображения
            orig_x = event.x / self.scale_factor
            orig_y = event.y / self.scale_factor
            
            # Проверка, зажата ли клавиша Ctrl (event.state & 0x4 означает Ctrl)
            ctrl_pressed = event.state & 0x4
            
            # Если Ctrl зажат, начать перетаскивание изображения
            if ctrl_pressed:
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                self.drag_data["dragging"] = True
                return
            
            # Проверка, попадает ли курсор в существующий бокс (без Ctrl)
            for i, (class_name, x1, y1, x2, y2) in enumerate(self.bboxes):
                if x1 <= orig_x <= x2 and y1 <= orig_y <= y2:
                    # Установка текущего редактируемого бокса
                    self.current_box = i
                    # Проверка положения курсора для определения режима редактирования
                    if abs(orig_x - x1) < 10 and abs(orig_y - y1) < 10:
                        self.edit_data["mode"] = "resize"
                        self.edit_data["corner"] = "top_left"
                    elif abs(orig_x - x2) < 10 and abs(orig_y - y2) < 10:
                        self.edit_data["mode"] = "resize"
                        self.edit_data["corner"] = "bottom_right"
                    elif abs(orig_x - x1) < 10 and abs(orig_y - y2) < 10:
                        self.edit_data["mode"] = "resize"
                        self.edit_data["corner"] = "bottom_left"
                    elif abs(orig_x - x2) < 10 and abs(orig_y - y1) < 10:
                        self.edit_data["mode"] = "resize"
                        self.edit_data["corner"] = "top_right"
                    elif abs(orig_x - x1) < 10 or abs(orig_x - x2) < 10:
                        self.edit_data["mode"] = "move"
                        self.edit_data["edge"] = "vertical"
                    elif abs(orig_y - y1) < 10 or abs(orig_y - y2) < 10:
                        self.edit_data["mode"] = "move"
                        self.edit_data["edge"] = "horizontal"
                    else:
                        self.edit_data["mode"] = "drag_box"
                    # Открытие окна редактирования для выбранного бокса
                    self.open_edit_window()
                    return
            
            # Если Ctrl не зажат и курсор не в боксе, начать создание нового бокса
            self.creating_box = True
            self.start_x = orig_x
            self.start_y = orig_y

        #================================================================
        # Функция обновления создаваемого бокса или перетаскивания.
        # Рисует новый бокс в реальном времени или перемещает изображение.
        #================================================================
        def update_box_or_drag(self, event):
            # Преобразование координат мыши в исходные координаты изображения
            orig_x = event.x / self.scale_factor
            orig_y = event.y / self.scale_factor
            
            # Если создаётся новый бокс
            if self.creating_box and self.start_x != orig_x and self.start_y != orig_y:
                # Создание временной копии изображения
                frame = self.original_frame.copy()
                # Отрисовка существующих боксов
                for class_name, x1, y1, x2, y2 in self.bboxes:
                    color = self.class_colors.get(class_name, (0, 255, 0))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                # Отрисовка создаваемого бокса
                x1, y1 = int(min(self.start_x, orig_x)), int(min(self.start_y, orig_y))
                x2, y2 = int(max(self.start_x, orig_x)), int(max(self.start_y, orig_y))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Обновление изображения
                self.update_image(frame)
            
            # Если редактируется существующий бокс
            elif self.current_box is not None and self.edit_data["mode"]:
                class_name, x1, y1, x2, y2 = self.bboxes[self.current_box]
                if self.edit_data["mode"] == "resize":
                    if self.edit_data["corner"] == "top_left":
                        x1, y1 = int(orig_x), int(orig_y)
                    elif self.edit_data["corner"] == "bottom_right":
                        x2, y2 = int(orig_x), int(orig_y)
                    elif self.edit_data["corner"] == "bottom_left":
                        x1, y2 = int(orig_x), int(orig_y)
                    elif self.edit_data["corner"] == "top_right":
                        x2, y1 = int(orig_x), int(orig_y)
                elif self.edit_data["mode"] == "move":
                    dx = int(orig_x - (x1 + x2) / 2)
                    dy = int(orig_y - (y1 + y2) / 2)
                    x1 += dx
                    x2 += dx
                    y1 += dy
                    y2 += dy
                # Обновление координат бокса
                self.bboxes[self.current_box] = (class_name, x1, y1, x2, y2)
                # Перерисовка изображения
                self.redraw_image()
            
            # Если перетаскивается изображение (с Ctrl)
            elif self.drag_data["dragging"]:
                # Вычисление смещения по X с учётом чувствительности
                dx = int((event.x - self.drag_data["x"]) * self.drag_sensitivity)
                # Вычисление смещения по Y с учётом чувствительности
                dy = int((event.y - self.drag_data["y"]) * self.drag_sensitivity)
                # Обновление позиции изображения по X
                self.image_x += dx
                # Обновление позиции изображения по Y
                self.image_y += dy
                # Применение новой позиции
                self.update_position()
                # Обновление текущих координат мыши
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y


        #================================================================
        # Функция завершения создания бокса или перетаскивания.
        # Финализирует новый бокс или завершает редактирование.
        #================================================================
        def finish_box_or_drag(self, event):
            # Преобразование координат мыши в исходные координаты изображения
            orig_x = event.x / self.scale_factor
            orig_y = event.y / self.scale_factor
            
            # Если создавался новый бокс
            if self.creating_box:
                self.creating_box = False
                if self.start_x != orig_x and self.start_y != orig_y:
                    x1, y1 = int(min(self.start_x, orig_x)), int(min(self.start_y, orig_y))
                    x2, y2 = int(max(self.start_x, orig_x)), int(max(self.start_y, orig_y))
                    # Добавление нового бокса с временным классом "new"
                    self.bboxes.append(("new", x1, y1, x2, y2))
                    self.current_box = len(self.bboxes) - 1
                    # Открытие окна редактирования для нового бокса
                    self.open_edit_window()
                self.redraw_image()
            
            # Завершение редактирования бокса
            elif self.current_box is not None:
                self.edit_data["mode"] = None
                self.edit_data["corner"] = None
                self.edit_data["edge"] = None
            
            # Завершение перетаскивания изображения
            self.drag_data["dragging"] = False
        
        #================================================================
        # Функция открытия окна редактирования bounding box'а.
        # Позволяет задать класс, удалить или сохранить бокс.
        #================================================================
        def open_edit_window(self):
            # Закрытие предыдущего окна редактирования, если оно открыто
            if self.edit_window:
                self.edit_window.destroy()
            
            # Создание нового окна редактирования
            self.edit_window = tk.Toplevel(self.master)
            self.edit_window.title("Редактирование Bounding Box")
            self.edit_window.geometry("300x150")
            
            # Получение данных текущего бокса
            class_name, x1, y1, x2, y2 = self.bboxes[self.current_box]
            
            # Создание поля ввода класса
            tk.Label(self.edit_window, text="Класс:").pack(pady=5)
            class_entry = tk.Entry(self.edit_window)
            class_entry.insert(0, class_name)
            class_entry.pack()
            
            # Создание кнопки удаления бокса
            delete_btn = tk.Button(self.edit_window, text="Удалить", 
                                 command=lambda: self.delete_box(class_entry))
            delete_btn.pack(pady=5)
            
            # Создание кнопки сохранения бокса
            save_btn = tk.Button(self.edit_window, text="Сохранить", 
                               command=lambda: self.save_box(class_entry))
            save_btn.pack(pady=5)
        
        #================================================================
        # Функция удаления текущего bounding box'а.
        # Удаляет бокс из списка и обновляет изображение.
        #================================================================
        def delete_box(self, class_entry):
            # Удаление текущего бокса из списка
            del self.bboxes[self.current_box]
            # Закрытие окна редактирования
            self.edit_window.destroy()
            self.edit_window = None
            self.current_box = None
            # Перерисовка изображения без удалённого бокса
            self.redraw_image()
        
        #================================================================
        # Функция сохранения текущего bounding box'а.
        # Обновляет класс и записывает аннотации в файл.
        #================================================================
        def save_box(self, class_entry):
            # Получение нового класса из поля ввода
            new_class = class_entry.get().strip()
            if not new_class:
                new_class = "unknown"
            # Обновление класса текущего бокса
            _, x1, y1, x2, y2 = self.bboxes[self.current_box]
            self.bboxes[self.current_box] = (new_class, x1, y1, x2, y2)
            # Запись всех боксов в файл аннотации
            annotation_path = os.path.join(self.annotations_dir, 
                                         self.image_files[self.index].replace('.jpg', '.txt'))
            with open(annotation_path, 'w') as f:
                for class_name, x1, y1, x2, y2 in self.bboxes:
                    f.write(f"{class_name} {x1} {y1} {x2} {y2}\n")
            # Закрытие окна редактирования
            self.edit_window.destroy()
            self.edit_window = None
            self.current_box = None
            # Перерисовка изображения
            self.redraw_image()
        
        #================================================================
        # Функция обработки движения мыши. Подсвечивает бокс при наведении
        # и обновляет курсор для редактирования.
        #================================================================
        def on_mouse_motion(self, event):
            # Проверка наличия исходного изображения и bounding box'ов
            if self.original_frame is None or not self.bboxes:
                # Выход из функции, если данных нет
                return
            
            # Преобразование координат мыши в исходные координаты изображения
            orig_x = event.x / self.scale_factor
            orig_y = event.y / self.scale_factor
            # Вывод координат мыши на canvas для отладки
            print(f"Координаты мыши на canvas: ({event.x}, {event.y})")
            # Вывод текущего масштаба для отладки
            print(f"Масштаб: {self.scale_factor}")
            # Вывод координат в исходном изображении для отладки
            print(f"Координаты в исходном изображении: ({orig_x}, {orig_y})")
            
            # Создание копии изображения для обработки
            frame = self.original_frame.copy()
            highlighted = False
            
            # Проверка попадания курсора в бокс для подсветки
            for i, (class_name, x1, y1, x2, y2) in enumerate(self.bboxes):
                # Вывод координат проверяемого бокса для отладки
                print(f"Проверка бокса {class_name}: ({x1}, {y1}, {x2}, {y2})")
                if x1 <= orig_x <= x2 and y1 <= orig_y <= y2:
                    # Создание затемнённого слоя
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (100, 100, 100), -1)
                    alpha = self.transparency
                    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                    # Восстановление области внутри бокса
                    frame[y1:y2, x1:x2] = self.original_frame[y1:y2, x1:x2]
                    highlighted = True
                    # Вывод сообщения о подсветке для отладки
                    print(f"Подсвечен бокс {class_name}")
                    break
            
            # Отрисовка всех боксов
            for class_name, x1, y1, x2, y2 in self.bboxes:
                color = self.class_colors.get(class_name, (0, 255, 0))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{class_name}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Обновление курсора для редактирования
            for i, (class_name, x1, y1, x2, y2) in enumerate(self.bboxes):
                if x1 <= orig_x <= x2 and y1 <= orig_y <= y2:
                    if abs(orig_x - x1) < 10 and abs(orig_y - y1) < 10:
                        self.image_label.config(cursor="size_nw_se")
                    elif abs(orig_x - x2) < 10 and abs(orig_y - y2) < 10:
                        self.image_label.config(cursor="size_nw_se")
                    elif abs(orig_x - x1) < 10 and abs(orig_y - y2) < 10:
                        self.image_label.config(cursor="size_ne_sw")
                    elif abs(orig_x - x2) < 10 and abs(orig_y - y1) < 10:
                        self.image_label.config(cursor="size_ne_sw")
                    elif abs(orig_x - x1) < 10 or abs(orig_x - x2) < 10:
                        self.image_label.config(cursor="size_we")
                    elif abs(orig_y - y1) < 10 or abs(orig_y - y2) < 10:
                        self.image_label.config(cursor="size_ns")
                    else:
                        self.image_label.config(cursor="crosshair")
                    break
            else:
                self.image_label.config(cursor="crosshair")
            
            # Обновление изображения
            self.update_image(frame)
        
        #================================================================
        # Вспомогательная функция для перерисовки изображения.
        # Используется после изменения боксов.
        #================================================================
        def redraw_image(self):
            # Создание копии изображения
            frame = self.original_frame.copy()
            # Отрисовка всех боксов
            for class_name, x1, y1, x2, y2 in self.bboxes:
                color = self.class_colors.get(class_name, (0, 255, 0))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{class_name}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            # Обновление изображения
            self.update_image(frame)
        
        #================================================================
        # Вспомогательная функция для обновления изображения на canvas.
        # Преобразует массив в Tkinter-формат и отображает.
        #================================================================
        def update_image(self, frame):
            # Преобразование изображения в RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Создание объекта PIL Image
            img = Image.fromarray(frame_rgb)
            # Изменение размера с учётом масштаба
            new_width = int(img.width * self.scale_factor)
            new_height = int(img.height * self.scale_factor)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # Преобразование в формат Tkinter
            self.tk_image = ImageTk.PhotoImage(image=img)
            # Установка нового изображения
            self.image_label.configure(image=self.tk_image)
            self.image_label.image = self.tk_image
        
        # Остальные функции остаются без изменений для краткости
        def update_transparency(self, value):
            self.transparency = float(value)
            self.load_image()
        
        def update_position(self):
            self.canvas.coords(self.image_id, self.image_x, self.image_y)
            self.canvas.configure(scrollregion=(self.image_x, self.image_y, 
                                              self.image_x + self.tk_image.width(), 
                                              self.image_y + self.tk_image.height()))
            img_width = self.tk_image.width()
            img_height = self.tk_image.height()
            canvas_width = self.canvas.winfo_width() or 1024
            canvas_height = self.canvas.winfo_height() or 768
            center_x = self.image_x + canvas_width // 2
            center_y = self.image_y + canvas_height // 2
            self.relative_center_x = center_x / img_width if img_width > 0 else 0.5
            self.relative_center_y = center_y / img_height if img_height > 0 else 0.5
        
        def update_sensitivity(self, value):
            self.drag_sensitivity = float(value)
        
        def update_scale(self, value):
            old_center_x = self.image_x + self.tk_image.width() / 2
            old_center_y = self.image_y + self.tk_image.height() / 2
            self.scale_factor = float(value)
            self.load_image()
            new_width = self.tk_image.width()
            new_height = self.tk_image.height()
            self.image_x = old_center_x - new_width / 2
            self.image_y = old_center_y - new_height / 2
            self.update_position()
        
        def on_mouse_wheel(self, event):
            old_center_x = self.image_x + self.tk_image.width() / 2
            old_center_y = self.image_y + self.tk_image.height() / 2
            if event.delta > 0:
                self.scale_factor += 0.1
            else:
                self.scale_factor -= 0.1
            self.scale_factor = max(0.1, min(3.0, self.scale_factor))
            self.scale_slider.set(self.scale_factor)
            self.load_image()
            new_width = self.tk_image.width()
            new_height = self.tk_image.height()
            self.image_x = old_center_x - new_width / 2
            self.image_y = old_center_y - new_height / 2
            self.update_position()
        
        def next_image(self):
            if self.index < len(self.image_files) - 1:
                self.index += 1
                self.load_image()
        
        def prev_image(self):
            if self.index > 0:
                self.index -= 1
                self.load_image()
        
        def go_to_frame(self):
            input_value = self.frame_entry.get().strip()
            if not input_value:
                return
            if input_value.isdigit():
                frame_num = int(input_value)
                if 1 <= frame_num <= len(self.image_files):
                    self.index = frame_num - 1
                    self.load_image()
                else:
                    messagebox.showerror("Ошибка", f"Номер кадра должен быть от 1 до {len(self.image_files)}")
            else:
                matching_files = [f for f in self.image_files if input_value.lower() in f.lower()]
                if matching_files:
                    self.index = self.image_files.index(matching_files[0])
                    self.load_image()
                else:
                    messagebox.showerror("Ошибка", "Файл с таким именем не найден")
            self.frame_entry.delete(0, tk.END)

    # Создание главного окна приложения Tkinter
    root = tk.Tk()
    # Создание объекта класса ImageViewer с передачей главного окна и директорий
    viewer = ImageViewer(root, frames_dir, annotations_dir)
    # Запуск основного цикла обработки событий Tkinter
    root.mainloop()
    # Попытка закрытия окна после завершения работы
    try:
        # Закрытие главного окна
        root.destroy()
    # Обработка ошибки, если окно уже было закрыто
    except tk.TclError:
        # Вывод сообщения, если окно уже уничтожено
        print("Окно уже было уничтожено, пропускаем destroy")

# Установка пути к директории с кадрами
frames_directory = r"D:\ИИ_Команда\Проект_Ресторан19.11.2024\Блокноты\Скрипт для разметки\frames"
# Установка пути к директории с аннотациями
annotations_directory = r"D:\ИИ_Команда\Проект_Ресторан19.11.2024\Блокноты\Скрипт для разметки\annotations"
# Вызов функции просмотра аннотированных кадров с указанными директориями
view_annotated_frames(frames_directory, annotations_directory)