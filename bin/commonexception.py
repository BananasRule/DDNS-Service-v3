## @exception FatalError Shared error to be thrown when program cannot continue
class FatalError(Exception):
    pass


## Function to record logg a fatal error and then raise the Fatal Error exception
# @param logger Logger to use to record the error
# @param message Message to log
# @throws FatalError This should not be caught except by main
def log_fatal(logger, message):
    logger.critical(message)
    raise FatalError
