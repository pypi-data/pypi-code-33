#!/usr/bin/env python
from csr_cloud import meta_utils

if __name__ == "__main__":
    csr_metadata = meta_utils.MetaDataUtils()
    csr_metadata.dump_metadata()
    csr_metadata.pretty_metadata()
