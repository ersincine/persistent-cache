import os
import shutil
import pickle
import io
import tokenize
import re
import inspect
from functools import wraps
from functools import lru_cache


"""
import cv2 as cv
import copyreg


def _pickle_keypoints(kp):
    return cv.KeyPoint, (*kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id)


def _pickle_dmatches(dmatch):
    return cv.DMatch, (dmatch.queryIdx, dmatch.trainIdx, dmatch.imgIdx, dmatch.distance)


copyreg.pickle(cv.KeyPoint().__class__, _pickle_keypoints)
copyreg.pickle(cv.DMatch().__class__, _pickle_dmatches)

# Uncomment these if needed.
# Add more if needed.

"""


def _minify_code(code, remove_prints=True):
    # Based on https://stackoverflow.com/a/62074206
    # Remove empty lines, comments, etc. + prints if desired.
    if remove_prints:
        code = "\n".join(line for line in code.splitlines() if not re.sub(r"\s+", "", line).startswith("print("))
    io_obj = io.StringIO(code)
    minified = ""
    prev_token_type = tokenize.INDENT
    last_line_no = -1
    last_col = 0
    for token in tokenize.generate_tokens(io_obj.readline):
        token_type, token_string, (start_line, start_col), (end_line, end_col), _ = token
        if start_line > last_line_no:
            last_col = 0
        if start_col > last_col:
            minified += " " * (start_col - last_col)
        if token_type != tokenize.COMMENT:
            if token_type == tokenize.STRING:
                if prev_token_type not in (tokenize.INDENT, tokenize.NEWLINE) and start_col > 0:
                    minified += token_string
            else:
                minified += token_string
        prev_token_type = token_type
        last_col = end_col
        last_line_no = end_line
    minified = "\n".join(line for line in minified.splitlines() if line.strip())
    return minified


def _hashcode(obj):
    if obj.__class__.__module__ == 'builtins':
        return hash(obj)
    """
    # Uncomment this if needed.
    import numpy as np
    if isinstance(obj, np.array):
        return hash(obj.data)
    """
    # TODO: Add more types.
    # TODO: isinstance(val, types.FunctionType) -> str(hash(inspect.getsource(function)))
    # (Also use for generate_cache_path)
    assert False


def _generate_cache_filename(*args, **kwargs):
    names = list(sorted(kwargs))   # Permutation invariance for kwargs
    objects_to_hash = tuple(list(args) + names + [kwargs[x] for x in names])
    cache_id = hash(objects_to_hash)
    cache_filename = str(cache_id) + ".data"
    return cache_filename


def _load_result(cache_path):
    # main_dir/function_name/function_hashcode/cache_filename
    assert os.path.isfile(cache_path)
    f = open(cache_path, "rb")
    cached_result = pickle.load(f)
    f.close()
    #print("LOADED:", cache_path)
    return cached_result


def _save_result(computed_result, main_dir, function_name, function_hashcode, cache_name):
    directory = os.path.join(main_dir, function_name, function_hashcode)
    os.makedirs(directory, exist_ok=True)

    path = os.path.join(directory, cache_name)
    assert not os.path.isfile(path)

    f = open(path, "wb")
    pickle.dump(computed_result, f)
    f.close()


@lru_cache(maxsize=None)
def _directory_exists(path):
    return os.path.isdir(path)


@lru_cache(maxsize=None)
def _file_exists(path):
    return os.path.isfile(path)


@lru_cache(maxsize=None)
def _delete_obsolete_caches_once(main_dir, function_name):
    def _delete_obsolete_caches():
        # function_name = function.__name__
        path = os.path.join(main_dir, function_name)
        if os.path.isdir(path):
            function_versions = [(root, os.path.getmtime(root)) for root, _, _ in os.walk(path)][1:]
            last_modified_dir = max(function_versions, key=lambda x: x[1])[0]
            for function_version_dir, _ in function_versions:
                if function_version_dir != last_modified_dir:
                    shutil.rmtree(function_version_dir)
                    function_hashcode = function_version_dir[function_version_dir.rfind("/") + 1:]
                    os.remove(os.path.join(main_dir, function_name + "_" + function_hashcode + ".py"))

    _delete_obsolete_caches()


def _create_text_file(path, content="", encoding="utf8"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding=encoding) as f:
        f.write(content)


def persistent_cache(dir="caches", remove_obsolete=True, ignore_prints=True):
    def cached_function(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            assert os.environ["PYTHONHASHSEED"] == "0", "Hash randomization must be disabled."
            use_cache = kwargs.pop("cache", True)  # function(..., cache=True) or function(..., cache=False). True by default.
            if use_cache:
                function_name = function.__name__
                function_hashcode = str(hash(_minify_code(inspect.getsource(function), remove_prints=ignore_prints)))
                cache_filename = _generate_cache_filename(*args, **kwargs)
                cache_directory = os.path.join(dir, function_name, function_hashcode)
                if _directory_exists(cache_directory):
                    cache_path = os.path.join(cache_directory, cache_filename)
                    if _file_exists(cache_path):
                        cached_result = _load_result(cache_path)
                        return cached_result
                else:
                    _create_text_file(os.path.join(dir, f"{function_name}_{function_hashcode}.py"), inspect.getsource(function))

            computed_result = function(*args, **kwargs)

            if use_cache:
                _save_result(computed_result, dir, function_name, function_hashcode, cache_filename)
                if remove_obsolete:
                    _delete_obsolete_caches_once(dir, function_name)

            return computed_result

        return wrapper
    return cached_function
