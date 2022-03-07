import inspect
import os
from functools import wraps
from .persistent_cache_utils import generate_cache_filename, load_result, save_result, create_text_file, directory_exists, file_exists, \
    delete_obsolete_caches_once, minify_code


def persistent_cache(dir="caches", remove_obsolete=True, ignore_prints=True):
    def cached_function(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            assert os.environ["PYTHONHASHSEED"] == "0", "Hash randomization must be disabled."
            use_cache = kwargs.pop("cache", True)  # function(..., cache=True) or function(..., cache=False). True by default.
            if use_cache:
                function_name = function.__name__
                function_hashcode = str(hash(minify_code(inspect.getsource(function), remove_prints=ignore_prints)))
                cache_filename = generate_cache_filename(*args, **kwargs)
                cache_directory = os.path.join(dir, function_name, function_hashcode)
                if directory_exists(cache_directory):
                    cache_path = os.path.join(cache_directory, cache_filename)
                    if file_exists(cache_path):
                        cached_result = load_result(cache_path)
                        return cached_result
                else:
                    create_text_file(os.path.join(dir, f"{function_name}_{function_hashcode}.py"), inspect.getsource(function))

            computed_result = function(*args, **kwargs)

            if use_cache:
                save_result(computed_result, dir, function_name, function_hashcode, cache_filename)
                if remove_obsolete:
                    delete_obsolete_caches_once(dir, function_name)

            return computed_result

        return wrapper
    return cached_function
