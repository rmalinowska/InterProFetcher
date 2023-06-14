# Copyright 1999-2000 by Jeffrey Chang.  All rights reserved.
# Copyright 2008-2013 by Michiel de Hoon.  All rights reserved.
# Revisions copyright 2011-2016 by Peter Cock. All rights reserved.
# Revisions copyright 2015 by Eric Rasche. All rights reserved.
# Revisions copyright 2015 by Carlos Pena. All rights reserved.
#
# This file is part of the Biopython distribution and governed by your
# choice of the "Biopython License Agreement" or the "BSD 3-Clause License".
# Please see the LICENSE file that should have been included as part of this
# package.

from time import sleep
import io
import json
import os
import re
import ssl
import sys
import warnings

from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib import request


def browse_proteins(database: str, organism: str, reviewed: bool = False, write_on_sdout: bool = True, save_to_file: bool = False):
    """
    Browse proteins from different databases and organisms.

    Args:
        database (str): name of the database (InterPro, cathgene3d, cdd, hamap, ncbifam, panther, pfam, pirsf, prints, profile, prosite, sfld, smart, ssf).
        organism (str, optional): species name.
        reviewed (bool, optional): only reviewed proteins. Defaults to False.
        write_on_sdout (bool, optional): write results on stdout. Defaults to True.
        save_to_file (bool, optional): save results to a csvfile. Defaults to False.

    Returns:
        list: protein accession numbers
    """
    if reviewed:
        uniprot = "reviewed"
    else:
        uniprot = "UniProt"
    if organism != "":
        organism_string = "search=" + "%20".join(re.split("\s+", organism.lower().strip())) + "&"
    else:
        organism_string = ""

    BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/protein/{uniprot}/entry/{database}/?{organism_string}page_size=200"
    print(BASE_URL)
    

    context = ssl._create_unverified_context()

    next = BASE_URL
    last_page = False #
    result_ids = []
    attempts = 0

    while next:
        try:
            req = request.Request(next)
            res = request.urlopen(req, context = context)
            if res.status == 408:
                sleep(61)
                continue
            elif res.status == 204:
               break
            payload = json.loads(res.read().decode())
            next = payload["next"]
            attempts = 0
            if not next: #
                last_page = True #
        except HTTPError as e:
            if e.code == 400:
                sleep(61)
                continue
            else:
                if attempts < 3:
                   attempts += 1
                   sleep(61)
                   continue
                else:
                    sys.stderr.write("LAST URL: " + next)
                    raise e
        except Exception as e:
            sys.stderr.write("LAST URL: " + next)
            raise e
        for i, item in enumerate(payload["results"]):
            accesion = item["metadata"]["accession"]
            result_ids.append(accesion)
            if write_on_sdout:
                sys.stdout.write(accesion + "\n")
            if save_to_file:
                with open("protein_accessions_" + database + "_" + "_".join(re.split("\s+", organism)) + ".csv", "a+") as f:
                    f.write(accesion + "\n")
        
        if next:
            sleep(1)
    
    if result_ids == []:
        print("There is no data associated with this request.")
        sys.exit()
    else:
        return result_ids
    

def browse_structures(database: str, keyword: str, resolution: str = "", write_on_stdout: bool = True, save_to_file: bool = False):
    """
    Browse PDB structures from different databases based on a specific keyword and resolution.

    Args:
        database (str): name of the database (InterPro, cathgene3d, cdd, hamap, ncbifam, panther, pfam, pirsf, prints, profile, prosite, sfld, smart, ssf).
        keyword (str): keyword used to filter the entries.
        resolution (str, optional): resolution of the structure. Defaults to "". Available resolutions: '0-2', '2-4', '4-100'.
        write_on_stdout (bool, optional): write results on stdout. Defaults to True.
        save_to_file (bool, optional): save results to a csv file. Defaults to False.

    Returns:
        list: PDB accession numbers
    """


    if keyword != "":
        keyword_string = "search=" + "%20".join(re.split("\s+", keyword.lower().strip())) + "&"
    else:
        keyword_string = ""
    if resolution != "":
        resolution_string = "resolution=" + resolution + "&"
    else:
        resolution_string = ""

    BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/structure/PDB/entry/{database}/?{resolution_string}{keyword_string}page_size=200"

    context = ssl._create_unverified_context()

    next = BASE_URL
    last_page = False
    result_ids = []
    attempts = 0
    if save_to_file:
        f =  open("structures_pdb_ids_" + database + "_" + "_".join(re.split("\s+", keyword)) + ".csv", "a+")

    while next:
        try:
            req = request.Request(next)
            res = request.urlopen(req, context=context)
            if res.status == 408:
                sleep(61)
                continue
            elif res.status == 204:
                break
            payload = json.loads(res.read().decode())
            next = payload["next"]
            attempts = 0
            if not next:
                last_page = True
        except HTTPError as e:
            if e.code == 408:
                sleep(61)
                continue
            else:
                if attempts < 3:
                    attempts += 1
                    sleep(61)
                    continue
                else:
                    sys.stderr.write("LAST URL: " + next)
                    raise e
        except Exception as e:
            sys.stderr.write("LAST URL: " + next)
            raise e

        for i, item in enumerate(payload["results"]):
            accesion = item["metadata"]["accession"]
            result_ids.append(accesion)
            if write_on_stdout:
                sys.stdout.write(accesion + "\n")
            if save_to_file:
                f.write(accesion + "\n")
        
        if next:
            sleep(1)
    
    if result_ids == []:
        print("There is no data associated with this request.")
        sys.exit()
    else:
        return result_ids


def download_pdb_structures(PDB_ids: list, output_path: str):
    """
    Download PDB files from the list of PDB ids.

    Args:
        PDB_ids (list): list of PDB ids.
        output_path (str): path to the output directory.
    """
    if output_path == "":
        output_path = "."
    else:
        output_path = output_path.strip()
    
    if not output_path.endswith("/"):
        output_path += "/"
    
    context = ssl._create_unverified_context()

    for pdb_id in PDB_ids:
        print("Downloading " + pdb_id + "...")
        pdb_id = pdb_id.strip()
        url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
        try:
            req = request.Request(url)
            res = request.urlopen(req, context=context)
            output_filename = output_path + pdb_id + ".pdb"
            with open(output_filename, "w") as f:
                f.write(res.read().decode())

        except HTTPError as e:
            if e.code == 404:
                sys.stderr.write(f"WARNING: {pdb_id}.pdb is not found in the PDB database. Trying to download CIF file.\n")
                try:
                    url = f"https://files.rcsb.org/download/{pdb_id}.cif"
                    req = request.Request(url)
                    res = request.urlopen(req, context=context)
                    output_filename = output_path + pdb_id + ".cif"
                    with open(output_filename, "w") as f:
                        f.write(res.read().decode())
                except HTTPError as e:
                    if e.code == 404:
                        sys.stderr.write(f"WARNING: {pdb_id} is not found in the PDB database.\n")
                        continue
            else:
                raise e
        except Exception as e:
            raise e
        sleep(5)


def browse_by_type(type: str, keyword: str = "", write_on_sdout: bool = True, save_to_file: bool = False):
    """
    Browse entries from the InterPro database based on a specific type and keyword.

    Args:
        type (str): type of entry to browse (family, domain, homologous_superfamily, repeat, conserved_site, active_site, binding_site, ptm).
        keyword (str, optional): keyword used to filter the entries. Defaults to "".
        write_on_sdout (bool, optional): write results on stdout. Defaults to True.
        save_to_file (bool, optional): save results to a csv file. Defaults to False.

    Returns:
        list: accession numbers of selected type that are matching the request.
    """
    if keyword != "":
        keyword_string = "search=" + "%20".join(re.split("\s+", keyword.lower().strip())) + "&"
    else:
        keyword_string = ""
    BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/entry/InterPro/?type={type}&{keyword_string}page_size=200"
    
    context = ssl._create_unverified_context()

    next = BASE_URL
    last_page = False #
    result_ids = []
    while next:
        try:
            req = request.Request(next)
            res = request.urlopen(req, context = context)
            if res.status == 408:
                sleep(61)
                continue
            elif res.status == 204:
               break
            payload = json.loads(res.read().decode())
            next = payload["next"]
            attempts = 0
            if not next: #
                last_page = True #
        except HTTPError as e:
            if e.code == 400:
                sleep(61)
                continue
            else:
                if attempts < 3:
                   attempts += 1
                   sleep(61)
                   continue
                else:
                    sys.stderr.write("LAST URL: " + next)
                    raise e
        except Exception as e:
            sys.stderr.write("LAST URL: " + next)
            raise e
        for i, item in enumerate(payload["results"]):
            accesion = item["metadata"]["accession"]
            result_ids.append(accesion)
            if write_on_sdout:
                sys.stdout.write(accesion + "\n")
            if save_to_file:
                with open(type + "_accessions_" + "_".join(re.split("\s+", keyword)) + ".csv", "a+") as f:
                    f.write(accesion + "\n")
        
        if next:
            sleep(1)
    
    if result_ids == []:
        print("There is no data associated with this request.")
        sys.exit()
    else:
        return result_ids
    

def browse_proteomes(organism: str, write_on_sdout: bool = True, save_to_file: bool = False):
    """
    Browse proteomes from the InterPro database for a specific organism.

    Args:
        organism (str): name of the organism to browse with.
        write_on_sdout (bool, optional): write results on stdout. Defaults to True.
        save_to_file (bool, optional): save results to a csv file. Defaults to False.

    Return:
        list: accession numbers of proteomes that are matching the request.
    """
    organism_string = "%20".join(re.split("\s+", organism.lower().strip()))
    BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/proteome/uniprot/entry/InterPro/?search={organism_string}&page_size=200"

    context = ssl._create_unverified_context()

    next = BASE_URL
    last_page = False #
    result_ids = []
    while next:
        try:
            req = request.Request(next)
            res = request.urlopen(req, context = context)
            if res.status == 408:
                sleep(61)
                continue
            elif res.status == 204:
               break
            payload = json.loads(res.read().decode())
            next = payload["next"]
            attempts = 0
            if not next: #
                last_page = True #
        except HTTPError as e:
            if e.code == 400:
                sleep(61)
                continue
            else:
                if attempts < 3:
                   attempts += 1
                   sleep(61)
                   continue
                else:
                    sys.stderr.write("LAST URL: " + next)
                    raise e
        except Exception as e:
            sys.stderr.write("LAST URL: " + next)
            raise e
        for i, item in enumerate(payload["results"]):
            accesion = item["metadata"]["accession"]
            result_ids.append(accesion)
            if write_on_sdout:
                sys.stdout.write(accesion + "\n")
            if save_to_file:
                with open("proteome_accessions_" + "_".join(re.split("\s+", organism)) + ".csv", "a+") as f:
                    f.write(accesion + "\n")
        
        if next:
            sleep(1)
    
    if result_ids == []:
        print("There is no data associated with this request.")
        sys.exit()
    else:
        return result_ids
    
def browse_by_database(database: str, type: str = "", keyword: str = "", write_on_sdout: bool = True, save_to_file: bool = False):
    """
    Browse entries from selected database based on a specific type and keyword.

    Args:
        database (str): name of the database (cathgene3d, cdd, hamap, ncbifam, panther, pfam, pirsf, prints, profile, prosite, sfld, smart, ssf).
        type (str, optional): type of entry to browse (family, domain, repeat, conserved_site, unknown).
        keyword (str, optional): keyword used to filter the entries. Defaults to "".
        write_on_sdout (bool, optional): write results on stdout. Defaults to True.
        save_to_file (bool, optional): save results to a csv file. Defaults to False.
    
    Returns:
        list: accession numbers that are matching the request.
    """
    if keyword != "":
        keyword_string = "search=" + "%20".join(re.split("\s+", keyword.lower().strip())) + "&"
    else:
        keyword_string = ""
    if type != "":
        type_string = "type=" + type + "&"
    else:
        type_string = ""
    BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/entry/{database}/?{type_string}{keyword_string}page_size=200"

    context = ssl._create_unverified_context()

    next = BASE_URL
    last_page = False 
    result_ids = []
    while next:
        try:
            req = request.Request(next)
            res = request.urlopen(req, context = context)
            if res.status == 408:
                sleep(61)
                continue
            elif res.status == 204:
               break
            payload = json.loads(res.read().decode())
            next = payload["next"]
            attempts = 0
            if not next: #
                last_page = True #
        except HTTPError as e:
            if e.code == 400:
                sleep(61)
                continue
            else:
                if attempts < 3:
                   attempts += 1
                   sleep(61)
                   continue
                else:
                    sys.stderr.write("LAST URL: " + next)
                    raise e
        except Exception as e:
            sys.stderr.write("LAST URL: " + next)
            raise e
        for i, item in enumerate(payload["results"]):
            accesion = item["metadata"]["accession"]
            result_ids.append(accesion)
            if write_on_sdout:
                sys.stdout.write(accesion + "\n")
            if save_to_file:
                with open(database + "_" + type + "_accessions" + "_".join(re.split("\s+", keyword)) + ".csv", "a+") as f:
                    f.write(accesion + "\n")
        
        if next:
            sleep(1)
    
    if result_ids == []:
        print("There is no data associated with this request.")
        sys.exit()
    else:
        return result_ids
    

def fetch_protein_sequences(accession_numbers: list[str], output_path: str):
    """
    Fetch protein sequences based on the given accession numbers and save them to a file.
    If there is no sequence found for a given accession number, a warning message is displayed.

    Args:
        accession_numbers (list[str]): list of protein accession numbers to browse.
        output_path (str): name of the file to save the sequences.
    """

    HEADER_SEPARATOR = "|"
    LINE_LENGTH = 80

    context = ssl._create_unverified_context()
    not_found = 0

    with open(output_path, "w") as file:
        for accession_number in accession_numbers:
            try:
                url = f"https://www.ebi.ac.uk/interpro/api/protein/UniProt/{accession_number}"
                req = request.Request(url, headers={"Accept": "application/json"})
                res = request.urlopen(req, context=context)
                payload = json.loads(res.read().decode())
                seq = payload["metadata"]["sequence"]
                file.write(">" + payload["metadata"]["accession"] + HEADER_SEPARATOR + payload["metadata"]["name"] + "\n")
                fasta_seq_fragments = [seq[i:i+LINE_LENGTH] for i in range(0, len(seq), LINE_LENGTH)]
                for fasta_seq_fragment in fasta_seq_fragments:
                    file.write(fasta_seq_fragment + "\n")

                sleep(1)

            except HTTPError as e:
                if e.code == 408:
                    sleep(61)
                    continue
                elif e.code == 404:
                    sys.stderr.write(f"WARNING: {accession_number} not found.\n")
                else:
                    raise e

            except Exception as e:
                raise e

    if not_found != len(accession_numbers):
        print("The downloaded sequences were saved to a file:", output_path)
    else:
        print("Provided accession numbers not found")


def fetch_proteomes(proteome_ids, output_directory):
    """
    Fetch proteomes based on the given InterPro proteome IDs and save them to individual FASTA files.
    If a proteome is not found for a given ID, a warning message is displayed.

    Args:
        proteome_ids (list): list of proteome IDs to fetch.
        output_directory (str): directory to save the proteome files.

    """
    for proteome_id in proteome_ids:
        print("Downloading " + proteome_id + "...")
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/InterPro/proteome/uniprot/{proteome_id}/?page_size=200&extra_fields=sequence"

        HEADER_SEPARATOR = "|"
        LINE_LENGTH = 80


        context = ssl._create_unverified_context()

        next = BASE_URL
        last_page = False

        with open(os.path.join(output_directory, proteome_id + ".fasta"), "w+") as out_file:

            attempts = 0
            while next:
                try:
                    req = request.Request(next, headers={"Accept": "application/json"})
                    res = request.urlopen(req, context=context)
                    if res.status == 408:
                        sleep(61)
                        continue
                    elif res.status == 204:
                        break
                    payload = json.loads(res.read().decode())
                    next = payload["next"]
                    attempts = 0
                    if not next:
                        last_page = True
                except HTTPError as e:
                    if e.code == 408:
                        sleep(61)
                        continue
                    else:
                        if attempts < 3:
                            attempts += 1
                            sleep(61)
                            continue
                        else:
                            sys.stderr.write("LAST URL: " + next)
                            raise e

                for i, item in enumerate(payload["results"]):
                                       
                    out_file.write(">" + item["metadata"]["accession"] + HEADER_SEPARATOR + item["metadata"]["name"] + "\n")

                    seq = item["extra_fields"]["sequence"]
                    for fasta_seq_fragment in [seq[i:i+LINE_LENGTH] for i in range(0, len(seq), LINE_LENGTH)]:
                        out_file.write(fasta_seq_fragment + "\n")
                
                if next:
                    sleep(1)


def fetch_entries(database: str, accession_number: str, output_directory):
    """
    Fetch sequences based on the given a databse and accession number and save them to FASTA file.
    Accession numbers might be from different databases and different types (families, domains, etc).
    If an accession number is not found, a warning message is displayed.

    Args:
        accession_numbers (list): list of accession numbers to fetch.
        output_directory (str): directory to save the sequences.
    """
    # https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/pfam/PF00003/
    # https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/InterPro/IPR000006/
    # BASE_URL = "https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/ncbifam/NF033510/?page_size=200&extra_fields=sequence"

    HEADER_SEPARATOR = "|"
    LINE_LENGTH = 80

    context = ssl._create_unverified_context()
    not_found = 0

    BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/{database}/{accession_number}/?page_size=200&extra_fields=sequence"
    context = ssl._create_unverified_context()

    next = BASE_URL
    last_page = False 
    print("Downloading " + accession_number + "...")

    while next:
        try:
            req = request.Request(next)
            res = request.urlopen(req, context = context)
            if res.status == 408:
                sleep(61)
                continue
            elif res.status == 204:
                break
            payload = json.loads(res.read().decode())
            next = payload["next"]
            attempts = 0
            if not next:
                last_page = True 
        except HTTPError as e:
            if e.code == 400:
                sleep(61)
                continue
            elif e.code == 404:
                sys.stderr.write(f"WARNING: No data found for ID: {accession_number}\n")
                sys.exit()
            else:
                if attempts < 3:
                    attempts += 1
                    sleep(61)
                    continue
                else:
                    sys.stderr.write("LAST URL: " + next)
                    raise e
        except Exception as e:
            sys.stderr.write("LAST URL: " + next)
            raise e

        with open(os.path.join(output_directory, accession_number + ".fasta"), "w+") as out_file:
            for i, item in enumerate(payload["results"]):             
                        out_file.write(">" + item["metadata"]["accession"] + HEADER_SEPARATOR + item["metadata"]["name"] + "\n")
                        seq = item["extra_fields"]["sequence"]
                        for fasta_seq_fragment in [seq[i:i+LINE_LENGTH] for i in range(0, len(seq), LINE_LENGTH)]:
                            out_file.write(fasta_seq_fragment + "\n")
                
        if next:
            sleep(1)
