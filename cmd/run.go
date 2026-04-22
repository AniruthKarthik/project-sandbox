package cmd

import (
	"fmt"
	"time"
)

func start() {
	fmt.Println("monitor loop started")

	for {
		runCycle()
		time.Sleep(15 * time.Minute)
	}
}

func runCycle() {
	fmt.Println("running cycle....")
}
