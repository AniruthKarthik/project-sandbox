# Leaderboard CLI

This project is a command-line interface (CLI) for managing a leaderboard. It uses a C++ application for the front-end and a Java application for the back-end, which connects to a Dolt database.

## Features

*   Generate random user data for the leaderboard.
*   View top and last players.
*   View players within a specific rank range.
*   Add, update, and delete users.
*   Calculate the sum of scores for top, last, or a range of players.
*   Execute custom SQL queries on the database.

## Prerequisites

*   A C++ compiler that supports C++14 (e.g., g++)
*   Java Development Kit (JDK)
*   Dolt
*   MySQL Connector/J (included in the project)

## Setup

1.  **Initialize Dolt:**
    Before running the application, you need to initialize a Dolt repository and start the Dolt SQL server.

    ```bash
    dolt init
    dolt sql-server &
    ```

2.  **Configure Database User:**
    The application connects to the Dolt database using the username 'ani' and an empty password. Make sure you have a user with these credentials in your Dolt database. You can create a user in Dolt using the following command:

    ```bash
    dolt sql -q "CREATE USER 'ani'@'localhost' IDENTIFIED BY ''"
    dolt sql -q "GRANT ALL PRIVILEGES ON *.* TO 'ani'@'localhost'"
    ```

## Build and Run

To build and run the application, use the following command:

```bash
make cli
```

This will compile the C++ and Java code and start the interactive CLI.

## Commands

The following commands are available in the Leaderboard CLI:

*   `generate <n>`: Generates `n` random users and populates the leaderboard.
    *   Example: `generate 10`

*   `top <n>`: Displays the top `n` players from the leaderboard.
    *   Example: `top 5`

*   `last <n>`: Displays the last `n` players from the leaderboard.
    *   Example: `last 5`

*   `from <m> to <n>`: Displays players ranked from `m` to `n`.
    *   Example: `from 3 to 7`

*   `add <id> <name> <score>`: Adds a new user with the given `id`, `name`, and `score`.
    *   Example: `add 100 "kilschd dc" 23323`

*   `update <id> <score>`: Updates the score of the user with the given `id`.
    *   Example: `update 21 232323`

*   `delete <id>`: Deletes the user with the given `id`.
    *   Example: `delete 23`

*   `sum top <n>`: Calculates and displays the sum of scores for the top `n` players.
    *   Example: `sum top 5`

*   `sum last <n>`: Calculates and displays the sum of scores for the last `n` players.
    *   Example: `sum last 5`

*   `sum from <m> to <n>`: Calculates and displays the sum of scores for players ranked from `m` to `n`.
    *   Example: `sum from 3 to 7`

*   `customsql <query>`: Executes a custom SQL query on the database. The query must end with a semicolon.
    *   Example: `customsql SELECT COUNT(*) FROM scores;`

*   `exit`: Exits the Leaderboard CLI.
