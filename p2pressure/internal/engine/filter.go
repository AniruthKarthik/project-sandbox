package engine

import (
	"p2pressure/internal/model"
	"time"
)

// FilterRecent returns events that occurred within the last 24 hours.
func FilterRecent(data map[string][]model.Event) map[string][]model.Event {
	cutoff := time.Now().Add(-24 * time.Hour)
	result := make(map[string][]model.Event)

	for user, events := range data {
		var filtered []model.Event
		for _, e := range events {
			if e.CreatedAt.After(cutoff) || e.CreatedAt.Equal(cutoff) {
				filtered = append(filtered, e)
			}
		}
		result[user] = filtered
	}

	return result
}
