Feature: Shipping Service
  Scenario: Creating a shipping order
    Given a shipping service
    When I create a shipping order with order_id "order123", user_id "user123", and address "address123"
    Then the shipping order should have order_id "order123", user_id "user123", and address "address123"
