import java.sql.*;
import java.util.Random;
import java.util.StringJoiner;

public class DBConnector {

    // --- Database Configuration ---
    // Make sure to create this database in your Dolt/MySQL instance
    private static final String DB_NAME = "leaderboard_db"; 
    // Assumes DoltDB/MySQL is running on localhost default port
    private static final String DB_URL_SERVER = "jdbc:mysql://localhost:3306/";
    private static final String DB_URL = DB_URL_SERVER + DB_NAME;
    // Replace with your DB user and password
    private static final String USER = "ani";
    private static final String PASS = ""; // Default for many local setups

    private static final String TABLE_NAME = "scores";

    public static void main(String[] args) {
        if (args.length == 0) {
            System.err.println("Usage: java DBConnector <command> [options]");
            return;
        }

        try {
            ensureDatabaseExists();
        } catch (SQLException e) {
            System.err.println("Failed to ensure database exists. Please check your MySQL connection and credentials.");
            e.printStackTrace();
            return;
        }

        String command = args[0];
        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASS)) {
            // Ensure table exists
            initializeDatabase(conn);

            switch (command) {
                case "generate":
                    if (args.length > 1) {
                        int count = Integer.parseInt(args[1]);
                        generateData(conn, count);
                    }
                    break;
                case "add":
                    if (args.length > 3) {
                        int id = Integer.parseInt(args[1]);
                        String name = args[2];
                        int score = Integer.parseInt(args[3]);
                        addUser(conn, id, name, score);
                    }
                    break;
                case "update":
                     if (args.length > 2) {
                        int id = Integer.parseInt(args[1]);
                        int score = Integer.parseInt(args[2]);
                        updateUser(conn, id, score);
                    }
                    break;
                case "delete":
                     if (args.length > 1) {
                        int id = Integer.parseInt(args[1]);
                        deleteUser(conn, id);
                    }
                    break;
                case "get_all":
                    getAllUsers(conn);
                    break;
                case "customsql":
                    if (args.length > 1) {
                        // Re-join arguments that might have been split by the shell
                        StringJoiner sj = new StringJoiner(" ");
                        for (int i = 1; i < args.length; i++) {
                            sj.add(args[i]);
                        }
                        executeCustomSql(conn, sj.toString());
                    }
                    break;
                default:
                    System.err.println("Unknown command: " + command);
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    private static void ensureDatabaseExists() throws SQLException {
        try (Connection conn = DriverManager.getConnection(DB_URL_SERVER, USER, PASS);
             Statement stmt = conn.createStatement()) {
            stmt.executeUpdate("CREATE DATABASE IF NOT EXISTS " + DB_NAME);
        }
    }

    private static void initializeDatabase(Connection conn) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            // Use IF NOT EXISTS to prevent errors on subsequent runs
            String createTableSQL = "CREATE TABLE IF NOT EXISTS " + TABLE_NAME + " ("
                                  + "id INT PRIMARY KEY, "
                                  + "name VARCHAR(255) NOT NULL, "
                                  + "score INT NOT NULL)";
            stmt.executeUpdate(createTableSQL);

            // Check if the 'name' column exists before trying to add it
            ResultSet rs = conn.getMetaData().getColumns(null, null, TABLE_NAME, "name");
            if (!rs.next()) {
                stmt.executeUpdate("ALTER TABLE " + TABLE_NAME + " ADD COLUMN name VARCHAR(255) NOT NULL");
            }
        }
    }
    
    private static void generateData(Connection conn, int count) throws SQLException {
         // Clear existing data
        try (Statement stmt = conn.createStatement()) {
            stmt.executeUpdate("DELETE FROM " + TABLE_NAME);
            System.out.println("Cleared old data.");
        }

        String sql = "INSERT INTO " + TABLE_NAME + " (id, name, score) VALUES (?, ?, ?)";
        Random rand = new Random();
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            for (int i = 1; i <= count; i++) {
                pstmt.setInt(1, i);
                pstmt.setString(2, generateRandomName());
                pstmt.setInt(3, rand.nextInt(10000)); // Scores between 0 and 9999
                pstmt.addBatch();
            }
            pstmt.executeBatch();
            System.out.println("Successfully generated " + count + " users.");
        }
    }

    private static String generateRandomName() {
        String[] firstNames = {"John", "Jane", "Peter", "Mary", "David", "Susan", "Robert", "Karen", "Michael", "Lisa"};
        String[] lastNames = {"Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"};
        Random rand = new Random();
        String firstName = firstNames[rand.nextInt(firstNames.length)];
        String lastName = lastNames[rand.nextInt(lastNames.length)];
        return firstName + " " + lastName;
    }
    
    private static void addUser(Connection conn, int id, String name, int score) throws SQLException {
        String sql = "INSERT INTO " + TABLE_NAME + " (id, name, score) VALUES (?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            pstmt.setString(2, name);
            pstmt.setInt(3, score);
            int rowsAffected = pstmt.executeUpdate();
             if (rowsAffected > 0) {
                System.out.println("User " + name + " added successfully.");
            } else {
                System.out.println("Could not add user " + name + ".");
            }
        }
    }

    private static void updateUser(Connection conn, int id, int score) throws SQLException {
        String sql = "UPDATE " + TABLE_NAME + " SET score = ? WHERE id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, score);
            pstmt.setInt(2, id);
            int rowsAffected = pstmt.executeUpdate();
            if (rowsAffected > 0) {
                System.out.println("User with id " + id + " updated successfully.");
            } else {
                System.out.println("User with id " + id + " not found.");
            }
        }
    }

    private static void deleteUser(Connection conn, int id) throws SQLException {
        String sql = "DELETE FROM " + TABLE_NAME + " WHERE id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            int rowsAffected = pstmt.executeUpdate();
            if (rowsAffected > 0) {
                System.out.println("User " + id + " deleted successfully.");
            } else {
                System.out.println("User " + id + " not found.");
            }
        }
    }

    private static void getAllUsers(Connection conn) throws SQLException {
        String sql = "SELECT id, name, score FROM " + TABLE_NAME;
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            while (rs.next()) {
                // Output format for C++ to parse: id name\tscore
                System.out.println(rs.getInt("id") + " " + rs.getString("name") + "\t" + rs.getInt("score"));
            }
        }
    }

    private static void executeCustomSql(Connection conn, String sql) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            boolean hasResultSet = stmt.execute(sql);

            if (hasResultSet) {
                try (ResultSet rs = stmt.getResultSet()) {
                    ResultSetMetaData rsmd = rs.getMetaData();
                    int columnsNumber = rsmd.getColumnCount();
                    
                    // Print header
                    for (int i = 1; i <= columnsNumber; i++) {
                        System.out.printf("%-20s", rsmd.getColumnName(i));
                    }
                    System.out.println();
                    for (int i = 1; i <= columnsNumber; i++) {
                        System.out.printf("%-20s", "--------------------");
                    }
                    System.out.println();


                    // Print rows
                    while (rs.next()) {
                        for (int i = 1; i <= columnsNumber; i++) {
                            System.out.printf("%-20s", rs.getString(i));
                        }
                        System.out.println();
                    }
                }
            } else {
                System.out.println("Query executed successfully. " + stmt.getUpdateCount() + " rows affected.");
            }
        }
    }
}