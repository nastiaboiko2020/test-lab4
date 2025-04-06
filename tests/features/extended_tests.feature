Feature: Extended tests for Product, ShoppingCart, and Order
  We want to test edge cases and boundary behavior of the e-shop system

  Scenario: Check product availability with zero amount
    Given The product has availability of 0
    When I check if 1 items are available
    Then The product should not be available

  Scenario: Check product availability with negative amount
    Given The product has availability of 5
    When I check if -1 items are available
    Then The product should be available

  Scenario: Add product to cart with zero amount
    Given The product has availability of 10
    And An empty shopping cart
    When I add product to the cart in amount 0
    Then Product is added to the cart successfully

  Scenario: Add product to cart with negative amount
    Given The product has availability of 10
    And An empty shopping cart
    When I add product to the cart in amount -1
    Then Product is not added to cart successfully

  Scenario: Remove non-existent product from cart
    Given An empty shopping cart
    And A product with name "Book"
    When I remove the product from the cart
    Then The cart should be empty

  Scenario: Calculate total for empty cart
    Given An empty shopping cart
    When I calculate the total price
    Then The total price should be 0

  Scenario: Submit order with empty cart
    Given An empty shopping cart
    And An order with the cart
    When I place the order
    Then The order should be placed successfully

  Scenario: Add product with None amount to cart
    Given The product has availability of 10
    And An empty shopping cart
    When I add product to the cart with None amount
    Then Product is not added to cart successfully

  Scenario: Buy product with exact available amount
    Given The product has availability of 5
    When I buy 5 items of the product
    Then The product should have 0 items available

  Scenario: Create product with negative price
    Given I create a product with price -10 and availability 5
    When I check the product price
    Then The product price should be -10