#ifndef SEGMENT_TREE_H
#define SEGMENT_TREE_H

#include <string>
#include <vector>

struct User
{
	int id;
	int score;
	std::string name;
};

class SegmentTree {
  public:
	SegmentTree(const std::vector<User> &users);

	void update(int index, int new_score);

	long long query_sum(int l, int r);

  private:
	std::vector<long long> tree;
	std::vector<User> users;
	int n;

	void build(int node, int start, int end);

	void update_tree(int node, int start, int end, int idx, int val);

	long long query_tree_sum(int node, int start, int end, int l, int r);
};

#endif
