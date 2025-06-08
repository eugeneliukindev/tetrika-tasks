from __future__ import annotations

import inspect
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from inspect import Signature
    from typing import Any, Final


LOG_DEFAULT_FORMAT: Final[str] = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    level: int = logging.INFO,
    format_: str = LOG_DEFAULT_FORMAT,
    datefmt: str = LOG_DATE_FORMAT,
) -> None:
    logging.basicConfig(
        level=level,
        format=format_,
        datefmt=datefmt,
    )


log = logging.getLogger(__name__)


def strict[T, **P](func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        log.debug("Начата проверка типов для функции %s", func.__name__)
        sig: Signature = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()  # На случай, если есть значения по умолчанию (хотя по условию их нет)

        # Тут важно подметить, что если мы используем ленивую подгрузку аннотаций типов (from __future__ import annotations)
        # Или просто "..." То у нас через param.annotation в inspect аннотации будут как строки, а не как нужные нам типы
        type_hints: dict[str, Any] = inspect.get_annotations(
            func, eval_str=True
        )  # Можно использовать typing.get_type_hints
        log.debug("Типы параметров для %s: %s", func.__name__, type_hints)

        for name, value in bound_args.arguments.items():
            if name in type_hints:
                log.debug(
                    "Проверка аргумента '%s' (значение: %s) на соответствие типу %s", name, value, type_hints[name]
                )
                if not isinstance(value, type_hints[name]):
                    error_msg = "Аргумент '%s' должен быть типа %s, а не %s" % (
                        name,
                        type_hints[name].__name__,
                        type(value).__name__,
                    )

                    log.error(error_msg)
                    raise TypeError(error_msg)

        log.debug("Проверка типов для %s завершена успешно", func.__name__)
        result = func(*args, **kwargs)
        log.debug("Функция %s вернула: %s", func.__name__, result)
        return result

    return wrapper


@strict
def sum_two(a: int, b: int) -> int:
    log.debug("Вычисление суммы %d и %d", a, b)
    return a + b


if __name__ == "__main__":
    configure_logging()
    log.info("Запуск демонстрации проверки типов")
    log.info("Тест корректного случая: sum_two(1, 2)")
    print(sum_two(1, 2))  # >>> 3

    log.info("Тест некорректного случая: sum_two(1, 2.4)")
    print(sum_two(1, 2.4))  # >>> TypeError
