package testutil

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/fatih/color"
)

func isOK[T any](result, expected T) bool {
	return reflect.DeepEqual(result, expected)
}

func isOKStr[T any](result, expected T) string {
	if reflect.DeepEqual(result, expected) {
		return "OK"
	}
	return "ERROR"
}

type TestData[T any, E any] struct {
	Input    T
	Expected E
}

func RunTest[T any, E any](t *testing.T, testedFunc func(T) E, data []TestData[T, E]) {
	green := color.New(color.FgGreen)
	red := color.New(color.FgHiRed)

	results := make([]E, len(data))

	for i, d := range data {
		result := testedFunc(d.Input)
		results[i] = result

		clr := func() *color.Color {
			if reflect.DeepEqual(result, d.Expected) {
				return green
			}
			return red
		}()

		clr.EnableColor() // this is required as go test does shenanigans with colored output
		fmt.Fprintln(t.Output(),
			clr.Sprintf("[%s] %#v -> %#v, expected: %#v", isOKStr(result, d.Expected), d.Input, result, d.Expected))
		clr.DisableColor()
	}

	for i, d := range data {
		if !reflect.DeepEqual(results[i], d.Expected) {
			t.FailNow()
		}
	}
}
