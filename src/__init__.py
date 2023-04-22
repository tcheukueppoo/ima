from .image   import Image
from .search  import Search
from .options import ParseOptions
from .        import exceptions
from .utils   import (
    get_base_url,
    # ...
)

def main():
    opts, args = ParseOptions()
    print("options: ")
    print(opts)
    print("args: ")
    print(args)
