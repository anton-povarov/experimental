package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type Effector func(context.Context) (string, error)

func Throttle(e Effector, max uint, refill uint, d time.Duration) Effector {
	var tokens = max
	var once sync.Once
	return func(ctx context.Context) (string, error) {
		if ctx.Err() != nil {
			return "", ctx.Err()
		}
		once.Do(
			func() {
				ticker := time.NewTicker(d)
				go func() {
					defer ticker.Stop()
					for {
						select {
						case <-ctx.Done():
							return
						case <-ticker.C:
							tokens = min(tokens+refill, max)
						}
					}
				}()
			},
		)
		if tokens <= 0 {
			return "", fmt.Errorf("too many calls")
		}
		tokens--
		return e(ctx)
	}
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	e := func(ctx context.Context) (string, error) {
		return "Hello, World!", nil
	}

	throttled := Throttle(e, 2, 1, 1*time.Second)

	for range 5 {
		result, err := throttled(ctx)
		if err != nil {
			fmt.Println(err)
			continue
		}
		fmt.Println(result)
	}
}
