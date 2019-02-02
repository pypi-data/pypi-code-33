import tqdm
import numpy as np
import pickle
from yo_extensions import *
import os
from collections import OrderedDict
import copy
import sys


EXTENTION = '.kraken.pkl'


def unwrap(obj, prefix = '', result=None):
    if result is None:
        result = OrderedDict()
    if isinstance(obj, dict):
        for key, value in obj.items():
            unwrap(value,
                   prefix+('_' if prefix!='' else '')+str(key),
                   result)
    else:
        result[prefix] = obj
    return result


class IterationStatus(OrderedEnum):
    Failed = 0
    Success = 1
    Skipped = 2



class IterationResult:
    def __init__(self,
                 status : IterationStatus,
                 result: Optional[Any] = None,
                 condition: Optional[Any] = None,
                 exception_info: Optional[Any] = None
                 ):
        self.status = status
        self.result = result
        self.condition = condition
        self.exception_info = exception_info


class _IterClass:
    def __init__(self, method, cache_to_folder, handle_exception_callback):
        self.method = method
        self.cache_to_folder = cache_to_folder
        self.handle_exception_callback = handle_exception_callback


    def process(self, config: Any) -> Optional[IterationResult]:
        if self.cache_to_folder is not None:
            cache_path = os.path.join(self.cache_to_folder, str(config['iteration']) + EXTENTION)
            if os.path.isfile(cache_path):
                return IterationResult(IterationStatus.Skipped)

        condition = copy.deepcopy(config)

        value = None
        status = IterationStatus.Success
        exception = None

        if self.handle_exception_callback is None:
            value = self.method(**condition)
        else:
            try:
                value = self.method(**condition)
            except:
                exception = sys.exc_info()
                self.handle_exception_callback(condition)
                status = IterationStatus.Failed

        result = IterationResult(status,value,condition,exception)

        if self.cache_to_folder is not None:
            cache_path = os.path.join(self.cache_to_folder, str(config['iteration']) + EXTENTION)
            with open(cache_path, 'wb') as file:
                pickle.dump(result, file)
            return IterationResult(IterationStatus.Success)
        else:
            return result


def release(method: Callable,
            configs: Iterable,
            pandas_extractor : Callable[[Any,Any],pd.DataFrame] = lambda df, _ : df,
            shuffle: Union[bool, int] = False,
            handle_exception_callback: Optional[Callable[[Any],None]] = None,
            special_iterations: Optional[Iterable[int]] = None,
            cache_to_folder: Optional[str] = None,
            with_tqdm: bool =True,
            parallel_kwargs: Optional[Dict] = None) -> Union[pd.DataFrame,List[IterationResult]]:
    configs = (Query
               .en(configs)
               .select(copy.deepcopy)
               .with_indices()
               .foreach_and_continue(lambda z: z.item.update(iteration=z.index))
               .select(lambda z: z.item)
               .to_list()
               )

    if special_iterations is not None:
        special_iterations = list(special_iterations)
        configs = np.array(configs)
        configs = list(configs[special_iterations])

    shuffle_seed = None
    if not isinstance(shuffle,bool):
        shuffle_seed = shuffle
    elif shuffle:
        shuffle_seed = np.random.randint(0)

    if shuffle_seed is not None:
        configs = np.array(configs)
        permutation = np.random.RandomState(shuffle_seed).permutation(len(configs))
        configs = list(configs[permutation])

    if with_tqdm:
        configs = tqdm.tqdm_notebook(configs, total=len(configs))

    if cache_to_folder:
        print(os.path.abspath(cache_to_folder))
        os.makedirs(cache_to_folder, exist_ok=True)

    executor = _IterClass(method,cache_to_folder, handle_exception_callback)

    output = [] # type: Optional[List[IterationResult]]

    if parallel_kwargs is None:
        output = (
            Query
            .en(configs)
            .select(executor.process)
            .to_list()
        )
    else:
        output = (
            Query
            .en(configs)
            .parallel_select(executor.process,**parallel_kwargs)
            .to_list()
        )

    if cache_to_folder:
        return output
    else:
        if pandas_extractor is None:
            return output
        else:
            return combine_result(output,pandas_extractor)


def load_results_iter(folder: str, files=None) -> Iterable[IterationResult]:
    if files is None:
        files = [file for file in os.listdir(folder) if file.endswith(EXTENTION)]
    else:
        files = [str(f)+EXTENTION for f in files]
    for file in Query.en(files).feed(with_progress_bar()):
        with open(os.path.join(folder, file), 'rb') as f:
            yield pickle.load(f)


def load(folder,  pd_extractor = lambda df, _ : df, exclude_config_fields = None) -> Union[List[IterationResult],pd.DataFrame]:
    loading = load_results_iter(folder)
    if pd_extractor is None:
        return list(loading)
    else:
        return combine_result(loading,
            pd_extractor,
            exclude_config_fields
        )


def combine_result(results, pd_extractor = lambda df, _ : df, exclude_config_fields = None) -> pd.DataFrame:
    output = None
    conditions = []
    for result in results:
        if result.status!=IterationStatus.Success:
            continue
        condition = unwrap(result.condition)
        pd_result = pd_extractor(result.result, condition)
        pd_result['iteration'] = condition['iteration']
        if output is None:
            output = pd_result
        else:
            output = output.append(pd_result)
        if exclude_config_fields is not None:
            for field in exclude_config_fields:
                del condition[field]
        conditions.append(condition)

    conditions = pd.DataFrame(conditions)
    output = output.merge(conditions.set_index('iteration'), left_on='iteration',right_index=True)
    output = output.reset_index(drop=True)
    return output


def invoke(factory):
    kwargs = copy.deepcopy(factory)
    del kwargs['ctor']
    factory.instance = factory.ctor(**kwargs)
    factory.name = factory.ctor.__name__
    return factory
