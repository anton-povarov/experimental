package say_hello_wf

import (
	"time"

	"temporal/hello/say_hello"

	"go.temporal.io/sdk/temporal"
	"go.temporal.io/sdk/workflow"
)

func SayHelloWorkflow(ctx workflow.Context, args say_hello.Args) (string, error) {
	ao := workflow.ActivityOptions{
		StartToCloseTimeout: 10 * time.Second,
	}
	ctx = workflow.WithActivityOptions(ctx, ao)

	var result string
	var err error

	// this is a "remote" activity, executed via the Temporal server
	err = workflow.ExecuteActivity(ctx, SayHello, args.Name).Get(ctx, &result)
	if err != nil {
		return "", err
	}

	if args.Uppercase {
		{ // prevent activity options leaking to later invocations through `ctx`

			// [!] we need fast retries here, so run activity as Local
			retryPolicy := &temporal.RetryPolicy{
				InitialInterval:    1 * time.Millisecond,
				BackoffCoefficient: 5.0,                    // 1 -> 5 -> 25 -> 125 -> 625ms
				MaximumInterval:    500 * time.Millisecond, // caps out at 4 attempts
				MaximumAttempts:    10,
			}

			ctx := workflow.WithLocalActivityOptions(
				ctx,
				workflow.LocalActivityOptions{
					RetryPolicy: retryPolicy,

					// single run timeout
					// for Local Activity - this seems to include all the retry waits
					// i.e. observed
					// attempt1 has ~36ms budget
					// attempt2 has ~34ms budget (retry 1, 1ms retry interval + some execution time spent)
					// attempt3 has ~28ms budget (retry 2, 1ms from attempt1 + 5ms retry interval)
					// attempt4 has ~2ms budget  (retry 3, 1ms from attempt1 + 5ms attempt2 + 25ms attempt3)
					StartToCloseTimeout: 36 * time.Millisecond,
				},
			)
			err := workflow.ExecuteLocalActivity(ctx, Uppercase, result).Get(ctx, &result)
			if err != nil {
				return result, err
			}
		}
	}

	if args.ExclamationCount > 0 {
		err = workflow.ExecuteActivity(ctx, AddExclamation, result, args.ExclamationCount).Get(ctx, &result)
		if err != nil {
			return result, err
		}
	}

	return result, nil
}
