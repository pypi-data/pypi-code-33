from typing import List, Optional

import attr
from cortex_profiles.implicit.schema.implicit_hierarchy import derive_hierarchy_from_attribute_tags
from cortex_profiles.implicit.schema import implicity_generate_tag_oriented_profile_schema_from_config
from cortex_profiles.types.schema import ProfileSchema, ProfileTagSchema, ProfileGroupSchema, ProfileAttributeSchema
from cortex_profiles.types.schema_config import SchemaConfig
from cortex_client.utils import current_cortex_cli_profile_config


class ProfileSchemaBuilder(object):

    def __init__(self, tenantId:str=None, environmentId:str="cortex/default", schemaId:Optional[str]=None):
        self.tenantId = tenantId if tenantId is not None else  current_cortex_cli_profile_config()["account"]
        self.environmentId = environmentId
        self._schema: ProfileSchema = self._enrich_schema(ProfileSchema())
        if schemaId is not None:
            self._schema = attr.evolve(self._schema, id=schemaId)

    def _enrich_schema(self, schema) -> ProfileSchema:
        return attr.evolve(schema, tenantId=self.tenantId, environmentId=self.environmentId)

    def append_hierarchical_schema_from_config(self, schema_confg:SchemaConfig):
        self._schema:ProfileSchema = attr.evolve(
            self._schema,
            taxonomy=derive_hierarchy_from_attribute_tags(
                schema_confg,
                implicity_generate_tag_oriented_profile_schema_from_config(schema_confg, self.tenantId, self.environmentId)
            )
        )
        return self

    def append_tag_oriented_schema_from_config(self, schema_confg:SchemaConfig) :
        self._schema:ProfileSchema = self._schema + self._enrich_schema(implicity_generate_tag_oriented_profile_schema_from_config(schema_confg, self.tenantId, self.environmentId))
        return self

    def append_tags(self, tags:List[ProfileTagSchema]):
        self._schema = attr.evolve(self._schema, tags=(self._schema.tags + tags))
        return self

    def append_groups(self, groups: List[ProfileGroupSchema]):
        # ... need to merge the tags in each group!
        self._schema = attr.evolve(self._schema, groups=(self._schema.groups + groups))
        return self

    def append_attributes(self, attributes: List[ProfileAttributeSchema]):
        self._schema = attr.evolve(self._schema, attributes=(self._schema.attributes + attributes))
        return self

    def get_schema(self) -> ProfileSchema:
        return self._schema
