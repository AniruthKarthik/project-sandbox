package poller

import (
	"p2pressure/internal/github"
	"p2pressure/internal/model"
)

type Poller struct {
	client *github.Client
}

func NewPoller(client *github.Client) *Poller {
	return &Poller{client: client}
}

func (p *Poller) Poll(users []string) map[string][]model.Event {
	res := make(map[string][]model.Event)

	for _, user := range users {
		events, err := p.client.FetchEvents(user)
		if err != nil {
			continue
		}
		res[user] = events
	}

	return res
}
