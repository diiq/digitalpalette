from api.models.pigment import Pigment

import inspect
import sys

all_models = [cls for _, cls in
              inspect.getmembers(sys.modules[__name__],
                                 inspect.isclass)]
