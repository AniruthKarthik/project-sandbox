package model

import "time"

type Event struct {
	ID        string
	Type      string
	CreatedAt time.Time
}
