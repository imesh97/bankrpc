"""
bankRPC - Distributed Banking
By: Imesh Nimsitha
2025/02/05
Server.py Implementation
"""

from os import getenv
import bank_pb2_grpc
import bank_pb2
import redis
import json
import grpc
from concurrent import futures

class BankService(bank_pb2_grpc.BankServiceServicer):
    """Implements the gRPC bank service"""

    def __init__(self):
        """Initialize Redis connection"""
        self.redis = redis.Redis(getenv("REDIS_HOST", "localhost"), port=6379, db=0)
        self.MAX_RETRIES = 3  # No infinite retries (deadlock prevention)

    def _get_account(self, account_id):
        """Helper function for getting JSON account data from Redis"""
        data = self.redis.get(account_id)
        return json.loads(data) if data else None

    def _set_account(self, account_id, data):
        """Helper function for setting JSON account data in Redis"""
        self.redis.set(account_id, json.dumps(data))

    def CreateAccount(self, request, context):
        """Creates a new account"""
        retries = 0
        while retries < self.MAX_RETRIES:  # Prevents optimistic locking
            try:
                with self.redis.pipeline() as pipe:
                    pipe.watch(request.account_id)
                    if self.redis.exists(request.account_id):  # Check if account already exists
                        context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                        context.set_details('Account already exists.')
                        return bank_pb2.AccountResponse()

                    data = {  # New account data
                        "account_type": request.account_type,
                        "balance": 0.0
                    }
                    self._set_account(request.account_id, data)

                    return bank_pb2.AccountResponse(account_id=request.account_id,message="Account created.")
            
            except redis.WatchError:
                retries += 1
                continue
        
        context.set_code(grpc.StatusCode.ABORTED)
        context.set_details('Failed to create account after multiple retries.')
        return bank_pb2.AccountResponse()

    def GetBalance(self, request, context):
        """Retrieves the balance for the account"""
        data = self._get_account(request.account_id)
        if not data:  # Check if account exists
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Account not found. Please check the account ID.')
            return bank_pb2.BalanceResponse()

        return bank_pb2.BalanceResponse(account_id=request.account_id, balance=data['balance'], message="Balance retrieved.")
    
    def Deposit(self, request, context):
        """Deposits the amount into the account"""
        if request.amount <= 0:  # Check if amount is positive
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Transaction amount must be positive.')
            return bank_pb2.TransactionResponse()

        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                with self.redis.pipeline() as pipe:
                    pipe.watch(request.account_id)  # Watch for account data changes
                    data = self._get_account(request.account_id)
                    if not data:  # Check if account exists
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details('Account not found. Please check the account ID.')
                        return bank_pb2.TransactionResponse()
                    
                    data['balance'] += request.amount  # Update balance
                    pipe.multi()  # Start transaction
                    pipe.set(request.account_id, json.dumps(data))
                    pipe.execute()  # Execute the transaction
                    return bank_pb2.TransactionResponse(account_id=request.account_id, balance=data['balance'], message="Deposit successful.")
            
            except redis.WatchError:  # Handle concurrent updates
                retries += 1
                continue
        
        context.set_code(grpc.StatusCode.ABORTED)
        context.set_details('Failed to update account after multiple retries.')
        return bank_pb2.TransactionResponse()
    
    def Withdraw(self, request, context):
        """Withdraws the amount from the account"""
        if request.amount <= 0:  # Check if amount is positive
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Transaction amount must be positive.')
            return bank_pb2.TransactionResponse()
        
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                with self.redis.pipeline() as pipe:
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
                    
                    data['balance'] -= request.amount  # Update balance
                    pipe.multi()  # Transaction occurs
                    pipe.set(request.account_id, json.dumps(data))
                    pipe.execute()
                    return bank_pb2.TransactionResponse(account_id=request.account_id, balance=data['balance'], message="Withdraw successful.")
            
            except redis.WatchError:
                retries += 1
                continue
        
        context.set_code(grpc.StatusCode.ABORTED)
        context.set_details('Failed to update account after multiple retries.')
        return bank_pb2.TransactionResponse()
    
    def CalculateInterest(self, request, context):
        """Calculates the interest on the account"""
        if request.annual_interest_rate <= 0:  # Check if annual interest rate is positive
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Annual interest rate must be a positive value.')
            return bank_pb2.TransactionResponse()
        
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                with self.redis.pipeline() as pipe:
                    pipe.watch(request.account_id)
                    data = self._get_account(request.account_id)
                    if not data:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details('Account not found. Please check the account ID.')
                        return bank_pb2.TransactionResponse()
                    
                    data['balance'] += data['balance'] * (request.annual_interest_rate / 100)  # Calculate interest and deposit
                    pipe.multi()  # Transaction occurs
                    pipe.set(request.account_id, json.dumps(data))
                    pipe.execute()
                    return bank_pb2.TransactionResponse(account_id=request.account_id, balance=data['balance'], message="Interest calculated and deposited.")
            
            except redis.WatchError:
                retries += 1
                continue
        
        context.set_code(grpc.StatusCode.ABORTED)
        context.set_details('Failed to update account after multiple retries.')
        return bank_pb2.TransactionResponse()
        

def serve():
    """Starts the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # Locking mechanism with 10 threads
    bank_pb2_grpc.add_BankServiceServicer_to_server(BankService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
