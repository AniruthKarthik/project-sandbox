package engine

type PressureResult struct {
	Pressure int
	Active   bool
	Others   int
	Self     int
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
