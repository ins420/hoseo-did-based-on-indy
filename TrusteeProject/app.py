#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# app.py

import os
import json

from flask import Flask, request, render_template
from Crypto.Hash import SHA256
from string import ascii_letters, digits
from random import choice

from stp_core.crypto.nacl_wrappers import Signer
from plenum.common.constants import STEWARD, TRUSTEE
from plenum.common.keygen_utils import init_bls_keys
from plenum.common.member.steward import Steward
from plenum.common.member.member import Member
from plenum.common.signer_did import DidSigner
from plenum.common.util import hexToFriendly

app = Flask(__name__)
hashed_passcode = "927fb0961e2cf6ba2691a31aaf47cd610468e87b00905e7d7890b995298609f4"

trustee_defs = list()
steward_defs = list()
node_defs = list()

trustee_def = {
    "name": "Trustee",
    "sigseed": b'CHnCtcXSXTTSRLtk2Ixm6XyeI40R2FzH'
}
trustee_signer = DidSigner(seed=trustee_def["sigseed"])
trustee_def["nym"] = trustee_signer.identifier
trustee_def["verkey"] = trustee_signer.verkey

trustee_defs.append(trustee_def)


def get_seed() -> str:
    characters = ascii_letters + digits
    seed = str()
    for _ in range(32):
        seed += choice(characters)
    return seed


@app.after_request
def add_header(resp):
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("trustee_login.html")
    else:  # if request.method == "POST"
        if SHA256.new(request.form["passcode"].encode()).hexdigest() == hashed_passcode:
            return render_template("trustee_home.html")
        else:
            return "Passcode is incorrect."


@app.route("/trustee_home", methods=["GET"])
def trustee_home():
    if request.method == "GET":
        return render_template("trustee_home.html")
    else:
        return "The wrong approach."


@app.route("/add_genesis_steward", methods=["GET", "POST"])
def add_genesis_steward():
    if request.method == "GET":
        return render_template("add_genesis_steward.html", steward_defs=steward_defs)
    else:
        if request.form["steward_name"] in [steward_def["name"] for steward_def in steward_defs]:
            return render_template("add_genesis_steward.html",
                                   steward_defs=steward_defs,
                                   error="Steward Name already exists.")

        steward_def = {
            "name": request.form["steward_name"],
            "sigseed": get_seed().encode()
        }
        steward_signer = DidSigner(seed=steward_def["sigseed"])
        steward_def["nym"] = steward_signer.identifier
        steward_def["verkey"] = steward_signer.verkey
        steward_defs.append(steward_def)

        return render_template("add_genesis_steward.html", steward_defs=steward_defs)


@app.route("/add_genesis_node", methods=["GET", "POST"])
def add_genesis_node():
    if request.method == "GET":
        return render_template("add_genesis_node.html", steward_defs=steward_defs, node_defs=node_defs)
    else:
        port = [node_def["port"] for node_def in node_defs] + \
               [node_def["client_port"] for node_def in node_defs]

        if request.form["node_name"] in [node_def["name"] for node_def in node_defs]:
            return render_template("add_genesis_node.html",
                                   steward_defs=steward_defs,
                                   node_defs=node_defs,
                                   error="Node Name already exists.")

        if int(request.form["node_port"]) in port:
            return render_template("add_genesis_node.html",
                                   steward_defs=steward_defs,
                                   node_defs=node_defs,
                                   error="Node-Node Port already exists.")

        if int(request.form["client_port"]) in port:
            return render_template("add_genesis_node.html",
                                   steward_defs=steward_defs,
                                   node_defs=node_defs,
                                   error="Node-Client Port already exists.")
        
        if request.form["node_port"] == request.form["client_port"]:
            return render_template("add_genesis_node.html",
                                   steward_defs=steward_defs,
                                   node_defs=node_defs,
                                   error="Node-Node Port and Node-Client Port are the same.")

        steward_nym = None
        for steward_def in steward_defs:
            if request.form["steward"] == steward_def["name"]:
                steward_nym = steward_def["nym"]
                for node_def in node_defs:
                    if steward_def["nym"] == node_def["steward_nym"]:
                        return render_template("add_genesis_node.html",
                                               steward_defs=steward_defs,
                                               node_defs=node_defs,
                                               error="Steward does not exist or is unavailable.")

        node_def = {
            "name": request.form["node_name"],
            "ip": request.form["node_ip"],
            "port": int(request.form["node_port"]),
            "client_port": int(request.form["client_port"]),
            "idx": len(node_defs) + 1,
            "sigseed": get_seed().encode(),
            "steward_nym": steward_nym
        }
        node_def["verkey"] = Signer(node_def["sigseed"]).verhex
        node_defs.append(node_def)

        return render_template("add_genesis_node.html", steward_defs=steward_defs, node_defs=node_defs)


@app.route("/generate_domain_genesis", methods=["GET"])
def generate_domain_genesis():
    if request.method == "GET":
        genesis_domain_ledger_txns = list()
        sequence_num = 1

        for idx in range(len(trustee_defs)):
            trustee_txn = Member.nym_txn(trustee_defs[idx]["nym"],
                                         verkey=trustee_defs[idx]["verkey"],
                                         role=TRUSTEE,
                                         seq_no=sequence_num,
                                         protocol_version=None)
            genesis_domain_ledger_txns.append(trustee_txn)
            sequence_num += 1

        for idx in range(len(steward_defs)):
            steward_txn = Member.nym_txn(steward_defs[idx]["nym"],
                                         verkey=steward_defs[idx]["verkey"],
                                         role=STEWARD,
                                         creator=trustee_defs[0]["nym"],  # What about Trustees?
                                         seq_no=sequence_num,
                                         protocol_version=None)
            genesis_domain_ledger_txns.append(steward_txn)
            sequence_num += 1
        
        with open("/var/www/html/trustee/domain_transactions_genesis", 'w') as domain_ledger:
            for txn in genesis_domain_ledger_txns:
                domain_ledger.write(json.dumps(txn, ensure_ascii=False).replace(' ', '') + '\n')

        return render_template("trustee_home.html")
    else:
        return "The wrong approach."


@app.route("/generate_pool_genesis", methods=["GET"])
def generate_pool_genesis():
    if request.method == "GET":
        genesis_pool_ledger_txns = list()

        for idx, node_def in enumerate(node_defs):
            verkey = node_defs[idx]["verkey"]
            blskey, key_proof = init_bls_keys("",
                                              node_def["name"],
                                              node_def["sigseed"])
            node_nym = hexToFriendly(verkey)
            node_txn = Steward.node_txn(node_def["steward_nym"],
                                        node_def["name"],
                                        node_nym,
                                        node_def["ip"],
                                        node_def["port"],
                                        node_def["client_port"],
                                        blskey=blskey,
                                        bls_key_proof=key_proof,
                                        seq_no=idx + 1,
                                        protocol_version=None)
            genesis_pool_ledger_txns.append(node_txn)
            os.system("rm -rf {}".format(node_def["name"]))
        
        with open("/var/www/html/trustee/pool_transactions_genesis", 'w') as pool_ledger:
            for txn in genesis_pool_ledger_txns:
                pool_ledger.write(json.dumps(txn, ensure_ascii=False).replace(' ', '') + '\n')
        

            return render_template("trustee_home.html")
    else:
        return "The wrong approach."


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
