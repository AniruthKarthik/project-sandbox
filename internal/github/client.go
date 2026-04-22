package github

import (
	"encoding/json"
	"fmt"
	"net/http"
	"p2pressure/internal/model"
	"time"
)

type Client struct {
	BaseURL string
}

func NewClient() *Client {
	return &Client{
		BaseURL: "https://api.github.com",
	}
}

type githubEvent struct {
	ID        string `json:"id"`
	Type      string `json:"type"`
	CreatedAt string `json:"created_at"`
}

func (c *Client) FetchEvents(username string) ([]model.Event, error) {
	url := fmt.Sprintf("%s/users/%s/events", c.BaseURL, username)

	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed: %s", resp.Status)
	}

	var raw []githubEvent
	if err := json.NewDecoder(resp.Body).Decode(&raw); err != nil {
		return nil, err
	}

	var events []model.Event

	for _, e := range raw {
		t, err := time.Parse(time.RFC3339, e.CreatedAt)
		if err != nil {
			continue
		}

		events = append(events, model.Event{
			ID:        e.ID,
			Type:      e.Type,
			CreatedAt: t,
		})
	}

	return events, nil
}
