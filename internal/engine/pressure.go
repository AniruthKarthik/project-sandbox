package engine

import (
	"fmt"
	"p2pressure/internal/model"
	"time"
)

type PressureResult struct {
	Pressure int
	Active   bool
	Others   int
	Self     int
}

type AfterMeReport struct {
	Count      int
	LatestUser string
}

func ComputePressure(scores map[string]int, self string) PressureResult {
	var othersTotal int
	var selfScore int

	for user, score := range scores {
		if user == self {
			selfScore = score
			continue
		}
		othersTotal += score
	}

	pressure := othersTotal - selfScore

	active := false
	if othersTotal > 0 && selfScore == 0 {
		active = true
	}

	return PressureResult{
		Pressure: pressure,
		Active:   active,
		Others:   othersTotal,
		Self:     selfScore,
	}
}

func AnalyzeAfterMe(allEvents map[string][]model.Event, self string, lastSelfTime time.Time) AfterMeReport {
	if lastSelfTime.IsZero() {
		lastSelfTime = time.Now().Add(-24 * time.Hour)
	}
	report := AfterMeReport{}
	var newestOtherTime time.Time

	for user, events := range allEvents {
		if user == self {
			continue
		}

		for _, e := range events {
			if e.Type == "PushEvent" && e.CreatedAt.After(lastSelfTime) {
				report.Count++
				if e.CreatedAt.After(newestOtherTime) {
					newestOtherTime = e.CreatedAt
					report.LatestUser = user
				}
			}
		}
	}
	return report
}

func GetMessage(report AfterMeReport) string {
	if report.Count == 0 {
		return "✅ You are doing good, good to go!"
	}

	switch {
	case report.Count > 10:
		return fmt.Sprintf("💀 CRITICAL: %d COMMITS SINCE YOUR LAST ONE! ARE YOU EVEN WORKING?!", report.Count)
	case report.Count > 5:
		return fmt.Sprintf("⚠️ You're falling behind! %d commits have been made since your last. %s is leaving you in the dust.", report.Count, report.LatestUser)
	case report.Count == 1:
		return fmt.Sprintf("👀 %s has made a commit, what about u?", report.LatestUser)
	default:
		return fmt.Sprintf("🚩 %d commits have been made by others since your last one. Take a lead?", report.Count)
	}
}
