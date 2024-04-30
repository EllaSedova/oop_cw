import random
import threading
import time


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
            start_time_offset = random.randint(0, 360)  # Случайное время от 0 до 1 часа
            event_start_time = time.time() + start_time_offset  # Время начала события
            self.events_final.append((event, event_start_time))  # Сохранение события и времени начала
            #print('events.append', event_start_time)
            #print(f"Событие '{event.name}' начнется в {time.strftime('%H:%M:%S', time.localtime(event_start_time))}")
        print("Генерация событий завершена.")

        # Сортировка событий по времени начала
        self.events_final.sort(key=lambda x: x[1])
        # Вывод окончательно отсортированного списка событий
        print("Окончательный список событий:")
        for event, start_time in self.events_final:
            print(f"Событие '{event.name}' начнется в {time.strftime('%H:%M:%S', time.localtime(start_time))} '{event.duration}'")

    def start(self):
        def event_tracking(event, event_start_time):
            event_end_time = event_start_time + event.duration
            print(
                f"Событие '{event.name}' начнется в {time.strftime('%H:%M:%S', time.localtime(event_start_time))} и закончится в {time.strftime('%H:%M:%S', time.localtime(event_end_time))}")

            # Ожидание до начала события
            while time.time() < event_start_time:
                time.sleep(1)

            UserInterface.notify_event_start(event.name, event_start_time)

            # Ожидание до окончания события
            while time.time() < event_end_time:
                time.sleep(1)

            UserInterface.notify_event_end(event.name, event_end_time)

        # Создание и запуск потока для каждого события
        for event, event_start_time in self.events_final:
            event_thread = threading.Thread(target=event_tracking, args=(event, event_start_time))
            event_thread.start()

class UserInterface:
    @staticmethod
    def notify_event_start(event_name, start_time):
        print(f"НАЧАЛОСЬ Событие '{event_name}' началось в {time.strftime('%H:%M:%S', time.localtime(start_time))}")

    @staticmethod
    def notify_event_end(event_name, end_time):
        print(f"ЗАКОНЧИЛОСЬ Событие '{event_name}' закончилось в {time.strftime('%H:%M:%S', time.localtime(end_time))}")

def main():
    alarm = Alarm()
    alarm.load_parameters('parameters.txt')  # Загрузка параметров из файла
    alarm.generate_events(20)  # Генерация 20 случайных событий
    alarm.start()  # Начало отслеживания событий

if __name__ == "__main__":
    main()