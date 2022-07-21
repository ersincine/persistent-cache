# persistent-cache
**@persistent_cache() is a persistent @functools.cache.**

Example usages include the following:
    
    
## Pause and continue

Let's say the loop below takes a day to finish. I can terminate (pause) the program anytime I need. Then I can run it again (continue).

    for a in range(50):
        for b in range(50):
            slow_func_that_writes_to_files(a, b)
            
## Batch processing

Maybe I want to visualize the results of calc. I can perform these computations during my sleep. When I start working, I can quickly run:

    for a in range(1000):
        x = calc(a)
        display(x)
    
## Interactive experiments

In an interactive shell (or a Jupyter Notebook), I can do many experiments calling slow functions. Inputs will sometimes repeat.

    result = match_images("img-3.png", "img-7.png")  # Maybe I already did this before. 
