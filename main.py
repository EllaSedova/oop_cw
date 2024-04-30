import random
import threading
import time
import tkinter as tk


class Event:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration


class Alarm:
    def __init__(self):
        self.events = []
        self.events_final = []

    def load_parameters(self, file_name):
        print("Загрузка параметров из файла...")
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                name, duration = line.strip().split(': ')
                event = Event(name, int(duration))
                self.events.append(event)
        print("Загрузка параметров завершена.")
        print("Загружено {} событий".format(len(self.events)))
        for e in self.events:
            print(e.name, e.duration)

    def generate_events(self, num_events):
        print(f"Генерация {num_events} случайных событий...")
        for _ in range(num_events):
            event = random.choice(self.events)
            start_time_offset = random.randint(0, 360)  # случайное время от 0 до 1 минуты
            event_start_time = time.time() + start_time_offset  # время начала события
            self.events_final.append((event, event_start_time))  # сохранение события и времени начала
        print("Генерация событий завершена.")

        # сортировка событий по времени начала
        self.events_final.sort(key=lambda x: x[1])
        # вывод окончательно отсортированного списка событий
        print("Окончательный список событий:")
        for event, start_time in self.events_final:
            print(f"Событие '{event.name}' начнется в {time.strftime('%H:%M:%S', time.localtime(start_time))} '{event.duration}'")

    def start(self, gui):  # добавляем параметр gui
        def event_tracking(event, event_start_time):
            event_end_time = event_start_time + event.duration
            print(
                f"Событие '{event.name}' начнется в {time.strftime('%H:%M:%S', time.localtime(event_start_time))} и закончится в {time.strftime('%H:%M:%S', time.localtime(event_end_time))}")

            # ожидание до начала события
            while time.time() < event_start_time:
                time.sleep(1)

            gui.notify_event_start(event)  # показать уведомление о начале события

            # ожидание до окончания события
            while time.time() < event_end_time:
                time.sleep(1)

            gui.notify_event_end(event.name)  # показать уведомление о завершении события

        # создание и запуск потока для каждого события
        for event, event_start_time in self.events_final:
            event_thread = threading.Thread(target=event_tracking, args=(event, event_start_time))
            event_thread.start()


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Alarm GUI")

        self.clock_label = tk.Label(root, font=('Helvetica', 48))
        self.clock_label.pack(pady=20)

        self.events_frame = tk.Frame(root)
        self.events_frame.pack(pady=20)

        self.alarm = Alarm()
        self.alarm.load_parameters('parameters.txt')  # загрузка параметров из файла
        self.alarm.generate_events(20)  # генерация 20 случайных событий
        self.alarm.start(self)  # начало отслеживания событий с передачей экземпляра GUI

        self.update_clock()

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def notify_event_start(self, event):
        event_label = tk.Label(self.events_frame, text=f"Началось событие '{event.name}'")
        event_label.pack(side="top", padx=5)  # размещаем сообщение о событии

        remaining_time_label = tk.Label(self.events_frame, text=f"Осталось времени: {event.duration} сек.")
        remaining_time_label.pack(side="top")  # размещаем таймер события

        def update_timer():
            event.duration -= 1
            remaining_time_label.config(text=f"Осталось времени: {event.duration} сек.")
            if event.duration <= 0:
                event_label.pack_forget()  # скрыть сообщение о событии
                remaining_time_label.pack_forget()  # скрыть таймер
                return
            remaining_time_label.after(1000, update_timer)  # обновить таймер через 1 секунду

        update_timer()  # запустить таймер при старте события
    def notify_event_end(self, event_name):
        event_label = tk.Label(self.events_frame, text=f"Закончилось событие '{event_name}'")
        event_label.pack()


def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
