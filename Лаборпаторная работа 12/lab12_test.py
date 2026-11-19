"""Тесты лабораторной работы 12. Запуск: python -m unittest -v test_lab12"""

import asyncio
import contextlib
import io
import unittest
from unittest import mock

import lab12
from lab12 import Config, run_pipeline


async def quiet_run(data: list[dict], config: Config = Config()) -> lab12.PipelineResult:
    """Запускает конвейер без вывода в консоль."""
    with contextlib.redirect_stdout(io.StringIO()):
        async with asyncio.timeout(10):
            return await run_pipeline(data, config)


class PipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_1_all_records_valid(self) -> None:
        data = [{'student': 'А', 'grade': 70}, {'student': 'Б', 'grade': 40}]
        outcome = await quiet_run(data)
        self.assertEqual(len(outcome.results), 2)
        self.assertEqual(outcome.errors, [])

    async def test_2_empty_name(self) -> None:
        data = [{'student': '', 'grade': 90}, {'student': 'Б', 'grade': 80}]
        outcome = await quiet_run(data)
        self.assertEqual(len(outcome.errors), 1)
        self.assertIn('Не указано имя', outcome.errors[0])
        self.assertEqual(len(outcome.results), 1)

    async def test_3_grade_out_of_range(self) -> None:
        data = [
            {'student': 'А', 'grade': -1},
            {'student': 'Б', 'grade': 101},
            {'student': 'В', 'grade': 0},
            {'student': 'Г', 'grade': 100},
        ]
        outcome = await quiet_run(data)
        self.assertEqual(len(outcome.errors), 2)
        self.assertEqual(len(outcome.results), 2)

    async def test_4_queue_size_one(self) -> None:
        queue: asyncio.Queue = asyncio.Queue(maxsize=1)
        await queue.put(1)
        with self.assertRaises(TimeoutError):
            async with asyncio.timeout(0.2):
                await queue.put(2)  # производитель ждет свободного места
        data = [{'student': str(i), 'grade': 50 + i} for i in range(6)]
        outcome = await quiet_run(data, Config(queue_size=1))
        self.assertEqual(len(outcome.results), 6)  # данные не теряются

    async def test_5_one_and_two_consumers(self) -> None:
        data = [{'student': str(i), 'grade': 60} for i in range(8)]
        one = await quiet_run(data, Config(consumers=1))
        two = await quiet_run(data, Config(consumers=2))
        self.assertLess(two.elapsed, one.elapsed)

    async def test_6_exception_in_process(self) -> None:
        async def broken(record: dict, attempt: int) -> dict:
            raise RuntimeError('сбой')

        data = [{'student': str(i), 'grade': 60} for i in range(4)]
        with mock.patch.object(lab12, 'process', broken):
            outcome = await quiet_run(data)  # join завершается, зависания нет
        self.assertEqual(len(outcome.errors), 4)
        self.assertEqual(outcome.results, [])

    async def test_7_empty_input(self) -> None:
        outcome = await quiet_run([])
        self.assertEqual(lab12.average_grade(outcome.results), 0.0)
        self.assertEqual(outcome.results, [])
        self.assertEqual(outcome.errors, [])

    async def test_8_retry_after_temporary_error(self) -> None:
        data = [{'student': 'А', 'grade': 80, 'fail_times': 2}]
        outcome = await quiet_run(data)
        self.assertEqual(len(outcome.results), 1)
        self.assertEqual(outcome.errors, [])

    async def test_9_timeout_after_attempts(self) -> None:
        data = [{'student': 'А', 'grade': 80, 'delay': 1.0}]
        outcome = await quiet_run(data, Config(timeout=0.1, max_attempts=2))
        self.assertEqual(outcome.results, [])
        self.assertIn('превышено время ожидания', outcome.errors[0])


if __name__ == '__main__':
    unittest.main(verbosity=2)