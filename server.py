import bank_pb2_grpc
import bank_pb2
import redis
import json
import grpc
from concurrent import futures

class BankService(bank_pb2_grpc.BankServiceServicer):
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def _get_account(self, account_id):
        data = self.redis.get(account_id)
        return json.loads(data) if data else None

    def _set_account(self, account_id, data):
        self.redis.set(account_id, json.dumps(data))

    def CreateAccount(self, request, context):
        if self.redis.exists(request.account_id):
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('Account already exists.')
            return bank_pb2.AccountResponse()

        data = {
            "account_type": request.account_type,
            "balance": 0.0
        }
        self._set_account(request.account_id, data)

        return bank_pb2.AccountResponse(account_id=request.account_id,message="Account created.")

    def GetBalance(self, request, context):
        data = self._get_account(request.account_id)
        if not data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Account not found. Please check the account ID.')
            return bank_pb2.BalanceResponse()

        return bank_pb2.BalanceResponse(account_id=request.account_id, balance=data['balance'], message="Balance retrieved.")
    
    def Deposit(self, request, context):
        if request.amount <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Transaction amount must be positive.')
            return bank_pb2.TransactionResponse()

        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(request.account_id)
                    data = self._get_account(request.account_id)
                    if not data:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details('Account not found. Please check the account ID.')
                        return bank_pb2.TransactionResponse()
                    
                    data['balance'] += request.amount
                    pipe.multi()
                    pipe.set(request.account_id, json.dumps(data))
                    pipe.execute()
                    self._set_account(request.account_id, data)
                    return bank_pb2.TransactionResponse(account_id=request.account_id, balance=data['balance'], message="Deposit successful.")
                except redis.WatchError:
                    continue
    
    def Withdraw(self, request, context):
        if request.amount <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Transaction amount must be positive.')
            return bank_pb2.TransactionResponse()
        
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(request.account_id)
                    data = self._get_account(request.account_id)
                    if not data:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details('Account not found. Please check the account ID.')
                        return bank_pb2.TransactionResponse()
                    
                    if data['balance'] < request.amount:
                        context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                        context.set_details('Insufficient funds for the requested withdrawal.')
                        return bank_pb2.TransactionResponse()
                    
                    data['balance'] -= request.amount
                    pipe.multi()
                    pipe.set(request.account_id, json.dumps(data))
                    pipe.execute()
                    self._set_account(request.account_id, data)
                    return bank_pb2.TransactionResponse(account_id=request.account_id, balance=data['balance'], message="Withdraw successful.")
                except redis.WatchError:
                    continue
    
    def CalculateInterest(self, request, context):
        if request.annual_interest_rate <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Annual interest rate must be a positive value.')
            return bank_pb2.TransactionResponse()
        
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(request.account_id)
                    data = self._get_account(request.account_id)
                    if not data:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details('Account not found. Please check the account ID.')
                        return bank_pb2.TransactionResponse()
                    
                    data['balance'] += data['balance'] * (request.annual_interest_rate / 100)
                    pipe.multi()
                    pipe.set(request.account_id, json.dumps(data))
                    pipe.execute()
                    self._set_account(request.account_id, data)
                    return bank_pb2.TransactionResponse(account_id=request.account_id, balance=data['balance'], message="Interest calculated and deposited.")
                except redis.WatchError:
                    continue

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bank_pb2_grpc.add_BankServiceServicer_to_server(BankService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
