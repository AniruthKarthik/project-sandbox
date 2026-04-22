package main

import (
	"log"
	"p2pressure/cmd"
)

func main() {
	if err := cmd.Execute; err != nil {
		log.Fatal(err)
	}
}
