package engine

import "p2pressure/internal/model"

var weights = map[string]int{
	"PushEvent":         3,
	"PullRequestEvent":  5,
	"IssueCommentEvent": 1,
}

func Score(data map[string][]model.Event) map[string]int {
	result := make(map[string]int)

	for user, events := range data {
		score := 0

		for _, e := range events {
			if w, ok := weights[e.Type]; ok {
				score += w
			}
		}

		result[user] = score
	}

	return result
}
