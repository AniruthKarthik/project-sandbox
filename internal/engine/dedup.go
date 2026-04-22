package engine

import (
	"p2pressure/internal/model"
	"p2pressure/internal/storage"
)

func FilterNewEvents(
	data map[string][]model.Event,
	state *storage.State,
) map[string][]model.Event {

	result := make(map[string][]model.Event)

	for user, events := range data {
		lastID := state.LastEventID[user]

		var fresh []model.Event

		for _, e := range events {
			if e.ID == lastID {
				break
			}
			fresh = append(fresh, e)
		}

		if len(events) > 0 {
			state.LastEventID[user] = events[0].ID
		}

		result[user] = fresh
	}

	return result
}
