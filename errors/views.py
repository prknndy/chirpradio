###
### Copyright 2010 The Chicago Independent Radio Project
### All Rights Reserved.
###
### Licensed under the Apache License, Version 2.0 (the "License");
### you may not use this file except in compliance with the License.
### You may obtain a copy of the License at
###
###     http://www.apache.org/licenses/LICENSE-2.0
###
### Unless required by applicable law or agreed to in writing, software
### distributed under the License is distributed on an "AS IS" BASIS,
### WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
### See the License for the specific language governing permissions and
### limitations under the License.
###

from errors.middleware import CATCHABLE

def _test_errorhandler(request):
    """URL for forcing an error during manual and automated testing.
    
    You can simulate the exception contained in the catchable tuple by 
    specifying their index on the query string.  For example:
    
    http://127.0.0.1:8000/errors/_test_errorhandler?type=0
    http://127.0.0.1:8000/errors/_test_errorhandler?type=1
    ...
    
    """
    if 'type' in request.GET:
        SimulatedException = CATCHABLE[int(request.GET['type'])][0]
    else:
        SimulatedException = lambda: RuntimeError(
            "When the moon shines on the 5th house on the 7th hour, "
            "your shoe laces will unravel.")
        
    raise SimulatedException()
