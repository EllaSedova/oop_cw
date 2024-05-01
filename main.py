import copy
import random
import threading
import time
import tkinter as tk
from tkinter import ttk


class Event:
    def __init__(self, name, duration, done):
        self.name = name
        self.duration = duration
        self.__done = done
    
    def is_done(self):
        return self.__done

    def set_done(self, value):
        if isinstance(value, bool):
            self.__done = value
        else:
            raise ValueError("Значение должно быть булевым (True или False)")

class Manager:
    def __init__(self):
        self.events = []
        self.events_final = []

    def add_event(self, event):
        # Добавляет событие в массив событий
        self.events.append(event)
    
    def load_parameters(self, file_name):
        print("Загрузка параметров из файла...")
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                name, duration = line.strip().split(': ')
                event = Event(name, int(duration), False)
                self.add_event(event)
        print("Загрузка параметров завершена.")
        print("Загружено {} событий".format(len(self.events)))
        for e in self.events:
            print(e.name, e.duration, e.is_done())

    def generate_events(self, num_events):
        print(f"Генерация {num_events} случайных событий...")
        for _ in range(num_events):
            event = random.choice(self.events)
            event_copy = copy.deepcopy(event)  # Создаем глубокую копию события
            start_time_offset = random.randint(0, 360)  # случайное время от 0 до 1 минуты
            event_start_time = time.time() + start_time_offset  # время начала события
            self.events_final.append((event_copy, event_start_time))  # сохранение копии события и времени начала
        print("Генерация событий завершена.")

        # сортировка событий по времени начала
        self.events_final.sort(key=lambda x: x[1])
        # вывод окончательно отсортированного списка событий
        print("Окончательный список событий:")
        for event, start_time in self.events_final:
            print(f"Событие '{event.name}' начнется в {time.strftime('%H:%M:%S', time.localtime(start_time))} '{event.duration}' закончилось - '{event.is_done()}'")

class Alarm:
    def __init__(self, events):
        # self.events = []
        self.events_final = events
        self.running = False  # Переменная для отслеживания состояния будильника


    def start(self, gui):  # добавляем параметр gui
        self.running = True  # Установим флаг, что будильник включен

        def event_tracking(event_final):
            event, event_start_time = event_final  # Распаковываем кортеж
            event_end_time = event_start_time + event.duration
            print(
                f"Событие '{event.name}' начнется в {time.strftime('%H:%M:%S', time.localtime(event_start_time))} и закончится в {time.strftime('%H:%M:%S', time.localtime(event_end_time))}")

            # ожидание до начала события
            while time.time() < event_start_time:
                if not self.running:  # Проверяем, выключен ли будильник
                    return
                time.sleep(1)
            if event_start_time >= time.time()-1 and event_start_time <= time.time()+1:
                gui.notify_event_start(event)  # показать уведомление о начале события
                # ожидание до окончания события
                while time.time() < event_end_time:
                    if not self.running:  # Проверяем, выключен ли будильник
                        return
                    time.sleep(1)
            else:
                event.set_done(True)
                return

        # создание и запуск потока для каждого события
        for i in range(len(self.events_final)):
            if not self.events_final[i][0].is_done():
                event_thread = threading.Thread(target=event_tracking, args=(self.events_final[i],))
                event_thread.start()

    def stop(self):
        self.running = False  # Устанавливаем флаг, что будильник выключен


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Alarm GUI")

        self.clock_label = tk.Label(root, font=('Helvetica', 48), bg="white")  # Устанавливаем начальный фон за часами
        self.clock_label.pack(pady=20)

        self.events_frame = tk.Frame(root)
        self.events_frame.pack(pady=20)

        # Добавляем кнопку для включения/выключения будильника
        self.clock_label.config(bg="red")  # Изменяем цвет фона за часами
        self.toggle_button = tk.Button(root, text="Включить", command=self.toggle_alarm)
        self.toggle_button.pack()

        # Добавляем кнопку для открытия списка событий
        self.show_events_button = tk.Button(root, text="Показать события", command=self.show_events)
        self.show_events_button.pack()

        self.manager = Manager()
        self.manager.load_parameters('parameters.txt')  # загрузка параметров из файла
        self.manager.generate_events(20)  # генерация 20 случайных событий

        self.alarm = Alarm(self.manager.events_final)
        self.update_clock()

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def notify_event_start(self, event):
        event_label = tk.Label(self.events_frame, text=f"Началось событие '{event.name}'")
        event.set_done(True)
        event_label.pack(side="top", padx=5)  # размещаем сообщение о событии

        remaining_time_label = tk.Label(self.events_frame, text=f"Осталось времени: {event.duration} сек.")
        remaining_time_label.pack(side="top")  # размещаем таймер события

        def update_timer(duration):
            duration -= 1
            remaining_time_label.config(text=f"Осталось времени: {duration} сек.")
            if duration <= 0:
                event_label.pack_forget()  # скрыть сообщение о событии
                remaining_time_label.pack_forget()  # скрыть таймер
                return
            remaining_time_label.after(1000, update_timer, duration)  # обновить таймер через 1 секунду

        update_timer(event.duration)  # запустить таймер при старте события

    def toggle_alarm(self):
        if self.alarm.running:
            self.alarm.stop()  # Если будильник включен, выключаем его
            self.clock_label.config(bg="red")  # Изменяем цвет фона за часами
            self.toggle_button.config(text="Включить")  # Изменяем текст кнопки
        else:
            self.alarm.start(self)  # Если будильник выключен, включаем его
            self.clock_label.config(bg="green")  # Изменяем цвет фона за часами
            self.toggle_button.config(text="Выключить")  # Изменяем текст кнопки

    def show_events(self):
        events_window = tk.Toplevel(self.root)
        events_window.title("Список событий")

        columns = ("Название", "Время начала", "Время окончания", "Статус")
        events_tree = ttk.Treeview(events_window, columns=columns, show="headings")
        events_tree.pack(fill="both", expand=True)
        # Устанавливаем заголовки для столбцов
        for col in columns:
            events_tree.heading(col, text=col)

        # Создаем тег стиля для строки с событием, имеющим статус "Прошло"
        events_tree.tag_configure("passed_event", background="#FFDDDD")  # бледно красный цвет

        for event, start_time in self.alarm.events_final:
            start_time_str = time.strftime('%H:%M:%S', time.localtime(start_time))
            end_time_str = time.strftime('%H:%M:%S', time.localtime(start_time + event.duration))
            status = "Прошло" if event.is_done() else "Не прошло"
            # Вставляем данные события в таблицу
            if event.is_done():
                events_tree.insert("", "end", values=(event.name, start_time_str, end_time_str, status),
                                   tags=("passed_event",))
            else:
                events_tree.insert("", "end", values=(event.name, start_time_str, end_time_str, status))

        def update_events_list():
            for event in events_tree.get_children():
                events_tree.delete(event)
            for event, start_time in self.alarm.events_final:
                start_time_str = time.strftime('%H:%M:%S', time.localtime(start_time))
                end_time_str = time.strftime('%H:%M:%S', time.localtime(start_time + event.duration))
                status = "Прошло" if event.is_done() else "Не прошло"
                if event.is_done():
                    events_tree.insert("", "end", values=(event.name, start_time_str, end_time_str, status),
                                       tags=("passed_event",))
                else:
                    events_tree.insert("", "end", values=(event.name, start_time_str, end_time_str, status))

        update_events_list()

        def refresh_events_list():
            update_events_list()
            events_window.after(1000, refresh_events_list)

        refresh_events_list()

def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()