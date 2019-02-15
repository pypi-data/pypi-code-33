class Model:
    """
    Simple ODM mapping to convert MongoDB dict into an object
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def convert_dict_to_object(cls, data_dict):
        if data_dict:
            obj = cls(**data_dict)  # convert data dictionary (from MongoDB) into class object
            return obj
        else:
            return None
