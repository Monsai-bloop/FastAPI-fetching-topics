# import pytest

# # production code
# def process_payment(payment_gateway, amount):
#     response = payment_gateway.charge(amount)
#     if response == "Success":
#         return "Payment processed successfully"
#     else:
#         raise ValueError("Payment failed")
    

# def test_process_payment_with_side_effect(mocker):
#     mock_payment_gateway = mocker.Mock()
#     mock_payment_gateway.charge.side_effect = ["Success", ValueError("Insufficient funds")]
    
#     assert process_payment(mock_payment_gateway, 100) == "Payment processed successfully"
#     with pytest.raises(ValueError, match="Insufficient funds"):
#         process_payment(mock_payment_gateway, 200)
    
#     assert mock_payment_gateway.charge.call_count == 2