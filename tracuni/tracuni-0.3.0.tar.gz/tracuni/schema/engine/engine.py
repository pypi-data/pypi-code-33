#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Обработчик схем

    Управление схемами извлечения данных для различных вариантов точек

    Используется три уровня схем (в порядке убывания приоритета):
        * пользовательская на конкретную точку
            передаётся как инициализирующий параметр декоратора
        * пользовательская карта схем
            передаётся от пользователя как инициализирующий параметр
            адаптера библиотеки. Передаётся в процессор в момент его
            создания при инициализации декоратора
        * стандартная карта схем
            импортируется из schema.standard
"""

from collections import namedtuple
import inspect

from typing import (
    TYPE_CHECKING,
    Any,
    Tuple,
    Generator,
    MutableSequence,
    Callable)

from tracuni.define.type import (
    Rule,
    DestinationSection,
    PipelineTee,
    PointContext,
)
from tracuni.define import errors as err
from tracuni.misc.select_coroutine import async_decorator

from .cache import SchemaEngineCache
from .feed import SchemaEngineFeed

if TYPE_CHECKING:
    from typing import List  # noqa
    from typing import Union  # noqa
    from typing import Optional  # noqa
    from tracuni.define.type import Destination  # noqa
    from tracuni.define.type import MethodNameToStage  # noqa
    from tracuni.define.type import (  # noqa
        RuleSet,
        Extractors,
    )
    from tracuni.define.type import Stage
    from tracuni.adapter import AdapterType  # noqa


class SchemaEngine(metaclass=SchemaEngineCache):
    """Обработчик схемы. Связь варианта со схемой извлечения данных

        * Обращается к экземпляру поставщика схем для получения списка
        применяемых правил, разбитых на фазы и дополнительных данных
        * Для заданного экземпляра объекта доступа к точке извлекает и
        возвращает данные согласно правилам и состоянию объекта доступа.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.schema_feed = None  # type: SchemaEngineFeed
        self.adapter = None  # type: AdapterType
        self.extractors = None  # type: Extractors

        self.method_to_stage = None  # type: Optional[MethodNameToStage]
        self.skip_secret_destinations = (
            None  # type: Optional[MutableSequence[Destination]]
        )
        self.secret_mask_method_name = None  # type: Optional[str]

        self._args = args
        self._kwargs = kwargs

    def observe_state_change(self, adapter: 'AdapterType'):
        """
            Обработчик схемы создаётся до того, как отработает фабрика адаптера,
            соответственно вторая часть инициализации должна проходить после
            того, как адаптер будетсоздан

        Parameters
        ----------
        adapter
            только что созданный экземпляр адаптера
        """
        self.adapter = adapter
        self._kwargs['custom_schema'] = adapter.custom_schema
        self.schema_feed = schema_feed = SchemaEngineFeed(
            *self._args,
            **self._kwargs,
        )
        self.extractors = schema_feed.parse()  # type: Extractors

        self.skip_secret_destinations = (
            schema_feed.get_skip_secret()
        )  # type: MutableSequence[Destination]

        self.secret_mask_method_name = (
            schema_feed.get_secret_mask_method_name()
        )  # type: str

    def is_tracer_disabled(self):
        return self.adapter is None

    @async_decorator
    def extract(self,
                point_context: PointContext,
                stage: 'Stage',
                ) -> Generator[Any, None, PointContext]:
        """Метод запускающий процесс получения и изменения исходных данных и
        данных участка для указанной точки и этапа

        Parameters
        ----------
        point_context
            Ссылки на данные точки и окружения с ключами, совпадающими с
            наименованиями секций источников и назначения.
        stage
            Фаза, к которой привязан обратившийся метод

        Returns
        -------
            Изменённый контекст точки
        """
        if stage is None:
            return point_context
        extractors = (
            self.extractors.get(stage) or []
        )  # type: Union[RuleSet, List]

        for extractor in extractors:
            extracted = yield from self._extract_values(
                extractor,
                point_context
            )
            if extracted is None or not len(extracted):
                continue
            point_context = self._pipe_values(
                extractor,
                point_context,
                extracted,
            )

        return point_context

###############################################################################
# Area privata

    @staticmethod
    @async_decorator
    def _extract_values(
        extractor: Rule,
        point_context: PointContext
    ) -> Generator[Any, None, Tuple[Any, ...]]:
        """

        Parameters
        ----------
        extractor
            Применяемое в данный момент правило извлечения.
        point_context
            Структура, хранящая ссылки на контекст источник данных и уже
            собранные данные. Нужна для получения контекста источника.
        Returns
        -------
            Собранные исходные значения
        """
        val = []
        # правило может содержать несколько источников
        for origin in extractor.origins:
            extracted = None

            # получаем ссылку на источник или пропускаем источник
            section_ref = getattr(
                point_context, origin.section.name.lower(), None
            )
            if section_ref is None:
                continue

            # метод извлечения, либо функция, которой передается ссылка на
            # источник, а она возвращает значение по своему разумению
            getter = origin.getter
            if callable(getter):
                is_yields = inspect.isgeneratorfunction(getter)
                if is_yields:
                    extracted = yield from getter(section_ref)
                else:
                    extracted = getter(section_ref)
            # либо метод извлечения может быть указан строкой, тогда это или
            # элемент словаря, или атрибут объекта
            elif isinstance(getter, str):
                # отдельный случай прямой слэш - возращается исходный объект
                if getter == '/':
                    extracted = section_ref
                elif isinstance(section_ref, dict):
                    extracted = section_ref.get(getter)
                else:
                    extracted = getattr(section_ref, getter, None)
            elif getter is None:
                extracted = section_ref

            # if extracted is None:
            #     continue
            val.append(extracted)

        # данные, полученные из всех указанных в правиле источников,
        # собираются в кортеж
        return tuple(val)

    def _pipe_values(
        self,
        extractor: Rule,
        point_context: PointContext,
        val: Any,
    ) -> PointContext:
        """Конвейер обрботки извлекаемых значений

            Вызывает цепочку методов передавая от одного к другому данные в
            текущем состоянии, обрабатывает дополнительную команду ответвления
            данных и список подавленных обработчиков.

        Parameters
        ----------
        extractor
            Правило извелечения
        val
            Данные в текущем состоянии
        point_context
            Структура, хранящая ссылки на контекст источник данных и уже
            собранные данные.
        Returns
        -------
            Изменённый контекст точки
        """

        for process in extractor.pipeline:
            if (
                callable(process)
                and
                not self._skip_secret(process, extractor.destination)
            ):
                new_val = process(val)

                if isinstance(new_val, PipelineTee):
                    for section, new_values in new_val.side_story.items():
                        s_name = section.name.lower()
                        old_values = getattr(point_context, s_name, None)
                        if isinstance(old_values, dict):
                            old_values.update(new_values)
                        elif isinstance(old_values, list):
                            old_values.append(new_values)
                        else:
                            # noinspection PyProtectedMember
                            point_context = PointContext(**{
                                **point_context._asdict(),
                                **new_values,
                            })
                    new_val = new_val.main_story
                val = new_val

        point_context = self._update_point_context(
            extractor,
            point_context,
            val
        )
        return point_context

    @staticmethod
    def _update_point_context(
        extractor: Rule,
        point_context: PointContext,
        val: Any,
    ) -> PointContext:
        """

        Parameters
        ----------
        extractor
            Правило из которого берутся данныи по назначению записи
        point_context
            Модифицируемый контекст точки, вернется к держателю точки и
            будет обработан на его стороне
        val
            Значение которое надо отправить в контекст

        Returns
        -------
            Изменённый контекст точки
        """

        # noinspection PyProtectedMember
        dest = point_context._asdict().get(
            extractor.destination.section.name.lower()
        )
        if dest is None:
            return point_context
        elif isinstance(dest, MutableSequence):
            dest.append(val)
        elif isinstance(dest, dict):
            dest[extractor.destination.name] = val
        elif "PointArguments" in str(type(dest)):
            # noinspection PyProtectedMember
            old_vals = dest._asdict()
            new_args = namedtuple("PointArguments", old_vals)(**{
                **old_vals,
                extractor.destination.name: {
                    **(old_vals.get(
                        extractor.destination.name,
                        {}
                    ) or {}),
                    **val,
                }
            })
            # noinspection PyProtectedMember
            point_context = PointContext(**{
                **point_context._asdict(),
                "point_args": new_args,
            })
        else:
            try:
                if extractor.destination.name:
                    setattr(dest, extractor.destination.name, val)
            except AttributeError:
                raise err.ProcessorExtractCantSetDestinationAttr

        return point_context

    def _skip_secret(self, fn: Callable, destination: "Destination") -> bool:
        """Проверка условия пропуска обработчика маскирования по команде

        Parameters
        ----------
        fn
            Обработчик
        destination
            Описание назначения для проверки применения команды

        Returns
        -------
            Флаг надо ли запускать данный обработчик
        """
        fn_name = getattr(fn, '__name__', '')
        if self.secret_mask_method_name != fn_name:
            return False

        return (
            (
                Destination(DestinationSection.ALL, "")
                in
                self.skip_secret_destinations
            )
            or
            destination in self.skip_secret_destinations
        )
