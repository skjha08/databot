Feature: DataBot Spec v1.0 Behavior

  Scenario: Happy path EDA
    Given a user provides a valid CSV filepath and a data analysis query
    When the DataBot routes to the appropriate skill
    Then the agent MUST call `load_dataset` before any other tool
    And it should output a JSON response with status "success"

  Scenario: Blocked directory traversal
    Given a user provides a filepath containing ".." or starting with "/"
    When the DataBot receives the input
    Then it MUST reject the request before touching any tools
    And it should return a JSON response with status "error"

  Scenario: Blocked prompt injection
    Given a user provides a query that matches known injection patterns like "ignore previous instructions"
    When the DataBot validates the input
    Then it MUST reject the request before routing to any skill
    And it should return a JSON response with status "error"

  Scenario: Missing-value warning trigger
    Given a user provides a valid CSV dataset and query
    And the dataset contains a column with greater than 30% missing values
    When the DataBot processes the query and calls tools
    Then the final JSON response's `warnings` list MUST mention the high percentage of missing values
