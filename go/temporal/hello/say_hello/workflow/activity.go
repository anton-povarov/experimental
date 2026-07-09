package say_hello_wf

import (
	"context"
	"fmt"
	"strings"
	"time"

	"go.temporal.io/sdk/activity"
)

func SayHello(ctx context.Context, name string) (string, error) {
	return fmt.Sprintf("hello %s", name), nil
}

func Uppercase(ctx context.Context, message string) (string, error) {
	info := activity.GetInfo(ctx)
	attempt := info.Attempt
	time_allocated := info.Deadline.Sub(info.StartedTime)
	timeout := time.Until(info.Deadline)

	logger := activity.GetLogger(ctx)
	logger.Debug(fmt.Sprintf("--- executing UPPERCASE [attempt %d, t_alloc: %v, timeout: %v] --- ", attempt, time_allocated, timeout))

	if attempt <= 3 {
		// return "", temporal.NewApplicationErrorWithOptions(
		// 	"random failure injected",
		// 	"NextDelay", temporal.ApplicationErrorOptions{
		// 		NextRetryDelay: 1 * time.Millisecond,
		// 	})

		return "", fmt.Errorf("random failure injected")
	}

	return strings.ToUpper(message), nil
}

func AddExclamation(ctx context.Context, message string, count int) (string, error) {
	return message + strings.Repeat("!", count), nil
}
