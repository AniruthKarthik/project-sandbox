package main

import (
	"fmt"
	"os"
	"p2pressure/cmd"
)

func main() {
	if err := cmd.Execute(); err != nil {
		fmt.Println("ERROR:", err)
		os.Exit(1)
	}
}
