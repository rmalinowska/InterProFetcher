#!/usr/bin/env python3

import Bio
from Bio import InterProFetcher


#browse_proteins

#danio_rerio_proteins = InterProFetcher.browse_proteins(database = "ncbifam", organism = "danio rerio", reviewed = True, save_to_file = False)
# OK

#browse_structures

#myoglobin = InterProFetcher.browse_structures(database = "InterPro", resolution = "0-2", keyword = "myoglobin", save_to_file = False)
# OK

#InterProFetcher.download_pdb_structures(PDB_ids = ['11as', '1a3z', '4jkj'], output_path = "InterProFetcherTesting")
# OK

#browse_by_type

# cystatin_families = InterProFetcher.browse_by_type(type = 'family', keyword = 'cystatin', write_on_sdout = True, save_to_file = False)

#OK

# InterProFetcher.browse_by_type(type = 'conserved_site', keyword = 'DNA', write_on_sdout = False, save_to_file = False))


# #browse_proteoms

#s_cerevisiae_proteomes = InterProFetcher.browse_proteomes(organism = 'saccharomyces cerevisiae', write_on_sdout = True, save_to_file = True)
# OK

# print(InterProFetcher.browse_proteomes(organism = 'Escherichia Coli', write_on_sdout = False, save_to_file = False))


# #browse_by_database

# pfam_transmembrane_domains = InterProFetcher.browse_by_database(database = 'pfam', type = 'domain', keyword = 'transmembrane', write_on_sdout = True, save_to_file = False)
# OK

# InterProFetcher.browse_by_database(database = 'ncbifam', type = 'repeat', write_on_sdout = False, save_to_file = True)


# InterProFetcher.fetch_protein_sequences(accession_numbers = ['Q9Y2H1', 'Q9Y2H2'], output_path = "InterProFetcherTesting/proteins.fasta")
# OK

#InterProFetcher.fetch_protein_sequences(['A0A067XG51', 'A0A006', 'A0A009F5T3'], output_path = "InterProFetcherTesting/proteins2.fasta")
# OK

# InterProFetcher.fetch_proteomes(proteome_ids = ['UP000000216', 'UP000000227'], output_directory = "InterProFetcherTesting")
# OK

# InterProFetcher.fetch_entries(database = 'InterPro', accession_number = 'IPR000006', output_directory = "InterProFetcherTesting")
# InterProFetcher.fetch_entries(database = 'pfam', accession_number = 'PF00003', output_directory = "InterProFetcherTesting")
# InterProFetcher.fetch_entries(database = 'ncbifam', accession_number = 'NF000535', output_directory = "InterProFetcherTesting")
# OK
