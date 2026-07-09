package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"temporal/hello/constants"
	"temporal/hello/say_hello" // knows only about args, but doesn't know workflow implementation details

	"go.temporal.io/sdk/client"
)

type Args struct {
	wf_args say_hello.Args
}

func parseCommandLineOrExit() Args {
	if len(os.Args) < 2 {
		log.Fatalf("usage: start <name> [options]")
	}

	args := Args{
		wf_args: say_hello.Args{
			Name:             os.Args[1],
			Uppercase:        true,
			ExclamationCount: 3,
		},
	}

	fs := flag.NewFlagSet("", flag.ContinueOnError)
	fs.BoolVar(&args.wf_args.Uppercase, "u", false, "uppercase the greeting string")
	fs.IntVar(&args.wf_args.ExclamationCount, "e", 1, "number of exclamation marks to add, 0 to disable")

	err := func() error {
		if strings.HasPrefix(os.Args[1], "-") {
			return fmt.Errorf("first arg must be a name to greet, have an arg %s\n", os.Args[1])
		}
		if err := fs.Parse(os.Args[2:]); err != nil {
			return err
		}
		if len(fs.Args()) > 0 {
			return fmt.Errorf("unexpected extra positional args %v\n", fs.Args())
		}
		return nil
	}()
	if err != nil {
		fmt.Fprintf(os.Stderr, "ERROR: %s\n", err)
		fs.Usage()
		os.Exit(1)
	}

	return args
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lmicroseconds)

	args := parseCommandLineOrExit()

	ctx, cancel := context.WithTimeout(context.Background(), 5000*time.Millisecond)
	defer cancel()

	log.Printf("connecting to temporal server\n")

	dialCtx, dialCancel := context.WithTimeout(ctx, 100*time.Millisecond)
	defer dialCancel()

	cli, err := client.DialContext(dialCtx, client.Options{HostPort: constants.SERVER_ADDRESS})
	if err != nil {
		log.Fatalf("failed to start client: %v", err)
	}
	defer cli.Close()

	wopt := client.StartWorkflowOptions{
		// only one workflow with this ID can exist concurrently
		// Doc:
		//  The primary purpose of a Temporal Workflow ID is to serve as a business-level uniqueness constraint.
		//  By assigning a meaningful identifier (like an order number or customer ID),
		//  you ensure that only one open workflow with that specific ID exists at a time,
		//  preventing duplicate processing.
		ID:        fmt.Sprintf("say_hello_%s_%t_%d", args.wf_args.Name, args.wf_args.Uppercase, args.wf_args.ExclamationCount),
		TaskQueue: constants.TASK_QUEUE_NAME,
	}

	// we, err := cli.ExecuteWorkflow(ctx, wopt, hello.SayHelloWorkflow, args)
	we, err := cli.ExecuteWorkflow(ctx, wopt, say_hello.WORKFLOW_NAME, args.wf_args)
	if err != nil {
		log.Fatalf("failed to execute workflow: %v", err)
	}

	log.Printf("started workflow %v, run_id: %v\n", we.GetID(), we.GetRunID())

	var result string
	err = we.Get(ctx, &result)
	if err != nil {
		log.Fatalf("failed to get workflow result: %v", err)
	}

	log.Printf("got workflow result %q\n", result)
}
