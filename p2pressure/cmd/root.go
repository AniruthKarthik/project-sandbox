package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
)

var rootCmnd = &cobra.Command{
	Use:   "p2pressure",
	Short: "github activity notifier",
}

var watch bool

var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Start monitoring loop",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("starting p2pressure")
		start(watch)

	},
}

func Execute() error {
	return rootCmnd.Execute()
}

func init() {
	rootCmnd.AddCommand(runCmd)
	runCmd.Flags().BoolVarP(&watch, "watch", "w", false, "Run continuously in a loop")
}
