tests = [
    {
        "intervals": {
            "lesson": [1594663200, 1594666800],
            "pupil": [1594663340, 1594663389, 1594663390, 1594663395, 1594663396, 1594666472],
            "tutor": [1594663290, 1594663430, 1594663443, 1594666473],
        },
        "answer": 3117,
    },
    {
        "intervals": {
            "lesson": [1594702800, 1594706400],
            "pupil": [
                1594702789,
                1594704500,
                1594702807,
                1594704542,
                1594704512,
                1594704513,
                1594704564,
                1594705150,
                1594704581,
                1594704582,
                1594704734,
                1594705009,
                1594705095,
                1594705096,
                1594705106,
                1594706480,
                1594705158,
                1594705773,
                1594705849,
                1594706480,
                1594706500,
                1594706875,
                1594706502,
                1594706503,
                1594706524,
                1594706524,
                1594706579,
                1594706641,
            ],
            "tutor": [1594700035, 1594700364, 1594702749, 1594705148, 1594705149, 1594706463],
        },
        "answer": 3577,
    },
    {
        "intervals": {
            "lesson": [1594692000, 1594695600],
            "pupil": [1594692033, 1594696347],
            "tutor": [1594692017, 1594692066, 1594692068, 1594696341],
        },
        "answer": 3565,
    },
]


def appearance(intervals: dict[str, list[int]]) -> int:
    lesson_start, lesson_end = intervals["lesson"][0], intervals["lesson"][1]

    def process_intervals(times):
        # Разбиваем список на пары (start, end)
        intervals_list = []
        for i in range(0, len(times), 2):
            start = times[i]
            end = times[i + 1]
            # Убедимся, что интервал корректен (start < end)
            if start < end:
                # Обрезаем интервал по границам урока
                start = max(start, lesson_start)
                end = min(end, lesson_end)
                if start < end:
                    intervals_list.append((start, end))
        # Сортируем интервалы по времени начала
        intervals_list.sort()
        # Объединяем пересекающиеся интервалы
        merged = []
        for interval in intervals_list:
            if not merged:
                merged.append(interval)
            else:
                last_start, last_end = merged[-1]
                current_start, current_end = interval
                if current_start <= last_end:
                    # Пересекаются, объединяем
                    new_start = last_start
                    new_end = max(last_end, current_end)
                    merged[-1] = (new_start, new_end)
                else:
                    merged.append(interval)
        return merged

    pupil_intervals = process_intervals(intervals["pupil"])
    tutor_intervals = process_intervals(intervals["tutor"])

    # Поиск пересечений между pupil и tutor
    total_time = 0
    i = j = 0
    while i < len(pupil_intervals) and j < len(tutor_intervals):
        pupil_start, pupil_end = pupil_intervals[i]
        tutor_start, tutor_end = tutor_intervals[j]

        # Находим пересечение
        start = max(pupil_start, tutor_start)
        end = min(pupil_end, tutor_end)
        if start < end:
            total_time += end - start

        # Переходим к следующему интервалу
        if pupil_end < tutor_end:
            i += 1
        else:
            j += 1

    return total_time


if __name__ == "__main__":
    for i, test in enumerate(tests):
        test_answer = appearance(test["intervals"])
        assert test_answer == test["answer"], f"Error on test case {i}, got {test_answer}, expected {test['answer']}"
