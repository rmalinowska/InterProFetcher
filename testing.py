#!/usr/bin/env python3

import Bio
from Bio import InterProFetcher


print(InterProFetcher.browse_proteins(database = "pfam", organism = "gorilla gorilla", save_to_file = True))