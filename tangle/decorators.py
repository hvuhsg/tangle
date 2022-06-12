class Toggle:
    __global_round = 1
    __local_rounds = {}

    @classmethod
    def reset(cls):
        cls.__global_round += 1

    @classmethod
    def toggle(cls, off_value=None):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if self not in cls.__local_rounds:
                    cls.__local_rounds[self] = 0
                local_round = cls.__local_rounds[self]

                if local_round == cls.__global_round:
                    return off_value

                cls.__local_rounds[self] = cls.__global_round
                return func(self, *args, **kwargs)

            return wrapper

        return decorator


class Cache:
    store = {}

    @classmethod
    def lru(cls, func):
        def wrapper(self, *args, **kwargs):
            if self in cls.store:
                return cls.store[self]
            res = func(self, *args, **kwargs)
            cls.store[self] = res
            return res
        return wrapper

    @classmethod
    def reset(cls):
        cls.store = {}
