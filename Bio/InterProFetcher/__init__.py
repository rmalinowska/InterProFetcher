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


email = None
max_tries = 3
sleep_between_tries = 15
tool = "biopython"
api_key = None


def eprint(**keywds):
    print("It works, hello.")
    return "returned value"

def browse_proteins(database: str, organism: str = "", write_on_sdout: bool = True):
    """
    Browse proteins from different databases and organisms.

    Argument database is a name of the database, organism (optional argument) is a species name.

    Returns list of protein accession numbers that are matching the request.
    """
    if organism != "":
        organism_string = "%20".join(re.split("\s+", organism.lower().strip()))
        print(organism_string)
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/{database}/?search={organism_string}&page_size=200"
    
    else:
        BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/{database}/?page_size=200"

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
        except TimeoutError as e:
            sys.stderr.write("LAST URL: " + next)
            raise e
        except Exception as e:
            sys.stderr.write("LAST URL: " + next)
            raise e
        for i, item in enumerate(payload["results"]):
            result_ids.append(item["metadata"]["accession"])
            sys.stdout.write(item["metadata"]["accession"] + "\n")
        
        if next:
            sleep(1)
    
    if result_ids == []:
        print("There is no data associated with this request.")
        sys.exit()
    else:
        return result_ids
    

    # context = ssl._create_unverified_context()

    # next = BASE_URL
    # last_page = False

    
    # attempts = 0
    # while next:
    #     try:
    #         req = request.Request(next, headers={"Accept": "application/json"})
    #         res = request.urlopen(req, context=context)
    #         # If the API times out due a long running query
    #         if res.status == 408:
    #             # wait just over a minute
    #             sleep(61)
    #             # then continue this loop with the same URL
    #             continue
    #         elif res.status == 204:
    #             #no data so leave loop
    #             break
    #         payload = json.loads(res.read().decode())
    #         next = payload["next"]
    #         attempts = 0
    #         if not next:
    #             last_page = True
    #     except HTTPError as e:
    #         if e.code == 408:
    #             sleep(61)
    #             continue
    #         else:
    #             # If there is a different HTTP error, it wil re-try 3 times before failing
    #             if attempts < 3:
    #                 attempts += 1
    #                 sleep(61)
    #                 continue
    #             else:
    #                 sys.stderr.write("LAST URL: " + next)
    #                 raise e

    #     for i, item in enumerate(payload["results"]):
    #         sys.stdout.write(item["metadata"]["accession"]+"\n")