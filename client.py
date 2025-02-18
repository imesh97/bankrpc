"""
bankRPC - Distributed Banking
By: Imesh Nimsitha
2025/02/05
Client.py Implementation
"""

import bank_pb2_grpc
import bank_pb2
import grpc

class BankClient:
    """Client for the gRPC bank service"""

    def __init__(self, server_address="localhost:50051"):
        """Initializes new bank client"""
        self.channel = grpc.insecure_channel(server_address)
        self.stub = bank_pb2_grpc.BankServiceStub(self.channel)
    
    def create_account(self, account_id, account_type):
        """Creates a new bank account with error handling"""
        try:
            response = self.stub.CreateAccount(bank_pb2.AccountRequest(account_id=account_id, account_type=account_type))
            return response.message
        except grpc.RpcError as e:
            return f"Error: {e.details()}"
    
    def get_balance(self, account_id):
        """Retrieves the account balance with error handling"""
        try:
            response = self.stub.GetBalance(bank_pb2.AccountRequest(account_id=account_id))
            return response.balance
        except grpc.RpcError as e:
            return f"Error: {e.details()}"
    
    def deposit(self, account_id, amount):
        """Deposits the amount into the account with error handling"""
        try:
            response = self.stub.Deposit(bank_pb2.DepositRequest(account_id=account_id, amount=amount))
            return f"{response.message} | New balance: {response.balance}"
        except grpc.RpcError as e:
            return f"Error: {e.details()}"

    def withdraw(self, account_id, amount):
        """Withdraws the amount from the account with error handling"""
        try:
            response = self.stub.Withdraw(bank_pb2.WithdrawRequest(account_id=account_id, amount=amount))
            return f"{response.message} | New balance: {response.balance}"
        except grpc.RpcError as e:
            return f"Error: {e.details()}"

    def calculate_interest(self, account_id, interest_rate):
        """Calculates the interest for the account with error handling"""
        try:
            response = self.stub.CalculateInterest(bank_pb2.InterestRequest(account_id=account_id, annual_interest_rate=interest_rate))
            return f"{response.message} | New balance: {response.balance}"
        except grpc.RpcError as e:
            return f"Error: {e.details()}"

if __name__ == '__main__':
    client = BankClient()  # Initializes new bank client
    print("Client connected...")

    print("\nTEST CODE")  # Testing basic functionality
    print(client.create_account('admin123', 'Savings'))
    print(f"Balance: {client.get_balance('admin123')}")
    print(client.deposit('admin123', 1000.0))
    print(client.withdraw('admin123', 200.0))
    print(client.calculate_interest('admin123', 5.0))
    print(f"New Balance: {client.get_balance('admin123')}")
