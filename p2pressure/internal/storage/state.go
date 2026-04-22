package storage

import (
	"encoding/json"
	"os"
	"time"
)

type State struct {
	LastEventID        map[string]string `json:"last_event_id"`
	LastSelfCommitTime time.Time         `json:"last_self_commit_time"`
}

func NewState() *State {
	return &State{
		LastEventID:        make(map[string]string),
		LastSelfCommitTime: time.Time{},
	}
}

func Load(path string) (*State, error) {
	file, err := os.Open(path)
	if err != nil {
		return NewState(), nil
	}

	defer file.Close()

	var s State
	if err := json.NewDecoder(file).Decode(&s); err != nil {
		return &s, nil
	}

	if s.LastEventID == nil {
		s.LastEventID = make(map[string]string)
	}

	return &s, nil
}

func (s *State) Save(path string) error {
	file, err := os.Create(path)
	if err != nil {
		return nil
	}

	defer file.Close()

	return json.NewEncoder(file).Encode(s)
}
