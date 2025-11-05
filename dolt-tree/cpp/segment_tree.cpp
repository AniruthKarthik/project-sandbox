#include "segment_tree.h"
#include <iostream>

SegmentTree::SegmentTree(const std::vector<User> &initial_users)
{
	users = initial_users;
	n = users.size();
	if (n > 0)
	{
		tree.resize(4 * n);
		build(1, 0, n - 1);
	}
}

void SegmentTree::build(int node, int start, int end)
{
	if (start == end)
	{
		tree[node] = users[start].score;
	}
	else
	{
		int mid = (start + end) / 2;
		build(2 * node, start, mid);
		build(2 * node + 1, mid + 1, end);
		tree[node] = tree[2 * node] + tree[2 * node + 1];
	}
}

void SegmentTree::update(int index, int new_score)
{
	if (index < 0 || index >= n)
	{
		std::cerr << "Error: Invalid index for update." << std::endl;
		return;
	}
	int old_score = users[index].score;
	users[index].score = new_score;
	update_tree(1, 0, n - 1, index, new_score - old_score);
}

void SegmentTree::update_tree(int node, int start, int end, int idx, int diff)
{
	if (start == end)
	{
		tree[node] += diff;
		return;
	}
	int mid = (start + end) / 2;
	if (start <= idx && idx <= mid)
	{
		update_tree(2 * node, start, mid, idx, diff);
	}
	else
	{
		update_tree(2 * node + 1, mid + 1, end, idx, diff);
	}
	tree[node] = tree[2 * node] + tree[2 * node + 1];
}

long long SegmentTree::query_sum(int l, int r)
{
	if (n == 0 || l > r || l < 0 || r >= n)
	{
		return 0;
	}
	return query_tree_sum(1, 0, n - 1, l, r);
}

long long SegmentTree::query_tree_sum(int node, int start, int end, int l,
                                      int r)
{
	if (r < start || end < l)
	{
		return 0;
	}
	if (l <= start && end <= r)
	{
		return tree[node];
	}
	int mid = (start + end) / 2;
	long long p1 = query_tree_sum(2 * node, start, mid, l, r);
	long long p2 = query_tree_sum(2 * node + 1, mid + 1, end, l, r);
	return p1 + p2;
}
