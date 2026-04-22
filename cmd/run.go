package cmd

import (
	"fmt"
	"p2pressure/internal/engine"
	"p2pressure/internal/github"
	"p2pressure/internal/model"
	"p2pressure/internal/poller"
	"p2pressure/internal/storage"
	"time"
)

var (
	stateFile = "state.json"

	trackedUsers = []string{
		"adithya-menon-r",
		"Dakshin10",
	}

	selfUser = "AniruthKarthik"
)

func start(watch bool) {
	client := github.NewClient()
	poller := poller.NewPoller(client)

	state, err := storage.Load(stateFile)
	if err != nil {
		panic(err)
	}

	if !watch {
		runCycle(poller, state)
		state.Save(stateFile)
		return
	}

	fmt.Println("monitor loop started")
	for {
		runCycle(poller, state)
		state.Save(stateFile)
		time.Sleep(15 * time.Minute)
	}
}

func runCycle(p *poller.Poller, state *storage.State) {
	fmt.Println("running cycle...")

	// 1. fetch
	users := append(trackedUsers, selfUser)
	data := p.Poll(users)

	// Detect first runs before FilterNewEvents updates LastEventID
	isFirstRun := make(map[string]bool)
	for _, user := range users {
		if state.LastEventID[user] == "" {
			isFirstRun[user] = true
		}
	}

	// 2. dedup
	newEvents := engine.FilterNewEvents(data, state)

	// Apply 24h filter ONLY for first-run users
	firstRuns := make(map[string][]model.Event)
	for user, events := range newEvents {
		if isFirstRun[user] {
			firstRuns[user] = events
		}
	}

	filteredFirstRuns := engine.FilterRecent(firstRuns)

	// Update newEvents with filtered results for first-run users
	for user, events := range filteredFirstRuns {
		newEvents[user] = events
	}

	// 2.5 print events
	for user, events := range newEvents {
		if len(events) > 0 {
			fmt.Printf("Events for %s:\n", user)
			for _, e := range events {
				fmt.Printf("  - [%s] %s (%s)\n", e.CreatedAt.Format(time.RFC3339), e.Type, e.ID)
			}
		}
	}

	// 3. scoring
	scores := engine.Score(newEvents)

	// 4. pressure
	result := engine.ComputePressure(scores, selfUser)

	// 5. output
	if result.Active {
		fmt.Printf(
			"PRESSURE: others=%d self=%d diff=%d\n",
			result.Others,
			result.Self,
			result.Pressure,
		)
	} else {
		fmt.Println("no pressure")
	}
}
