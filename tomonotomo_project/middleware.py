import logging

logger = logging.getLogger(__name__)

class error500Middleware(object):
        def process_exception(self, request, exception):
                logger.exception('tomonotomo_project.middleware.error500Middleware - ' + str(exception))
                return None

