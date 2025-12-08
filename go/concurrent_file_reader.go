package main

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"strconv"
	"sync"
	"time"
)

func FindMaxProblem1() {
	ch := make(chan string, 5)

	go func() {
		var wg sync.WaitGroup

		for i := 0; i < 5; i++ {
			wg.Add(1)
			go func(ch chan<- string, i int) {
				defer wg.Done()
				msg := fmt.Sprintf("Goroutine %s", strconv.Itoa(i))
				ch <- msg
			}(ch, i)
		}
		wg.Wait()
		close(ch)
	}()

	for q := range ch {
		fmt.Println(q)
	}

	// for {
	// 	select {
	// 	case q, ok := <-ch:
	// 		fmt.Printf("%v %v\n", q, ok)
	// 		if !ok {
	// 			break // breaks 'case', not for
	// 		}
	// 	}
	// }
}

func readFileProducer(ctx context.Context, filename string) (<-chan string, <-chan error) {
	c := make(chan string)
	errc := make(chan error, 1) // buffered to make sure we can send errors without blocking

	go func() {
		defer close(errc)
		defer close(c)

		f, err := os.Open(filename)
		if err != nil {
			errc <- err
			return
		}
		defer f.Close()

		scanner := bufio.NewScanner(f)
		for scanner.Scan() {
			select {
			case <-ctx.Done():
				errc <- ctx.Err()
				return // return here as next send to error might block
			case c <- scanner.Text():
				// line is sent
			}
			time.Sleep(1 * time.Millisecond)
		}

		errc <- scanner.Err()
	}()

	return c, errc
}

func readFileConcurrently(ctx context.Context, filename string, concurrency int, handler func(string)) error {
	c, errc := readFileProducer(ctx, filename)

	var wg sync.WaitGroup
	for range concurrency {
		wg.Add(1)
		go func() {
			defer wg.Done()

		outerLoop:
			for {
				select {
				case <-ctx.Done():
					return
				case s, ok := <-c:
					if !ok {
						break outerLoop
					}
					handler(s)
				}
			}
		}()
	}

	wg.Wait()

	err := <-errc
	if err != nil {
		// if errors.Is(err, os.ErrNotExist) {
		if patherr, ok := err.(*os.PathError); ok {
			fmt.Printf("error: file does not exist: %v\n", patherr)
		} else {
			fmt.Printf("error: %v\n", err)
		}
	}
	return err
}

func main() {
	FindMaxProblem1()

	ctx := context.Background()
	ctx, cancel := context.WithTimeout(ctx, 100*time.Millisecond)
	defer cancel()

	readFileConcurrently(ctx, "1.go", 3, func(str string) {
		// these strings are processed by goroutines concurrently
		// so not guaranteed to be in order
		// reading from the channel is in order across goroutines, printing is not
		fmt.Printf("got string: %s\n", str)
	})
}
