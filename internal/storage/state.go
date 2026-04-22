package storage

import (
	"encoding/json"
	"os"
)

type State struct {
	LastEventID map[string]string `json:"last_event_id"`
}

func NewState() *State {
	return &State{
		LastEventID: make(map[string]string),
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
