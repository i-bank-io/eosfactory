import shutil

import eosfactory.core.logger as logger
import eosfactory.core.errors as errors
import eosfactory.core.config as config
import eosfactory.core.setup as setup
import eosfactory.core.teos as teos
import eosfactory.core.cleos as cleos
import eosfactory.core.cleos_set as cleos_set


class ContractBuilder():
    '''
    '''
    def __init__(
            self, contract_dir,
            verbosity=None,
            abi_file=None,
            wasm_file=None):

        self.contract_dir = config.contract_dir(contract_dir)
        
        if not self.contract_dir:
            raise errors.Error("""
                Cannot determine the contract directory. The path is 
                ``{}``.
                """.format(contract_dir))
            return

        self.abi_file = abi_file
        self.wasm_file = wasm_file

    def path(self):
        return self.contract_dir

    def build_wast(self):
        teos.WAST(self.contract_dir)

    def build_abi(self):
        teos.ABI(self.contract_dir)

    def build(self, force=True):
        if force or not self.is_built():
            self.build_abi()
            self.build_wast()

    def is_built(self):
        return cleos.contract_is_built(
            self.contract_dir, self.wasm_file, self.abi_file)

    def delete(self):
        try:
            shutil.rmtree(str(self.contract_dir))
            return True
        except:
            return False


class Contract(ContractBuilder):

    def __init__(
            self, account, contract_dir,
            abi_file=None, wasm_file=None,
            permission=None,
            expiration_sec=None,
            skip_signature=0, dont_broadcast=0, force_unique=0,
            max_cpu_usage=0, max_net_usage=0,
            ref_block=None,
            verbosity=None):
        
        super().__init__(
            contract_dir, verbosity=verbosity,
            abi_file=abi_file, wasm_file=wasm_file)
        self.account = account
        self.expiration_sec = expiration_sec
        self.skip_signature = skip_signature
        self.dont_broadcast = dont_broadcast
        self.force_unique = force_unique
        self.max_cpu_usage = max_cpu_usage
        self.max_net_usage = max_net_usage
        self.ref_block = ref_block
        self.verbosity = verbosity
        self.contract = None
        self._console = None

    def deploy(
        self, permission=None, dont_broadcast=None, payer=None):
        if not self.is_built():
            raise errors.Error('''
            Contract needs to be built before deployment.
            ''')
            return
        if dont_broadcast is None:
            dont_broadcast = self.dont_broadcast
        try:
            result = cleos_set.set_contract(
                self.account, self.contract_dir, 
                self.wasm_file, self.abi_file, 
                permission, self.expiration_sec, 
                self.skip_signature, dont_broadcast, self.force_unique,
                self.max_cpu_usage, self.max_net_usage,
                self.ref_block,
                is_verbose=False,
                json=False)

        except errors.LowRamError as e:
            logger.TRACE('''
            * RAM needed is {}.kByte, buying RAM {}.kByte.
            '''.format(
                e.needs_kbyte,
                e.deficiency_kbyte))

            buy_ram_kbytes = str(
                e.deficiency_kbyte + 1)
            if not payer:
                payer = self.account

            payer.buy_ram(buy_ram_kbytes, self.account)
        
            result = cleos_set.set_contract(
                self.account, self.contract_dir, 
                self.wasm_file, self.abi_file, 
                permission, self.expiration_sec, 
                self.skip_signature, dont_broadcast, self.force_unique,
                self.max_cpu_usage, self.max_net_usage,
                self.ref_block,
                is_verbose=False,
                json=False)

        logger.INFO('''
        * Contract {} is deployed. 
        '''.format(self.contract_dir))            
        
        self.contract = result

    def push_action(
            self, action, data,
            permission=None, expiration_sec=None, 
            skip_signature=0, dont_broadcast=0, force_unique=0,
            max_cpu_usage=0, max_net_usage=0,
            ref_block=None, json=False):
        self.account.push_action(action, data,
            permission, expiration_sec,
            skip_signature, dont_broadcast, force_unique,
            max_cpu_usage, max_net_usage,
            ref_block, json)

    def show_action(self, action, data, permission=None):
        ''' Implements the `push action` command without broadcasting. 
        '''
        self.account.show_action(action, data, permission)

    def table(
            self, table_name, scope="",
            binary=False, 
            limit=10, key="", lower="", upper=""):
        ''' Return contract's table object.
        '''
        return self.account.table(
            table_name, scope,
            binary, 
            limit, key, lower, upper)

    def code(self, code="", abi="", wasm=False):
        return self.account.code(code, abi, wasm)

    def console(self):
        return self._console

    def path(self):
        ''' Return contract directory path.
        '''
        if self.contract:
            return str(self.contract.contract_path_absolute)
        else:
            return str(self.contract_dir)
            
    def __str__(self):
        if self.contract and not self.contract.err_msg:
            return str(self.contract)
        else:
            return str(self.account)
