import time
from persistent_cache.persistent_cache import persistent_cache


@persistent_cache()
def slow_func(a, b=1):
    # This function takes long time to compute.
    # It contains comments, empty lines and prints.
    print("...")

    time.sleep(30)
    return a + b


if __name__ == "__main__":
    # Run this script twice.
    print(slow_func(1, b=2))

    # @persistent_cache() is a persistent functools.cache.

    # Notes:
    # minify_code(inspect.getsource(slow_func)) will be hashed to check if the code is changed.
    # If the code is changed, then we consider the previous caches obsolete.
    # We do not track changes made on the functions that are called in slow_func!
    # print(slow_func(1, 2, 3, d=4, e=5, use_cache=False)) for disabling the cache. (It will disable both reading and writing.)
    # More flexible usage: @persistent_cache(dir="caches", remove_obsolete=True, ignore_prints=True)
    # See __init__.py if the function returns some values which cannot be pickled.


    """
    Example usages include the following:
    
    Pause and continue:
    for a in range(50):
        for b in range(50):
            slow_func_that_writes_to_files(a, b)
    This loop takes a day to finish. I can terminate (pause) the program anytime I need. Then I can run again (continue).
    
    Batch processing:
    Maybe I want to visualize the results of calc. I can perform these computations during my sleep. When I start working, I can quickly run:
    for a in range(1000):
        x = calc(a)
        display(x)
    This may be a Jupyter Notebook. I can re-run it fast (Maybe for demonstration purposes).
    
    Interactive experiments:
    In an interactive shell (or a Jupyter Notebook), I can do many experiments using slow_func. Inputs will sometimes repeat.
    result = match_images("img-3.png", "img-7.png")  # Maybe I already did this before. 
        
    """
