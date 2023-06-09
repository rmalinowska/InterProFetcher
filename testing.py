#!/usr/bin/env python3

import Bio
from Bio import InterProFetcher


#InterProFetcher.browse_proteins(database = "pfam", organism = "gorilla gorilla", save_to_file = True)
thrombin_to_complex = InterProFetcher.browse_structures(database = "pirsf", keyword = "thrombin in complex", save_to_file = True)
thrombin_to_complex = thrombin_to_complex[0:100]
InterProFetcher.download_pdb_structures(PDB_ids = thrombin_to_complex, output_path = "InterProFetcherTesting")

print(InterProFetcher.browse_by_type('family', 'cystatin', False, True))

print(InterProFetcher.browse_by_type('conserved_site', 'DNA', False, False))