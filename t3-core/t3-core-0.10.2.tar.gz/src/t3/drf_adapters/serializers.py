from rest_framework import serializers


class ResourceSerializer(serializers.Serializer):
    resource_class = None

    def create(self, validated_data):
        user = None
        validated_data['request'] = self.context.get("request")

        assert self.resource_class is not None, '`resource_class` missing'
        # We are passing in `**validated_data` because URL params weren't
        # getting passed in during construction, like they do in the updates
        resource = self.resource_class(**validated_data)  # noqa
        return resource.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['request'] = self.context.get("request")
        if self.partial:
            return instance.partial_update(**validated_data)
        return instance.update(**validated_data)

    def partial_update(self, instance, validated_data):
        validated_data['request'] = self.context.get("request")
        return instance.partial_update(**validated_data)
