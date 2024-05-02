import os,sys
from web3 import Web3
import numpy as np
import pandas as pd
import dotenv
import log_filters
import json
import log_decoder
import ipfs_util
from datetime import datetime
import shutil

sys.path.append(os.path.dirname(__file__)+'/../analysis/preprocess')
sys.path.append(os.path.dirname(__file__)+'/../db/neo4j/ingestion')


import generate_triplet_spacy # not used atm.
import generate_triplet_llm
import content_parser
import neo4j_service
import queries as sql_queries


# load environment variables
dotenv.load_dotenv('../../../.env')
EAAC_ABI_PATH=os.getenv('EAAC_ABI_PATH')
f=open(EAAC_ABI_PATH)
EAAC_ABI = json.load(f)
EAAC_ABI = EAAC_ABI['abi']
IPFS_NODE = os.getenv('IPFS_NODE')
# global var to configure wrapper
MAX_TRIES = 10
TIME_DELAY = 2 # seconds

REQ_SIZE = 10000 # block size for fetching logs eth_getlogs

# establish a websocket connection 
# w3 = Web3(Web3.WebsocketProvider(os.getenv('RPC_PROVIDER')))  # websocket for sepolia testnet is not supported by Alchemy
# http connection 
w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_PROVIDER')))

# EAAC address
EAAC_addr = '0xd40f60Fcc2F9fDc9aC512Ba9B2887350Fd9f0fc8'
EAAC_addr = Web3.to_checksum_address(EAAC_addr) # double check 

# get recent block
recent_block = w3.eth.block_number

# check if history exists 
if(os.path.exists(f'{os.path.dirname(__file__)}/history.csv')):
    history = pd.read_csv(f'{os.path.dirname(__file__)}/history.csv')
    fromblock = max(history['block_number']) + 1
else:
    fromblock = recent_block - 1000   

interval = recent_block - fromblock


for ii, step in enumerate(np.arange(fromblock,recent_block,REQ_SIZE)):

    fromblock = step
    toblock = min(step + REQ_SIZE, recent_block)
    #get logs
    args = {}
    args['fromBlock'] =  fromblock #5724513
    args['toBlock'] = toblock # 5774644
    args['address'] = EAAC_addr
    args['topics'] = ['0x' + Web3.keccak(text='Report(address,string,string)').hex()]
    filter_params = log_filters.make_filter(args)

    # @log_filters.retry_on_error(max_retries=MAX_TRIES, delay=TIME_DELAY)
    def get_logs_try(w3,filter_params):
        logs = w3.eth.get_logs(filter_params)
        return logs

    logs = get_logs_try(w3, filter_params)

    if(logs is None):
        continue
        
    
    # decode logs to get ipfs hashes
    contract_abi = EAAC_ABI
    contract = w3.eth.contract(address=EAAC_addr, abi=contract_abi)
    event_abi_map = log_decoder.generate_event_abi_map(contract_abi)
    for log in logs:
        decoded_log = log_decoder.decode_log(log, event_abi_map, contract)
        ipfs_hash = decoded_log.args['report_hash']
        operator = decoded_log.args['operator'].lower()
        identifier = decoded_log.args['identifier'].lower()

        # retrieve the file
        report = ipfs_util.get_from_ipfs(IPFS_NODE, ipfs_hash)

        # convert report into natural language text
        nl_report = content_parser.concatenate_content(report)

        # generate triplets --> in rdf format
        rdf_formatted = generate_triplet_llm.extract_triplets(nl_report)

            
        # rdf file is saved to the local scratch dir
        rdf_path = f'{os.path.dirname(__file__)}/../analysis/scratch/triplets.rdf'
        with open(f'{rdf_path}', 'wb') as f:
            f.write(rdf_formatted)

        # convert rdf file into csv (atm. subgraph assignment pipeline in neo4j is more convenient with csv)
        csv_path = f'{os.path.dirname(__file__)}/../analysis/scratch/triplets.csv'
        generate_triplet_llm.convert_rdf_to_csv(rdf_path, csv_path)
        
        # ingest rdf into the graph DB
        # establish connection to neo4j
        neo4j = neo4j_service.Neo4jService(uri='bolt://127.0.0.1:7687')

        # set constraints (only for the first time)
        # constraints = sql_queries.set_constraints_csv()
        # for constraint in constraints:
        #     neo4j._graph.run(constraint)

        # ingest the csv file

        # copy the csv file to import dir
        import_csv_path = f'{os.path.dirname(__file__)}/../db/neo4j/docker/mount/neo4j/import/{os.path.basename(csv_path)}'
        shutil.copy(csv_path, import_csv_path)
        neo4j._graph.run(sql_queries.ingest_csv(operator, identifier, os.path.basename(csv_path), batch_size = 100))



        # generate history file (for tracking the progress)
        processed_bl_list = []
        for log in logs:
            processed_bl_list.append(log['blockNumber'])

        latest_bl = max(processed_bl_list)

        # history.csv file is created in the same dir.
        job_summary = {}
        job_summary['job_time'] = datetime.now()
        job_summary['block_number'] = latest_bl
        job_summary = pd.DataFrame(job_summary, index=[0])


        if(os.path.exists(f'{os.path.dirname(__file__)}/history.csv')):
            history = pd.read_csv(f'{os.path.dirname(__file__)}/history.csv')
            history = pd.concat([history, job_summary])
            history.to_csv(f'{os.path.dirname(__file__)}/history.csv', index=False)
        else:
            job_summary.to_csv(f'{os.path.dirname(__file__)}/history.csv', index=False)
