"""This module contains the general information for PolicyRefReq ManagedObject."""

from ...ucsmo import ManagedObject
from ...ucscoremeta import MoPropertyMeta, MoMeta
from ...ucsmeta import VersionMeta


class PolicyRefReqConsts:
    POLICY_OWNER_LOCAL = "local"
    POLICY_OWNER_PENDING_POLICY = "pending-policy"
    POLICY_OWNER_POLICY = "policy"


class PolicyRefReq(ManagedObject):
    """This is PolicyRefReq class."""

    consts = PolicyRefReqConsts()
    naming_props = set([u'refConvertedDn'])

    mo_meta = MoMeta("PolicyRefReq", "policyRefReq", "refreq-[ref_converted_dn]", VersionMeta.Version212a, "InputOutput", 0x3f, [], ["admin"], [u'policyElement'], [], [None])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version212a, MoPropertyMeta.INTERNAL, 0x2, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version212a, MoPropertyMeta.READ_ONLY, 0x4, 0, 256, None, [], []), 
        "policy_owner": MoPropertyMeta("policy_owner", "policyOwner", "string", VersionMeta.Version212a, MoPropertyMeta.READ_ONLY, None, None, None, None, ["local", "pending-policy", "policy"], []), 
        "ref_converted_dn": MoPropertyMeta("ref_converted_dn", "refConvertedDn", "string", VersionMeta.Version212a, MoPropertyMeta.NAMING, 0x8, 1, 510, None, [], []), 
        "ref_policy_dn": MoPropertyMeta("ref_policy_dn", "refPolicyDn", "string", VersionMeta.Version212a, MoPropertyMeta.READ_ONLY, None, 0, 256, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version212a, MoPropertyMeta.READ_ONLY, 0x10, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version212a, MoPropertyMeta.READ_WRITE, 0x20, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "policyOwner": "policy_owner", 
        "refConvertedDn": "ref_converted_dn", 
        "refPolicyDn": "ref_policy_dn", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, ref_converted_dn, **kwargs):
        self._dirty_mask = 0
        self.ref_converted_dn = ref_converted_dn
        self.child_action = None
        self.policy_owner = None
        self.ref_policy_dn = None
        self.sacl = None
        self.status = None

        ManagedObject.__init__(self, "PolicyRefReq", parent_mo_or_dn, **kwargs)
