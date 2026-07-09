package main

import (
	"context"
	"log"
	"log/slog"

	// temporal constants
	"temporal/hello/constants"

	// workflows
	"temporal/hello/say_hello"
	say_hello_wf "temporal/hello/say_hello/workflow"

	// temporal system stuff
	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/worker"
	"go.temporal.io/sdk/workflow"
)

func main() {
	// this will also set options used by slog
	log.SetFlags(log.LstdFlags | log.Lmicroseconds)
	log.SetPrefix("[worker] ")
	slog.SetLogLoggerLevel(slog.LevelDebug)

	ctx := context.Background()

	cli, err := client.DialContext(ctx, client.Options{
		HostPort: constants.SERVER_ADDRESS,
		Logger:   slog.Default(),
	})
	if err != nil {
		log.Fatalf("could not start client: %v", err)
	}
	defer cli.Close()

	w := worker.New(cli, constants.TASK_QUEUE_NAME, worker.Options{
		EnableLoggingInReplay: true,
	})

	w.RegisterActivity(say_hello_wf.SayHello)
	w.RegisterActivity(say_hello_wf.Uppercase)
	w.RegisterActivity(say_hello_wf.AddExclamation)

	// w.RegisterWorkflow(say_hello_wf.SayHelloWorkflow)
	w.RegisterWorkflowWithOptions(say_hello_wf.SayHelloWorkflow, workflow.RegisterOptions{Name: say_hello.WORKFLOW_NAME})
	w.RegisterWorkflowWithOptions(say_hello_wf.SayHelloWorkflow, workflow.RegisterOptions{Name: "say_hello.workflow"})

	log.Printf("worker starting\n")

	err = w.Run(worker.InterruptCh())
	if err != nil {
		log.Fatalf("failed to start worker: %v", err)
	}
}
