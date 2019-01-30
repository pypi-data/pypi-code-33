# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from aliyunsdkcore.request import RpcRequest
class InnerUntagResourcesRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Tag-Inner', '2018-11-09', 'InnerUntagResources', 'tag', 'innerAPI')

	def get_ResourceOwnerId(self):
		return self.get_query_params().get('ResourceOwnerId')

	def set_ResourceOwnerId(self,ResourceOwnerId):
		self.add_query_param('ResourceOwnerId',ResourceOwnerId)

	def get_TagOwnerUid(self):
		return self.get_query_params().get('TagOwnerUid')

	def set_TagOwnerUid(self,TagOwnerUid):
		self.add_query_param('TagOwnerUid',TagOwnerUid)

	def get_DeleteAll(self):
		return self.get_query_params().get('DeleteAll')

	def set_DeleteAll(self,DeleteAll):
		self.add_query_param('DeleteAll',DeleteAll)

	def get_Scope(self):
		return self.get_query_params().get('Scope')

	def set_Scope(self,Scope):
		self.add_query_param('Scope',Scope)

	def get_TagOperator(self):
		return self.get_query_params().get('TagOperator')

	def set_TagOperator(self,TagOperator):
		self.add_query_param('TagOperator',TagOperator)

	def get_TagOwnerBid(self):
		return self.get_query_params().get('TagOwnerBid')

	def set_TagOwnerBid(self,TagOwnerBid):
		self.add_query_param('TagOwnerBid',TagOwnerBid)

	def get_ResourceIds(self):
		return self.get_query_params().get('ResourceIds')

	def set_ResourceIds(self,ResourceIds):
		for i in range(len(ResourceIds)):	
			if ResourceIds[i] is not None:
				self.add_query_param('ResourceId.' + str(i + 1) , ResourceIds[i]);

	def get_ResourceOwnerAccount(self):
		return self.get_query_params().get('ResourceOwnerAccount')

	def set_ResourceOwnerAccount(self,ResourceOwnerAccount):
		self.add_query_param('ResourceOwnerAccount',ResourceOwnerAccount)

	def get_OwnerAccount(self):
		return self.get_query_params().get('OwnerAccount')

	def set_OwnerAccount(self,OwnerAccount):
		self.add_query_param('OwnerAccount',OwnerAccount)

	def get_OwnerId(self):
		return self.get_query_params().get('OwnerId')

	def set_OwnerId(self,OwnerId):
		self.add_query_param('OwnerId',OwnerId)

	def get_ResourceType(self):
		return self.get_query_params().get('ResourceType')

	def set_ResourceType(self,ResourceType):
		self.add_query_param('ResourceType',ResourceType)

	def get_TagKeys(self):
		return self.get_query_params().get('TagKeys')

	def set_TagKeys(self,TagKeys):
		for i in range(len(TagKeys)):	
			if TagKeys[i] is not None:
				self.add_query_param('TagKey.' + str(i + 1) , TagKeys[i]);

	def get_Category(self):
		return self.get_query_params().get('Category')

	def set_Category(self,Category):
		self.add_query_param('Category',Category)