from aether_shared.utilities.api_utils import api_utils

class services_util(object):

    @staticmethod
    def instantiate_class(classname, *args):
        parts = classname.split(".")
        module = __import__(classname)

        for component in parts[1:]:
            module = getattr(module, component)
        class_ = getattr(module, classname.split(".")[-1])
        instance = class_(*args)
        return instance

    @staticmethod
    def instantiate_protobuf(classname):
        parts = classname.split(".")
        module = __import__(".".join(classname.split(".")[:-1]))

        for component in parts[1:]:
            module = getattr(module, component)
        instance = module()
        return instance

    @staticmethod
    def run_method_on_handler(obj, method_key, available_methods, request, logger):
        if method_key not in available_methods:
            return api_utils.log_and_return_status(
                "Requested Method not supported: {}".format(request), 400, request, logger)

        try:
            func = getattr(obj, available_methods[method_key])
        except AttributeError:
            return api_utils.log_and_return_status(
                "Requested Method not found on Resource:".format(request), 400, request, logger, exc_info=True)

        try:
            response = func(request)
        except Exception:
            return api_utils.log_and_return_status("Method {} failed.".format(request), 500, request, logger, exc_info=True)

        logger.info("Request {}. Response: {:.10000}".format(request, str(response)))
        return response
