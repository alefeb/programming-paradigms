"""Лабораторная работа 12. Асинхронный конвейер обработки оценок студентов."""

import asyncio
import time
from dataclasses import dataclass

SENTINEL = object()

# Учебный набор данных. Две последние записи содержат ошибки.
RECORDS: list[dict] = [
    {'student': 'Алия', 'grade': 85},
    {'student': 'Дамир', 'grade': 54},
    {'student': 'Руслан', 'grade': 78},
    {'student': '', 'grade': 91},
    {'student': 'Мадина', 'grade': 105},
]

# Дополнительные записи для проверки повторов и тайм аута.
# fail_times: сколько первых попыток завершатся временной ошибкой.
# delay: время имитации сохранения в секундах.
EXTRA_RECORDS: list[dict] = [
    {'student': 'Айгерим', 'grade': 92, 'fail_times': 1},
    {'student': 'Бекзат', 'grade': 67, 'delay': 1.0},
    {'student': 'Томирис', 'grade': 60},
]


class TemporaryError(Exception):
    """Временная ошибка сервиса. Операцию нужно повторить."""


@dataclass(frozen=True)
class Config:
    """Параметры конвейера."""

    consumers: int = 2
    queue_size: int = 3
    timeout: float = 0.6
    max_attempts: int = 3


@dataclass
class PipelineResult:
    """Итог одного запуска конвейера."""

    results: list[dict]
    errors: list[str]
    elapsed: float


async def producer(queue: asyncio.Queue, data: list[dict], consumers: int) -> None:
    """Кладет записи в очередь и отправляет сигнал завершения каждому потребителю."""
    for record in data:
        await asyncio.sleep(0.15)  # имитация получения из сервиса
        await queue.put(record)
        print('Получено:', record)
    for _ in range(consumers):
        await queue.put(SENTINEL)


def validate(record: dict) -> None:
    """Проверяет имя студента и диапазон оценки."""
    student = str(record.get('student', '')).strip()
    grade = record.get('grade')
    if not student:
        raise ValueError('Не указано имя')
    if not isinstance(grade, (int, float)) or not 0 <= grade <= 100:
        raise ValueError('Оценка должна быть от 0 до 100')


async def process(record: dict, attempt: int) -> dict:
    """Имитирует сохранение записи и определяет статус."""
    await asyncio.sleep(record.get('delay', 0.25))  # имитация сохранения
    if attempt <= record.get('fail_times', 0):
        raise TemporaryError('Сервис сохранения недоступен')
    validate(record)
    grade = record['grade']
    return {
        'student': record['student'],
        'grade': grade,
        'status': 'зачет' if grade >= 60 else 'незачет',
    }


async def process_with_retry(record: dict, config: Config) -> dict:
    """Вызывает process с тайм аутом и ограниченным числом повторов."""
    attempt = 0
    while True:
        attempt += 1
        try:
            async with asyncio.timeout(config.timeout):
                return await process(record, attempt)
        except (TemporaryError, TimeoutError) as error:
            if attempt >= config.max_attempts:
                raise
            print(f'Повтор {attempt} для {record.get("student")!r}: '
                  f'{type(error).__name__}')
            await asyncio.sleep(0.05 * attempt)


async def consumer(
    name: str,
    queue: asyncio.Queue,
    out_queue: asyncio.Queue,
    errors: list[str],
    config: Config,
) -> None:
    """Берет записи из очереди, обрабатывает и передает результат дальше."""
    while True:
        item = await queue.get()
        try:
            if item is SENTINEL:
                print(name, 'завершен')
                return
            try:
                result = await process_with_retry(item, config)
            except ValueError as error:
                errors.append(f'{item}: {error}')
            except TemporaryError:
                errors.append(f'{item}: сервис недоступен после '
                              f'{config.max_attempts} попыток')
            except TimeoutError:
                errors.append(f'{item}: превышено время ожидания')
            except Exception as error:  # непредвиденная ошибка не останавливает join
                errors.append(f'{item}: непредвиденная ошибка {error!r}')
            else:
                await out_queue.put(result)
                print(name, 'обработал', result)
        finally:
            queue.task_done()


async def saver(out_queue: asyncio.Queue, storage: list[dict]) -> None:
    """Третья стадия. Сохраняет результаты в хранилище."""
    while True:
        result = await out_queue.get()
        try:
            if result is SENTINEL:
                return
            await asyncio.sleep(0.05)  # имитация записи в хранилище
            storage.append(result)
        finally:
            out_queue.task_done()


async def run_pipeline(data: list[dict], config: Config = Config()) -> PipelineResult:
    """Запускает конвейер producer, queue, consumer, queue, saver."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=config.queue_size)
    out_queue: asyncio.Queue = asyncio.Queue(maxsize=config.queue_size)
    storage: list[dict] = []
    errors: list[str] = []
    started = time.perf_counter()

    save_task = asyncio.create_task(saver(out_queue, storage))
    workers = [
        asyncio.create_task(consumer(f'worker-{i}', queue, out_queue, errors, config))
        for i in range(1, config.consumers + 1)
    ]
    await producer(queue, data, config.consumers)
    await queue.join()
    await asyncio.gather(*workers)

    await out_queue.put(SENTINEL)
    await out_queue.join()
    await save_task
    return PipelineResult(storage, errors, time.perf_counter() - started)


def average_grade(results: list[dict]) -> float:
    """Возвращает средний балл. Для пустого списка возвращает 0.0."""
    if not results:
        return 0.0
    return sum(item['grade'] for item in results) / len(results)


def print_report(outcome: PipelineResult) -> None:
    """Выводит итоговую статистику, ошибки и рейтинг."""
    print(f'Обработано: {len(outcome.results)}')
    print(f'Ошибок: {len(outcome.errors)}')
    print(f'Средний балл: {average_grade(outcome.results):.2f}')
    print(f'Время: {outcome.elapsed:.2f} с')
    for error in outcome.errors:
        print('Ошибка:', error)
    print('Рейтинг:')
    ranking = sorted(outcome.results, key=lambda item: item['grade'], reverse=True)
    for place, item in enumerate(ranking, start=1):
        print(f'  {place}. {item["student"]}: {item["grade"]} ({item["status"]})')


async def compare_consumers(data: list[dict]) -> None:
    """Сравнивает время работы с одним и двумя потребителями."""
    import contextlib
    import io

    times: dict[int, float] = {}
    for count in (1, 2):
        with contextlib.redirect_stdout(io.StringIO()):
            outcome = await run_pipeline(data, Config(consumers=count))
        times[count] = outcome.elapsed
        print(f'Потребителей: {count}, время: {outcome.elapsed:.2f} с')
    print(f'Ускорение: {times[1] / times[2]:.2f} раза')


async def main() -> None:
    print('=== Базовый запуск ===')
    print_report(await run_pipeline(RECORDS))

    print('\n=== Повторы и тайм аут ===')
    print_report(await run_pipeline(RECORDS + EXTRA_RECORDS))

    print('\n=== Один и два потребителя ===')
    await compare_consumers(RECORDS + EXTRA_RECORDS[2:] * 3)


if __name__ == '__main__':
    asyncio.run(main())