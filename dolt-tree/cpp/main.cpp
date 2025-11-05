#include "segment_tree.h"
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

// --- Global Variables ---
std::vector<User> leaderboard_data;
std::unique_ptr<SegmentTree> seg_tree;
std::map<int, int> user_id_to_index;

// --- Function Prototypes ---
std::string exec_java(const std::vector<std::string> &args);
void refresh_data();
void print_header(const std::string &title);
void print_footer();
void print_users(const std::vector<User> &users, int start_rank = 1);
void handle_generate(int n);
void handle_top(int n);
void handle_last(int n);
void handle_range(int m, int n);
void handle_sum_top(int n);
void handle_sum_last(int n);
void handle_sum_range(int m, int n);
void handle_update(int id, int score);
void handle_add(int id, const std::string &name, int score);
void handle_delete(int id);
void handle_custom_sql(std::string full_query);

// --- Main Function ---
int main()
{
	refresh_data();

	std::string line;
	std::cout << "Leaderboard CLI> " << std::flush;
	while (std::getline(std::cin, line))
	{
		std::stringstream ss(line);
		std::string command;
		ss >> command;

		try
		{
			if (command == "generate" && ss)
			{
				int n;
				ss >> n;
				handle_generate(n);
			}
			else if (command == "top" && ss)
			{
				int n;
				ss >> n;
				handle_top(n);
			}
			else if (command == "last" && ss)
			{
				int n;
				ss >> n;
				handle_last(n);
			}
			else if (command == "from" && ss)
			{
				int m, n;
				std::string to_str;
				ss >> m >> to_str >> n;
				if (to_str == "to")
					handle_range(m, n);
				else
					std::cerr << "Invalid range format. Use: from M to N"
				          << std::endl;
			}
			else if (command == "update" && ss)
			{
				int id, score;
				ss >> id >> score;
				handle_update(id, score);
			}
			else if (command == "add" && ss)
			{
				int id, score;
				std::string name;
				ss >> id >> std::quoted(name) >> score;
				handle_add(id, name, score);
			}
			else if (command == "delete" && ss)
			{
				int id;
				ss >> id;
				handle_delete(id);
			}
			else if (command == "sum" && ss)
			{
				std::string sub_cmd;
				ss >> sub_cmd;
				if (sub_cmd == "top" && ss)
				{
					int n;
					ss >> n;
					handle_sum_top(n);
				}
				else if (sub_cmd == "last" && ss)
				{
					int n;
					ss >> n;
					handle_sum_last(n);
				}
				else if (sub_cmd == "from" && ss)
				{
					int m, n;
					std::string to_str;
					ss >> m >> to_str >> n;
					if (to_str == "to")
						handle_sum_range(m, n);
					else
						std::cerr
						    << "Invalid range format. Use: sum from M to N"
						    << std::endl;
				}
				else
				{
					std::cerr << "Invalid sum command." << std::endl;
				}
			}
			else if (command == "customsql")
			{
				std::string rest_of_line;
				std::getline(ss, rest_of_line);
				rest_of_line.erase(0, rest_of_line.find_first_not_of(" \t\n\r\f\v"));
				handle_custom_sql(rest_of_line);
			}
			else if (command == "exit")
			{
				break;
			}
			else if (!command.empty())
			{
				std::cerr << "Unknown command: " << command << std::endl;
			}
		}
		catch (const std::exception &e)
		{
			std::cerr << "Error: " << e.what() << std::endl;
		}

		std::cout << "Leaderboard CLI> " << std::flush;
	}
	return 0;
}

// --- Core Logic Implementations ---

// Executes a command and gets its output
std::string exec(const char *cmd)
{
	std::array<char, 128> buffer;
	std::string result;
	std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
	if (!pipe)
	{
		throw std::runtime_error("popen() failed!");
	}
	while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr)
	{
		result += buffer.data();
	}
	return result;
}

// Function to call the Java DB connector
std::string exec_java(const std::vector<std::string> &args)
{
	std::string cmd = "java -cp .:mysql-connector-j-8.0.33/mysql-connector-j-8.0.33.jar DBConnector";
	for (const auto &arg : args)
	{
		cmd += " \"" + arg + "\"";
	}
	return exec(cmd.c_str());
}


// Fetches all data from DB and rebuilds the segment tree
void refresh_data()
{
	leaderboard_data.clear();
	user_id_to_index.clear();
	std::string result = exec_java({"get_all"});
	std::stringstream ss(result);
	std::string line;
	while (std::getline(ss, line))
	{
		std::stringstream line_ss(line);
		User u;
		line_ss >> u.id;
		line_ss.ignore(); // ignore the space after id
		std::getline(line_ss, u.name, '\t'); // read name until tab
		line_ss >> u.score;
		leaderboard_data.push_back(u);
	}

	// Sort by score descending for ranking
	std::sort(leaderboard_data.begin(), leaderboard_data.end(),
	          [](const User &a, const User &b) { return a.score > b.score; });

	for (size_t i = 0; i < leaderboard_data.size(); ++i)
	{
		user_id_to_index[leaderboard_data[i].id] = i;
	}

	seg_tree = std::make_unique<SegmentTree>(leaderboard_data);
}

// --- Output Formatting ---
void print_header(const std::string &title)
{
	std::cout << "================== " << title
	          << " ==================" << std::endl;
	std::cout << std::left << std::setw(8) << "Rank" << std::setw(12)
	          << "User ID" << std::setw(20) << "Name" << std::setw(10) << "Score" << std::endl;
	std::cout << "---------------------------------------------------" << std::endl;
}

void print_footer()
{
	std::cout << "===================================================" << std::endl;
}

void print_users(const std::vector<User> &users, int start_rank)
{
	if (users.empty())
	{
		std::cout << "=== No dataset available ===" << std::endl;
		return;
	}
	for (size_t i = 0; i < users.size(); ++i)
	{
		std::cout << std::left << std::setw(8) << start_rank + i
		          << std::setw(12) << users[i].id << std::setw(20) << users[i].name << std::setw(10)
		          << users[i].score << std::endl;
	}
}

// --- Command Handlers ---

void handle_generate(int n)
{
	std::cout << "Generating " << n << " random users..." << std::endl;
	exec_java({"generate", std::to_string(n)});
	refresh_data();
	std::cout << "Dataset generated and loaded." << std::endl;
}

void handle_top(int n)
{
	print_header("Top " + std::to_string(n) + " Players");
	if (leaderboard_data.empty())
	{
		std::cout << "=== No dataset available ===" << std::endl;
	}
	else
	{
		std::vector<User> top_users;
		for (int i = 0; i < std::min((int)leaderboard_data.size(), n); ++i)
		{
			top_users.push_back(leaderboard_data[i]);
		}
		print_users(top_users, 1);
	}
	print_footer();
}

void handle_last(int n)
{
	print_header("Last " + std::to_string(n) + " Players");
	if (leaderboard_data.empty())
	{
		std::cout << "=== No dataset available ===" << std::endl;
	}
	else
	{
		std::vector<User> last_users;
		int size = leaderboard_data.size();
		for (int i = 0; i < std::min(size, n); ++i)
		{
			last_users.push_back(leaderboard_data[size - 1 - i]);
		}
		std::reverse(last_users.begin(), last_users.end());
		print_users(last_users, size - last_users.size() + 1);
	}
	print_footer();
}

void handle_range(int m, int n)
{
	print_header("Players Ranked " + std::to_string(m) + " to " +
	             std::to_string(n));
	if (leaderboard_data.empty())
	{
		std::cout << "=== No dataset available ===" << std::endl;
	}
	else if (m > n || m < 1)
	{
		std::cerr << "Invalid rank range." << std::endl;
	}
	else
	{
		std::vector<User> range_users;
		for (int i = m - 1; i < std::min((int)leaderboard_data.size(), n); ++i)
		{
			range_users.push_back(leaderboard_data[i]);
		}
		print_users(range_users, m);
	}
	print_footer();
}

void handle_sum_top(int n)
{
	print_header("Sum of Top " + std::to_string(n) + " Scores");
	if (leaderboard_data.empty())
	{
		std::cout << "=== No dataset available ===" << std::endl;
	}
	else
	{
		long long sum = seg_tree->query_sum(
		    0, std::min((int)leaderboard_data.size(), n) - 1);
		std::cout << "Total Score: " << sum << std::endl;
	}
	print_footer();
}

void handle_sum_last(int n)
{
	print_header("Sum of Last " + std::to_string(n) + " Scores");
	if (leaderboard_data.empty())
	{
		std::cout << "=== No dataset available ===" << std::endl;
	}
	else
	{
		int size = leaderboard_data.size();
		long long sum = seg_tree->query_sum(std::max(0, size - n), size - 1);
		std::cout << "Total Score: " << sum << std::endl;
	}
	print_footer();
}

void handle_sum_range(int m, int n)
{
	print_header("Sum of Scores from Rank " + std::to_string(m) + " to " +
	             std::to_string(n));
	if (leaderboard_data.empty())
	{
		std::cout << "=== No dataset available ===" << std::endl;
	}
	else if (m > n || m < 1)
	{
		std::cerr << "Invalid rank range." << std::endl;
	}
	else
	{
		long long sum = seg_tree->query_sum(
		    m - 1, std::min((int)leaderboard_data.size(), n) - 1);
		std::cout << "Total Score: " << sum << std::endl;
	}
	print_footer();
}

void handle_update(int id, int score)
{
	std::cout << "Updating user " << id << " with score " << score << "..." << std::endl;
	std::string result =
	    exec_java({"update", std::to_string(id), std::to_string(score)});
	std::cout << result;
	refresh_data();
}

void handle_add(int id, const std::string &name, int score)
{
	std::cout << "Adding user " << name << " with score " << score << "..." << std::endl;
	std::string result =
	    exec_java({"add", std::to_string(id), name, std::to_string(score)});
	std::cout << result;
	refresh_data();
}

void handle_delete(int id)
{
	std::cout << "Deleting user " << id << "..." << std::endl;
	std::string result = exec_java({"delete", std::to_string(id)});
	std::cout << result;
	refresh_data();
}

void handle_custom_sql(std::string full_query)
{
    if (full_query.empty()) {
        std::cout << "Enter custom SQL query (end with ';'):" << std::endl;
        std::string query_line;
        std::cout << "SQL> ";
        while (std::getline(std::cin, query_line))
        {
            full_query += query_line + " ";
            if (query_line.find(';') != std::string::npos)
            {
                break;
            }
            std::cout << "  -> ";
        }
    }

	std::cout << "Executing query..." << std::endl;
	std::string result = exec_java({"customsql", full_query});
	print_header("Custom Query Result");
	std::cout << result;
	print_footer();
}

