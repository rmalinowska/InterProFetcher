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

def browse_proteins(database):
    BASE_URL = f"https://www.ebi.ac.uk:443/interpro/api/protein/UniProt/entry/{database}/?page_size=200"
    context = ssl._create_unverified_context()

    next = BASE_URL
    last_page = False
    attempts = 0
    print("Dzien dobry")
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
            print("Payload next", next)
            attempts = 0 #?
            if not next:
               last_page = True
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
        for i, item in enumerate(payload["results"]):
            print(item["metadata"]["accession"])
        
        if next:
            sleep(1)
           