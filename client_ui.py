import bank_pb2_grpc
from client import BankClient
import grpc
import streamlit as st

def main():
    """Run the Streamlit web interface"""

    st.title("🏦 bankRPC — Distributed Banking")  # title and description
    st.markdown("Connect and interact with the [gRPC](https://grpc.io/) Banking Service. Powered by [Redis](https://redis.io/). Developed by [Nimsitha](https://www.nimsitha.com).")

    if 'client' not in st.session_state:  # initializes new client with empty session state
        st.session_state.client = None

    with st.sidebar:  # Create sidebar to connect to server
        st.header("Service Connection")
        server_address = st.text_input(
            "Server Address", 
            "localhost:50051",
            help="Format: hostname:port"
        )
        
        if st.button("Connect to Bank Service"):
            try:
                st.session_state.client = BankClient()
                st.session_state.client.channel = grpc.insecure_channel(server_address)
                st.session_state.client.stub = bank_pb2_grpc.BankServiceStub(
                    st.session_state.client.channel
                )
                st.success("Connected to bank service...")
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")

    if st.session_state.client:  # If client is connected -> show management UI
        st.header("Bank Account Management")
        operation = st.selectbox(
            "Choose Operation",
            ["Create Account", "Deposit", "Withdraw", 
             "Calculate Interest", "Check Balance"]
        )

        # Choosing between different operations
        if operation == "Create Account":
            with st.form("create_account"):
                account_id = st.text_input("Account ID")
                account_type = st.selectbox("Account Type", ["savings", "checking"])
                submitted = st.form_submit_button("Create Account")
                
                if submitted:
                    result = st.session_state.client.create_account(account_id, account_type)
                    if "Error" in result:
                        st.error(result)
                    else:
                        st.success(result)

        elif operation == "Deposit":
            with st.form("deposit"):
                account_id = st.text_input("Account ID")
                amount = st.number_input("Amount", min_value=0.01, format="%.2f")
                submitted = st.form_submit_button("Deposit")
                
                if submitted:
                    result = st.session_state.client.deposit(account_id, amount)
                    if "Error" in result:
                        st.error(result)
                    else:
                        st.success(result)

        elif operation == "Withdraw":
            with st.form("withdraw"):
                account_id = st.text_input("Account ID")
                amount = st.number_input("Amount", min_value=0.01, format="%.2f")
                submitted = st.form_submit_button("Withdraw")
                
                if submitted:
                    result = st.session_state.client.withdraw(account_id, amount)
                    if "Error" in result:
                        st.error(result)
                    else:
                        st.success(result)

        elif operation == "Calculate Interest":
            with st.form("interest"):
                account_id = st.text_input("Account ID")
                rate = st.number_input("Annual Interest Rate (%)", min_value=0.01, format="%.2f")
                submitted = st.form_submit_button("Calculate Interest")
                
                if submitted:
                    result = st.session_state.client.calculate_interest(account_id, rate)
                    if "Error" in result:
                        st.error(result)
                    else:
                        st.success(result)

        elif operation == "Check Balance":
            with st.form("balance"):
                account_id = st.text_input("Account ID")
                submitted = st.form_submit_button("Check Balance")
                
                if submitted:
                    result = st.session_state.client.get_balance(account_id)
                    if "Error" in str(result):
                        st.error(result)
                    else:
                        st.metric("Current Balance", f"${result:.2f}")

    else:  # Must connect to server before using management UI
        st.warning("Please connect to the bank service using the sidebar first.")

if __name__ == "__main__":
    main()