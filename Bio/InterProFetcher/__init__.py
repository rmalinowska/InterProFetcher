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
import re
import ssl
import sys
import warnings

from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib import request


def browse_proteins(database: str, organism: str, write_on_sdout: bool = True, save_to_file: bool = False):
    """
    Browse proteins from different databases and organisms.

    Argument database is a name of the database, organism (optional argument) is a species name.

    Returns list of protein accession numbers that are matching the request.
    """
    if organism != "":
        organism_string = "%20".join(re.split("\s+", organism.lower().strip()))
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/{database}/?search={organism_string}&page_size=200"
    
    else:
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/{database}/?page_size=200"

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
    



#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def browse_structures(database: str, keyword: str, resolution: str = "", write_on_stdout: bool = True, save_to_file: bool = False):

    if keyword != "":
        keyword_string = "%20".join(re.split("\s+", keyword.lower().strip()))
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/structure/PDB/entry/{database}/?search={keyword_string}&page_size=200"
    else:
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/structure/PDB/entry/{database}/?page_size=200"
    print(BASE_URL)

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
            if f:
                f.write(accesion + "\n")
        
        if next:
            sleep(1)
    
    if result_ids == []:
        print("There is no data associated with this request.")
        sys.exit()
    else:
        return result_ids

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def download_pdb_structures(PDB_ids: list, output_path: str):
    """
    Download PDB files from the list of PDB ids.
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
            print(res.status)
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

    Argument type is a type of entry to browse (e.g., family, domain), keyword (optional argument) is a keyword used to filter the entries.

    Returns list of accession numbers of selected type that are matching the request.
    """
    if keyword != "":
        keyword_string = "%20".join(re.split("\s+", keyword.lower().strip()))
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/entry/InterPro/?type={type}&search={keyword_string}&page_size=200"
    
    else:
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/entry/InterPro/?type={type}&page_size=200"

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

    Argument organism is a name of the organism to browse with.

    Returns list of proteome accession numbers that are matching the request.
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
    
def browse_by_database(database: str, type: str, keyword: str = "", write_on_sdout: bool = True, save_to_file: bool = False):
    """
    Browse entries from selected database based on a specific type and keyword.

    
    Argument database is the name of the database to browse (e.g., UniProt, InterPro), type is the type of entry to browse (e.g., family, domain), and keyword (optional argument) is a keyword used to filter the entries.

    Returns list of accession numbers of selected type from selected database that are matching the request.
    """
    if keyword != "":
        keyword_string = "%20".join(re.split("\s+", keyword.lower().strip()))
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/entry/{database}/?type={type}&search={keyword}&page_size=200"
    
    else:
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/entry/{database}/?type={type}&page_size=200"

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
                with open(database + "_" + type + "_accessions_" + "_".join(re.split("\s+", keyword)) + ".csv", "a+") as f:
                    f.write(accesion + "\n")
        
        if next:
            sleep(1)
    
    if result_ids == []:
        print("There is no data associated with this request.")
        sys.exit()
    else:
        return result_ids