from RequestsManager import RequestsManager

_requests_manager = None

def getRequestManager():
    global _requests_manager
    if _requests_manager is None:
        _requests_manager = RequestsManager()
    return _requests_manager
