import os,sys
import web3
from dotenv import load_dotenv
load_dotenv('../.env')
import json
from eth_account import Account
import requests
# EAAC parser
from . import agent_parser


def check_env_variable(var_name):
    # Attempt to retrieve the environment variable using os.getenv()
    value = os.getenv(var_name)
    # Check if the environment variable is None (not set)
    if value is None:
        # Raise an exception with a custom error message
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    
def check_ipfs_node():
    try:
        ipfs_node = os.getenv('IPFS_NODE')
        response = requests.post(f"http://127.0.0.1:5001/api/v0/version", timeout=5)  # Set a timeout for the request
        return response.status_code

    except requests.exceptions.RequestException as e:
        raise f"Failed to connect to IPFS node: {e}"

# env_vars = ['EAAC_ABI_PATH', 'IPFS_NODE', 'EAAC_ADDR']
# global vars
# ABI
check_env_variable('EAAC_ABI_PATH')
EAAC_ABI_PATH=os.getenv('EAAC_ABI_PATH')
f=open(EAAC_ABI_PATH)
EAAC_ABI = json.load(f)
EAAC_ABI = EAAC_ABI['abi']

#IPFS node
check_env_variable('IPFS_NODE')
IPFS_NODE= os.getenv('IPFS_NODE')

# EAAC deployment address
check_env_variable('EAAC_ADDR')
EAAC_ADDR = os.getenv('EAAC_ADDR')

#upload to ipfs
def upload_to_ipfs(file_path):
    # Load the JSON content to ensure it's properly formatted
    with open(f'{file_path}', 'rb') as file:  # Read as binary
        files = {'file': ('report.json', file)}  # Prepare the file
        add_response = requests.post('http://127.0.0.1:5001/api/v0/add', files=files)
        add_result = add_response.json()

    print("Added file hash:", add_result['Hash'])
    ipfs_hash = add_result['Hash']
    # Pin the file
    pin_response = requests.post(f'http://127.0.0.1:5001/api/v0/pin/add?arg={ipfs_hash}')
    pin_result = pin_response.json()
    print("Pinning result:", pin_result)

    return add_result['Hash']

# Retrieve and save the file
def get_from_ipfs(file_hash):
    # Retrieve the file using its hash
    get_response = requests.post(f'http://127.0.0.1:5001/api/v0/cat?arg={file_hash}')
    content = get_response.text
    json_content = json.loads(content)
    return json_content



# for langchain agent
def invoke_wrapper(original_invoke, executor_instance):
    """Decorator to wrap the 'invoke' method to add custom post-invocation logic."""
    def wrapped_invoke(*args, **kwargs):
        # Call the original method
        result = original_invoke(*args, **kwargs)
        
        # Custom logic after invoking
        print("Invoke method called (langchain). Checking for changes and running downstream tasks...")
        executor_instance.post_actions_langchain(result)
        
        return result
    return wrapped_invoke

# for crewai crew
def kickoff_wrapper(original_kickoff, executor_instance):
    """Decorator to wrap the 'invoke' method to add custom post-invocation logic."""
    def wrapped_kickoff(*args, **kwargs):
        # Call the original method
        result = original_kickoff(*args, **kwargs)
        
        # Custom logic after invoking
        print("Kickoff method called (crewai). Checking for changes and running downstream tasks...")
        executor_instance.post_actions_crewai(result)
        
        return result
    return wrapped_kickoff
# for autogen userproxy

def initchat_wrapper(original_initchat, executor_instance):
    """Decorator to wrap the 'invoke' method to add custom post-invocation logic."""
    def wrapped_initchat(*args, **kwargs):
        # Call the original method
        result = original_initchat(*args, **kwargs)
        
        # Custom logic after invoking
        print("Initchat method called (autogen). Checking for changes and running downstream tasks...")
        executor_instance.post_actions_autogen(result)
        
        return result
    return wrapped_initchat



# currently only assuming "invoke" methods of langchain
class CustomAgentExecutor:
    def __init__(self, agent_executor, identifier=None, output_path='.'):
        self.w3 = web3.Web3(web3.Web3.HTTPProvider(os.getenv('RPC_PROVIDER')))
        if not self.w3.is_connected():
            print("Failed to connect to the RPC node!")
            sys.exit(1)

        self.agent_executor = agent_executor
        self.identifier = identifier
        # self.register_to_EAAC(self.identifier) # for the downstream on-chain interaction we need to get approval. (not used for now)
        self.output_file = f'{output_path}/report.json'

        # check necessary conditions
        # for env_var in env_vars:
        #     check_env_variable('EAAC_ABI_PATH')
        response = check_ipfs_node()
        if(response==200):
            print("All env variables are set and IPFS node is functional. EAAC ready.")

    def __getattr__(self, name):
        """Delegate attribute access to the original AgentExecutor object."""
        attr = getattr(self.agent_executor, name)
        if callable(attr) and name == "invoke":  #langchain
            # Wrap only the 'invoke' method to postprocess
            return invoke_wrapper(attr, self)

        elif callable(attr) and name == "kickoff": # crewai
            # Wrap only the 'kickoff' method to postprocess
            return kickoff_wrapper(attr, self)

        elif callable(attr) and name == "initiate_chat": # autogen
            # Wrap only the 'initiate_chat' method to postprocess
            return initchat_wrapper(attr, self)

        return attr

    # not used for now as registering step currently doesn't serve unique purpose
    def register_to_EAAC(self, identifier:str=None):
        contract = self.w3.eth.contract(address=EAAC_ADDR, abi=EAAC_ABI)
        account = Account.from_key(os.getenv('PRIVATE_KEY'))
        print(account)
        
        # Call the function
        # if identifier is None:
        #     fn = contract.functions.register_agent_generic(account)
            # tx = self.build_tx(account, fn)
            # tx_hash = self.sign_send_tx(tx,account)
            # tx_receipt = self.get_tx_receipt(tx_hash)
        #     print(f"Registered agent (generic) to EAAC")
        # # case users want to put unique identifier for their agent/agent group
        # else:
        #     fn = contract.functions.register_agent(account, identifier)
        #     tx = self.build_tx(account, fn)
            # tx_hash = self.sign_send_tx(tx,account)
            # tx_receipt = self.get_tx_receipt(tx_hash)
        #     print(f"Registered agent {identifier} to EAAC")


    def report_to_EAAC(self,ipfs_hash:str, identifier:str=None):
        contract = self.w3.eth.contract(address=EAAC_ADDR, abi=EAAC_ABI)
        account = Account.from_key(os.getenv('PRIVATE_KEY'))
        
        # Call the function
        if identifier is None:
            fn = contract.functions.report_activity_generic(account.address,ipfs_hash)
            tx = self.build_tx(account, fn)
            tx_hash = self.sign_send_tx(tx,account)
            tx_receipt = self.get_tx_receipt(tx_hash)
            print(f"Reported activity of the agent (generic) to EAAC")
        # case users want to put unique identifier for their agent/agent group
        else:
            fn = contract.functions.report_activity(account.address, identifier, ipfs_hash)
            tx = self.build_tx(fn, account)
            tx_hash = self.sign_send_tx(tx,account)
            tx_receipt = self.get_tx_receipt(tx_hash)
            print(f"Reported activity of the agent (generic) to EAAC")


        
    def post_actions_langchain(self, response):
        print("[EAAC] Running downstream tasks for a langchain agent...")
        # parse the response
        # content is a EAAC_content 
        content = agent_parser.parse_langchain_agent(self, response)
        agent_parser.save_to_json(content, self.output_file)
        # upload to IPFS
        ipfs_hash = upload_to_ipfs(self.output_file)
        # report with the resulting ipfs hash
        self.report_to_EAAC(ipfs_hash, self.identifier)
        print("Reported activity to EAAC")
        
        
    def post_actions_crewai(self, response):
        print("[EAAC] Running downstream tasks for a crewai agent group...")
        # parse the response
        # content is a EAAC_content 
        content = agent_parser.parse_crewai_agent(self, response)
        agent_parser.save_to_json(content, self.output_file)
        # upload to IPFS
        ipfs_hash = upload_to_ipfs(self.output_file)
        # report with the resulting ipfs hash
        self.report_to_EAAC(ipfs_hash, self.identifier)
        print("Reported activity to EAAC")


    def post_actions_autogen(self, response):
        print("[EAAC] Running downstream tasks for an autogen agent group...")
        # parse the response
        # content is a EAAC_content 
        content = agent_parser.parse_autogen_agent(self, response)
        agent_parser.save_to_json(content, self.output_file)
        # upload to IPFS
        ipfs_hash = upload_to_ipfs(self.output_file)
        # report with the resulting ipfs hash
        self.report_to_EAAC(ipfs_hash, self.identifier)
        print("Reported activity to EAAC")


    def build_tx(self, fn_with_input, account):
        tx = fn_with_input.build_transaction({
              'chainId': int(os.getenv('CHAIN_ID')),  # Sepolia chainID
                'gas': 2000000,
                'gasPrice': self.w3.to_wei('100', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
        return tx

    def sign_send_tx(self, tx, account):
        signed_tx = self.w3.eth.account.sign_transaction(tx, os.getenv('PRIVATE_KEY'))
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f'Transaction hash: {tx_hash.hex()}')
        return tx_hash

    def get_tx_receipt(self, tx_hash):
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Transaction receipt: {tx_receipt}')
        return tx_receipt
